import flask_login
import flask_wtf
import wtforms

from personal_site import constants, db, models


class ShareSecretForm(flask_wtf.Form):
    shortname = wtforms.StringField(
        "Secret shortname",
        validators=[
            # TODO: alphanum + - or _
            wtforms.validators.Length(max=constants.SECRET_SHORTNAME_MAX_LEN),
        ],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    person = wtforms.StringField(
        "Your name",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(max=constants.SECRET_PERSON_NAME_MAX_LEN),
        ],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    response = wtforms.StringField(
        "Your secret",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(max=constants.SECRET_RESPONSE_MAX_LEN),
        ],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    expected_responses = wtforms.IntegerField(
        "How many *other* responses are expected?",
    )
    recaptcha = flask_wtf.RecaptchaField()
    submit = wtforms.SubmitField()

    def __init__(self, *args,**kwargs):
        super(ShareSecretForm, self).__init__(*args, **kwargs)
        self.secret = None
        self.secret_response = None

    def validate(self):
        if not super(ShareSecretForm, self).validate():
            return False

        self.secret = models.Secret.get_by_shortname(self.shortname.data)
        if self.secret is None:
            self.secret = models.Secret(
                shortname=self.shortname.data,
                # Add one for this user
                expected_responses=self.expected_responses.data + 1,
            )
            db.session.add(self.secret)
            db.session.commit()

        # Don't allow submissions if the secret already has all required responses
        if self.secret.expected_responses == self.secret.actual_responses:
            self.shortname.errors.append("That secret already has all required responses")
            return False

        self.secret_response = models.SecretResponse(
            secret_id=self.secret.id,
            person=self.person.data,
            response=self.response.data,
        )

        self.secret.actual_responses += 1
        db.session.add(self.secret_response)
        db.session.commit()

        return True


class BugReportForm(flask_wtf.Form):
    report_type = wtforms.SelectField(
        "What kind of report are you submitting?",
        coerce=int,
        choices=[(opt.as_int, opt.text) for opt in models.REPORT_TYPES],
        validators=[
            wtforms.validators.InputRequired(),
        ],
    )
    text_response = wtforms.TextAreaField(
        "Description",
        validators=[
            wtforms.validators.DataRequired(),
        ],
        render_kw={"class": "form-control", "rows": 20, "style": "resize: vertical"},
    )
    recaptcha = flask_wtf.RecaptchaField()
    submit = wtforms.SubmitField()

    def validate(self):
        if not super(BugReportForm, self).validate():
            return False

        user = None
        if flask_login.current_user.is_authenticated:
            user = flask_login.current_user
        bug_report = models.BugReport(
            user=user,
            report_type=self.report_type.data,
            text_response=self.text_response.data,
        )
        db.session.add(bug_report)
        db.session.commit()

        return True
