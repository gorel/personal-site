import flask_wtf
import wtforms

from personal_site.auth import models


def LengthRequired(lower=-1, upper=-1):
    if lower == -1 and upper == -1:
        raise ValueError("Must set either lower or upper bounds")

    def _wrap(form, field):
        if lower == -1:
            # Only validate upper bound
            if len(form.field.data) > upper:
                raise wtforms.ValidationError(
                    f"Cannot be more than {upper} characters long")
        elif upper == -1:
            # Only validate lower bound
            if len(form.field.data) < lower:
                raise wtforms.ValidationError(
                    f"Must be at least {lower} characters long")
        else:
            # Validate both bounds
            if not (lower <= len(form.field.data) <= upper):
                raise wtforms.ValidationError(
                    f"Must be between {lower} and {upper} characters long")

    return _wrap


class RegisterForm(flask_wtf.Form):
    # Form fields
    name = wtforms.TextField(
        "Name",
        validators=[
            wtforms.validators.DataRequired(),
        ],
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
            LengthRequired(lower=8),
            wtforms.validators.EqualTo(
                "confirm_password",
                message="Passwords must match",
            ),
        ],
    )
    confirm_password = wtforms.PasswordField("Confirm Password")
    remember = wtforms.BooleanField("Remember me?")

    def __init__(self, *args, **kwargs):
        flask_wtf.Form.__init__(self, *args, **kwargs)
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
            name=self.name.data,
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

    def __init__(self, *args, **kwargs):
        flask_wtf.Form.__init__(self, *args, **kwargs)
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
        flask_wtf.Form.__init__(self, *args, **kwargs)
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
            LengthRequired(lower=8),
            wtforms.validators.EqualTo(
                "confirm_password",
                message="Passwords must match",
            ),
        ],
    )
    confirm_password = wtforms.PasswordField("Confirm Password")
