from flask import Flask,redirect,url_for,render_template,request
from wtforms import Form, BooleanField, TextField, PasswordField, validators

class AnswerForm(Form):
    Answer = TextField('Answer', [validators.Length(min=4, max=1000)])