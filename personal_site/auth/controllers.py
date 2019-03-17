"""
Authentication and related behavior
"""

import flask
import flask_login
import flask_mail

from personal_site import db, mail
from personal_site.auth import forms, models


auth = flask.Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        db.session.add(form.user)
        db.session.commit()

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


@auth.route("/verify_account/<token>")
def verify_account(token):
    user = models.User.gen_user_for_token("verify_account", token)
    if user is not None:
        user.verify_email()
        flask.flash("Verified email successfully. Welcome!", "alert-success")
    return flask.redirect(flask.url_for("default.home"))


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if flask_login.current_user.is_authenticated:
        # User should be going through account flow
        return flask.redirect(flask.url_for("default.home"))
    user = models.User.gen_user_for_token("reset_password", token)
    flask.current_app.logger.warning(f"->->->user is {user}")
    if user is None:
        return flask.redirect(flask.url_for("default.home"))

    form = forms.SetNewPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flask_login.login_user(user)
        flask.flash("Password reset successfully", "alert-success")
        return flask.redirect(flask.url_for("default.home"))
    else:
        return flask.render_template("auth/set_new_password.html", form=form, title="Reset your password")
