import os

class Config:
    SECRET_KEY = 'your_secret_key'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'marcocoppola135@gmail.com'
    MAIL_PASSWORD = 'rp9uqL,5\reTJN'
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'my-secret-pw')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'asset_managment')
