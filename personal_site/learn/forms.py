import flask
import flask_login
import flask_wtf
import wtforms

from personal_site import db

from personal_site.learn import models


class AskQuestionForm(flask_wtf.FlaskForm):
    question = wtforms.TextAreaField(
        "What's your question?",
        validators=[wtforms.validators.DataRequired()],
        render_kw={"class": "form-control", "rows": 10, "style": "resize: vertical"},
    )
    show_anon = wtforms.BooleanField("Show as anonymous to classmates?")
    submit = wtforms.SubmitField("Submit")

    def __init__(self, page_name, *args, **kwargs):
        super(AskQuestionForm, self).__init__(*args, **kwargs)
        self.page_name = page_name
        self.learn_question = None

    def validate(self):
        if not super(AskQuestionForm, self).validate():
            return False

        self.learn_question = models.LearnQuestion(
            page_name=self.page_name,
            question=self.question.data,
            asker=flask_login.current_user,
            show_anon=self.show_anon.data,
        )

        db.session.add(self.learn_question)
        db.session.commit()
        return True


class AnswerQuestionForm(flask_wtf.FlaskForm):
    answer = wtforms.TextAreaField(
        "Question answer",
        validators=[wtforms.validators.DataRequired()],
        render_kw={"class": "form-control", "rows": 10, "style": "resize: vertical"},
    )
    mark_as_good = wtforms.BooleanField('Mark as "good question"?')
    submit = wtforms.SubmitField("Submit")

    def __init__(self, question, *args, **kwargs):
        super(AnswerQuestionForm, self).__init__(*args, **kwargs)
        self.question = question

    def validate(self):
        if not super(AnswerQuestionForm, self).validate():
            return False

        self.question.answer = self.answer.data
        self.question.good_question = self.mark_as_good.data

        db.session.commit()
        return True
