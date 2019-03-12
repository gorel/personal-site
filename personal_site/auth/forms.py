import flask_wtf
import wtforms

from personal_site import constants
from personal_site.auth import models


class RegisterForm(flask_wtf.Form):
    username = wtforms.TextField(
        "Username",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(max=constants.USERNAME_MAX_LEN),
        ],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    email = wtforms.TextField(
        "Email",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Email(),
        ],
    )
    password = wtforms.PasswordField(
        "Password",
        validators=[
            wtforms.validators.InputRequired(),
            wtforms.validators.Length(min=constants.PASSWORD_MIN_LEN),
            wtforms.validators.EqualTo(
                "confirm_password",
                message="Passwords must match",
            ),
        ],
    )
    confirm_password = wtforms.PasswordField("Confirm Password")
    remember = wtforms.BooleanField("Remember me?")
    submit = wtforms.SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        if not flask_wtf.Form.validate(self):
            return False

        # Check if the user has already registered before
        user = models.User.get_by_email(self.email.data)
        if user is not None:
            if user.check_password(self.password.data):
                # Account exists and passwords match
                self.user = user
                return True
            else:
                self.email.errors.append("Email already registered. Did you forget your password?")
                return False

        # Create new user
        self.user = models.User(
            username=self.username.data,
            email=self.email.data,
            password=self.password.data,
        )
        return True


class LoginForm(flask_wtf.Form):
    email = wtforms.TextField(
        "Email",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Email(),
        ],
    )
    password = wtforms.PasswordField(
        "Password",
        validators=[
            wtforms.validators.InputRequired(),
        ],
    )
    remember = wtforms.BooleanField("Remember Me?")
    submit = wtforms.SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        if not flask_wtf.Form.validate(self):
            return False

        user = models.User.get_by_email(self.email.data)
        if user is None:
            self.email.errors.append("No account with that email found")
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append("Incorrect password")
            return False

        self.user = user
        return True


class ForgotPasswordForm(flask_wtf.Form):
    email = wtforms.TextField(
        "Email",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Email(),
        ],
    )

    def __init__(self, *args, **kwargs):
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        if not flask_wtf.Form.validate(self):
            return False

        user = models.User.get_by_email(self.email.data)
        if user is None:
            self.email.errors.append("No account with that email found")
            return False

        self.user = user
        return True


class SetNewPasswordForm(flask_wtf.Form):
    password = wtforms.PasswordField(
        "Password",
        validators=[
            wtforms.validators.InputRequired(),
            wtforms.validators.Length(min=8),
            wtforms.validators.EqualTo(
                "confirm_password",
                message="Passwords must match",
            ),
        ],
    )
    confirm_password = wtforms.PasswordField("Confirm Password")
