import flask
import flask_login
import flask_wtf
import wtforms

from personal_site.learn import models


class AskQuestionForm(flask_wtf.Form):
    question = wtforms.TextAreaField(
        "What's your question?",
        validators=[wtforms.validators.DataRequired()],
        render_kw={"class": "form-control", "rows": 10, "style": "resize: vertical"},
    )
    show_anon = wtforms.BooleanField("Show as anonymous to classmates?")
    submit = wtforms.SubmitField("Submit")

    def __init__(self, page, *args, **kwargs):
        super(AskQuestionForm, self).__init__(*args, **kwargs)
        self.page = page
        self.learn_question = None

    def validate(self):
        if not super(AskQuestionForm, self).validate():
            return False

        self.question = models.LearnQuestion(
            question=self.question.data,
            page=self.page,
            asker=flask_login.current_user,
            show_anon=self.show_anon.data,
        )
        return True
