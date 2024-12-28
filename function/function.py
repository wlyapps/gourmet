import csv
from datetime import datetime
import io
import base64

import requests
from flask import Blueprint, session, request, redirect, render_template, jsonify, url_for, send_file
from flask_session import Session
from werkzeug.utils import secure_filename

from random import randint, uniform

import config
from config import app_vars
from joker import sql

page_function_bp = Blueprint("function", __name__, template_folder="templates")

@page_function_bp.route('/function', methods=['GET', 'POST'])
def function():
    config_html = {
        "html": "",
        "tag": "",
    }

    page = request.args.get("page")
    pedido = request.args.get("pedido")
    telefone = request.args.get("telefone")

    if page == "consulta":
        if pedido:
            status_pedido = config.person_function.retornar_values(tabela="pedidos",
                                                                   person_command=f"""
                                                                   SELECT * FROM pedidos
                                                                   WHERE id = {pedido} 
                                                                   AND status != 'Finalizado'
            """)

            if status_pedido:
                config_html["tag"] = "info"
                config_html["html"] = f"""
                <p>Nome: {status_pedido[0][2]}</p>
                <p>Telefone: {status_pedido[0][1]}</p>
                <p>Status: {status_pedido[0][-1]}</p>
                """
            else:
                config_html["tag"] = "info"
                config_html["html"] = f"""
                <p>Não há Pedidos em Aberto!</p>
                """

        else:
            status_pedido = config.person_function.retornar_values(tabela="pedidos",
                                                                   person_command=f"""
                                                                   SELECT * FROM pedidos
                                                                   WHERE telefone = '{telefone}' 
                                                                   AND status != 'Finalizado'
            """)

            if status_pedido:
                config_html["tag"] = "info"
                config_html["html"] = f"""
                <p>Nome: {status_pedido[0][2]}</p>
                <p>Telefone: {status_pedido[0][1]}</p>
                <p>Status: {status_pedido[0][-1]}</p>
                """
            else:
                config_html["tag"] = "info"
                config_html["html"] = f"""
                <p>Não há Pedidos em Aberto para o número informado!</p>
                """

        return jsonify(config_html), 200

    else:
        return redirect(url_for("index.index"))