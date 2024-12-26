from datetime import datetime
import io
import base64

from flask import Blueprint, session, request, redirect, render_template, url_for
from flask_session import Session
from werkzeug.utils import secure_filename

from random import randint, uniform

import config
from config import app_vars
from joker import sql

page_home_bp = Blueprint("index", __name__, template_folder="templates")


@page_home_bp.route('/', methods=['GET', 'POST'])
def index():
    config_html = {
        "rodape": config.app_vars.rodape,
        "itens": config.person_function.retornar_values(tabela="produtos")
    }
    session["link_payment"] = None

    # print(config_html)

    if request.method == "POST":
        links = {
            "8": "https://mpago.la/1nsf4sY",
            "16": "https://mpago.la/2NvYbej",
            "24": "https://mpago.la/17UkVnV",
            "32": "https://mpago.la/23sAU46",
            "40": "https://mpago.la/2SmmL8h",
            "48": "https://mpago.la/2aEEMVK",
            "56": "https://mpago.la/2nkHwhn",
            "64": "https://mpago.la/2uR4i7U",
            "72": "https://mpago.la/2wk1v3s",
            "80": "https://mpago.la/2XPmYUQ",
            "88": "https://mpago.la/1UcxsDu",
            "96": "https://mpago.la/1s2vRGi",
            "104": "https://mpago.la/17rsKGd",
            "whatsapp": "https://web.whatsapp.com/send/?phone=5511970843369&text=Olá,Tive%20problemas%20com%20meu%20Pedido%20de%20Delícias%20Gourmet...&type=phone_number&app_absent=0"
        }

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
        pagamentoOnline = request.form["pagamentoOnline"]
        total = request.form["total"]

        dadosCLiente = [telefone, nome, formaEntrega, metodoPagamento,
                        cep, rua, numero, complemento,cidade,
                        resumo,
                        pagamentoOnline,
                        total]
        url = links[f"{total}"] if f"{total}" in links.keys() else links["whatsapp"]

    return render_template("index.html", html=config_html)
