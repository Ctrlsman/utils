from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from flask import current_app
import smtplib
import os


def send_file_mail(file_path, subject, tolist, content='', acc=None):
    sender = current_app.config['EMAIL_SENDER']
    password = current_app.config['EMAIL_PASSWORD']
    user = current_app.config['EMAIL_USER']
    smtpserver = current_app.config['EMAIL_SMTP_SERVER']

    f = open(file_path, 'rb')
    mail_body = f.read()
    att = MIMEApplication(mail_body)
    att.set_charset('utf8')
    att.add_header('Content-Disposition', 'attachment', filename=os.path.split(file_path)[1])
    f.close()
    msg = MIMEText(content, 'plain', 'utf-8')

    msgroot = MIMEMultipart('related')
    msgroot['Subject'] = subject
    msgroot['to'] = ','.join(tolist)
    msgroot['Cc'] = acc
    msgroot['from'] = sender

    msgroot.attach(msg)
    msgroot.attach(att)

    smtp = smtplib.SMTP_SSL()
    smtp.connect(smtpserver)
    smtp.login(user, password)
    smtp.sendmail(sender, tolist, msgroot.as_string())
    smtp.quit()
