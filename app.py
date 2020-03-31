from flask import Flask, render_template, request, redirect, url_for, session, logging, jsonify, send_file
import pymysql
from wtforms import Form, StringField, TextAreaField, IntegerField, PasswordField, SelectField, validators
from passlib.hash import sha256_crypt
from datetime import timedelta
import os

class GroupForm(Form):
    day = SelectField('Day of week', choices = [('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday')])
    time = StringField('Starting time', [validators.Length(min=3, max=5)])
    id = 0

class NewGroupForm(GroupForm):
    subject = SelectField('Subject', choices = [(2, 'b'),(1, 'b')], coerce = int)


class RegisterForm(Form):
    username = StringField ('Username', [validators.Length(min=1, max=30)])
    first_name = StringField('First name', [validators.Length(min=3, max=30)])
    last_name = StringField('Last name', [validators.Length(min=3, max=30)])
    index_number = StringField('Index number', [validators.Length(min=6, max=6)])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message = 'Passwords do not match')])
    confirm = PasswordField('Confirm password')

class EditSubjectForm(Form):
    name = StringField('Subject Name', [validators.Length(min=3, max=50)])

def db_connection():
    return pymysql.connect(
        host = 'localhost',
        user = 'andrzej',
        password = 'pass',
        db = 'groups',
        cursorclass = pymysql.cursors.DictCursor
    )


#returns dict of groups created for a subject of given id
def get_groups(id):
    id = str(id)
    mysql = db_connection()
    cur = mysql.cursor()
    cur.execute('SELECT * FROM group_list WHERE subject_id = %s', [id])
    res = cur.fetchall()
    cur.close()
    mysql.close()
    return res

#returns all subjects created
def get_subjects():
    mysql = db_connection()
    cur = mysql.cursor()
    cur.execute('SELECT s_id, name FROM subjects')
    res = cur.fetchall()
    cur.close()
    mysql.close()
    return res

app = Flask(__name__)
app.secret_key = 'wqewqeqweqsfxxs23fw'

#kills session after n minutes of inactivity
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes = 10)

#mysql = db_connection()

from route import *
from admin import *

if __name__ == '__main__':
    #first visible on local network, second one on localhost only
    app.run(debug = True, host = '0.0.0.0', port = '5000')
    # app.run(debug = True)
