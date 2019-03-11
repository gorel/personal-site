import enum

import flask_wtf
import wtforms

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
    )
    submit = wtforms.SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super(ErrorReportForm, self).__init__(*args, **kwargs)
        self.error_report = None

    def validate(self):
        if not flask_wtf.Form.validate(self):
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
