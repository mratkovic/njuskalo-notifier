import smtplib
import logging
from email.mime.text import MIMEText


class Mail(object):

    def __init__(self, username, password, smtp_server='smtp.gmail.com', port=587):
        self.server = smtplib.SMTP(smtp_server, port)
        self.server.ehlo()
        self.server.starttls()
        self.server.login(username, password)

        self.username = username

    def send_mail(self, subject, body, to_address):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.username
        msg['To'] = to_address

        try:
            self.server.send_message(msg)
        except smtplib.SMTPException:
            logging.error("Error: unable to send email")
        finally:
            self.server.quit()
