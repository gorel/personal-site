"""
Performs webapp startup procedures
"""

import logging
import logging.handlers

import elasticsearch
import flask
import flask_bootstrap
import flask_bcrypt
import flask_login
import flask_mail
import flask_moment
import flask_sqlalchemy
import flask_wtf

import htmlmin.main

import site_config


bootstrap = flask_bootstrap.Bootstrap()
db = flask_sqlalchemy.SQLAlchemy()
login_manager = flask_login.LoginManager()
bcrypt = flask_bcrypt.Bcrypt()
mail = flask_mail.Mail()
moment = flask_moment.Moment()
csrf = flask_wtf.CSRFProtect()


def create_app(config_class=site_config.Config):
    # Create app
    app = flask.Flask(__name__)
    app.config.from_object(config_class)

    # Set up extensions
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)

    # Enable ElasticSearch for wiki pages
    app.elasticsearch = elasticsearch.Elasticsearch([app.config["ELASTICSEARCH_URL"]])

    # Set up logging if we aren't in debug/testing mode
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

    # Register error handlers if we aren't in debug/testing mode
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
            flask.flash("Something went wrong :( A log has been generated.", "alert-warning")
            return flask.redirect(flask.url_for("default.home", error=error))

        # Minify sent HTML
        @app.after_request
        def response_minify(response):
            if response.content_type == "text/html; charset=utf-8":
                response.set_data(htmlmin.main.minify(response.get_data(as_text=True)))
            return response

    # Import all blueprints from controllers
    from personal_site.controllers import default
    from personal_site.admin.controllers import admin
    from personal_site.auth.controllers import auth
    from personal_site.forum.controllers import forum
    from personal_site.profile.controllers import profile
    from personal_site.wiki.controllers import wiki

    # Register blueprints
    app.register_blueprint(default)
    app.register_blueprint(admin)
    app.register_blueprint(auth)
    app.register_blueprint(forum)
    app.register_blueprint(profile)
    app.register_blueprint(wiki)

    return app
