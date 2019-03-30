import enum

import flask_wtf
import wtforms

from personal_site import constants, db

from personal_site.admin import models


class WarnUserForm(flask_wtf.Form):
    reason = wtforms.StringField(
        "Reason for warning?",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(max=constants.WARNING_MAX_LEN),
        ]
    )
    submit = wtforms.SubmitField("Submit")

    def __init__(self, user, *args, **kwargs):
        super(WarnUserForm, self).__init__(*args, **kwargs)
        self.user = user
        self.warning = None

    def validate(self):
        if not super(WarnUserForm, self).validate():
            return False

        self.warning = models.Warning(user=self.user, reason=self.reason.data)

        db.session.add(self.warning)
        db.session.commit()
        return True
