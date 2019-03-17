import datetime

import flask
import flask_login

from personal_site import constants, db
from personal_site.wiki import forms, models

import personal_site.admin.utils as admin_utils


wiki = flask.Blueprint("wiki", __name__, url_prefix="/wiki")


@wiki.errorhandler(404)
def error404(error):
    return flask.render_template("wiki/404.html", error=error), 404


@wiki.before_request
def load_search_form():
    flask.g.search_form = forms.SearchForm()


@wiki.route("/search")
def search():
    data = flask.g.search_form.q.data
    if not flask.g.search_form.validate():
        return flask.redirect(flask.url_for("wiki.index"))
    page = flask.request.args.get("page", 1, type=int)
    wikipages, total = models.WikiPage.search(data, page, constants.ES_PAGE_SIZE)

    prev_url = None
    next_url = None
    if total > page * constants.ES_PAGE_SIZE:
        next_url = flask.url_for("wiki.search", q=data, page=page + 1)
    if page > 1:
        prev_url = flask.url_for("wiki.search", q=data, page=page - 1)

    return flask.render_template(
        "wiki/search.html",
        title="Search",
        wikipages=wikipages,
        prev_url=prev_url,
        next_url=next_url,
    )


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
        return flask.render_template("wiki/new.html", form=form, title="New page")


@wiki.route("/<page_idname>", methods=["GET", "POST"])
def view(page_idname):
    page = models.WikiPage.get_by_idname_or_404(page_idname)
    question_form = forms.AskQuestionForm(page)

    if question_form.validate_on_submit():
        db.session.add(question_form.wiki_question)
        db.session.commit()

        flask.redirect(flask.url_for("wiki.view", page_idname=page_idname))
    else:
        page.views += 1
        db.session.commit()
        return flask.render_template(
            "wiki/view.html",
            page=page,
            question_form=question_form,
            title=page.name,
        )


@wiki.route("/<page_idname>/edit", methods=["GET", "POST"])
@flask_login.login_required
@admin_utils.admin_required
def edit(page_idname):
    page = models.WikiPage.get_by_idname_or_404(page_idname)
    form = forms.EditWikiPageForm(page)

    if form.validate_on_submit():
        db.session.commit()
        return flask.redirect(flask.url_for("wiki.view", page_idname=form.page.idname))
    else:
        form.page_name.data = page.name
        form.page_content.data = page.content
        return flask.render_template("wiki/edit.html", form=form, title="Edit page")


@wiki.route("/<page_idname>/delete", methods=["POST"])
@flask_login.login_required
@admin_utils.admin_required
def delete(page_idname):
    page = models.WikiPage.get_by_idname_or_404(page_idname)
    db.session.delete(page)
    db.session.commit()

    flask.flash("Page deleted successfully", "alert-success")
    return flask.redirect(flask.url_for("wiki.index"))
