"""
Default routing for the site not within any module
"""

import flask

from personal_site import db, forms, models


default = flask.Blueprint("default", __name__)


@default.route("/")
@default.route("/home")
@default.route("/index.html")
def home():
    return flask.render_template("index.html")


@default.route("/about")
def about():
    return flask.render_template("about.html")


@default.route("/share_secret", methods=["GET", "POST"])
def share_secret():
    form = forms.ShareSecretForm()
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
