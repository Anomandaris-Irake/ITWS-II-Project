from flask import Flask,redirect,url_for,render_template,request
import sqlite3
from wtforms import Form, BooleanField, TextField, PasswordField, validators, StringField


class AnswerForm(Form):
    Answer = TextField('Answer', [validators.Length(min=4, max=1000)])


class QuestionForm(Form):
    Question = TextField('Question', [validators.Length(min=4, max=1000)])


conn=sqlite3.connect('data.db', check_same_thread=False)
c=conn.cursor()

app=Flask(__name__)
@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/courses/')
@app.route('/courses/<courseid>')
def showquestions(courseid=1):
	global c
	global conn
	c.execute('select course,courseid from courses where courseid=?', (courseid,))
	coursename=c.fetchall()
	c.execute('select uid,question,courseid,qid,upvotes from questions where courseid=?',(courseid,))
	qu=c.fetchall()
	ques=sorted(qu,key=lambda x:x[4],reverse=True)
	q=[]
	for i in ques:
		c.execute('select name from users where uid=?',(i[0],))
		a=c.fetchall()
		q.append([i,a[0][0]])
	return render_template("coursemain.html", coursename=coursename, q=q)

@app.route('/answers/')
@app.route('/answers/<qid>')
def showanswers(qid=1):
	global c
	global conn
	c.execute('select * from answers where qid=?',(qid,))
	a=c.fetchall()
	ans=sorted(a,key=lambda x:x[3],reverse=True)
	c.execute('select question,qid from questions where qid=?',(qid,))
	ques=c.fetchall()
	return render_template("answers.html", ques=ques,ans=ans)

@app.route('/allcourses/')
def showcourses():
	global c
	global conn
	c.execute('''select * from courses''')
	courses=c.fetchall()
	return render_template('allcourses.html', courses=courses)

@app.route('/trial')
def trial():
	return redirect(url_for('index'))

@app.route('/submitanswer/<qid>',methods=['GET','POST'])
def submitanswer(qid=1):
	error=None
	form=AnswerForm(request.form)
	global c
	global conn
	if request.method=='POST':
		answer=form.Answer.data
		t=(qid,1,answer,0)
		c.execute('insert into answers values(?,?,?,?)',t)
		conn.commit()
		return redirect(url_for('index'))
	return render_template('submitanswer.html',form=form)

@app.route('/submitquestion/<courseid>',methods=['GET','POST'])
def submitquestion(courseid=1):
	error=None
	form=QuestionForm(request.form)
	global c
	global conn
	if request.method=='POST':
		question=form.Question.data
		c.execute('select courseid from questions')
		Ques=c.fetchall()
		qid=len(Ques)+1
		t=(qid,1,courseid,question,1)
		c.execute('insert into questions values(?,?,?,?,?)',t)
		conn.commit()
		return redirect(url_for('index'))
	return render_template('submitquestion.html',form=form)



