from flask import Flask
from flask_session import Session

import config
from config import create_sql

from home.home_page import page_home_bp
from pedidos.pedidos import page_pedidos_bp
from function.function import page_function_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = config.Config.SECRET_KEY
app.config['SESSION_TYPE'] = config.Config.SESSION_TYPE
app.config['SESSION_FILE_DIR'] = config.Config.SESSION_FILE_DIR
Session(app)


app.register_blueprint(page_home_bp)
app.register_blueprint(page_pedidos_bp)
app.register_blueprint(page_function_bp)

create_sql.tables()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)