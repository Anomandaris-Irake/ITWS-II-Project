from flask import Flask,flash,redirect,url_for,render_template,request
import sqlite3
from passlib.hash import sha512_crypt
from wtforms import Form, BooleanField, TextField, PasswordField, validators, StringField
from config import *


conn=sqlite3.connect('data.db', check_same_thread=False)
c=conn.cursor()

app=Flask(__name__)
app.secret_key = 'MKhJHJH798798kjhkjhkjGHh'

    
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
    c.execute('select answers.*,name from answers,users where answers.uid=users.uid and qid=?',(qid,))
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

@app.route('/submitanswer/<qid>',methods=['GET','POST'])
def submitanswer(qid=1):
    error=None
    form=AnswerForm(request.form)
    global c
    global conn
    if 'username' not in session:
    	return redirect(url_for('login'))
    if request.method=='POST':
	    answer=form.Answer.data
	    name=session['username']
	    c.execute('select uid from users where name=?', (name,))
	    x=c.fetchall()
	    userid=x[0][0]
	    t=(qid,userid,answer,0)
	    c.execute('insert into answers values(?,?,?,?)',t)
	    conn.commit()
	    return redirect(url_for('index'))
    return render_template('submitanswer.html',form=form)

@app.route('/submitquestion/<courseid>',methods=['GET','POST'])
def submitquestion(courseid=1):
    error=None
    form=QuestionForm(request.form)
    if 'username' not in session:
    	return redirect(url_for('login'))
    global c
    global conn
    if request.method=='POST':
        question=form.Question.data
        c.execute('select courseid from questions')
        Ques=c.fetchall()
        qid=len(Ques)+1
        name=session['username']
        c.execute('select uid from users where name=?',(name,))
        x=c.fetchall()
        userid=x[0][0]
        t=(qid,userid,courseid,question,1)
        c.execute('insert into questions values(?,?,?,?,?)',t)
        conn.commit()
        return redirect(url_for('index'))
    return render_template('submitquestion.html',form=form)


@app.route('/signup', methods=["GET","POST"])
def signup():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        email = form.email.data
        password = sha512_crypt.encrypt((str(form.password.data)))
        global c
        global conn
        c.execute("select * from users where name = ?",(name,))
        x=c.fetchall()
        description=form.description.data
        if len(x) > 0:
            flash("That username is already taken, please choose another")
            return render_template('signup.html',form=form,username_taken=1)
        else:
            c.execute('select uid from users')
            usrs=c.fetchall()
            uid=len(usrs)+1		
            c.execute("insert into users values (?,?,?,?,?)",(uid, name, email, password,description))
            conn.commit()
            flash("Thanks for registering!")
            return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/login/',methods=["POST","GET"])
def login():
    form=LoginForm(request.form)
    if request.method == "GET":
    	return render_template("login.html", form=form, wrong=0)
    if request.method == "POST":
        next = request.values.get('next')
        if(authenticate(request)==False):
            return render_template("login.html", form=form, wrong=1)
        if(authenticate(request)==True):
            if not next:
                return render_template("index.html")
            else:
                return redirect(next)

@app.route('/logout/',methods=['POST','GET'])
def logout():
    if 'username' in session:
        name = session.pop('username')
        return render_template("result.html",message=name+" has logged out")
    return render_template("result.html",message="Please login first :-)")


@app.route('/user/<uid>')
def showuser(uid=1):
	global c
	global conn
	c.execute('select * from users where uid=?',(uid,))
	user=c.fetchone()
	totalupvotes=0
	c.execute('select upvotes from questions where uid=?', (uid,))
	x=c.fetchall()
	for i in x:
		totalupvotes+=i[0]
	c.execute('select upvotes from answers where uid=?', (uid,))
	x=c.fetchall()
	for i in x:
		totalupvotes+=i[0]
	return render_template('showuser.html', user=user,totalupvotes=totalupvotes)


