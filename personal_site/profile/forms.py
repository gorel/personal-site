import flask_login
import flask_wtf
import wtforms

from personal_site import constants, db
import personal_site.auth.models as auth_models


class EditAccountForm(flask_wtf.FlaskForm):
    username = wtforms.TextField(
        "Username",
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.Length(max=constants.USERNAME_MAX_LEN),
        ],
    )
    email = wtforms.TextField(
        "Email address",
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.Email(),
        ],
    )
    password = wtforms.PasswordField(
        "Password",
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.Length(min=constants.PASSWORD_MIN_LEN),
            wtforms.validators.EqualTo(
                "confirm_password",
                message="Passwords must match",
            ),
        ],
        render_kw={"class": "form-control", "placeholder": "Leave blank to keep current password"},
    )
    confirm_password = wtforms.PasswordField(
        "Confirm Password",
        render_kw={"class": "form-control", "placeholder": "Leave blank to keep current password"},
    )
    submit = wtforms.SubmitField("Submit", render_kw={"class": "btn btn-primary"})

    def validate(self):
        if not super(EditAccountForm, self).validate():
            return False

        user = flask_login.current_user
        user.username = self.username.data or user.username

        if self.email.data:
            user.email = self.email.data
            user.email_verified = False
            user.send_email_verification_link()

        if self.password.data:
            user.set_password(self.password.data)

        db.session.commit()
        return True
