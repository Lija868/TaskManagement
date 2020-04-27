
import pymysql
import schedule
import time

import csv
import datetime
import os
from datetime import date
from datetime import timedelta
import json
import sys

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

arguments = sys.argv[1:]
if not arguments:
    exit()
config_file_path = arguments[0]


with open(config_file_path, 'r') as f:
    config = json.load(f)

host = config['db_config']['host_ip']
user = config['db_config']['user_name']
password = config['db_config']['password']
db = config['db_config']['db_name']
file_path = config['app_config']['csv_file_folder']
from_mail = config['email_config']['from_mail']
to_mail = config['email_config']['to_mail']
from_mail_password = config['email_config']['from_mail_password']


def getConnection():
    con = pymysql.connect(host, user, password, db, charset='utf8')
    return con


def send_mail(file_name, file_path):
    # instance of MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = from_mail
    msg['To'] = to_mail
    msg['Subject'] = "Weekly Task List"
    body = "Task list analysis"
    msg.attach(MIMEText(body, 'plain'))
    actual_path = file_path + "\\" + file_name
    attachment = open(actual_path, "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % file_name)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(from_mail, from_mail_password)
    text = msg.as_string()
    response = s.sendmail(from_mail, to_mail, text)
    s.quit()

def export_users_csv():

    query = "SELECT `api_v0_task`.`task_name`, `api_v0_task`.`task_description`, `api_v0_task`.`task_start_time`, `api_v0_task`.`expected_completetion_time`," \
            " `api_v0_task`.`actual_completetion_time` FROM `api_v0_task` " \
            "WHERE `api_v0_task`.`task_start_time` BETWEEN %s AND %s"

    end_date = datetime.datetime.today().date()
    start_date = (datetime.datetime.today() - timedelta(days=5)).date()
    try:
        con = getConnection()
        cursor = con.cursor()
        cursor.execute(query, (start_date, end_date))
        result_set = cursor.fetchall()
        folder_name = str(date.today())
        path = file_path + folder_name
        if not os.path.isdir(path):
            os.mkdir(path)
        file_name = "task.csv"
        csvfile = open(path + '\\' + file_name, 'w', newline='')
        writer = csv.writer(csvfile)
        writer.writerow(['Task name', 'task_description', 'task_start_times', 'expected_completetion_time',
                         'actual_completetion_time'])
        for task in result_set:
            writer.writerow(task)
        csvfile.close()
        send_mail(file_name, path)


    except Exception as e:
        return


schedule.every().saturday.at("00:57").do(export_users_csv)

# Loop so that the scheduling task
# keeps on running all time.
while True:
    # Checks whether a scheduled task
    # is pending to run or not
    schedule.run_pending()
    time.sleep(1)
