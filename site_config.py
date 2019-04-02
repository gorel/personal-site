import os

import dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    SERVER_HOST = os.environ.get("SERVER_HOST")
    FLASK_RUN_PORT = int(os.environ.get("FLASK_RUN_PORT"))
    DEBUG = bool(os.environ.get("FLASK_DEBUG")) or False
    TESTING = os.environ.get("TESTING") or False
    LOGFILE = os.environ.get("LOGFILE")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SHELVE_FILENAME = os.environ.get("SHELVE_FILENAME")

    REDIS_URL = os.environ.get("REDIS_URL")
    RQ_NAME = os.environ.get("RQ_NAME")

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
    RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")
    RECAPTCHA_DATA_ATTRS = {"theme": "dark"}

    SECRET_KEY = os.environ.get("SECRET_KEY")
    ADMIN = os.environ.get("ADMIN_EMAIL")
    EXT_ADMIN = os.environ.get("EXT_ADMIN_EMAIL")
    LANGUAGES = ["en"]
