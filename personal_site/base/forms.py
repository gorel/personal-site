import json
import random

import flask
import flask_login
import flask_wtf
import wtforms

from personal_site import constants, db
from personal_site.base import models


def check_allowed_characters(charset, message=None):
    charset_str = "".join(sorted(charset))
    if message is None:
        message = f"Valid characters for this field: '{charset_str}'"
    # Checks that all characters in field.data are in the allowed charset
    def _check_allowed_characters(form, field):
        for c in field.data:
            if c not in charset:
                raise wtforms.ValidationError(message)
    return _check_allowed_characters


class ShareSecretForm(flask_wtf.FlaskForm):
    shortname = wtforms.StringField(
        "Secret shortname",
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.Length(max=constants.SECRET_SHORTNAME_MAX_LEN),
            check_allowed_characters(constants.SECRET_SHORTNAME_CHARSET),
        ],
        render_kw={
            "class": "form-control",
            "autocomplete": "off",
            "placeholder": constants.SECRET_SHORTNAME_PLACEHOLDER_TEXT,
        },
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

    def __init__(self, secret, *args,**kwargs):
        super(ShareSecretForm, self).__init__(*args, **kwargs)
        self.secret = secret
        self.secret_response = None
        if secret is not None:
            del self.shortname
            del self.expected_responses

    def validate(self):
        if not super(ShareSecretForm, self).validate():
            return False

        if self.secret is None and len(self.shortname.data) == 0:
            self.shortname.data = "".join(
                random.choice(tuple(constants.SECRET_SHORTNAME_CHARSET))
                for _ in range(constants.SECRET_SHORTNAME_GEN_LEN)
            )

        if self.secret is None:
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
            # If the user clicked a direct link, shortname field is removed
            msg = "That secret already has all required responses"
            if self.shortname is not None:
                self.shortname.errors.append(msg)
            else:
                flask.flash(
                    json.dumps({
                        "msg": msg,
                        "link": flask.url_for("default.secret", secret_id=self.secret.id),
                    }),
                    "alert-warning",
                )
            return False

        self.secret_response = models.SecretResponse(
            secret=self.secret,
            person=self.person.data,
            response=self.response.data,
        )

        db.session.add(self.secret_response)
        db.session.commit()

        return True


class StartMihkGameForm(flask_wtf.FlaskForm):
    num_players = wtforms.IntegerField(
        "How many players will be in the game?",
        wtforms.validators.DataRequired(),
    )
    creator_is_fs = wtforms.BooleanField(
        "Will you be acting as the Forensic Investigator?"
    )
    player = wtforms.StringField(
        "Your name",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(max=constants.MIHK_PLAYER_NAME_MAX_LEN),
        ],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )

    def validate(self):
        if not super(StartMihkGameForm, self).validate():
            return False

        self.game = models.MihkGame(
            num_players=self.num_players.data,
            creator_is_fs=self.creator_is_fs.data,
        )
        db.session.add(self.game)
        db.session.commit()

        role = self.game.get_role()
        self.player = models.MihkPlayer(name=self.player.data, game_id=self.game.id, role=role)
        db.session.add(self.player)
        db.session.commit()

        return True


class JoinMihkGameForm(flask_wtf.FlaskForm):
    player = wtforms.StringField(
        "Your name",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(max=constants.MIHK_PLAYER_NAME_MAX_LEN),
        ],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )

    def __init__(self, game, *args, **kwargs):
        super(JoinMihkGameForm, self).__init__(*args, **kwargs)
        self.game = game

    def validate(self):
        if not super(JoinMihkGameForm, self).validate():
            return False

        if len(self.game.players) == self.game.num_players:
            self.player.errors.append("The game is full")
            return False

        role = self.game.get_role()
        self.player = models.MihkPlayer(name=self.player.data, game_id=self.game.id, role=role)
        db.session.add(self.player)
        db.session.commit()

        return True


class BugReportForm(flask_wtf.FlaskForm):
    report_type = wtforms.SelectField(
        "What kind of report are you submitting?",
        coerce=int,
        choices=[(k, v) for k, v in models.REPORT_TYPES.items()],
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
