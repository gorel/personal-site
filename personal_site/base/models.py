import datetime

import flask
import redis
import rq

from personal_site import constants, db


REPORT_TYPES = {
    1: "Report a bug",
    2: "Feature request",
    3: "Request new lesson",
}
REPORT_TYPES_INVERSE = {
    "BUG_REPORT": 1,
    "FEATURE_REQUEST": 2,
    "LESSON_REQUEST": 3,
}


class Task(db.Model):
    id = db.Column(db.String(constants.TASK_ID_LEN), primary_key=True)
    name = db.Column(db.String(constants.TASK_NAME_MAX_LEN), index=True)
    description = db.Column(db.String(constants.TASK_DESC_MAX_LEN))
    meta = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            return rq.job.Job.fetch(self.id, connection=flask.current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100


class SecretResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    secret_id = db.Column(db.Integer, db.ForeignKey("secret.id"))
    person = db.Column(db.String(constants.SECRET_PERSON_NAME_MAX_LEN))
    response = db.Column(db.String(constants.SECRET_RESPONSE_MAX_LEN))

    def __init__(self, secret, person, response):
        self.secret = secret
        self.person = person
        self.response = response
        self.secret.actual_responses += 1


class Secret(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortname = db.Column(db.String(constants.SECRET_SHORTNAME_MAX_LEN), index=True)
    responses = db.relationship("SecretResponse", backref="secret")
    expected_responses = db.Column(db.Integer)
    actual_responses = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


    def __init__(self, shortname, expected_responses):
        self.shortname = shortname
        self.expected_responses = expected_responses
        self.actual_responses = 0

    @classmethod
    def get_by_shortname(cls, shortname):
        return cls.query.filter_by(shortname=shortname).first()


class BugReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    report_type = db.Column(db.Integer)
    text_response = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship("User", foreign_keys=[user_id])

    def __init__(self, user, report_type, text_response):
        if report_type not in REPORT_TYPES.keys():
            raise ValueError(f"Invalid report type ({report_type}) not in {REPORT_TYPES.keys()}")
        self.user = user
        self.report_type = report_type
        self.text_response = text_response

    @property
    def report_type_str(self):
        return REPORT_TYPES[self.report_type]