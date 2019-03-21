import datetime

import flask
import flask_login

from personal_site import constants, db
from personal_site.forum import forms, models

import personal_site.auth.utils as auth_utils


forum = flask.Blueprint("forum", __name__, url_prefix="/forum")

@forum.route("/")
def index():
    page = flask.request.args.get("page", 1, type=int)
    posts = models.Post.query.order_by(
        models.Post.last_activity.desc()).paginate(page, constants.POSTS_PER_PAGE)
    return flask.render_template("forum/index.html", posts=posts)


@forum.route("/new_post", methods=["GET", "POST"])
@flask_login.login_required
@auth_utils.require_verified_email
def new_post():
    form = forms.NewPostForm()
    if form.validate_on_submit():
        db.session.add(form.post)
        db.session.commit()
        return flask.redirect(flask.url_for("forum.view_post", post_id=form.post.id))
    else:
        return flask.render_template("forum/new_post.html", form=form, title="New post")


@forum.route("<int:post_id>/edit", methods=["GET", "POST"])
@flask_login.login_required
@auth_utils.require_verified_email
def edit_post(post_id):
    post = models.Post.query.get_or_404(post_id)
    form = forms.EditPostForm(post)
    if form.validate_on_submit():
        db.session.commit()
        flask.redirect(flask.url_for("forum.view_post", post_id=form.post.id))
    else:
        form.body.data = post.body
        form.show_anon.data = post.show_anon
        flask.render_template("forum/edit_post.html", post=post, form=form, title="Edit post")


@forum.route("/<int:post_id>")
def view_post(post_id):
    post = models.Post.query.get_or_404(post_id)
    page = flask.request.args.get("page", 1, type=int)
    comments = post.comments.order_by(
        models.Comment.posted_at).paginate(page, constants.COMMENTS_PER_PAGE)
    return flask.render_template("forum/view_post.html", post=post, comments=comments)


@forum.route("/<int:post_id>/comment", methods=["GET", "POST"])
@flask_login.login_required
@auth_utils.require_verified_email
def new_comment(post_id):
    post = models.Post.query.get_or_404(post_id)
    form = forms.NewCommentForm(post)

    if form.validate_on_submit():
        db.session.add(form.comment)
        db.session.commit()
        return flask.redirect(flask.url_for("forum.view_post", post_id=post_id))
    else:
        return flask.render_template("forum/new_comment.html", form=form, post=post)


@forum.route("/<int:post_id>/<int:comment_id>/edit", methods=["GET", "POST"])
@flask_login.login_required
@auth_utils.require_verified_email
def edit_comment(post_id, comment_id):
    post = models.Post.query.get_or_404(post_id)
    comment = models.Comment.query.get_or_404(comment_id)
    form = forms.EditCommentForm(post, comment)

    if form.validate_on_submit():
        db.session.commit()
        return flask.redirect(flask.url_for("forum.view_post", post_id=post_id))
    else:
        form.body.data = comment.body
        form.show_anon.data = comment.show_anon
        return flask.render_template("forum/edit_comment.html", form=form, post=post)
