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
    )
    person = wtforms.StringField(
        "Your name",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(max=constants.SECRET_PERSON_NAME_MAX_LEN),
        ],
    )
    response = wtforms.StringField(
        "Your secret",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(max=constants.SECRET_RESPONSE_MAX_LEN),
        ],
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

        self.secret_response = models.SecretResponse(
            secret_id=self.secret.id,
            person=self.person.data,
            response=self.response.data,
        )

        self.secret.actual_responses += 1
        db.session.add(self.secret_response)
        db.session.commit()

        return True
