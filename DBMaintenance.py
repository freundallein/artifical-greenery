from AGControl import *
import psycopg2
import threading
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Database:
    def __init__(self, config):
        self.db_addr = "db configuration DSN like"
        self.smtp_server = config['smtp_server']
        self.smtp_port = int(config['smtp_port'])
        self.agc_mail = config['agc_mail']
        self.mail_pass = config['agc_mail_pass']
        self.recieve_mail = config['recieve_mail']

    def get_db_addr(self):
        return self.db_addr

    def get_smtp_server(self):
        return self.smtp_server

    def get_smtp_port(self):
        return self.smtp_port

    def get_agc_mail(self):
        return self.agc_mail

    def get_recieve_mail(self):
        return self.recieve_mail

    def get_mail_pass(self):
        return self.mail_pass


DB = Database(CONFIG)


def time_check_for_write():
    if re.search(r':00:30|:30:30', time.strftime('%H:%M:%S')):
        return True


def time_check_for_read():
    if re.search(r'12:15s:00', time.strftime('%H:%M:%S')):
        return True


def form_status_tuple():
    status_tuple = ('NOW()',
                    status.get_humidity(),
                    status.get_temperature(),
                    controls.get_light_status(),
                    controls.get_fan_status(),
                    controls.get_autocontrol_flag(),)
    return status_tuple


def db_writing():
    if time_check_for_write():
        try:
            conn = psycopg2.connect(DB.get_db_addr())
            cur = conn.cursor()
            sql_insertion = """INSERT INTO agc_table (
                date,
                humidity,
                temperature,
                light,
                fan,
                autocontrol)
                VALUES (%s,%s,%s,%s,%s,%s);"""
            try:
                cur.execute(sql_insertion, form_status_tuple())
                conn.commit()
                conn.close()
                time.sleep(1)
            except psycopg2.Error as err:
                print(err)
                logging.error(err)
                time.sleep(10)
        except psycopg2.Error as err:
            print(err)
            logging.error(err)


def db_reading():
    if time_check_for_read():
        try:
            conn = psycopg2.connect(DB.get_db_addr())
            cur = conn.cursor()
            sql_selection = """SELECT (
                date,
                humidity,
                temperature,
                light,
                fan,
                autocontrol)
                FROM agc_table
                WHERE date >= (NOW() - INTERVAL '1 DAY')
                ;"""
            try:
                cur.execute(sql_selection)
                data = cur.fetchall()
                conn.close()
                mail_send(data)
                time.sleep(1)
            except psycopg2.Error as err:
                print(err)
                logging.error(err)
                time.sleep(10)
        except psycopg2.Error as err:
            print(err)
            logging.error(err)


def form_mail_message(data):
    message_table = 'DATETIME HUMIDITY TEMPERATURE LIGHTS FAN AUTOCONTROL\n'
    for row in data:
        message_table += '\n' + str(row)
    message = MIMEMultipart()
    message['From'] = DB.get_agc_mail()
    message['To'] = DB.get_recieve_mail()
    message['Subject'] = 'Artificial Greenery Daily Report'
    message.attach(MIMEText(message_table))
    return message.as_string()


def mail_send(data):
    try:
        smtp_conn = smtplib.SMTP(DB.get_smtp_server(), DB.get_smtp_port(), timeout=30)
        smtp_conn.ehlo()
        smtp_conn.starttls()
        smtp_conn.login(DB.get_agc_mail(), DB.get_mail_pass())
        try:
            smtp_conn.sendmail(DB.get_agc_mail(), DB.get_recieve_mail(), form_mail_message(data))
            smtp_conn.quit()
        except smtplib.SMTPException as err:
            print(err)
            logging.error(err)
    except smtplib.SMTPException as err:
        print(err)
        logging.error(err)


def db_maintenance():
    while controls.get_working_flag():
        db_write_thread = threading.Thread(target=db_writing, args=())
        db_read_thread = threading.Thread(target=db_reading, args=())

        db_write_thread.start()
        db_read_thread.start()

        db_write_thread.join()
        db_read_thread.join()
