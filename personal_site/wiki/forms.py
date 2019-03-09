import flask_wtf
import wtforms

from personal_site.wiki import models


class AddWikiPageForm(flask_wtf.Form):
    page_name = wtforms.TextField(
        "Page name",
        validators=[
            wtforms.validators.DataRequired(),
            # TODO - magic constant
            wtforms.validators.Length(max=64)
        ],
    )
    page_content = wtforms.TextAreaField(
        "Content",
        validators=[
            wtforms.validators.DataRequired(),
        ],
    )

    def __init__(self, *args, **kwargs):
        flask_wtf.Form.__init__(self, *args, **kwargs)
        self.page = None

    def validate(self):
        if not flask_wtf.Form.validate(self):
            return False

        idname = WikiPage.name_to_idname(self.page_name)
        page = WikiPage.get_by_idname(idname)
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
    page_name = wtforms.TextField(
        "Page name",
        validators=[
            wtforms.validators.DataRequired(),
            # TODO - magic constant
            wtforms.validators.Length(max=64)
        ],
    )
    page_content = wtforms.TextAreaField(
        "Content",
        validators=[
            wtforms.validators.DataRequired(),
        ],
    )

    def __init__(self, page, *args, **kwargs):
        flask_wtf.Form.__init__(self, *args, **kwargs)
        self.page = page

    def validate(self):
        if not flask_wtf.Form.validate(self):
            return False

        idname = WikiPage.name_to_idname(self.page_name)
        page = WikiPage.get_by_idname(idname)
        # Page is allowed to be None if the page was renamed
        if page is not None and page.id != self.page.id:
            self.page_name.errors.append("Page name not unique")
            return False

        self.page.name = self.page_name.data
        self.page.content = self.page_content.data
        return True
