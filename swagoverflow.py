from flask import Flask,flash,redirect,url_for,render_template,request
import sqlite3
from passlib.hash import sha512_crypt
from config import *
from wtforms import Form, BooleanField, TextField, PasswordField, validators, StringField


conn=sqlite3.connect('data.db', check_same_thread=False)
c=conn.cursor()

app=Flask(__name__)
app.secret_key = 'MKhJHJH798798kjhkjhkjGHh'


@app.route('/')
@app.route('/index',methods=["GET", "POST"])
def index():
	form=SearchBar(request.form)
	if request.method=="GET":
		return render_template('index.html',form=form)
	elif request.method=="POST":
		search=form.search.data
		c.execute('select * from courses where courses match ?',(search,))
		courses=c.fetchall()
		numcourses=len(courses)
		c.execute('select * from questions where question match ?',(search,))
		q=c.fetchall()
		ques=sorted(q,key=	lambda x:x[4],reverse=True)
		numques=len(ques)
		c.execute('select * from users where name match ?',(search,))
		users=c.fetchall()
		numusers=len(users)
		return render_template('searchresults.html',courses=courses,numcourses=numcourses,ques=ques,numques=numques,users=users,numusers=numusers,search=search)

@app.route('/courses/')
@app.route('/courses/<courseid>/<page>')
def showquestions(courseid=1,page=1,sortby="upvotes"):
    global c
    global conn
    c.execute('select course,courseid from courses where courseid=?', (courseid,))
    coursename=c.fetchall()
    c.execute('select uid,question,courseid,qid,upvotes from questions where courseid=?',(courseid,))
    qu=c.fetchall()
    if 'sortby' not in request.args:
            ques=sorted(qu,key=lambda x:x[4],reverse=True)
    elif request.args['sortby']=="upvotes":
        ques=sorted(qu,key=lambda x:x[4],reverse=True)
    elif request.args['sortby']!="upvotes":
        ques=sorted(qu,key=lambda x:x[3],reverse=True)
    qe=[]
    totalpages=(len(qu)//5)+1
    for i in ques:
        c.execute('select name from users where uid=?',(i[0],))
        a=c.fetchall()
        qe.append([i,a[0][0]])
    q=qe[5*(int(page)-1):5*(int(page))]
    return render_template("coursemain.html", coursename=coursename, q=q,totalpages=totalpages,page=page)

@app.route('/answers/')
@app.route('/answers/<qid>/<page>')
def showanswers(qid=1,page=1,sortby="upvotes"):
    global c
    global conn
    c.execute('select answers.*,name from answers,users where answers.uid=users.uid and qid=?',(qid,))
    a=c.fetchall()
    totalpages=(len(a)//5)+1
    if 'sortby' not in request.args:
        an=sorted(a,key=lambda x:x[3],reverse=True)
    elif request.args['sortby']=="upvotes":
        an=sorted(a,key=lambda x:x[3],reverse=True)
    elif request.args['sortby']!="upvotes":
        an=sorted(a,key=lambda x:x[1],reverse=True)
    ans=an[5*(int(page)-1):5*(int(page))]
    c.execute('select question,qid from questions where qid=?',(qid,))
    ques=c.fetchone()
    return render_template("answers.html", ques=ques,ans=ans,totalpages=totalpages,page=page,qid=qid)

@app.route('/allcourses/')
def showcourses():
    global c
    global conn
    c.execute('''select * from courses''')
    courses=c.fetchall()
    c.execute('select * from subscriptions')
    subscriptions=c.fetchall()
    return render_template('allcourses.html', courses=courses,subscriptions=subscriptions,toreturn='0')

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
        c.execute('select * from answers')
        x=c.fetchall()
        aid=len(x)+1
        t=(qid,userid,answer,0,str(aid))
        c.execute('insert into answers values(?,?,?,?,?)',t)
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
        t=(str(qid),userid,courseid,question,0)
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
            c.execute("insert into users values (?,?,?,?,?)",(str(uid), name, email, password,description))
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
                return redirect(url_for('index'))
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
    for i in x :
        totalupvotes+=i[0]
    c.execute('select upvotes from answers where uid=?', (uid,))
    x=c.fetchall()
    for i in x :
        totalupvotes+=i[0]
    c.execute('select question,qid from questions where uid=?',(uid,))
    ques=c.fetchall()
    aq=[]
    uq=[]
    for i in ques :
        c.execute('select * from answers where qid=?',(ques[0][1],))
        ps=c.fetchall()
        if(len(ps)>0) :
            aq.append(i)
        else :
            uq.append(i)
    c.execute('select questions.question,questions.qid,answers.answer,answers.aid from questions,answers where answers.qid=questions.qid and answers.uid=?',(uid,))
    ans=c.fetchall()
    return render_template('showuser.html', user=user,aq=aq , uq=uq , ans=ans,totalupvotes=totalupvotes,uid=uid)

@app.route('/question_upvote/<qid>/<uid>/<previous_link>')
def question_upvote(previous_link,qid,uid):
    global c
    global conn
    c.execute('select * from question_votes where uid=? and qid=?',(uid,qid,))
    x=c.fetchall()
    if(len(x)==0):
        c.execute('insert into question_votes values(?,?)', (qid,uid))
        conn.commit()
        c.execute('select upvotes from questions where qid=?',(qid,))
        x=c.fetchone()
        upvotes=x[0]
        upvotes+=1
        c.execute('update questions set upvotes=? where qid=?',(upvotes,qid))
        conn.commit()
        return redirect(url_for("showquestions",courseid=previous_link,page=1))
    else:
        return redirect(url_for("showquestions",courseid=previous_link,page=1))


@app.route('/answer_upvote/<aid>/<uid>/<previous_link>')
def answer_upvote(aid,previous_link,uid):
    global c
    global conn
    c.execute('select * from answer_votes where uid=? and aid=?',(uid,aid,))
    x=c.fetchall()
    if(len(x)==0):
        c.execute('insert into answer_votes values(?,?)', (aid,uid,))
        conn.commit()
        c.execute('select * from answer_votes where aid=?',(aid,))
        x=c.fetchall()
        upvotes=len(x)
        c.execute('update answers set upvotes=? where aid=?',(upvotes,aid,))
        conn.commit()
        return redirect(url_for("showanswers",qid=previous_link,page=1))
    else:
        return redirect(url_for("showanswers",qid=previous_link,page=1))


@app.route('/question_downvote/<qid>/<uid>/<previous_link>')
def question_downvote(previous_link,qid,uid):
    global c
    global conn
    c.execute('delete from question_votes where uid=? and qid=?',(uid,qid))
    conn.commit()
    c.execute('select * from question_votes where qid=?',(qid,))
    x=c.fetchall()
    upvotes=len(x)
    c.execute('update questions set upvotes=? where qid=?',(upvotes,qid))
    conn.commit()
    return redirect(url_for("showquestions",courseid=previous_link,page=1))


@app.route('/answer_downvote/<aid>/<uid>/<previous_link>')
def answer_downvote(aid,previous_link,uid):
    global c
    global conn
    c.execute('delete from answer_votes where uid=? and aid=?',(uid,aid,))
    conn.commit()
    c.execute('select * from answer_votes where aid=?', (aid,))
    x=c.fetchall()
    upvotes=len(x)
    c.execute('update answers set upvotes=? where aid=?', (upvotes,aid,))
    conn.commit()
    return redirect(url_for("showanswers",qid=previous_link,page=1))

@app.route('/subscribe/<uid>/<courseid>')
def subscribe(uid,courseid):
    global c
    global conn
    c.execute('insert into subscriptions values(?,?)',(uid,courseid,))
    conn.commit()
    return redirect(url_for('showcourses'))


@app.route('/unsubscribe/<uid>/<courseid>/<toreturn>')
def unsubscribe(uid,courseid,toreturn):
    global c
    global conn
    c.execute('delete from subscriptions where uid=? and courseid=?',(uid,courseid,))
    conn.commit()
    if(toreturn!='1'):
        return redirect(url_for('showcourses'))
    else:
        return redirect(url_for('mysubscriptions'))

@app.route('/mysubscriptions/')
def mysubscriptions():
    global c
    global conn
    c.execute('select courseid from subscriptions where uid=?', (session['uid'],))
    courseids=c.fetchall()
    courses=[]
    for i in courseids:
        c.execute('select course from courses where courseid=?',(i[0],))
        coursename=c.fetchone()
        courses.append((i[0],coursename[0]))
    c.execute('select * from subscriptions where uid=?', session['uid'])
    subscriptions=c.fetchall()
    return render_template('allcourses.html', courses=courses,subscriptions=subscriptions,toreturn='1')

@app.route('/editpage/<uid>', methods=["GET","POST"])
def editpage(uid):
    form = EditForm(request.form)
    if request.method == "POST" :
        global c
        global conn
        a = len(str(form.email.data))
        email = form.email.data
        b = len(str(form.password.data))
        password = sha512_crypt.encrypt((str(form.password.data)))
        d = len(str(form.description.data))
        description = form.description.data
        if a>0 :
            c.execute("update users set email = ? where uid = ?",(email,uid,))
        if b>0 :
            c.execute("update users set password = ? where uid = ?",(password,uid,))
        if d>0 :
            c.execute("update users set description = ? where uid = ?",(description,uid,))
        conn.commit()
        return redirect(url_for('index'))

    return render_template('editpage.html', form=form, uid=str(uid))

@app.route('/editquestion/<qid>', methods=["GET","POST"])
def editquestion(qid):
    form = EditQuestion(request.form)
    q=[]
    c.execute("select question from questions where qid=?",(qid,))
    b=c.fetchall()
    for i in b:
        q.append(i)
    if request.method == "POST" :
        global c
        global conn
        a = len(str(form.question.data))
        question = form.question.data
        if a>0 :
            c.execute("update questions set question = ? where qid = ?",(question,qid,))
        conn.commit()
        return redirect(url_for('index'))

    return render_template('editquestion.html', form=form, qid=qid, q=q)

@app.route('/editanswer/<aid>', methods=["GET","POST"])
def editanswer(aid):
    form = EditAnswer(request.form)
    ans=[]
    c.execute("select answer from answers where aid=?",(aid,))
    b=c.fetchall()
    for i in b:
        ans.append(i)
    if request.method == "POST" :
        global c
        global conn
        a = len(str(form.answer.data))
        answer = form.answer.data
        if a>0 :
            c.execute("update answers set answer = ? where aid = ?",(answer,aid,))
        conn.commit()
        return redirect(url_for('index'))

    return render_template('editanswer.html', form=form, aid=aid, ans=ans)
