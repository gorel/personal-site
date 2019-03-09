import datetime

import flask
import flask_login

import personal_site.auth.models as auth_models


forum = flask.Blueprint("forum", __name__, url_prefix="/forum")

@forum.route("/")
def index():
    return flask.render_template("forum/index.html")
