"""
Authentication and related behavior
"""

import flask
import flask_login

from personal_site import constants
from personal_site.auth import forms, models


auth = flask.Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flask_login.login_user(form.user, remember=form.remember.data)
        return flask.redirect(flask.request.args.get("next")
            or flask.url_for("default.home"))
    else:
        return flask.render_template("auth/register.html", form=form, title="Register")


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        flask_login.login_user(form.user, remember=form.remember.data)
        return flask.redirect(flask.request.args.get("next")
            or flask.url_for("default.home"))
    else:
        return flask.render_template("auth/login.html", form=form, title="Login")


@auth.route("/logout", methods=["POST"])
def logout():
    if flask_login.current_user.is_authenticated:
        flask_login.logout_user()
    return flask.redirect(flask.url_for("default.home"))


@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = forms.ForgotPasswordForm()
    if form.validate_on_submit():
        form.user.send_reset_password_email()
        flask.flash("Sent password reset email", "alert-success")
        return flask.redirect(flask.url_for("auth.login"))
    else:
        return flask.render_template("auth/forgot.html", form=form, title="Forgot your password?")


@auth.route("/resend_verification_email")
@flask_login.login_required
def resend_verification_email():
    user = flask_login.current_user
    user.send_verify_account_email()
    flask.flash(f"Sent verification email to {user.email}", "alert-success")
    return flask.redirect(flask.url_for("default.home"))


@auth.route("/verify_account/<token>")
def verify_account(token):
    user = models.User.gen_user_for_token(constants.VERIFY_ACCOUNT_TOKEN_STR, token)
    if user is not None:
        user.verify_email()
        flask.flash("Verified email successfully. Welcome!", "alert-success")
    return flask.redirect(flask.url_for("default.home"))


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if flask_login.current_user.is_authenticated:
        flask.flash("You should do that from your profile", "alert-warning")
        return flask.redirect(flask.url_for("profile.index"))
    user = models.User.gen_user_for_token(constants.RESET_PASSWORD_TOKEN_STR, token)
    if user is None:
        return flask.redirect(flask.url_for("default.home"))

    form = forms.SetNewPasswordForm(user)
    if form.validate_on_submit():
        flask_login.login_user(user)
        flask.flash("Password reset successfully", "alert-success")
        return flask.redirect(flask.url_for("default.home"))
    else:
        return flask.render_template("auth/set_new_password.html", form=form, title="Reset your password")
