import os

import flask
import flask_login

from personal_site import constants, db
from personal_site.learn import forms, models

import personal_site.admin.utils as admin_utils

learn = flask.Blueprint("learn", __name__, url_prefix="/learn")


@learn.route("/")
def index():
    most_popular = models.LearnPageStats.query.order_by(
        models.LearnPageStats.views.desc()).limit(5).all()
    return flask.render_template("learn/index.html", most_popular=most_popular)


@learn.route("/pages/<name>", methods=["GET", "POST"])
def view(name):
    filepath = os.path.join(constants.LEARN_PAGE_TEMPLATE_DIR, name)
    template_fullpath = os.path.join(constants.TEMPLATE_DIR, filepath)
    flask.current_app.logger.info(template_fullpath)
    if not os.path.exists(template_fullpath):
        flask.abort(404)

    page_stats = models.LearnPageStats.query.get(name)
    if page_stats is None and os.path.exists(template_fullpath):
        page_stats = models.LearnPageStats(name)
        db.session.add(page_stats)
        db.session.commit()

    form = forms.AskQuestionForm(page_stats)
    if form.validate_on_submit():
        db.session.add(form.learn_question)
        db.session.commit()

        flask.redirect(flask.url_for("learn.view", name=name))
    else:
        page_stats.views += 1
        db.session.commit()
        return flask.render_template(
            filepath,
            page_stats=page_stats,
            form=form,
        )
