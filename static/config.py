from flask import Flask,redirect,url_for,render_template,request
from wtforms import Form, BooleanField, TextField, PasswordField, validators


class AnswerForm(Form):
    Answer = TextField('Answer', [validators.Length(min=4, max=1000)])


class QuestionForm(Form):
    Question = TextField('Question', [validators.Length(min=4, max=1000)])

class RegistrationForm(Form):
    name = TextField('name', [validators.Length(min=4, max=20)])
    email = TextField('email', [validators.Length(min=6, max=50)])
    password = PasswordField('password', [validators.Required(),validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Apr 08, 2018)', [validators.Required()])
