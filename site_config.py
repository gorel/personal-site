import os

import dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    SERVER_HOST = os.environ.get("SERVER_HOST")
    SERVER_PORT = int(os.environ.get("SERVER_PORT")) or 9999
    SITE_URL = os.environ.get("SITE_URL")
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT")) or 25
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    SECRET_KEY = os.environ.get("SECRET_KEY")
    ADMINS = [os.environ.get("ADMIN_EMAIL")]
    LANGUAGES = ["en"]

