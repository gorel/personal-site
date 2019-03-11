import flask
import flask_login

from personal_site import db

import personal_site.auth.models as auth_models

from personal_site.profile import forms

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
