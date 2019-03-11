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
        email = form.email.data
        pw_reset = models.PasswordReset(user=User.get_by_email(email))

        db.session.add(pw_reset)
        db.session.commit()

        email_title = "Reset your password"
        site = flask.current_app.config["SITE_URL"]
        url = f"{site}/auth/reset_password/{pw_reset.key}"
        email_content = f"Click this link to reset your password: {url}"
        email_content += "\nThis link will expire in 48 hours."

        msg = flask_mail.Message(email_title, recipients=[email])
        msg.body = email_content
        mail.send(msg)

        flask.flash("Sent password reset email", "alert-success")
        return flask.redirect(flask.url_for("auth.login"))
    else:
        return flask.render_template("auth/forgot.html", form=form, title="Forgot your password?")


@auth.route("/reset_password/<reset_key>", methods=["GET", "POST"])
def reset_password(reset_key):
    user = models.PasswordReset.get_by_key(reset_key)
    if user is None:
        flask.flash("Invalid password reset key (did it expire?)", "alert-warning")
        return flask.redirect(flask.url_for("default.home"))

    form = forms.SetNewPasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        # Invalidate all open password resets
        for pw_reset in user.pw_reset:
            db.session.delete(pw_reset)
        user.set_password(password)
        db.session.commit()

        flask_login.login_user(user)

        flask.flash("Password reset successfully", "alert-success")
        return flask.redirect(flask.url_for("default.home"))
    else:
        return flask.render_template("auth/set_new_password.html", form=form, title="Reset your password")
