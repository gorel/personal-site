import functools

import flask
import flask_login


def require_verified_email(f):
    @functools.wraps(f)
    def _wrap(*args, **kwargs):
        if not flask_login.current_user.email_verified:
            flask.flash(
                "You must verify your email before you're allowed to do that",
                "alert-warning",
            )
            return flask.redirect(flask.referrer or flask.url_for("default.home"))
        return f(*args, **kwargs)
    return _wrap


