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
        "tag": "tag-primary",
        "frete-resumo": []
    }

    page = request.args.get("page")

    if page == "produtos":
        ...
    else:
        return redirect(url_for("index.index"))