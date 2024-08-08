from flask import Flask,render_template,url_for,request,redirect,flash,session
from flask_session import Session
import mysql.connector
from otp import genotp
from cmail import sendmail
from key import secret_key
from stoken import token,dtoken

app=Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
Session(app)
mydb=mysql.connector.connect(host='localhost',user='root',password='nitish',db='spm')
app.secret_key=b'\xdb?7\t.\xfc'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sign',methods=['POST','GET'])
def sign():
    if request.method=='POST':
        print(request.form)
        fname=request.form['sfname']
        lname=request.form['slname']
        email=request.form['email']
        passw=request.form['passw']
        phno=request.form['phno']
        # try:
        #     type(fname)==int
        # except Exception as e:
        #     print(e)
            
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(email) from stu_info where email=%s',[email])
        data=cursor.fetchone()[0]
        #data=cursor.fetchall()
        #print(data)
        # print(fname,lname,email,passw,phno)
        if data==0:
            otp=genotp()
            data={'otp':otp,'email':email,'fname':fname,'lname':lname,'passw':passw,'phno':phno}
            subject="OTP verification for SPM application"
            body=f'Registration otp for SPM application {otp}'
            sendmail(to=email,subject=subject,body=body)
            return redirect(url_for('verifyotp',data1=token(data=data)))
        else:
            flash('Email already exists')
            return redirect(url_for('sign'))
        # cursor=mydb.cursor(buffered=True)
        # cursor.execute('insert into stu_info(stu_fname,stu_lname,email,ph_no,password) values(%s,%s,%s,%s,%s)',[fname,lname,email,phno,passw])
        # mydb.commit()
        # cursor.close()
        # print('done')
        
    return render_template('signup.html')
@app.route('/otp/<data1>',methods=['GET','POST'])
def verifyotp(data1):
    try:
        data2=dtoken(data=data1)
        print(data2)
    except Exception as e:
        print(e)
        return "time out of otp"
    else:
        if request.method=='POST':
            uotp=request.form['verify']
            if uotp==data2['otp']:
                cursor=mydb.cursor(buffered=True)
                cursor.execute('insert into stu_info(stu_fname,stu_lname,email,ph_no,password) values(%s,%s,%s,%s,%s)',[data2['fname'],data2['lname'],data2['email'],data2['phno'],data2['passw']])
                mydb.commit()
                cursor.close()
                flash('registration succesful')
                return redirect(url_for('login'))
                #print('done')
            else:
                return "the entered otp is wrong please check your mail"
    
    finally:
        print('done')
    
    return render_template('verify.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['em']
        passwrd=request.form['pw']
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select email,password from stu_info where email=%s',[email])
            data=cursor.fetchone()
            print(data[1])
            
        except Exception as e:
            print(e)
            return "email wrong"
        else:
            if data[1]==passwrd.encode('utf-8'):
                session['email']=email
                if not session.get(email):
                    session[email]={}
                return render_template('panel.html')
            else:
                return flash('invalid password')
    return render_template('login.html')

@app.route('/addnotes',methods=['POST','GET'])
def addnotes():
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        cursor=mydb.cursor(buffered=True)
        #cursor.execute('insert into notes(title,content,added_by) values(%s,%s,%s)',[title,content,])
    return render_template('notes.html')


app.run(debug=True,use_reloader=True)
    