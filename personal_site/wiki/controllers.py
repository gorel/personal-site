import datetime
import markdown

from markdown.extensions import (
    extra,
    nl2br,
    toc,
    wikilinks,
)

import flask
import flask_login
import flask_mail

from personal_site import db, mail
from personal_site.wiki import forms, models

import personal_site.auth.models as auth_models
import personal_site.admin.utils as admin_utils


WIKI_EXTENSIONS = [
    extra.ExtraExtension(),
    nl2br.Nl2BrExtension(),
    toc.TocExtension(),
    wikilinks.WikiLinkExtension(base_url="/wiki/"),
]

MD = markdown.Markdown(extensions=WIKI_EXTENSIONS)


wiki = flask.Blueprint("wiki", __name__, url_prefix="/wiki")


@wiki.route("/")
def index():
    return flask.render_template("wiki/index.html")


@wiki.route("/new", methods=["GET", "POST"])
@flask_login.login_required
@admin_utils.admin_required
def new():
    form = forms.AddWikiPageForm()
    if form.validate_on_submit():
        db.session.add(form.page)
        db.session.commit()
        return flask.redirect(flask.url_for("wiki.view", page_name=form.page.name))
    else:
        return flask.render_template("wiki/new.html", form=form)


@wiki.route("/<page_idname>")
def view(page_idname):
    page = WikiPage.get_by_idname_or_404(page_idname)
    page.views += 1
    db.session.commit()

    html = MD.convert(page.content)
    return flask.render_template("wiki/view.html", page=page, html=html, toc=MD.toc)


@wiki.route("/<page_idname>/edit", methods=["GET", "POST"])
@flask_login.login_required
@admin_utils.admin_required
def edit(page_idname):
    page = WikiPage.get_by_idname_or_404(page_idname)
    form = forms.EditWikiPageForm(page)

    if page.validate_on_submit():
        db.session.commit()
        return flask.redirect(flask.url_for("wiki.view", page_name=form.page.name))
    else:
        form.page_name.data = page.name
        form.page_content.data = page.content
        return flask.render_template("wiki/edit.html", form=form)


@wiki.route("/<page_idname>/delete", methods=["POST"])
@flask_login.login_required
@admin_utils.admin_required
def delete(page_idname):
    page = WikiPage.get_by_idname_or_404(page_idname)
    db.session.delete(page)
    db.session.commit()

    flask.flash("Page deleted successfully")
    return flask.redirect(flask.url_for("wiki.index"))
