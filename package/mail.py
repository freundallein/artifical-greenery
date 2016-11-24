import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTPException

from package import config


def form_mail_message(data):
    message_table = 'DATETIME HUMIDITY TEMPERATURE LIGHTS FAN AUTOCONTROL\n'
    for row in data:
        message_table += '\n' + str(row)
    message = MIMEMultipart()
    message['From'] = config.agc_mail
    message['To'] = '; '.join(config.recieve_mails)
    message['Subject'] = 'Artificial Greenery Daily Report'
    message.attach(MIMEText(message_table))
    return message.as_string()


def mail_send(data):
    try:
        smtp_conn = SMTP(config.smtp_server, config.smtp_port, timeout=30)
        smtp_conn.ehlo()
        smtp_conn.starttls()
        smtp_conn.login(config.agc_mail, config.agc_mail_pass)
        try:
            smtp_conn.sendmail(config.agc_mail, config.recieve_mails, form_mail_message(data))
            smtp_conn.quit()
        except SMTPException as err:
            print(err)
            logging.error(err)
    except SMTPException as err:
        print(err)
        logging.error(err)
