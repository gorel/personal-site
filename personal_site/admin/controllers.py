import functools
import json

import flask
import flask_login

from personal_site import constants, db
import personal_site.models as default_models

from personal_site.admin import forms, models, utils

import personal_site.auth.models as auth_models


admin = flask.Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/")
@flask_login.login_required
@utils.admin_required
def index():
    return flask.render_template("admin/index.html")


@admin.route("/users")
@admin.route("/users/")
@admin.route("/users/<int:page_num>")
@flask_login.login_required
@utils.admin_required
def users(page_num=1):
    users = auth_models.User.query.paginate(page_num, constants.ADMIN_USERS_PER_PAGE)
    return flask.render_template("admin/users.html", users=users, title="Users")


@admin.route("/bug_reports")
@admin.route("/bug_reports/")
@admin.route("/bug_reports/<int:page_num>")
@flask_login.login_required
@utils.admin_required
def bug_reports(page_num=1):
    bug_reports = default_models.BugReport.query.paginate(page_num, constants.ADMIN_BUG_REPORTS_PER_PAGE)
    return flask.render_template("admin/bug_reports.html", bug_reports=bug_reports, title="Bug Reports")


@admin.route("/send_warning/<int:user_id>", methods=["GET", "POST"])
@utils.admin_required
def warn_user(user_id):
    user = auth_models.User.query.get_or_404(user_id)
    form = forms.WarnUserForm(user)

    if form.validate_on_submit():
        flask.flash(
            json.dumps({
                "msg": f"Sent a warning to {user.username}",
            }),
            "alert-info",
        )
        return flask.redirect(flask.url_for("admin.users"))
    else:
        return flask.render_template("admin/warn_user.html", form=form, title="Warn user")


@admin.route("/view_warnings/<int:user_id>")
@utils.admin_required
def view_warnings(user_id):
    user = auth_models.User.query.get_or_404(user_id)
    # Likely don't need to paginate, because if it got to that point,
    # probably we have already banned the user
    warnings = user.warnings.order_by(models.Warning.timestamp.desc()).all()
    return flask.render_template("admin/view_warnings.html", user=user, warnings=warnings)


@admin.route("/ban/<int:user_id>", methods=["POST"])
@flask_login.login_required
@utils.admin_required
def ban_user(user_id):
    user = auth_models.User.query.get_or_404(user_id)
    user.set_banned(True)

    flask.flash(
        json.dumps({
            "msg": f"User {user.username} has been banned.",
        }),
        "alert-info",
    )
    return flask.redirect(flask.url_for("admin.users"))


@admin.route("/unban/<int:user_id>", methods=["POST"])
@flask_login.login_required
@utils.admin_required
def unban_user(user_id):
    user = auth_models.User.query.get_or_404(user_id)
    user.set_banned(False)

    flask.flash(
        json.dumps({
            "msg": f"User {user.username} has been unbanned.",
        }),
        "alert-info",
    )
    return flask.redirect(flask.url_for("admin.users"))


@admin.route("/users/delete/<int:user_id>", methods=["POST"])
@flask_login.login_required
@utils.admin_required
def delete_user(user_id):
    if flask_login.current_user.id == user_id:
        flask.flash(
            json.dumps({
                "msg": "Now that doesn't seem like a great idea...",
            }),
            "alert-danger",
        )
        return flask.redirect(flask.url_for("admin.users"))

    user = auth_models.User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flask.flash(
        json.dumps({
            "msg": "Deleted user account",
        }),
        "alert-info",
    )
    return flask.redirect(flask.url_for("admin.users"))
