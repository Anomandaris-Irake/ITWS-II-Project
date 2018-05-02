from flask import Flask,flash,redirect,url_for,render_template,request,session
import sqlite3
from passlib.hash import sha512_crypt
from wtforms import Form, BooleanField, TextField, PasswordField, validators, StringField

class AnswerForm(Form):
    Answer = TextField('Answer', [validators.Length(min=4, max=1000)])

class EditAnswer(Form):
    answer = TextField('Answer', [validators.length(min=4, max=1000)])

class LoginForm(Form):
    Username = TextField('Username', [validators.Length(min=4, max=1000)])
    Password = PasswordField('Password', [validators.Length(min=4, max=1000)])
    Rememberme = BooleanField('Remember me')

class QuestionForm(Form):
    Question = TextField('Question', [validators.Length(min=4, max=1000)])

class EditQuestion(Form):
    question = TextField('Question', [validators.Length(min=4, max=1000)])

class RegistrationForm(Form):
    name = TextField('name', [validators.Length(min=4, max=20)])
    email = TextField('email', [validators.Length(min=6, max=50)])
    password = PasswordField('password', [validators.Required(),validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Apr 08, 2018)', [validators.Required()])
    description = TextField('Tell us something about yourselves')

class SearchBar(Form):
	search=TextField("Search")

def authenticate(request):
	con = sqlite3.connect("data.db")
	username = request.form['Username']
	password = request.form['Password']
	sqlQuery = "select password from users where name = '%s'"%username
	cursor = con.cursor()
	cursor.execute(sqlQuery)
	row = cursor.fetchone()
	status = False
	if row:
		status = sha512_crypt.verify(password,row[0])
		if status:
			msg = username + "has logged in successfully"
			session['username'] = username
			cursor.execute('select uid from users where name=?', (username,))
			x=cursor.fetchone()
			session['uid']=str(x[0])
	else:
		msg = username + "login failed"

	return status

class EditForm(Form):
    email = TextField('email', [validators.Length(min=6, max=50)])
    password = PasswordField('password', [validators.Required(),validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    description = TextField('Edit the description u had')
