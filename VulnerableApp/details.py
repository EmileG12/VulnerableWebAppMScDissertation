from flask import Blueprint, render_template_string, render_template, request, url_for, redirect
from pathlib import Path
import sqlite3
import hashlib
import os
from flask_login import login_required

from .models import User

details = Blueprint('details', __name__)

# Get the absolute path to the database file in a cross-platform way
def get_db_path():
    """Get the absolute path to the database file"""
    # Get the directory where this file is located
    current_dir = Path(__file__).parent.absolute()
    # Go up one level to the project root and then to instance directory
    project_root = current_dir.parent
    instance_dir = project_root / 'instance'
    # Ensure the instance directory exists
    instance_dir.mkdir(exist_ok=True)
    return str((instance_dir / 'db.sqlite').resolve())

instance_db_path = get_db_path()
from . import db

@details.route('/credit')
@login_required
def creditredirect():
    #Redirects to /credit/<userid> by getting the user id from the cookies and then providing them as a get argument
    #This is to make it more obvious to the student that they can manipulate the parameter
    userid=request.cookies.get('userid')
    return redirect(url_for('details.credit',userid=userid))

@details.route('/credit/<userid>')
@login_required
def credit(userid):
    #Added SQL injection vulnerability by executing a raw command, in case the student would like to experiment
    sqlconn = sqlite3.connect(get_db_path())
    cursor = sqlconn.cursor()
    cursor.execute("select * from Credit where userid=" + str(userid))
    result = cursor.fetchall()
    creditdetails = list(result[0])
    #We remove the user id from the result since it's not pertinent information
    creditdetails.pop(0)
    return render_template("details.html", creditdetails=creditdetails)

@details.route('/loginupdate')
@login_required
def loginupdate():
    userhash = request.cookies.get('userhash')
    userid = request.cookies.get('userid')
    return render_template("login_update.html",userhash=userhash, userid=userid)

@details.route('/changepassword')
def changepassword():
    newpassword = request.form.get('newpassword')
    userhash = request.form.get('userhash')
    db.session.query(User).filter(User.userhash == userhash).update({'password': str(newpassword)})
    db.session.commit()
    return redirect(url_for('details.loginupdate'))

@details.route('/changeusername')
def changeusername():
    newusername=request.args.get('newusername')
    print(newusername)
    userid = request.args.get('userid')
    print(userid)
    sqlconn = sqlite3.connect(get_db_path())
    cursor = sqlconn.cursor()
    print("update user set username='" + str(newusername) + "' where userid=" +str(userid))
    cursor.execute("update user set username='" + str(newusername) + "' where userid=" +str(userid))
    sqlconn.commit()
    return redirect(url_for('details.loginupdate'))

@details.route('/changename')
def changename():
    # Vulnerable route that allows changing the user's name
    # This creates a stored XSS vulnerability since the name is displayed without escaping on /profile
    newname = request.args.get('newname')
    userid = request.args.get('userid')
    print(f"Changing name to: {newname} for user: {userid}")
    
    if newname is None or userid is None:
        return redirect(url_for('details.loginupdate'))
    
    sqlconn = sqlite3.connect(get_db_path())
    cursor = sqlconn.cursor()
    
    try:
        # Use parameterized query to avoid SQL syntax errors but still allow XSS
        # This fixes the SQL injection but keeps the XSS vulnerability
        query = "UPDATE user SET name = ? WHERE userid = ?"
        print(f"Executing query: {query} with params: [{newname}, {userid}]")
        cursor.execute(query, (newname, userid))
        sqlconn.commit()
        print(f"Successfully updated name to: {newname}")
    except Exception as e:
        print(f"Database error: {e}")
        # Even if there's an error, continue to avoid breaking the flow
    finally:
        sqlconn.close()
    
    return redirect(url_for('details.loginupdate'))

@details.route('/deleteuser')
@login_required
def deleteuser():
    userid = request.cookies.get('userid')
    sqlconn = sqlite3.connect(get_db_path())
    cursor = sqlconn.cursor()
    cursor.execute("delete from user where userid=" + str(userid))
    cursor.execute("delete from credit where userid=" + str(userid))
    sqlconn.commit()
    response = redirect(url_for('auth.login'))
    response.delete_cookie('userhash')
    response.delete_cookie('userid')
    return render_template("delete_user.html")

@details.route('/deleteuser', methods=['POST'])
@login_required
def deleteuser_post():
    userid = request.cookies.get('userid')
    sqlconn = sqlite3.connect(get_db_path())
    cursor = sqlconn.cursor()
    cursor.execute("delete from user where userid=" + str(userid))
    cursor.execute("delete from credit where userid=" + str(userid))
    sqlconn.commit()
    response = redirect(url_for('auth.login'))
    response.delete_cookie('userhash')
    response.delete_cookie('userid')
    return render_template("delete_user.html")
