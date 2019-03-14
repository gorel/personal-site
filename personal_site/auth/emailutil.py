import threading

import flask
import flask_mail

from personal_site import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = flask_mail.Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    threading.Thread(
        target=send_async_email,
        args=(flask.current_app._get_current_object(), msg),
    ).start()
