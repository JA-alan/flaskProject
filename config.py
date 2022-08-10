import os

# 数据库配置
HOSTNAME = 'localhost'
PORT = '3306'
DATABASE = 'flask-hero'
USERNAME = 'root'
PASSWORD = 'asd123456'
DB_URL = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'\
    .format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URL
SQLALCHEMY_TRACK_MODIFICATIONS = True
DEBUG = True
SECRET_KEY = "jianganran1234"

# 邮箱配置
MAIL_SERVER = "smtp.163.com"
MAIL_PORT =465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEBUG = True
MAIL_USERNAME = "jiangantest@163.com"
MAIL_PASSWORD = "ZLFHMDHBHICAGTYY"
MAIL_DEFAULT_SENDER = "jiangantest@163.com"

# 服务器配置
BASE_URL_DEV = "43.138.182.131"
BASE_URL_TEST = "127.0.0.1"


# 日志配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))  # 项目根目录
LOG_PATH = os.path.join(PROJECT_ROOT, 'log', 'web.log')  # 日志路径


# 图片路径配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))  # 项目根目录
PHOTO_PATH = os.path.join(PROJECT_ROOT, 'static')
