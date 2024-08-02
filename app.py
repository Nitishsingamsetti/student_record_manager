from flask import Flask,render_template,url_for,request,redirect
import mysql.connector
from otp import genotp
from cmail import sendmail
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
        subject="OTP verification for SPM application"
        body=f'Registration otp for SPM application {otp}'
        sendmail(to=email,subject=subject,body=body)
        return redirect(url_for('verifyotp'))
        # cursor=mydb.cursor(buffered=True)
        # cursor.execute('insert into stu_info(stu_fname,stu_lname,email,ph_no,password) values(%s,%s,%s,%s,%s)',[fname,lname,email,phno,passw])
        # mydb.commit()
        # cursor.close()
        # print('done')
        
    return render_template('signup.html')
@app.route('/otp',methods=['GET','POST'])
def verifyotp():
    return render_template('verify.html')
    

app.run(debug=True,use_reloader=True)
    