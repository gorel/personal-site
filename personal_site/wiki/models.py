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

from personal_site import constants, db, search


MD = markdown.Markdown(extensions=WIKI_EXTENSIONS)


class WikiPage(db.Model, search.SearchableMixin):
    __searchable__ = ["name", "content"]
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

    def __init__(self, name, content):
        self.idname = self.name_to_idname(new_name)
        self.name = name
        self.content = content
        self.created_at = datetime.datetime.utcnow()
        self.last_modified_at = datetime.datetime.utcnow()
        self.creator = flask_login.current_user
        self.last_editor = flask_login.current_user
        self.views = 0

    def edit(self, editor, new_name, new_content):
        if self.name == new_name and self.content == new_content:
            return
        self.idname = self.name_to_idname(new_name)
        self.name = new_name
        self.content = new_content
        self.last_edtior = editor
        self.last_modified_at = datetime.datetime.utcnow()

    @property
    def was_edited(self):
        diff = abs(self.created_at - self.last_modified_at)
        return diff.seconds > 0

    @property
    def toc(self):
        contents = MD.convert(self.content)
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

    @staticmethod
    def name_to_idname(name):
        valid = string.ascii_letters + string.digits + " "
        stripped = "".join(
            c for c in name
            if c in valid
        )
        # Remove multiple spaces
        idname = re.sub(" +", " ", stripped)
        idname = idname.lower().replace(" ", "-")
        return idname

    @classmethod
    def get_by_idname(cls, idname):
        return cls.query.filter_by(idname=idname).first()

    @classmethod
    def get_by_idname_or_404(cls, idname):
        return cls.query.filter_by(idname=idname).first_or_404()
