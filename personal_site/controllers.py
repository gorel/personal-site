"""
Default routing for the site not wihtin any module
"""

import flask

default = flask.Blueprint("default", __name__)


@module_default.route("/")
@module_default.route("/home")
@module_default.route("/index.html")
def home():
    return flask.render_template("index.html")


@module_default.route("/about")
def about():
    return flask.render_template("about.html")
