import enum

import flask_wtf
import wtforms

from personal_site import constants

from personal_site.admin import models


class ReportType(enum.IntEnum):
    BUG_REPORT = 1
    FEATURE_REQUEST = 2


class ErrorReportForm(flask_wtf.Form):
    report_type = wtforms.SelectField(
        "Is this a bug or a feature request?",
        coerce=int,
        choices=[
            (ReportType.BUG_REPORT, "I'm reporting a bug"),
            (ReportType.FEATURE_REQUEST, "I'm making a feature request"),
        ],
        validators=[
            wtforms.validators.InputRequired(),
        ],
    )
    error = wtforms.HiddenField()
    textbox = wtforms.TextAreaField(
        "Description",
        validators=[
            wtforms.validators.DataRequired(),
        ],
        render_kw={"class": "form-control", "rows": 20, "style": "resize: vertical"},
    )
    submit = wtforms.SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super(ErrorReportForm, self).__init__(*args, **kwargs)
        self.error_report = None

    def validate(self):
        if not super(ErrorReportForm, self).validate():
            return False

        self.error_report = models.ErrorReport(
            error_text=self.error.data,
            user_text=self.textbox.data,
            report_type=self.report_type_to_str(self.report_type.data),
        )
        return True

    def report_type_to_str(self, report_type_data):
        if report_type_data == ReportType.BUG_REPORT:
            return "Bug report"
        elif report_type_data == ReportType.FEATURE_REQUEST:
            return "Feature request"


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
        return True
