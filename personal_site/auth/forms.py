import flask_wtf
import wtforms

from personal_site import constants, db
from personal_site.auth import models


class RegisterForm(flask_wtf.FlaskForm):
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
    recaptcha = flask_wtf.RecaptchaField()
    submit = wtforms.SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None
        self.show_forgot = False

    def validate(self):
        if not super(RegisterForm, self).validate():
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
                self.show_forgot = True
                return False

        # Create new user
        self.user = models.User(
            username=self.username.data,
            email=self.email.data,
            password=self.password.data,
        )

        db.session.add(self.user)
        db.session.commit()
        return True


class LoginForm(flask_wtf.FlaskForm):
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
        if not super(LoginForm, self).validate():
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


class ForgotPasswordForm(flask_wtf.FlaskForm):
    email = wtforms.TextField(
        "Email",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Email(),
        ],
    )
    submit = wtforms.SubmitField("Send email")

    def __init__(self, *args, **kwargs):
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        if not super(ForgotPasswordForm, self).validate():
            return False

        user = models.User.get_by_email(self.email.data)
        if user is None:
            self.email.errors.append("No account with that email found")
            return False

        self.user = user
        return True


class SetNewPasswordForm(flask_wtf.FlaskForm):
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
    submit = wtforms.SubmitField("Send email")

    def __init__(self, user, *args, **kwargs):
        super(SetNewPasswordForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate(self):
        if not super(SetNewPasswordForm, self).validate():
            return False

        self.user.set_password(self.password.data)
        db.session.commit()
        return True
