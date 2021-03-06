import collections
import datetime
import random

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


class MihkPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(constants.MIHK_PLAYER_NAME_MAX_LEN))
    game_id = db.Column(db.Integer, db.ForeignKey("mihk_game.id"))
    role = db.Column(db.Integer)


class MihkGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_players = db.Column(db.Integer)
    creator_is_fs = db.Column(db.Boolean)
    allow_extra_roles = db.Column(db.Boolean)
    players = db.relationship("MihkPlayer", backref="game")

    def role_to_str(self, role):
        return {
                0: "Forensic Scientist",
                1: "Murderer",
                2: "Accomplice",
                3: "Witness",
                4: "Investigator",
        }[role]

    def _get_all_roles(self):
        # I'm lazy and hard-coding this... it's bad.
        all_roles = [0, 1]
        if self.num_players > 5 and self.allow_extra_roles:
            all_roles += [2, 3]
        investigators = [4] * (self.num_players - len(all_roles))
        all_roles += investigators
        return all_roles

    def get_role(self, force_fs=False):
        # This is awful...
        if force_fs:
            return 0
        all_roles = self._get_all_roles()
        used_roles = [player.role for player in self.players]
        return random.choice(list((collections.Counter(all_roles) - collections.Counter(used_roles)).elements()))


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
