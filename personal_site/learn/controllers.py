import datetime
import json
import os

import flask
import flask_login
import flask_shelve

from personal_site import constants
from personal_site.learn import forms, models, utils

import personal_site.admin.utils as admin_utils
import personal_site.auth.utils as auth_utils

learn = flask.Blueprint("learn", __name__, url_prefix="/learn")


def get_learn_page_path_or_404(name):
    filepath = os.path.join(constants.LEARN_PAGE_TEMPLATE_DIR, name)
    template_fullpath = os.path.join(constants.TEMPLATE_DIR, filepath)
    flask.current_app.logger.info(template_fullpath)
    if not os.path.exists(template_fullpath):
        flask.abort(404)
    return filepath


@learn.route("/")
def index():
    most_popular = models.LearnPageStats.query.order_by(
        models.LearnPageStats.views.desc()).limit(5).all()
    return flask.render_template("learn/index.html", most_popular=most_popular)


@learn.route("/pages/<name>")
def view(name):
    filepath = get_learn_page_path_or_404(name)
    if flask_login.current_user.is_authenticated:
        flask_login.current_user.record_view(name)

    has_questions = models.LearnQuestion.query.filter_by(
        page_name=name).first() is not None

    return flask.render_template(
        filepath,
        page_name=name,
        has_questions=has_questions,
    )

@learn.route("/pages/<name>/questions", methods=["GET", "POST"])
def questions(name):
    get_learn_page_path_or_404(name)
    page = flask.request.args.get("page", 1, type=int)

    questions = models.LearnQuestion.query.filter_by(page_name=name)
    # Show good questions first
    questions = questions.order_by(
        models.LearnQuestion.good_question.desc()).paginate(page, constants.QUESTIONS_PER_PAGE)

    return flask.render_template(
        "learn/questions.html",
        questions=questions,
        page_name=name,
    )


@learn.route("/pages/<name>/ask_question", methods=["GET", "POST"])
@flask_login.login_required
@auth_utils.require_verified_email
def ask_question(name):
    get_learn_page_path_or_404(name)

    form = forms.AskQuestionForm(name)

    if form.validate_on_submit():
        flask.flash(
            json.dumps({
                "msg": "Your question has been submitted",
            }),
            "alert-success",
        )
        return flask.redirect(flask.url_for("learn.view", name=name))
    else:
        return flask.render_template(
            "learn/ask_question.html",
            form=form,
            page_name=name,
        )


@learn.route("/pages/answer_question/<int:qid>", methods=["GET", "POST"])
@admin_utils.admin_required
def answer_question(qid):
    question = models.LearnQuestion.query.get_or_404(qid)
    form = forms.AnswerQuestionForm(question)

    if form.validate_on_submit():
        return flask.redirect(flask.url_for("learn.questions", name=question.page_name))
    else:
        return flask.render_template("learn/answer_question.html", form=form)
