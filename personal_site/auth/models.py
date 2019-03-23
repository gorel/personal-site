import datetime
import hashlib
import random
import string
import time

import flask
import flask_login
import jwt

from personal_site import bcrypt, db, login_manager, mail
import personal_site.forum.models as forum_models


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(64), index=True, unique=True)
    pw_hash = db.Column(db.String(64))
    email_verified = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)

    warnings = db.relationship("Warning", backref="user", lazy="dynamic")

    notifications = db.relationship("Notification", backref="recipient", lazy="dynamic")
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    last_notification_read_time = db.Column(db.DateTime)

    tasks = db.relationship("Task", backref="user", lazy="dynamic")

    def __init__(self, username, email, password):
        flask_login.UserMixin.__init__(self)
        self.username = username
        self.email = email
        self.email_verified = False
        self.is_admin = False

        pw_bytes = bytes(password, encoding="utf-8")
        sha256 = hashlib.sha256(pw_bytes).hexdigest()
        self.pw_hash = bcrypt.generate_password_hash(sha256).decode("utf-8")
        self.send_verify_account_email()

    def set_password(self, new_password):
        pw_bytes = bytes(new_password, encoding="utf-8")
        sha256 = hashlib.sha256(pw_bytes).hexdigest()
        self.pw_hash = bcrypt.generate_password_hash(sha256).decode("utf-8")

    def check_password(self, password):
        pw_bytes = bytes(password, encoding="utf-8")
        sha256 = hashlib.sha256(pw_bytes).hexdigest()
        return bcrypt.check_password_hash(self.pw_hash, sha256)

    def gen_token(self, kind, exp_seconds=None):
        blob = {kind: self.id}
        if exp_seconds is not None:
            blob["exp"] = time.time() + exp_seconds
        return jwt.encode(
            blob,
            flask.current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    def set_banned(self, banned_status):
        # TODO: Send a notification/email here in the future
        self.is_banned = banned_status

    def launch_task(self, task_name, description, *args, **kwargs):
        # TODO: Can't get imports to work correctly here
        #if task_name not in flask.current_app.registered_tasks:
        #    raise NameError(f"Task {task_name} has not been registered")

        rq_job = flask.current_app.task_queue.enqueue(
            constants.TASK_PREFIX + task_name,
            self.id,
            *args,
            **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description, user=self)
        db.session.add(task)
        db.session.commit()
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self, complete=False).first()

    @classmethod
    def gen_user_for_token(cls, kind, token):
        try:
            obj = jwt.decode(
                token,
                flask.current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )
            flask.current_app.logger.info(f"jwt decode: {obj}")
            user_id = obj[kind]
        except Exception as e:
            flask.current_app.logger.warning(f"jwt decode exception: {e}")
            return None
        return cls.query.get(user_id)

    def send_verify_account_email(self):
        # TODO - Magic constant
        token = self.gen_token("verify_account")

        self.launch_task(
            name="send_email",
            description=f"Email verification for user_id={self.id}",
            # func args below
            email_props={
                "subject": "[LoganGore] Verify your email",
                "sender": flask.current_app.config["ADMINS"][0],
                "recipients": [self.email],
                "text_body": flask.render_template(
                    "auth/email/verify_account.txt",
                    user=self,
                    token=token,
                ),
                "html_body": flask.render_template(
                    "auth/email/verify_account.html",
                    user=self,
                    token=token,
                ),
            },
        )

    def verify_email(self):
        self.email_verified = True

    def send_reset_password_email(self):
        # 24 hours
        exp_seconds = 60 * 60 * 24
        # TODO: Magic constant
        token = self.gen_token("reset_password", exp_seconds=exp_seconds)

        self.launch_task(
            name="send_email",
            description=f"Password reset email for user_id={self.id}",
            # func args below
            email_props={
                "subject": "[LoganGore] Reset your password",
                "sender": flask.current_app.config["ADMINS"][0],
                "recipients": [self.email],
                "text_body": flask.render_template(
                    "auth/email/reset_password.txt",
                    user=self,
                    token=token,
                ),
                "html_body": flask.render_template(
                    "auth/email/reset_password.html",
                    user=self,
                    token=token,
                ),
            },
        )

    def get_new_notifications(self):
        last_read_time = self.last_notification_read_time or datetime.datetime(1900, 1, 1)
        self.last_notification_read_time = datetime.datetime.utcnow()
        return forum_models.Notification.query.filter_by(recipient=self).filter(
            forum_models.Notification.timestamp > last_read_time).limit(10)

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
