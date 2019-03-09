import datetime

import flask_login

from personal_site import db


class WikiPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idname = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    last_modified_at = db.Column(db.DateTime)

    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    creator = db.relationship("User")
    last_editor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    last_editor = db.relationship("User")

    views = db.Column(db.Integer)

    def __init__(self, idname, name, content):
        self.idname = idname
        self.name = name
        self.content = content
        self.created_at = datetime.datetime.utcnow()
        self.last_modified_at = datetime.datetime.utcnow()
        self.creator = flask_login.current_user
        self.last_editor = flask_login.current_user
        self.views = 0

    def __repr__(self):
        return f"<WikiPage {self.id}: {idname}>"

    def with_toc(self):
        """Return the page contents with a Table of Contents header"""
        return "\n".join(["[TOC]", "", self.content])

    @classmethod
    def get_by_idname(cls, idname):
        return cls.query.filter_by(idname=idname).first()

    @classmethod
    def get_by_idname_or_404(cls, idname):
        return cls.query.filter_by(idname=idname).first_or_404()
