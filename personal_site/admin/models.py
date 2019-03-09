import datetime
import os

from personal_site import db


class ErrorReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    error_text = db.Column(db.Text)
    user_text = db.Column(db.Text)
    report_type = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    sent = db.Column(db.Boolean)
    submitted_at = db.Column(db.DateTime)

    def __init__(self, error_text, user_text, report_type):
        self.error_text = error_text
        self.user_text = user_text
        self.report_type = report_type
        self.submitted_at = datetime.datetime.now()

    def __repr__(self):
        pass
