#!/usr/bin/python3
import os
import smtplib
import mysql.connector
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
import configparser
import time
import shutil
import gzip
import glob

LOG_FILE = '/var/log/envirocheck.log'
MAX_LOG_AGE = 2  # days
MAX_GZ_LOG_AGE = 7  # days

# Set up logging
def setup_logging():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def rotate_log_file():
    if os.path.exists(LOG_FILE):
        log_file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(LOG_FILE))
        if log_file_age.days >= MAX_LOG_AGE:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            compressed_log_file = f'/var/log/{timestamp}-envirocheck.log.gz'

            # Compress and rename the log file
            with open(LOG_FILE, 'rb') as f_in:
                with gzip.open(compressed_log_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Remove the old log file
            os.remove(LOG_FILE)

            # Create a new log file
            open(LOG_FILE, 'w').close()

            # Set appropriate permissions (if necessary)
            os.chmod(LOG_FILE, 0o666)  # This sets the file to be read/writable by all users
            logging.info(f'Log file rotated and new log file created: {compressed_log_file}')

def remove_old_gz_logs():
    # Find all gzipped log files
    gz_log_files = glob.glob('/var/log/*-envirocheck.log.gz')
    now = time.time()
    for gz_log_file in gz_log_files:
        file_age = now - os.path.getmtime(gz_log_file)
        if file_age > MAX_GZ_LOG_AGE * 86400:  # 86400 seconds in a day
            os.remove(gz_log_file)
            logging.info(f'Removed old gzipped log file: {gz_log_file}')

rotate_log_file()
remove_old_gz_logs()
setup_logging()

# Read environment variable for config file location
config_file_path = os.getenv('ENVIRO_INI_LOC')
if not config_file_path:
    logging.error('Environment variable ENVIRO_INI_LOC not set')
    raise EnvironmentError('ENVIRO_INI_LOC not set')

# Read the config file
config = configparser.ConfigParser()
config.read(config_file_path)

# Database credentials
db_config = {
    'user': config['database']['user'],
    'password': config['database']['password'],
    'host': config['database']['host'],
    'database': config['database']['database']
}

# Email configuration
smtp_server = config['email']['smtp_server']
smtp_port = config['email']['smtp_port']
smtp_user = config['email']['smtp_user']
smtp_password = config['email']['smtp_password']
email_from = config['email']['email_from']
email_to = config['email']['email_to']
email_subject = 'Enviro is Down'
email_body = 'Enviro needs to be rebooted'

# Retry configuration
max_retries = 3
retry_delay = 5  # in seconds

def send_email(subject, body):
    attempts = 0
    while attempts < max_retries:
        try:
            message = MIMEMultipart()
            message['From'] = email_from
            message['To'] = email_to
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(email_from, email_to, message.as_string())
            logging.info('Email sent successfully')
            return
        except smtplib.SMTPException as email_error:
            attempts += 1
            logging.error(f'Failed to send email on attempt {attempts}: {email_error}')
            if attempts < max_retries:
                logging.info(f'Retrying in {retry_delay} seconds...')
                time.sleep(retry_delay)
            else:
                logging.error('Max retries reached. Email could not be sent.')
                raise

def main():
    try:
        # Connect to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        logging.info('Connected to the database successfully')

        # Query the last available record
        cursor.execute("SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1")
        record = cursor.fetchone()

        if record:
            record_timestamp = record['timestamp']
            logging.info(f'Last record timestamp: {record_timestamp}')

            # Compare with the current system datetime
            current_datetime = datetime.now()
            if current_datetime - record_timestamp >= timedelta(minutes=30):
                logging.info('Timestamp is 30 minutes or more behind current datetime. Sending email...')
                send_email(email_subject, email_body)
            else:
                logging.info('Timestamp is within acceptable range')
        else:
            logging.warning('No records found in the readings table')

    except mysql.connector.Error as db_error:
        logging.error(f'Database error: {db_error.errno} - {db_error.msg}')
    except smtplib.SMTPException as email_error:
        logging.error(f'Email error: {email_error}')
    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()
        logging.info('Database connection closed')

if __name__ == '__main__':
    main()
