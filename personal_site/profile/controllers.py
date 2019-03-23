import flask
import flask_login

from personal_site import constants, db

import personal_site.auth.models as auth_models
import personal_site.forum.models as forum_models

from personal_site.profile import forms, models

profile = flask.Blueprint("profile", __name__, url_prefix="/profile")


@profile.route("/")
@profile.route("/<int:user_id>")
@flask_login.login_required
def index(user_id=None):
    user_id = user_id or flask_login.current_user.id
    user = auth_models.User.query.get(user_id)
    return flask.render_template("profile/index.html", user=user, title=f"{user.username}'s profile")


@profile.route("/edit", methods=["GET", "POST"])
def edit():
    form = forms.EditAccountForm()
    if form.validate_on_submit():
        db.session.commit()
        flask.flash("Your account has been updated successfully", "alert-success")
        return flask.redirect(flask.url_for("profile.index"))
    else:
        form.username.data = flask_login.current_user.username
        form.email.data = flask_login.current_user.email
        return flask.render_template("profile/edit.html", form=form, title="Edit profile")


@profile.route("/num_unread_notifications")
@flask_login.login_required
def num_unread_notifications():
    return flask.jsonify({"count": flask_login.current_user.unread_notifications})


@profile.route("/notifications")
@profile.route("/notifications/")
@profile.route("/notifications/<int:page_num>")
@flask_login.login_required
def notifications(page_num=1):
    user = flask_login.current_user
    last_read_time = user.last_notification_read_time or 0
    user.set_notification_read_time()
    notifs = user.notifications.order_by(models.Notification.timestamp.desc())
    notifs = notifs.paginate(page_num, constants.NOTIFICATIONS_PER_PAGE)
    return flask.render_template(
        "profile/notifications.html",
        user=user,
        notifications=notifs,
        last_read_time=last_read_time,
    )


@profile.route("/posts/<int:user_id>")
def posts_by_user(user_id):
    user = auth_models.User.query.get_or_404(user_id)
    page = flask.request.args.get("page", 1, type=int)

    # Privacy filter for show_anon must be checked
    posts = user.posts.order_by(forum_models.Post.posted_at.desc())
    if user_id != flask_login.current_user.id:
        posts = posts.filter(forum_models.Post.show_anon.is_(False))
    posts = posts.paginate(page, constants.COMMENTS_PER_PAGE)

    return flask.render_template("profile/posts_by_user.html", user=user, posts=posts)


@profile.route("/comments/<int:user_id>")
def comments_by_user(user_id):
    user = auth_models.User.query.get_or_404(user_id)
    page = flask.request.args.get("page", 1, type=int)

    # Privacy filter for show_anon must be checked
    comments = user.comments.order_by(forum_models.Comment.posted_at.desc())
    if user_id != flask_login.current_user.id:
        comments = comments.filter(forum_models.Comment.show_anon.is_(False))
    comments = comments.paginate(page, constants.COMMENTS_PER_PAGE)

    return flask.render_template("profile/comments_by_user.html", user=user, comments=comments)
