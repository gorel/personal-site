"""
Performs webapp startup procedures
"""

import logging

import flask
import flask_bcrypt
import flask_login
import flask_mail
import flask_sqlalchemy
import flask_wtf

import htmlmin.main


# Create app
print("Creating Flask app...", end="")
app = Flask(__name__)
print("Done.")

# Load configuration file
print("Loading config from object...", end="")
app.config.from_object("config")
print("Done.")

# Initialize database
print("Set up database...", end="")
db = flask_sqlalchemy.SQLAlchemy(app)
print("Done.")

# Create login manager
print("Creating login manager...", end="")
login_manager = flask_login.LoginManager(app)
print("Done.")

# Set up BCrypt password hashing
print("Initializing BCrypt library...", end="")
bcrypt = flask_bcrypt.Bcrypt(app)
print("Done.")

# Configure mail server
print("Configuring mail server...", end="")
mail = flask_mail.Mail(app)
print("Done.")

# Enable CSRF protection
print("Enable CSRF protection", end="")
csrf = flask_wtf.CsrfProtect(app)
print("Done.")

# Set up logging
print("Set up logger...", end="")
formatter = logging.Formatter(
    "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levename)s - %(message)s",
)
handler = logging.handlers.RotatingFileHandler(
    "site.log", maxBytes=10000, backupCount=2,
)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
print("Done.")

# Register error handlers
print("Registering error handlers...")

@app.errorhandler(404)
def error404(error):
    return flask.render_template("404.html", error=error), 404

@app.errorhandler(500)
def error500(error):
    app.logger.error(f"HTTP 500: {error}")
    if app.debug:
        return flask.redirect(flask.url_for("admin.bugsplat", error=error))
    else:
        flask.flash("Something went wrong :( A log has been generated.")
        return flask.redirect(flask.url_for("default.home", error=error))


print("Done.")

# Minify sent HTML
print("Define HTML content minifier...", end="")
@app.after_request
def response_minify(response):
    if response.content_type == "text/html; charset=utf-8":
        response.set_data(htmlmin.main.minify(response.get_data(as_text=True)))
    return response
print("Done.")

# Import all blueprints from controllers
from personal_site.controllers import default

# Register blueprints
app.register_blueprint(default)
