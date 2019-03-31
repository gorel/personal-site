"""
Default routing for the site not within any module
"""

import json

import flask

from personal_site.base import forms, models


default = flask.Blueprint("default", __name__)


@default.route("/")
@default.route("/home")
@default.route("/index.html")
def home():
    return flask.render_template("index.html")


@default.route("/share_secret", methods=["GET", "POST"])
@default.route("/share_secret/<secret_shortname>", methods=["GET", "POST"])
def share_secret(secret_shortname=None):
    secret = models.Secret.get_by_shortname(secret_shortname)
    form = forms.ShareSecretForm(secret)
    if form.validate_on_submit():
        return flask.redirect(flask.url_for("default.secret", secret_id=form.secret.id))
    else:
        return flask.render_template("share_secret.html", form=form)

@default.route("/secret/<int:secret_id>")
def secret(secret_id):
    secret = models.Secret.query.get_or_404(secret_id)
    return flask.render_template("secret.html", secret=secret)


@default.route("/secret_ready/<int:secret_id>")
def check_secret_ready(secret_id):
    secret = models.Secret.query.get_or_404(secret_id)
    response = {
        "responses": [],
        "expected_responses": secret.expected_responses,
        "actual_responses": secret.actual_responses,
    }
    ready = secret.expected_responses == secret.actual_responses
    if ready:
        response["responses"] = [
            {"person": sr.person, "response": sr.response}
            for sr in secret.responses
        ]
    return flask.jsonify(response)


@default.route("/bug_report", methods=["GET", "POST"])
def bug_report():
    form = forms.BugReportForm()
    if form.validate_on_submit():
        flask.flash(
            json.dumps({
                "msg": "Thank you for your report!",
            }),
            "alert-success",
        )
        return flask.redirect(flask.url_for("default.home"))
    else:
        return flask.render_template("bug_report.html", form=form)
