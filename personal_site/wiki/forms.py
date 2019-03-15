import datetime

import flask
import flask_login
import flask_wtf
import wtforms

from personal_site import constants
from personal_site.wiki import models


class AddWikiPageForm(flask_wtf.Form):
    page_name = wtforms.StringField(
        "Page name",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(max=constants.WIKIPAGE_MAX_LEN),
        ],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    page_content = wtforms.TextAreaField(
        "Content",
        validators=[
            wtforms.validators.DataRequired(),
        ],
        render_kw={"class": "form-control", "rows": 20, "style": "resize: vertical"},
    )
    submit = wtforms.SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super(AddWikiPageForm, self).__init__(*args, **kwargs)
        self.page = None

    def validate(self):
        if not super(AddWikiPageForm, self).validate():
            return False

        idname = models.WikiPage.name_to_idname(self.page_name.data)
        page = models.WikiPage.get_by_idname(idname)
        if page is not None:
            self.page_name.errors.append("Page name not unique")
            return False

        self.page = models.WikiPage(
            name=self.page_name.data,
            content=self.page_content.data,
        )
        return True


class EditWikiPageForm(flask_wtf.Form):
    page_name = wtforms.StringField(
        "Page name",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(max=constants.WIKIPAGE_MAX_LEN),
        ],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    page_content = wtforms.TextAreaField(
        "Content",
        validators=[
            wtforms.validators.DataRequired(),
        ],
        render_kw={"class": "form-control", "rows": 20, "style": "resize: vertical"},
    )
    submit = wtforms.SubmitField("Submit")

    def __init__(self, page, *args, **kwargs):
        super(EditWikiPageForm, self).__init__(*args, **kwargs)
        self.page = page

    def validate(self):
        if not super(EditWikiPageForm, self).validate():
            return False

        idname = models.WikiPage.name_to_idname(self.page_name.data)
        page = models.WikiPage.get_by_idname(idname)
        # Page is allowed to be None if the page was renamed
        if page is not None and page.id != self.page.id:
            self.page_name.errors.append("Page name not unique")
            return False

        self.page.edit(
            editor=flask_login.current_user,
            new_name=self.page_name.data,
            new_content=self.page_content.data,
        )
        return True


class AskQuestionForm(flask_wtf.Form):
    question = wtforms.TextAreaField(
        "What's your question?",
        validators=[wtforms.validators.DataRequired()],
        render_kw={"class": "form-control", "rows": 10, "style": "resize: vertical"},
    )
    submit = wtforms.SubmitField("Submit", render_kw={"class": "btn btn-primary"})

    def __init__(self, *args, **kwargs):
        super(AskQuestionForm, self).__init__(*args, **kwargs)
        self.wiki_question = None

    def validate(self):
        if not super(AskQuestionForm, self).validate():
            return False

        self.question = Question(
            question=self.question.data,
            asker=flask_login.current_user,
        )
        return True


class SearchForm(flask_wtf.Form):
    q = wtforms.StringField(
        "Search",
        validators=[wtforms.validators.DataRequired()],
    )

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = flask.request.args
        if "csrf_enabled" not in kwargs:
            kwargs["meta"] = {"csrf": False}
        super(SearchForm, self).__init__(*args, **kwargs)
