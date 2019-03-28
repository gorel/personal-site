import datetime
import enum
import os

from personal_site import db, constants

import personal_site.profile.models as profile_models


class Warning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    reason = db.Column(db.String(constants.WARNING_MAX_LEN))
    timestamp = db.Column(db.DateTime)

    def __init__(self, user, reason):
        self.user = user
        self.reason = reason
        self.timestamp = datetime.datetime.utcnow()
        self.send_notification()

    def send_notification(self):
        notification = profile_models.Notification(
            recipient=self.user,
            message=self.reason,
            icon=constants.WARNING_ICON,
            text_class=constants.WARNING_TEXT_CLASS,
        )
        db.session.add(notification)
        db.session.commit()
