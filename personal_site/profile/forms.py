import flask_login
import flask_wtf
import wtforms

from personal_site import constants
import personal_site.auth.models as auth_models


class EditAccountForm(flask_wtf.Form):
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
    )
    confirm_password = wtforms.PasswordField("Confirm Password")

    def validate(self):
        if not flask_wtf.Form.validate(self):
            return False

        user = flask_login.current_user
        user.username = self.username.data or user.username

        if self.email.data:
            user.email = self.email.data
            user.email_verified = False
            user.send_email_verification_link()

        if self.password.data:
            user.set_password(self.password.data)

        return True
