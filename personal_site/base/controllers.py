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


@default.route("/start_mihk", methods=["GET", "POST"])
def start_mihk():
    form = forms.StartMihkGameForm()
    if form.validate_on_submit():
        return flask.redirect(flask.url_for("default.mihk", game_id=form.game.id, player_id=form.player.id))
    else:
        return flask.render_template("start_mihk.html", form=form)


@default.route("/join_mihk/<int:game_id>", methods=["GET", "POST"])
def join_mihk(game_id):
    game = models.MihkGame.query.get_or_404(game_id)
    form = forms.JoinMihkGameForm(game)
    if form.validate_on_submit():
        return flask.redirect(flask.url_for("default.mihk", game_id=form.game.id, player_id=form.player.id))
    else:
        return flask.render_template("join_mihk.html", form=form, game=game)


@default.route("/mihk/<int:game_id>/<int:player_id>")
def mihk(game_id, player_id):
    game = models.MihkGame.query.get_or_404(game_id)
    return flask.render_template("mihk.html", game=game, player_id=player_id)


@default.route("/mihk_ready/<int:game_id>/<int:player_id>")
def check_mihk_ready(game_id, player_id):
    game = models.MihkGame.query.get_or_404(game_id)
    roles = [game.role_to_str(player.role) for player in game.players]
    player = models.MihkPlayer.query.get_or_404(player_id)

    # TODO - Make this... good. Don't hardcode value
    is_fs = player.role == 0
    response = {
        "players": [
            {
                "name": player.name,
                # TODO: Hard-code FS role again...
                "role": "(Hidden)" if player.id != player_id and not is_fs and player.role != 0 else game.role_to_str(player.role),
            }
            for player in game.players
        ],
        "remaining": game.num_players - len(game.players),
    }
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
