import datetime

import flask
import markdown

from personal_site import constants, db


class PostFollow(db.Model):
    __tablename__ = "post_follow"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))


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

    show_anon = db.Column(db.Boolean)

    followers = db.relationship("User", secondary="post_follow", lazy="dynamic")

    def __init__(self, author, title, body, show_anon):
        self.author_id = author.id
        self.title = title
        self.body = body
        self.num_comments = 0
        self.show_anon = show_anon

    def edit(self, new_body, new_anon_policy):
        if self.body == new_body and self.show_anon == new_anon_policy:
            return
        self.body = new_body
        self.show_anon = new_anon_policy
        self.edited_at = datetime.datetime.now()
        self.last_activity = datetime.datetime.now()

    def notify_followers(self, poster):
        url = flask.url_for("forum.view_post", post_id=self.id)
        for follower in self.followers:
            # Don't notify the comment author
            if follower.id != poster.id:
                follower.notify(constants.NEW_COMMENT_NOTIF_STR, url)

    @property
    def html_body(self):
        return markdown.markdown(self.body, extensions=["extra", "codehilite"])

    @property
    def was_edited(self):
        diff = abs(self.posted_at - self.edited_at)
        return diff.seconds > 0


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comment_idx = db.Column(db.Integer)
    body = db.Column(db.Text)

    posted_at = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    edited_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    show_anon = db.Column(db.Boolean)

    def __init__(self, post, author, body, show_anon):
        self.post_id = post.id
        # comment_idx helps with redirects after an edit
        post.num_comments += 1
        self.comment_idx = post.num_comments
        self.author_id = author.id
        self.body = body
        self.show_anon = show_anon

    def edit(self, new_body, new_anon_policy):
        if self.body == new_body and self.show_anon == new_anon_policy:
            return
        self.body = new_body
        self.show_anon = new_anon_policy
        self.edited_at = datetime.datetime.utcnow()

    @property
    def html_body(self):
        return markdown.markdown(self.body, extensions=["extra", "codehilite"])

    @property
    def was_edited(self):
        diff = abs(self.posted_at - self.edited_at)
        return diff.seconds > 0
