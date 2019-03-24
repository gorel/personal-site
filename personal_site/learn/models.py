import datetime
import markdown
import os

import flask_login

from personal_site import constants, db, search


class LearnPageStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(constants.LEARNPAGE_MAX_LEN), index=True)
    views = db.Column(db.Integer)

    def __init__(self, page_name):
        self.page_name = page_name
        self.views = 0

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(page_name=name).first()

    @classmethod
    def get_or_create(cls, name):
        filepath = os.path.join(constants.LEARN_PAGE_TEMPLATE_DIR, name)
        template_fullpath = os.path.join(constants.TEMPLATE_DIR, filepath)
        page_stats = cls.get_by_name(name)

        if page_stats is None and os.path.exists(template_fullpath):
            page_stats = cls(name)
            db.session.add(page_stats)
            db.session.commit()
        return page_stats


class LearnQuestion(db.Model, search.SearchableMixin):
    __searchable__ = ["page_name", "question", "answer"]
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(constants.LEARNPAGE_MAX_LEN), index=True)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)

    asker_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    asker = db.relationship("User", foreign_keys=[asker_id])
    show_anon = db.Column(db.Boolean)

    good_question = db.Column(db.Boolean, index=True, default=False)

    def __init__(self, page_name, question, asker, show_anon):
        self.page_name = page_name
        self.question = question
        self.asker = asker
        self.show_anon = show_anon

    def submit_answer(self, answer_text, mark_as_good=False):
        self.answer = answer_text
        self.good_question = mark_as_good

    @property
    def html_question(self):
        return markdown.markdown(self.question, extensions=["extra", "codehilite"])

    @property
    def html_answer(self):
        return markdown.markdown(self.answer, extensions=["extra", "codehilite"])

    def __repr__(self):
        return f"<Question {self.id}>"
