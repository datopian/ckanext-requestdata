import logging
import smtplib
import cgi
from paste.deploy.converters import asbool
from socket import error as socket_error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders

from pylons import config


log = logging.getLogger(__name__)

SMTP_SERVER = config.get('smtp.server', '')
SMTP_USER = config.get('smtp.user', '')
SMTP_PASSWORD = config.get('smtp.password', '')
SMTP_FROM = config.get('smtp.mail_from')


def send_email(content, to, subject, file=None):
    '''Sends email
       :param content: The body content for the mail.
       :type string:
       :param to: To whom will be mail sent
       :type string:
       :param subject: The subject of mail.
       :type string:


       :rtype: string

       '''

    msg = MIMEMultipart()

    from_ = SMTP_FROM

    if isinstance(to, basestring):
        to = [to]

    msg['Subject'] = subject
    msg['From'] = from_
    msg['To'] = ','.join(to)

    content = """\
        <html>
          <head></head>
          <body>
            <p>""" + content + """</p>
          </body>
        </html>
    """

    msg.attach(MIMEText(content, 'html', _charset='utf-8'))

    if isinstance(file, cgi.FieldStorage):
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(file.file.read())
        Encoders.encode_base64(part)

        extension = file.filename.split('.')[-1]

        part.add_header('Content-Disposition', 'attachment; filename=attachment.{0}'.format(extension))

        msg.attach(part)

    try:
        s = smtplib.SMTP(SMTP_SERVER)
        if SMTP_USER:
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
