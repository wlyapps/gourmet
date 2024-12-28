import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from joker import sql
from datetime import datetime
import io
import base64
import requests
import difflib


class Config:
    UPLOAD_FOLDER = 'static/etiquetas'
    IMAGE_FOLDER = 'static/images'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

    SECRET_KEY = 'Cpm@123*'
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './data_session/'
    SESSION_DOMINIO = 'https://delicias-w-gourmet.up.railway.app/'

class app_vars:
    # ACCESS_TOKEN = "TEST-4667742724479969-091116-015eb505e94cf5735b49477703f33624-172786625"
    ACCESS_TOKEN = "APP_USR-4667742724479969-091116-7aed5fed6dc44c0dd62f60ceb0411047-172786625"
    MELHOR_ENVIO_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiMWJjNTIxNjVhOGJjMjM4NzcwOTBhNWNiZjY2ZjRlNDExNjRkYjNkMDhmZDgwMjI2YWM5ZDYwOGRlODY0MDU1NzIxZjljNWY1OGY1OTU2NDciLCJpYXQiOjE3Mjk2NDE1OTMuMTQ1ODIzLCJuYmYiOjE3Mjk2NDE1OTMuMTQ1ODI1LCJleHAiOjE3NjExNzc1OTMuMTMzOTMxLCJzdWIiOiI5YjA3NTcyYy1iZjNjLTRlMTEtOGJiZC01ZjU0YmJiNTVlMTkiLCJzY29wZXMiOlsic2hpcHBpbmctY2FsY3VsYXRlIl19.UbggmYDQVvs1OzJQodRJoZsVwKEMWt2B0-eLoIW_3eQehay6Q7_ukcyCZsC4AlPDNwUdN7JKFxGmlKMLOnQCwLOPFOONhzb0T7l2DEZuloZ3re-eCF-HDdNipfTlK1kPv56-fj0J_bGnO6TtK4Q7tPYRtFnDb54Z6y7pXpC2ow_ceibsv9Q1e1qKn9d4ZqK9gB0Pmc1dXgwitpSuG9OixEBJsNm6ClOiXkuecGUK5V70IVxH42dF6UUtCYV5KF33c0oLRPEwzyvab4rX8Gc3XSqOIukYNCKnrgXFue18aYIKmkuoFqrLFAFuelta7EGCHlPFhi-cqlgVGQk95xhvLaStzLsiMiTI3xwZIK1K_4jPaAr_wimDzespM0jyQ0zTAkvgY1NN3qJmxiIFzp8dD7iVT0Q5EA8J3XGc6aR1Js0MbYJpC85N89nKatYnEonPfIa0YDVSkks7zoLuUwuWFy805j7lRZZwYrqOY906Zo6vRnIxLMfm5cdaj1Ab2kh4lyUhIZv3t-SS3D6hFCnr2mRJE43Q0fCjGNfHuSAw5jZs78SqPvG3iH-CgGKNOwj8FbAb8ut5EK77vIxyinrUglddoczQdqzrNQwXnFXNCl7MqFDg6rzXV82MrHo6WLFXlWlawKv1sm75KjXrPzBI0ceCPt1-gDopxDl_qo_sXQ8"
    exclude_payments = [
        {"id": "credit_card"},
        {"id": "debit_card"},
        {"id": "ticket"},
        {"id": "atm"}
    ]

    rodape = {
        "watsapp": "5511970843369",
        "copyriting": "© 2024 Delícias Gourmet. Todos os direitos reservados."
    }

class create_sql:
    def tables(*args):
        # construtor banco de dados
        sql.execute(banco="gelinhos.db", command="""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            preco NUMERIC NOT NULL,
            link_image TEXT NOT NULL,
            estoque NUMERIC NOT NULL,
            data_cadastro TEXT NOT NULL
        );
        """)

        sql.execute(banco="gelinhos.db", command="""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefone NUMERIC NOT NULL,
            nome TEXT NOT NULL,
            forma_entrega TEXT NOT NULL,
            metodo_pagamento TEXT NOT NULL,
            endereco TEXT NOT NULL,
            dados_pedido TEXT NOT NULL,
            total NUMERIC NOT NULL,
            data_cadastro TEXT NOT NULL
            status TEXT NOT NULL
        );
        """)

