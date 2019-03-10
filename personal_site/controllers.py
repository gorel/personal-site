"""
Default routing for the site not within any module
"""

import flask

default = flask.Blueprint("default", __name__)


@default.route("/")
@default.route("/home")
@default.route("/index.html")
def home():
    return flask.render_template("index.html")


@default.route("/about")
def about():
    return flask.render_template("about.html")
