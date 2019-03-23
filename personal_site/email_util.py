import flask_mail

from personal_site import mail


def send_email(subject, sender, recipients, text_body, html_body, attachments=None):
    msg = flask_mail.Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    mail.send(msg)
