import datetime

import flask
import flask_login
import flask_mail

from personal_site import db, mail
from personal_site.wiki import forms, models

import personal_site.auth.models as auth_models
import personal_site.admin.utils as admin_utils


wiki = flask.Blueprint("wiki", __name__, url_prefix="/wiki")


@wiki.route("/search")
def search():
    # TODO - set up elasticsearch
    pass


@wiki.route("/")
def index():
    most_popular = models.WikiPage.query.order_by(
        models.WikiPage.views.desc()).limit(5).all()
    return flask.render_template("wiki/index.html", most_popular=most_popular)


@wiki.route("/new", methods=["GET", "POST"])
@flask_login.login_required
@admin_utils.admin_required
def new():
    form = forms.AddWikiPageForm()
    if form.validate_on_submit():
        db.session.add(form.page)
        db.session.commit()
        return flask.redirect(flask.url_for("wiki.view", page_idname=form.page.idname))
    else:
        return flask.render_template("wiki/new.html", form=form)


@wiki.route("/<page_idname>")
def view(page_idname):
    page = models.WikiPage.get_by_idname_or_404(page_idname)
    page.views += 1
    db.session.commit()

    return flask.render_template("wiki/view.html", page=page)


@wiki.route("/<page_idname>/edit", methods=["GET", "POST"])
@flask_login.login_required
@admin_utils.admin_required
def edit(page_idname):
    page = models.WikiPage.get_by_idname_or_404(page_idname)
    form = forms.EditWikiPageForm(page)

    if page.validate_on_submit():
        db.session.commit()
        return flask.redirect(flask.url_for("wiki.view", page_idname=form.page.idname))
    else:
        form.page_name.data = page.name
        form.page_content.data = page.content
        return flask.render_template("wiki/edit.html", form=form)


@wiki.route("/<page_idname>/delete", methods=["POST"])
@flask_login.login_required
@admin_utils.admin_required
def delete(page_idname):
    page = models.WikiPage.get_by_idname_or_404(page_idname)
    db.session.delete(page)
    db.session.commit()

    flask.flash("Page deleted successfully", "alert-success")
    return flask.redirect(flask.url_for("wiki.index"))
