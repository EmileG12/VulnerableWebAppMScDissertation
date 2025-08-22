import sqlite3
from pathlib import Path
from flask import Blueprint, render_template, render_template_string, request
from flask_login import login_required

from . import db

# Import the database path function from details module
from .details import get_db_path

main = Blueprint('main', __name__)

@main.route('/index')
@login_required
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    userid = request.cookies.get('userid')
    instance_db_path = get_db_path()
    sqlconn = sqlite3.connect(instance_db_path)
    cursor = sqlconn.cursor()
    nameresult = cursor.execute("select name from user where userid='" + str(userid)+ "'").fetchall()
    username = nameresult[0][0] if nameresult else "Unknown User"
    print(f"Profile name from DB: {username}")
    
    # Use render_template_string to ensure XSS vulnerability
    # This bypasses any template auto-escaping
    template = '''
{% extends "base.html" %}

{% block content %}
<h1 class="title">
  Welcome, ''' + str(username) + '''!
</h1>
{% endblock %}
    '''
    
    return render_template_string(template)