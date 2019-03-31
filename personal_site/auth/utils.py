import functools
import json

import flask
import flask_login


def require_verified_email(f):
    @functools.wraps(f)
    def _wrap(*args, **kwargs):
        if not flask_login.current_user.email_verified:
            flask.flash(
                json.dumps({
                    "msg": f"You must verify your email before you're allowed to do that.",
                    "link": flask.url_for("auth.resend_verification_email"),
                }),
                "alert-warning",
            )
            return flask.redirect(flask.request.referrer or flask.url_for("default.home"))
        return f(*args, **kwargs)
    return _wrap


def require_not_banned(f):
    @functools.wraps(f)
    def _wrap(*args, **kwargs):
        if flask_login.current_user.is_banned:
            flask.flash(
                json.dumps({
                    "msg": "Your account is banned. You are not allowed to do that.",
                }),
                "alert-danger",
            )
            return flask.redirect(flask.request.referrer or flask.url_for("default.home"))
        return f(*args, **kwargs)
    return _wrap
