import logging
import smtplib
from socket import error as socket_error
from email.mime.text import MIMEText

from pylons import config


log = logging.getLogger(__name__)

SMTP_SERVER = config.get('smtp.server', '')
SMTP_USER = config.get('smtp.user', '')
SMTP_PASSWORD = config.get('smtp.password', '')
SMTP_FROM = config.get('smtp.mail_from')

def send_email(content, to, subject):
    '''Sends email
       :param content: The body content for the mail.
       :type string:
       :param to: To whom will be mail sent
       :type string:
       :param subject: The subject of mail.
       :type string:


       :rtype: string

       '''
    msg = MIMEText(content,'plain','UTF-8')
    from_ = SMTP_FROM
    if isinstance(to, basestring):
        to = [to]
    msg['Subject'] = subject
    msg['From'] = from_
    msg['To'] = ','.join(to)

    try:
        s = smtplib.SMTP(SMTP_SERVER)
        s.login(SMTP_USER, SMTP_PASSWORD)
        s.sendmail(from_, to, msg.as_string())
        s.quit()

        response_dict = {
            'success' : True,
            'message' : 'Email message was successfully sent.'
        }
        return response_dict
    except socket_error:
        log.critical('Could not connect to email server. Have you configured the SMTP settings?')
        error_dict = {
            'success': False,
            'message' : 'An error occured while sending the email. Try again.'
        }
        return error_dict
