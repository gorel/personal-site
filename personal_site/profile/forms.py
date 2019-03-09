import flask_login
import flask_wtf
import wtforms

import personal_site.auth.models as auth_models


class EditAccountForm(flask_wtf.Form):
    def validate(self):
        if not flask_wtf.Form.validate(self):
            return False

        user = flask_login.current_user
        user.username = self.username.data or user.username

        if self.email.data:
            user.email = self.email.data
            user.email_verified = False
            user.send_email_verification_link()

        if self.password.data:
            user.set_password(self.password.data)

        return True
