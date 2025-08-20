from flask import Blueprint, render_template, redirect, url_for, request, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user
auth = Blueprint('auth', __name__)

@auth.route('/')
def login():
    return render_template('login.html')

@auth.route('/logout')
def logout():
    return redirect(url_for('auth.login'))
...
@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    #Website has different responses for whether the username exists in the database or not
    #This is done to show the student how they could discover information on a webpage
    if not user:
        flash("Username does not exist")
        return redirect(url_for('auth.login'))
    if password != user.password:
        flash('Password is incorrect')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
    response = redirect(url_for('main.index'))
    response.set_cookie("userhash", value = user.userhash, max_age=None, expires=None, path='/', domain=None,secure=None,httponly=False)
    response.set_cookie("userid", value=str(user.userid), max_age=None, expires=None, path='/', domain=None, secure=None,httponly=False)
    login_user(user,True)
    # if the above check passes, then we know the user has the right credentials
    return response