class person_function():
    def allowed_file(*args):
        return '.' in args[0] and args[0].rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    def get_pages(*args, total, limite_page, page_number):
        total_pages = (total + limite_page - 1) // limite_page

        if page_number < 1 or page_number > total:
            return False

        inicio = (page_number - 1) * limite_page
        fim = min(inicio + limite_page, total)

        return (inicio, fim, total_pages)

    def retornar_values(*args, tabela, coluna=None, filtro=None, person_command=None):
        if person_command:
            resultado = sql.execute(banco="gelinhos.db", retorno=True, command=f"""
            {person_command}
            """)

            return resultado
        elif coluna and filtro:
            resultado = sql.execute(banco="gelinhos.db", retorno=True, command=f"""
            SELECT * FROM {tabela}
            WHERE {coluna} = ?
            """, insert_values=(filtro,))

            return resultado
        else:
            resultado = sql.execute(banco="gelinhos.db", retorno=True, command=f"""
            SELECT * FROM {tabela}
            {person_command if person_command else ""}
            """)

            return resultado

    def update_values(*args, person_command=None):
        resultado = sql.execute(banco="gelinhos.db", retorno=True, command=f"""
        {person_command if person_command else ""}
        """)

        return resultado

    def gravar_values(*args, tabela, colunas, dados):
        cols = ""
        values = ""
        max_cols = len(colunas)

        for idc, name_col in enumerate(colunas):
            cols += f"{name_col}, " if idc + 1 < max_cols else f"{name_col}"
            values += "?, " if idc + 1 < max_cols else "?"

        resultado = sql.execute(banco="gelinhos.db", retorno=True, command=f"""
        INSERT INTO {tabela} ({cols})
        VALUES ({values})
        """, insert_values=dados)

        return resultado

class Email:
    def envia_email_pedido(*args):
        pedido = args[0]
        telefone = args[1]
        nome = args[2]
        formaEntrega = args[3]
        metodoPagamento = args[4]
        endereco = args[5]
        resumo = args[6]
        total = args[7]
        data = args[8]
        status = args[9]

        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "wlyapps.suport@gmail.com"
        smtp_password = "egsa gcsf weza lnuv"

        # Configurações do e-mail
        email = "wesleynascimento.figueredo@gmail.com"
        subject = f"Novo Pedido Gelinhos Gourmet - {pedido}"

        body = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pedido do Cliente</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    color: #333;
                }
                .container {
                    width: 100%;
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                    border-radius: 10px;
                    overflow: hidden;
                }
                .header {
                    background-color: #0080FF;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }
                .header h1 {
                    margin: 0;
                }
                .content {
                    padding: 20px;
                }
                .content h2 {
                    color: #4CAF50;
                    font-size: 24px;
                    margin-bottom: 20px;
                }
                .content p {
                    font-size: 16px;
                    line-height: 1.5;
                }
                .content table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }
                .content table, .content th, .content td {
                    border: 1px solid #ddd;
                }
                .content th, .content td {
                    padding: 12px;
                    text-align: left;
                }
                .content th {
                    background-color: #f2f2f2;
                }
                .content td {
                    background-color: #ffffff;
                }
                .footer {
                    background-color: #f2f2f2;
                    text-align: center;
                    padding: 20px;
                    font-size: 14px;
                    color: #777;
                }
            </style>
        </head>
        """ + f"""
        <body>
            <div class="container">
                <div class="header">
                    <h1>Pedido Gelinho Gourmet</h1>
                </div>
                <div class="content">
                    <h4>Pedidos</h4>
                    <h2>Cliente: {nome},</h2>
                    <br>
                    <h2>Id Pedido: {pedido}</h2>
                    <p>Segue abaixo os itens Pedidos:</p>
                    <table>
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Valor</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>telefone</td>
                                <td>{telefone}</td>
                            </tr>
                            <tr>
                                <td>nome</td>
                                <td>{nome}</td>
                            </tr>
                            <tr>
                                <td>forma_entrega</td>
                                <td>{formaEntrega}</td>
                            </tr>
                            <tr>
                                <td>metodo_pagamento</td>
                                <td>{metodoPagamento}</td>
                            </tr>
                            <tr>
                                <td>endereco</td>
                                <td>{endereco}</td>
                            </tr>
                            <tr>
                                <td>dados_pedido</td>
                                <td>{resumo}</td>
                            </tr>
                            <tr>
                                <td>Data</td>
                                <td>{data}</td>
                            </tr>
                            <tr>
                                <td>Status</td>
                                <td>{status}</td>
                            </tr>
                            <tr>
                                <td colspan="1" style="text-align: right; font-weight: bold;">Total:</td>
                                <td style="font-weight: bold;">{total}</td>
                            </tr>
                        </tbody>
                    </table>
                    <br>
                    <br>
                </div>
                <div class="footer">
                    <div>
                        <h4>Eletronix Drop</h4>
                    </div>
                    <div style="margin-top: 10px;">
                        <a href="https://wa.me/5511987654321" target="_blank" style="text-decoration: none; color: green; font-size: 24px;">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp" style="width: 24px; height: 24px; vertical-align: middle;"> WhatsApp
                        </a>
                    </div>
                    <div style="margin-top: 20px; font-size: 12px; color: #888;">
                        <p>&copy; 2024 Eletronix Drop. Todos os direitos reservados.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Criando a mensagem
        message = MIMEMultipart()
        message["From"] = smtp_username
        message["To"] = email
        message["Subject"] = subject
        message.add_header("Content-Type", "text/html")

        # Iniciando a conexão com o servidor SMTP
        message.attach(MIMEText(body, "html"))

        # Iniciando a conexão com o servidor SMTP
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Inicia a camada de segurança TLS
            server.login(smtp_username, smtp_password)

            # Envia o e-mail
            server.sendmail(smtp_username, email, message.as_string())
        return True
