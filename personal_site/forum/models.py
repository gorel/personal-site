import datetime

from personal_site import constants, db


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    message = db.Column(db.String(constants.NOTIFICATION_MAX_LEN))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)

    def __init__(self, recipient, message):
        self.recipient_id = recipient.id
        self.message = message


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comments = db.relationship("Comment", backref="parent_post", lazy="dynamic")
    num_comments = db.Column(db.Integer)
    title = db.Column(db.String(constants.POST_TITLE_MAX_LEN))
    body = db.Column(db.Text)
    posted_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    edited_at = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    last_activity = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)

    def __init__(self, author, title, body):
        self.author_id = author.id
        self.title = title
        self.body = body
        self.num_comments = 0

    def edit(self, new_body):
        if self.body == new_body:
            return
        self.body = new_body
        self.edited_at = datetime.datetime.now()
        self.last_activity = datetime.datetime.now()


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    body = db.Column(db.Text)
    posted_at = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    edited_at = db.Column(db.DateTime)

    def __init__(self, post, author, body):
        self.post_id = post.id
        self.author_id = author.id
        self.body = body

    def edit(self, new_body):
        if self.body == new_body:
            return
        self.body = new_body
        self.edited_at = datetime.datetime.now()
