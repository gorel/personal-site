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
    )
    page_content = wtforms.TextAreaField(
        "Content",
        validators=[
            wtforms.validators.DataRequired(),
        ],
    )
    submit = wtforms.SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super(AddWikiPageForm, self).__init__(*args, **kwargs)
        self.page = None

    def validate(self):
        if not flask_wtf.Form.validate(self):
            return False

        idname = models.WikiPage.name_to_idname(self.page_name.data)
        page = models.WikiPage.get_by_idname(idname)
        if page is not None:
            self.page_name.errors.append("Page name not unique")
            return False

        self.page = models.WikiPage(
            idname=idname,
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
    )
    page_content = wtforms.TextAreaField(
        "Content",
        validators=[
            wtforms.validators.DataRequired(),
        ],
    )
    submit = wtforms.SubmitField("Submit")

    def __init__(self, page, *args, **kwargs):
        super(EditWikiPageForm, self).__init__(*args, **kwargs)
        self.page = page

    def validate(self):
        if not flask_wtf.Form.validate(self):
            return False

        idname = models.WikiPage.name_to_idname(self.page_name.data)
        page = models.WikiPage.get_by_idname(idname)
        # Page is allowed to be None if the page was renamed
        if page is not None and page.id != self.page.id:
            self.page_name.errors.append("Page name not unique")
            return False

        self.page.idname = idname
        self.page.name = self.page_name.data
        self.page.content = self.page_content.data
        self.page.last_editor = flask_login.current_user
        self.page.last_modified_at = datetime.datetime.utcnow()
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
            kwargs["csrf_enabled"] = False
        super(SearchForm, self).__init__(*args, **kwargs)
