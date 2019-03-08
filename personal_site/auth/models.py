import datetime
import hashlib
import random

import flask_login

from personal_site import bcrypt, db, login_manager, mail


RESET_LEN = 32


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


class PasswordReset(db.Model):
    __tablename__ = "password_reset"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    key = db.Column(db.String(RESET_LEN))
    expiration = db.Column(db.DateTime)

    def __init__(self, user, key=None):
        if key is None:
            key_exists_in_db = True
            while key_exists_in_db:
                key = ''.join(
                    random.choice(string.ascii_letters + string.digits)
                    for _ in range(RESET_LEN)
                )
                # Ensure key is unique
                pw_reset = self.__class__.query.filter_by(key=key).first()
                key_exists_in_db = pw_reset is not None

        self.user = user
        self.key = key
        # 48 hour expiration
        self.expiration = datetime.datetime.now() + datetime.timedelta(days=2)

    def __repr__(self):
        pass

    @classmethod
    def get_by_key(cls, key):
        pw_reset = cls.query.filter_by(key=key).first()
        if pw_reset is not None:
            return pw_reset.user
        return None


class User(db.Model, flask_login.UserMixin):
     __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64), index=True, unique=True)
    pw_hash = db.Column(db.String(64))
    email_verified = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)
    pw_reset = db.relationship(PasswordReset, backref="user")

    def __init__(self, name, email, password):
        flask_login.UserMixin.__init__(self)
        self.name = name
        self.email = email
        self.email_verified = False
        self.is_admin = False

        pw_bytes = bytes(password, encoding="utf-8")
        sha256 = hashlib.sha256(pw_bytes).hexdigest()
        self.pw_hash = bcrypt.generate_password_hash(sha256).decode("utf-8")


    def set_password(self, new_password):
        pw_bytes = bytes(new_password, encoding="utf-8")
        sha256 = hashlib.sha256(pw_bytes).hexdigest()
        self.pw_hash = bcrypt.generate_password_hash(sha256).decode("utf-8")

    def check_password(self, password):
        pw_bytes = bytes(password, encoding="utf-8")
        sha256 = hashlib.sha256(pw_bytes).hexdigest()
        return bcrypt.check_password_hash(self.pw_hash, sha256)

    def verify_email(self):
        self.email_verified = True

    def __repr__(self):
        pass

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
