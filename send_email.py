import smtplib
import ssl
from os.path import basename
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email import encoders

host = "smtp.gmail.com"
port = "465"

login = "dalefenech2006@gmail.com"
password = "qbjx ivbb cyai upql"

context = ssl.create_default_context()

to = "dalefenech2006@gmail.com"
subject = "Recorded Video"
body = "Here is the most recent recorded video."

msg = MIMEMultipart()
msg['From'] = login
msg['To'] = to
msg['Subject'] = subject

msg.attach(MIMEText(body, 'plain'))

def attachVideo(filename):
    attachment = open(filename,"rb")
    attachment_package = MIMEBase('application', 'octet-stream')
    attachment_package.set_payload((attachment).read())
    encoders.encode_base64(attachment_package)
    attachment_package.add_header("Content-Disposition","attachment; filename=" + filename)
    msg.attach(attachment_package)

    email = msg.as_string()

    with smtplib.SMTP_SSL(host,port,context=context) as server:
        server.login(login, password)
        server.sendmail(login,to,email)
