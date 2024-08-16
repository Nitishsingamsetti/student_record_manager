from flask import Flask, render_template, url_for, request, redirect, flash, session, send_file
from flask_session import Session
import mysql.connector
from otp import genotp
from cmail import sendmail
from key import secret_key
from stoken import token, dtoken
from io import BytesIO
import re

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = secret_key
Session(app)
mydb = mysql.connector.connect(host='localhost', user='root', password='nitish', db='spm')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sign', methods=['POST', 'GET'])
def sign():
    if request.method == 'POST':
        fname = request.form['sfname']
        lname = request.form['slname']
        email = request.form['email']
        passw = request.form['passw']
        phno = request.form['phno']

        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT COUNT(email) FROM stu_info WHERE email=%s', [email])
        data = cursor.fetchone()[0]

        if data == 0:
            otp = genotp()
            user_data = {'otp': otp, 'email': email, 'fname': fname, 'lname': lname, 'passw':passw, 'phno': phno}
            subject = "OTP verification for SPM application"
            body = f'Registration otp for SPM application {otp}'
            sendmail(to=email, subject=subject, body=body)
            return redirect(url_for('verifyotp', data1=token(data=user_data)))
        else:
            flash('Email already exists')
            return redirect(url_for('sign'))

    return render_template('signup.html')

