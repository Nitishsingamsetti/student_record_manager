import smtplib
from smtplib import SMTP
from email.message import EmailMessage
def sendmail(to,body,subject):
    server=smtplib.SMTP_SSL("smtp.gmail.com",587)
    server.login("nsingamsetti11@gmail.com","qdiv ovua clvq kwfz")
    msg=EmailMessage()
    msg['FROM']="nsingamsetti11@gmail.com"
    msg['TO']=to
    msg['SUBJECT']=subject
    msg.set_content(body)
    server.send_message(msg)
    server.close()