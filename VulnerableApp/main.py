import sqlite3
from pathlib import Path
from flask import Blueprint, render_template, render_template_string, request
from . import db
from .details import instance_db_path

main = Blueprint('main', __name__)

@main.route('/index')
def index():
    return render_template('index.html')

@main.route('/profile')
def profile():
    userid = request.cookies.get('userid')
    sqlconn = sqlite3.connect(instance_db_path)
    cursor = sqlconn.cursor()
    nameresult = cursor.execute("select name from user where userid='" + str(userid)+ "'").fetchall()
    print(nameresult[0][0])
    return render_template('profile.html',name=nameresult[0][0])