@app.route('/otp/<data1>', methods=['GET', 'POST'])
def verifyotp(data1):
    try:
        data2 = dtoken(data=data1)
    except Exception as e:
        print(e)
        return "Time out of OTP"

    if request.method == 'POST':
        uotp = request.form['verify']
        if uotp == data2['otp']:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('INSERT INTO stu_info(stu_fname, stu_lname, email, ph_no, password) VALUES(%s, %s, %s, %s, %s)', 
                           [data2['fname'], data2['lname'], data2['email'], data2['phno'], data2['passw']])
            mydb.commit()
            cursor.close()
            flash('Registration successful')
            return redirect(url_for('login'))
        else:
            return "The entered OTP is wrong. Please check your mail."

    return render_template('verify.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('email'):
        return redirect(url_for('panel'))

    if request.method == 'POST':
        email = request.form['em']
        passwrd = request.form['pw']

        try:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('SELECT email, password FROM stu_info WHERE email=%s', [email])
            data = cursor.fetchone()

            if data[1]==passwrd.encode('utf-8'):
                session['email']=email
                if not session.get(email):
                    session[email]={}
                return redirect(url_for('panel'))
            else:
                flash('Invalid email or password')
        except Exception as e:
            print(e)
            flash('An error occurred during login')

    return render_template('login.html')

@app.route('/addnotes', methods=['POST', 'GET'])
def addnotes():
    if not session.get('email'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        added_by = session.get('email')

        cursor = mydb.cursor(buffered=True)
        cursor.execute('INSERT INTO notes(title, note_content, added_by) VALUES(%s, %s, %s)', [title, content, added_by])
        mydb.commit()
        cursor.close()
        flash(f'Notes "{title}" added successfully')
        return redirect(url_for('panel'))

    return render_template('addnotes.html')

@app.route('/panel')
def panel():
    if not session.get('email'):
        return redirect(url_for('login'))
    return render_template('panel.html')

@app.route('/updatenotes/<notes_id>', methods=['POST', 'GET'])
def updatenotes(notes_id):
    if not session.get('email'):
        return redirect(url_for('login'))

    cursor = mydb.cursor(buffered=True)
    cursor.execute('SELECT title, note_content FROM notes WHERE notes_id=%s', [notes_id])
    note_data = cursor.fetchone()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor.execute('UPDATE notes SET title=%s, note_content=%s WHERE notes_id=%s', [title, content, notes_id])
        mydb.commit()
        cursor.close()
        flash(f'Notes "{title}" updated successfully')
        return redirect(url_for('panel'))

    return render_template('updatenotes.html', note_data=note_data)

@app.route('/viewnotes', methods=['POST', 'GET'])
def allnotes():
    if not session.get('email'):
        return redirect(url_for('login'))

    added_by = session.get('email')
    cursor = mydb.cursor(buffered=True)
    cursor.execute('SELECT notes_id, title, created_at FROM notes WHERE added_by=%s', [added_by])
    data = cursor.fetchall()
    return render_template('table.html', data=data)

@app.route('/logout')
def logout():
    if session.get('email'):
        session.pop('email')
    return redirect(url_for('login'))

@app.route('/viewnotes/<notes_id>')
def viewnotes(notes_id):
    if not session.get('email'):
        return redirect(url_for('login'))

    cursor = mydb.cursor(buffered=True)
    cursor.execute('SELECT title, note_content FROM notes WHERE notes_id=%s', [notes_id])
    note_data = cursor.fetchone()
    return render_template('viewnotes.html', note_data=note_data)

@app.route('/deletenotes/<notes_id>')
def deletenotes(notes_id):
    if not session.get('email'):
        return redirect(url_for('login'))

    cursor = mydb.cursor(buffered=True)
    cursor.execute('DELETE FROM notes WHERE notes_id=%s AND added_by=%s', [notes_id, session.get('email')])
    mydb.commit()
    cursor.close()
    flash(f'Notes "{notes_id}" deleted successfully')
    return redirect(url_for('panel'))

@app.route("/fileupload", methods=["GET", "POST"])
def fileupload():
    if not session.get('email'):
        return redirect(url_for('login'))

    if request.method == "POST":
        file = request.files['file']
        file_name = file.filename
        added_by = session.get('email')
        file_data = file.read()

        cursor = mydb.cursor(buffered=True)
        cursor.execute('INSERT INTO files_data(file_name, file_data, added_by) VALUES(%s, %s, %s)', [file_name, file_data, added_by])
        mydb.commit()
        cursor.close()
        flash(f"File '{file.filename}' added successfully")
        return redirect(url_for('panel'))

    return render_template("fileupload.html")

@app.route('/viewall_files')
def viewall_files():
    if not session.get('email'):
        return redirect(url_for('login'))

    added_by = session.get('email')
    cursor = mydb.cursor(buffered=True)
    cursor.execute('SELECT f_id, file_name, created_at FROM files_data WHERE added_by=%s', [added_by])
    data = cursor.fetchall()
    return render_template('allfiles.html', data=data)

@app.route('/view_file/<f_id>')
def view_file(f_id):
    if not session.get('email'):
        return redirect(url_for('login'))

    try:
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT file_name, file_data FROM files_data WHERE f_id=%s AND added_by=%s', [f_id, session.get('email')])
        fname, fdata = cursor.fetchone()
        bytes_data = BytesIO(fdata)
        filename = fname
        return send_file(bytes_data, download_name=filename, as_attachment=False)
    except Exception as e:
        print(e)
        return 'File not found'
    finally:
        cursor.close()

@app.route('/download_file/<f_id>')
def download_files(f_id):
    if not session.get('email'):
        return redirect(url_for('login'))

    try:
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT file_name, file_data FROM files_data WHERE f_id=%s AND added_by=%s', [f_id, session.get('email')])
        fname, fdata = cursor.fetchone()
        bytes_data = BytesIO(fdata)
        filename = fname
        return send_file(bytes_data, download_name=filename, as_attachment=True)
    except Exception as e:
        print(e)
        return 'File not found'
    finally:
        cursor.close()

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    if session.get('email'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        email = request.form['email']
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT COUNT(email) FROM stu_info WHERE email=%s', [email])
        count = cursor.fetchone()[0]

        if count == 0:
            flash('Email does not exist. Please register.')
            return redirect(url_for('sign'))
        elif count == 1:
            subject = "Reset link for SPM application"
            body = f'Reset link for SPM application {url_for("reset", data=token(data=email), _external=True)}'
            sendmail(to=email, subject=subject, body=body)
            flash('Reset link has been sent to your email')
        else:
            flash('Something went wrong')

    return render_template('forgot.html')

@app.route('/reset/<data>', methods=['GET', 'POST'])
def reset(data):
    try:
        email = dtoken(data=data)
    except Exception as e:
        print(e)
        return 'Something went wrong'

    if request.method == 'POST':
        npassword = request.form['npwd']
        cpassword = request.form['cpwd']

        if npassword == cpassword:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('UPDATE stu_info SET password=%s WHERE email=%s', [npassword, email])
            mydb.commit()
            cursor.close()
            flash('Password updated successfully')
            return redirect(url_for('login'))

    return render_template('newpassword.html')

@app.route('/search',methods=["GET,POST"])
def search():
    if session.get('email'):
        if request.method=="POST":
            name=request.form["sname"]
            strg=["A-Za-z0-9"]
            pattern=re.compile(f'^{strg}',re.IGNORECASE)
            if (pattern.match(name)):
                cursor=mydb.cursor(buffered=True)
                cursor.execute('select * from notes where added_by=%s and title like %s',[session.get('email'),name+'%'])
                sname=cursor.fetchall()
                cursor.execute('select f_id,file_name,created_at from files_data where added_by=%s and file_name like %s',[session.get('email'),name+'%'])
                fname=cursor.fetchall()
                cursor.close()
                return render_template('panel.html',sname=sname,fname=fname)
            else:
                flash('result nor found')
                return render_template(url_for('panel'))
        else:
            return redirect(url_for('login'))
    



if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
