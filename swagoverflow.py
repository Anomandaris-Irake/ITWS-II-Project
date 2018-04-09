from flask import Flask,redirect,url_for,render_template
import sqlite3

app=Flask(__name__)
@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/courses/')
@app.route('/courses/<courseid>')
def course(courseid=None):
	conn=sqlite3.connect('data.db')
	c=conn.cursor()
	c.execute('select course from courses where courseid=?', (courseid,))
	coursename=c.fetchall()
	c.execute('select uid,question,courseid,qid from questions where courseid=?',(courseid,))
	ques=c.fetchall()
	q=[]
	for i in ques:
		c.execute('select name from users where uid=?',(i[0],))
		a=c.fetchall()
		q.append([i,a[0][0]])
	return render_template("coursemain.html", coursename=coursename, q=q)
	conn.commit()
	conn.close()

@app.route('/answers/')
@app.route('/answers/<qid>')
def showanswers(qid=None):
	conn=sqlite3.connect('data.db')
	c=conn.cursor()
	c.execute('select * from answers where qid=?',(qid,))
	ans=c.fetchall()
	c.execute('select question from questions where qid=?',(qid,))
	ques=c.fetchall()
	return render_template("answers.html", ques=ques,ans=ans)
	conn.commit()
	conn.close()

@app.route('/allcourses/')
def showcourses():
	conn=sqlite3.connect('data.db')
	c=conn.cursor()
	c.execute('''select * from courses''')
	courses=c.fetchall()
	return render_template('allcourses.html', courses=courses)
	conn.commit()
	conn.close()