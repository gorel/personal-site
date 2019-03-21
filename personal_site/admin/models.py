import datetime
import os

from personal_site import db, constants

class Warning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    reason = db.Column(db.String(constants.WARNING_MAX_LEN))
    timestamp = db.Column(db.DateTime)

    def __init__(self, user, reason):
        self.user = user
        self.reason = reason
        self.timestamp = datetime.datetime.utcnow()


class ErrorReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    error_text = db.Column(db.Text)
    user_text = db.Column(db.Text)
    # TODO - Define report_type enum somewhere
    report_type = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    sent = db.Column(db.Boolean)
    submitted_at = db.Column(db.DateTime)

    def __init__(self, error_text, user_text, report_type):
        self.error_text = error_text
        self.user_text = user_text
        self.report_type = report_type
        self.submitted_at = datetime.datetime.utcnow()

    def __repr__(self):
        return f"<ErrorReport {self.id}>"
