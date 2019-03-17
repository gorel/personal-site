import datetime

import flask_login

from personal_site import constants, db, search


class LearnPageStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(constants.LEARNPAGE_MAX_LEN))
    views = db.Column(db.Integer)

    def __init__(self, page_name):
        self.page_name = page_name
        self.views = 0


class LearnQuestion(db.Model, search.SearchableMixin):
    __searchable__ = ["question", "answer"]
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)

    page_name = db.Column(db.String(constants.LEARNPAGE_MAX_LEN), index=True)

    asker_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    asker = db.relationship("User", foreign_keys=[asker_id])
    show_anon = db.Column(db.Boolean)

    good_question = db.Column(db.Boolean, index=True, default=False)

    def __init__(self, question, page_name, asker, show_anon):
        self.question = question
        self.page_name = page
        self.asker = asker
        self.show_anon = show_anon

    def submit_answer(self, answer_text, mark_as_good=False):
        self.answer = answer_text
        self.good_question = mark_as_good

    def __repr__(self):
        return f"<Question {self.id}>"
