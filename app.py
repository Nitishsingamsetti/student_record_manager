from flask import Flask,render_template,url_for,request
app=Flask(__name__)

@app.route('/',methods=['POST','GET'])
def home():
    if request.method=='POST':
        fname=request.form['sfname']
        lname=request.form['slname']
        email=request.form['email']
        passw=request.form['passw']
        phno=request.form['phno']
    
    return render_template('index.html')

app.run(debug=True)
    