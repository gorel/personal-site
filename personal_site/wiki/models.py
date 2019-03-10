import datetime
import re
import string

import markdown

from markdown.extensions import (
    extra,
    nl2br,
    toc,
    wikilinks,
)


WIKI_EXTENSIONS = [
    extra.ExtraExtension(),
    nl2br.Nl2BrExtension(),
    toc.TocExtension(),
    wikilinks.WikiLinkExtension(base_url="/wiki/"),
]

import flask_login

from personal_site import db


MD = markdown.Markdown(extensions=WIKI_EXTENSIONS)


class WikiPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idname = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    last_modified_at = db.Column(db.DateTime)

    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    creator = db.relationship("User", foreign_keys=[creator_id])
    last_editor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    last_editor = db.relationship("User", foreign_keys=[last_editor_id])

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

    @property
    def toc(self):
        return MD.toc

    @property
    def html(self):
        return MD.convert(self.content)

    @property
    def preview(self):
        contents = self.content[:200].replace("#", "") + "..."
        return MD.convert(contents)

    def __repr__(self):
        return f"<WikiPage {self.id}: {idname}>"

    @classmethod
    def name_to_idname(cls, name):
        valid = string.ascii_letters + string.digits + " "
        stripped = "".join(
            c for c in name
            if c in valid
        )
        # Remove multiple spaces
        idname = re.sub(" +", " ", name)
        return idname

    @classmethod
    def get_by_idname(cls, idname):
        return cls.query.filter_by(idname=idname).first()

    @classmethod
    def get_by_idname_or_404(cls, idname):
        return cls.query.filter_by(idname=idname).first_or_404()
