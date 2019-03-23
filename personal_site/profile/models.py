import datetime

from personal_site import constants, db


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    message = db.Column(db.String(constants.NOTIFICATION_MAX_LEN))
    url_link = db.Column(db.String(constants.NOTIFICATION_URL_LINK_MAX_LEN))
    icon = db.Column(db.String(constants.ICON_MAX_LEN))
    text_class = db.Column(db.String(constants.TEXT_CLASS_MAX_LEN))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)

    def __init__(self, recipient, message, url_link=None, text_class=None, icon=None):
        self.recipient = recipient
        self.message = message
        self.url_link = url_link
        self.text_class = text_class
        self.icon = icon
        self.send()

    def send(self):
        if self.recipient.unread_notifications is None:
            self.recipient.unread_notifications = 0
        self.recipient.unread_notifications += 1
        db.session.commit()
