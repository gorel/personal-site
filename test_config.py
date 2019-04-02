class TestConfig(object):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = "redis://"
    RQ_NAME = "personal_site-test"
    ADMIN = "noreply@logangore.dev"
    EXT_ADMIN = "noreply@logangore.dev"
    SECRET_KEY = "testing"
    SHELVE_FILENAME = "test_shelve.db"
    RECAPTCHA_PUBLIC_KEY = ""
    RECAPTCHA_PRIVATE_KEY = ""
