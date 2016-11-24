import re

import psycopg2
from package.AGControl import *


class Database:
    def __init__(self):
        self.db_addr = config.db_addr

    def get_db_addr(self):
        return self.db_addr


def time_check_for_write():
    if re.search(config.time_to_write, time.strftime('%H:%M:%S')):
        return True


def form_status_tuple():
    status_tuple = ('NOW()',
                    status.get_humidity(),
                    status.get_temperature(),
                    controls.get_light_status(),
                    controls.get_fan_status(),
                    controls.get_autocontrol_flag(),
                    )
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
                time.sleep(5)
        except psycopg2.Error as err:
            print(err)
            logging.error(err)


def db_reading():
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
            return data
        except psycopg2.Error as err:
            logging.error(err)
            time.sleep(5)
    except psycopg2.Error as err:
        logging.error(err)
        time.sleep(10)


def db_maintenance():
    while controls.get_working_flag():
        db_writing()

# Init DB

DB = Database()
