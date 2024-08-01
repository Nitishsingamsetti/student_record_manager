from flask import Flask,render_template,url_for,request
import mysql.connector
from otp import genotp
app=Flask(__name__)
mydb=mysql.connector.connect(host='localhost',user='root',password='nitish',db='spm')

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
        # print(fname,lname,email,passw,phno)
        otp=genotp()
        cursor=mydb.cursor(buffered=True)
        cursor.execute('insert into stu_info(stu_fname,stu_lname,email,ph_no,password) values(%s,%s,%s,%s,%s)',[fname,lname,email,phno,passw])
        mydb.commit()
        cursor.close()
        print('done')
    return render_template('signup.html')
    

app.run(debug=True,use_reloader=True)
    