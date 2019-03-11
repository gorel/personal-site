import datetime

import flask
import flask_login

import personal_site.auth.models as auth_models


forum = flask.Blueprint("forum", __name__, url_prefix="/forum")

@forum.route("/")
def index():
    return flask.render_template("forum/index.html")


@forum.route("/new_post", methods=["GET", "POST"])
def new_post():
    pass


@forum.route("<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    pass


@forum.route("/<int:post_id>")
def view_post(post_id):
    pass


@forum.route("/<int:post_id>/comment", methods=["GET", "POST"])
def new_comment(post_id):
    pass


@forum.route("/<int:post_id>/<int:comment_id>/edit", methods=["GET", "POST"])
def edit_comment(post_id, comment_id):
    pass
