import functools

import flask
import flask_login


def admin_required(f):
    @functools.wraps(f)
    def _wrap(*args, **kwargs):
        if not flask_login.current_user.is_admin:
            flask.flash("You must be an admin to perform that action")
            return flask.redirect(flask.url_for("default.home"))
    return _wrap


