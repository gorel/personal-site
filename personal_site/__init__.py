"""
Performs webapp startup procedures
"""

import logging
import logging.handlers

import elasticsearch
import flask
import flask_bcrypt
import flask_login
import flask_mail
import flask_migrate
import flask_moment
import flask_sqlalchemy
import flask_wtf

import htmlmin.main
import wtforms

import site_config


db = flask_sqlalchemy.SQLAlchemy()
login_manager = flask_login.LoginManager()
bcrypt = flask_bcrypt.Bcrypt()
mail = flask_mail.Mail()
migrate = flask_migrate.Migrate()
moment = flask_moment.Moment()
csrf = flask_wtf.CSRFProtect()


def register_jinja_utils(app):
    def _is_hidden_field(field):
        return isinstance(field, wtforms.fields.HiddenField)
    app.jinja_env.globals["bootstrap_is_hidden_field"] = _is_hidden_field


def set_up_logger(app):
    if not app.debug and not app.testing:
        formatter = logging.Formatter(
            "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levename)s - %(message)s",
        )
        handler = logging.handlers.RotatingFileHandler(
            "site.log", maxBytes=10000, backupCount=2,
        )
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)


def register_error_handlers(app):
    if not app.debug and not app.testing:
        @app.errorhandler(401)
        def error401(error):
            return flask.render_template("401.html", error=error), 401

        @app.errorhandler(404)
        def error404(error):
            return flask.render_template("404.html", error=error), 404

        @app.errorhandler(500)
        def error500(error):
            app.logger.error(f"HTTP 500: {error}")
            flask.flash(
                "Something went wrong :( A log has been generated.",
                "alert-warning",
            )
            return flask.redirect(flask.url_for("default.home", error=error))

        # Minify sent HTML
        @app.after_request
        def response_minify(response):
            if response.content_type == "text/html; charset=utf-8":
                response.set_data(htmlmin.main.minify(response.get_data(as_text=True)))
            return response


def create_app(config_class=site_config.Config):
    # Create app
    app = flask.Flask(__name__)
    app.config.from_object(config_class)

    # Set up extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    csrf.init_app(app)

    # Set up jinja utilities
    register_jinja_utils(app)

    # Enable ElasticSearch for searchable pages
    app.elasticsearch = elasticsearch.Elasticsearch([app.config["ELASTICSEARCH_URL"]])

    # Set up logging if we aren't in debug/testing mode
    set_up_logger(app)

    # Register error handlers if we aren't in debug/testing mode
    register_error_handlers(app)

    # Import all blueprints from controllers
    from personal_site.controllers import default
    from personal_site.admin.controllers import admin
    from personal_site.auth.controllers import auth
    from personal_site.forum.controllers import forum
    from personal_site.learn.controllers import learn
    from personal_site.profile.controllers import profile

    # Register blueprints
    app.register_blueprint(default)
    app.register_blueprint(admin)
    app.register_blueprint(auth)
    app.register_blueprint(forum)
    app.register_blueprint(learn)
    app.register_blueprint(profile)

    return app
