import datetime

import flask
import flask_login
import flask_wtf
import wtforms

from personal_site import constants
from personal_site.forum import models


class NewPostForm(flask_wtf.Form):
    title = wtforms.StringField(
        "Title",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(max=constants.POST_MAX_LEN),
        ],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    body = wtforms.TextAreaField(
        "Body",
        render_kw={"class": "form-control", "rows": 20, "style": "resize: vertical"},
    )
    submit = wtforms.SubmitField("Submit")


    def __init__(self, *args, **kwargs):
        super(NewPostForm, self).__init__(*args, **kwargs)
        self.post = None

    def validate(self):
        if not super(NewPostForm, self).validate():
            return False

        self.post = models.Post(
            author=flask_login.current_user,
            title=self.title.data,
            body=self.body.data,
        )
        return True


class EditPostForm(flask_wtf.Form):
    body = wtforms.TextAreaField(
        "Body",
        render_kw={"class": "form-control", "rows": 20, "style": "resize: vertical"},
    )
    submit = wtforms.SubmitField("Submit")

    def __init__(self, post, *args, **kwargs):
        super(NewPostForm, self).__init__(*args, **kwargs)
        self.post = post

    def validate(self):
        if not super(NewPostForm, self).validate():
            return False

        if self.post.author.id != flask_login.current_user.id:
            self.body.errors.append("You don't have permission to edit this post")
            self.body.errors.append("Are you sure you're logged in?")
            return False

        self.post.edit(self.body.data)
        return True


class NewCommentForm(flask_wtf.Form):
    body = wtforms.TextAreaField(
        "Body",
        render_kw={"class": "form-control", "rows": 20, "style": "resize: vertical"},
    )
    submit = wtforms.SubmitField("Submit")

    def __init__(self, post, *args, **kwargs):
        super(NewCommentForm, self).__init__(*args, **kwargs)
        self.post = post
        self.comment = None

    def validate(self):
        if not super(NewCommentForm, self).validate():
            return False

        self.comment = models.Comment(
            post=self.post,
            author=flask_login.current_user,
            body=self.body.data,
        )

        self.post.num_comments += 1
        self.post.last_activity = datetime.datetime.utcnow()
        return True


class EditCommentForm(flask_wtf.Form):
    body = wtforms.TextAreaField(
        "Body",
        render_kw={"class": "form-control", "rows": 20, "style": "resize: vertical"},
    )
    submit = wtforms.SubmitField("Submit")

    def __init__(self, post, comment, *args, **kwargs):
        super(NewcommentForm, self).__init__(*args, **kwargs)
        self.post = post
        self.comment = comment

    def validate(self):
        if not super(NewCommentForm, self).validate():
            return False

        if not self.comment.post.id != post.id:
            # TODO: Throw a bigger error here?
            self.body.errors.append("You can't move this comment to another post")
            self.body.errors.append("I'm really not sure how this even happened.")
            return False

        if self.comment.author.id != flask_login.current_user.id:
            self.body.errors.append("You don't have permission to edit this comment")
            self.body.errors.append("Are you sure you're logged in?")
            return False

        self.comment.edit(self.body.data)
        self.post.last_activity = datetime.datetime.utcnow()
        return True
