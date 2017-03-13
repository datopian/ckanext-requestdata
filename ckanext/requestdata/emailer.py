import logging
import smtplib
from socket import error as socket_error
from email.mime.text import MIMEText




log = logging.getLogger(__name__)

FROM = ""
SMTP_SERVER = ""
SMTP_USER = ""
SMTP_PASSWORD = ""

def send_email(content, to, from_=FROM):

    msg = MIMEText(content,'plain','UTF-8')

    if isinstance(to, basestring):
        to = [to]
    msg['Subject'] = "Request data"
    msg['From'] = from_
    msg['To'] = ','.join(to)

    try:
        s = smtplib.SMTP(SMTP_SERVER)
        s.login(SMTP_USER, SMTP_PASSWORD)
        s.sendmail(from_, to, msg.as_string())
        s.quit()

        return 'Email message was successfully sent.'
    except socket_error:
        log.critical('Could not connect to email server. Have you configured the SMTP settings?')

        return 'An error occured while sending the email. Try again.'