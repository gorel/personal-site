import os

import dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    SERVER_HOST = os.environ.get("SERVER_HOST")
    FLASK_RUN_PORT = int(os.environ.get("FLASK_RUN_PORT"))
    SITE_URL = os.environ.get("SITE_URL")
    DEBUG = bool(os.environ.get("FLASK_DEBUG")) or False
    LOGFILE = os.environ.get("LOGFILE")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SHELVE_FILENAME = os.environ.get("SHELVE_FILENAME")

    ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")

    REDIS_URL = os.environ.get("REDIS_URL")
    RQ_NAME = os.environ.get("RQ_NAME")

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    SECRET_KEY = os.environ.get("SECRET_KEY")
    ADMINS = [os.environ.get("ADMIN_EMAIL")]
    LANGUAGES = ["en"]

