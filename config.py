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
    SESSION_DOMINIO = 'http://192.168.0.113:8080/'

class app_vars:
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    # ACCESS_TOKEN = "TEST-4667742724479969-091116-015eb505e94cf5735b49477703f33624-172786625"
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

    def calcular_frete_melhor_envio(*args, api_key=app_vars.MELHOR_ENVIO_TOKEN, cep_origem, cep_destino, produtos):

        url = "https://www.melhorenvio.com.br/api/v2/me/shipment/calculate"

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Dados do pacote para cálculo
        payload = {
            "from": {"postal_code": cep_origem},
            "to": {"postal_code": cep_destino},
            "products": produtos,
            "services": "1,2",  # Pode-se especificar serviços específicos de envio, se quiser
        }

        # Fazendo a requisição para a API do Melhor Envio
        response = requests.post(url, json=payload, headers=headers)

        # Verificando se a requisição foi bem-sucedida
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Falha ao calcular o frete", "status_code": response.status_code}

    def calcular_frete_j3flex(*args, cep_destino, produtos):
        regioes_j3 = ['Francisco Morato', 'Cajamar Jordanésia', 'Franco da Rocha', 'Mairiporã Norte',
                      'Mairiporã Central', 'Mairiporã Sul', 'Caieiras', 'Santana de Parnaíba Central',
                      'Santana de Parnaíba Leste', 'Santana de Parnaíba Oeste', 'Itapevi Fundão', 'Barueri 1',
                      'Barueri 2', 'Osasco 1', 'Osasco 2', 'Osasco 3', 'Norte 1', 'Norte 2', 'Norte 3', 'Oeste 1',
                      'Oeste 2', 'Oeste 3', 'Centro', 'Sul 1', 'Sul 2', 'Sul 3', 'Cotia Norte', 'Cotia Central',
                      'Cotia Leste', 'Cotia Sudeste', 'Jandira Norte', 'Jandira Cotia', 'Taboão', 'Embu das Artes 1',
                      'Embu das Artes 2', 'São Caetano', 'São Bernardo 1', 'São Bernardo 2', 'São Bernardo 3',
                      'Diadema', 'Santo André 1', 'Santo André 2', 'Santo André 3', 'Mauá', 'Guarulhos 1',
                      'Guarulhos 2', 'Guarulhos 3', 'Guarulhos 4', 'Arujá', 'Itaquaquecetuba',
                      'Ferraz de Vasconcelos Poá', 'Leste 1', 'Leste 2', 'Leste 3', 'Leste 4', 'Leste 5',
                      'Mogi das Cruzes-Suzano Norte', 'Mogi das Cruzes Leste', 'Mogi das Cruzes Central',
                      'Mogi das Cruzes Sul', 'Suzano Central', 'Suzano Sul'] + ["São Paulo"]

        url = f"https://viacep.com.br/ws/{cep_destino}/json/"
        response = requests.get(url).json()

        localidade = response["localidade"]
        estado = response["estado"]

        if (estado == "São Paulo" and float(produtos[0]["width"]) <= 30 and float(produtos[0]["height"]) <= 30
            and float(produtos[0]["length"]) <= 30):
            similaridade = {regiao: difflib.SequenceMatcher(None, localidade, regiao).ratio() for regiao in regioes_j3}
            similaridade_ordenada = sorted(similaridade.items(), key=lambda item: item[1], reverse=True)

            score_final = 0
            for regiao, score in similaridade_ordenada[:5]:
                if score >= score_final:
                    score_final = round(score, 2)

            if score_final >= 0.7:
                return True
            else:
                return False
        else:
            return False

    def variacao_personalizada(*args, variacao):
        # select:Cor:Azul,Verde,Vermelho|input:Texto Personalizado:Escreva seu texto Personalizado para o Modelo

        html_variacao = ""
        if ":" in variacao:
            variacoes_person = variacao.split("|")
            idc = 1
            ids_existentes = []
            for item_var in variacoes_person:
                if "select" in item_var:
                    tipo, titulo, opcoes = item_var.split(":")
                    html_opcoes = ""

                    for opcao in opcoes.split(","):
                        html_opcoes += f'<option value="{opcao.lower()}">{opcao}</option>\n'

                    html_variacao += f"""
                    <label for="{titulo.lower()}" class="mr-2">{titulo}*:</label>
                    <select id="variacao_geral{idc}" class="form-control">
                        <option value="">Selecione</option>
                        {html_opcoes}
                    </select>
                    <p class="blink"><< Atenção >> Item com Variação, não Esqueça de Selecionar!</p>
                    """
                    idc += 1
                elif "input" in item_var:
                    tipo, titulo, opcoes = item_var.split(":")
                    html_variacao += f"""
                    <div class="form-group">
                        <label for="{titulo.lower()}">{titulo}*:</label>
                        <input type="text" class="form-control" id="variacao_geral{idc}" 
                        placeholder="{opcoes}">
                    </div>
                    <p class="blink"><< Atenção >> Item com Variação, não Esqueça de Informar!</p>
                    """
                    idc += 1
                else:
                    return []

            return html_variacao
        else:
            if variacao:
                html_opcoes = ""

                for opcao in variacao.split(","):
                    html_opcoes += f'<option value="{opcao.lower()}">{opcao}</option>\n'

                html_variacao = f"""
                <label for="variacao_geral" class="mr-2">Variação Geral*:</label>
                <select name="variacao_geral" id="variacao_geral" class="form-control">
                    <option value="">Selecione</option>
                    {html_opcoes}
                </select>
                <p class="blink"><< Atenção >> Item com Variação, não Esqueça de Selecionar!</p>
                """
                return html_variacao
            else:
                return []

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
