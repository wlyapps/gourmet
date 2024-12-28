from datetime import datetime, timedelta
import io
import base64
from threading import Thread

import mercadopago
import requests

from flask import Blueprint, session, request, redirect, render_template, url_for
from flask_session import Session
from werkzeug.utils import secure_filename

from random import randint, uniform

import config
from config import app_vars
from joker import sql

page_pedidos_bp = Blueprint("pedidos", __name__, template_folder="templates")


@page_pedidos_bp.route('/pedidos', methods=['GET', 'POST'])
def pedidos():
    session["html_message"] = ""
    config_html = {
        "rodape": config.app_vars.rodape,
        "itens": config.person_function.retornar_values(tabela="produtos"),
        "regioes": ["(Vl S Pedro)"]
    }

    pedido = request.args.get("pedido")

    if request.method == "POST":
        telefone = request.form["telefone"]
        nome = request.form["nome"]
        formaEntrega = request.form["formaEntrega"]
        metodoPagamento = request.form["metodoPagamento"]
        cep = request.form["cep"]
        rua = request.form["rua"]
        numero = request.form["numero"]
        complemento = request.form["complemento"]
        cidade = request.form["cidade"]
        resumo = request.form["resumo"]
        total = request.form["total"]
        pagamentoOnline = request.form["pagamentoOnline"]

        if float(total) < 15.0 and formaEntrega == "Entrega":
            session["html_message"] = '<p style="color: red;">Pedido mínimo para entrega é de 2 itens...</p>'
            return render_template("pedidos.html", html=config_html)
        elif float(total) == 0:
            session["html_message"] = '<p style="color: red;">Selecione pelo menos 1 Sabor...</p>'
            return render_template("pedidos.html", html=config_html)
        else:
            session["html_message"] = ''

        config.person_function.gravar_values(tabela="pedidos",
                                             colunas=["telefone", "nome", "forma_entrega", "metodo_pagamento",
                                                      "endereco", "dados_pedido", "total", "data_cadastro", "status"],
                                             dados=[telefone, nome, formaEntrega, metodoPagamento,
                                                    f"{rua}, {numero} - {complemento} - {cidade} - {cep}",
                                                    resumo, total, datetime.today().strftime("%d/%m/%Y %H:%M:%S"),
                                                    "Pedido Recebido"])

        num_pedido = config.person_function.retornar_values(tabela="pedidos",
                                                            person_command="SELECT MAX(id) FROM pedidos")[0][0]

        email_pedido = Thread(target=config.Email.envia_email_pedido,
                              args=(num_pedido, telefone, nome, formaEntrega, metodoPagamento,
                                    f"{rua}, {numero} - {complemento} - {cidade} - {cep}",
                                    resumo, total, datetime.today().strftime("%d/%m/%Y %H:%M:%S"),
                                    "Pedido Recebido",))
        email_pedido.daemon = True
        email_pedido.start()

        if metodoPagamento == "Pagamento Online":
            idempotency_key = f"{datetime.utcnow().timestamp()}"
            sdk = mercadopago.SDK(config.app_vars.ACCESS_TOKEN)

            request_options = mercadopago.config.RequestOptions()
            request_options.custom_headers = {'x-idempotency-key': idempotency_key}

            payment_data = {
                "items": [
                    {"id": 1, "title": "Gelinho Gourmet", "quantity": 1, "currency_id": "BRL", "unit_price": float(total)}
                ],
                "back_urls": {
                    "success": f"{config.Config.SESSION_DOMINIO}pedidos?pedido={num_pedido}",
                    "failure": f"{config.Config.SESSION_DOMINIO}pedidos?pedido={num_pedido}",
                    "pending": f"{config.Config.SESSION_DOMINIO}pedidos?pedido={num_pedido}"
                },
                "auto_return": "all",
                "transaction_amount": round(float(total), 2),
                "payment_methods": {
                    "default_payment_method_id": "pix",
                    "excluded_payment_types": config.app_vars.exclude_payments,
                    "installments": 1
                }
            }

            payment_response = sdk.preference().create(payment_data, request_options)
            payment = payment_response["response"]
            link_pagamento = payment["init_point"]

            # print(payment)

            return redirect(link_pagamento)
        else:
            return render_template("status.html", html=config_html)


    if pedido:
        config_html["pedido"] = pedido if pedido != "0000" else ""
        return render_template("status.html", html=config_html)
    else:
        return render_template("pedidos.html", html=config_html)