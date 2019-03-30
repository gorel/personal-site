import datetime

import flask
import flask_login
import flask_wtf
import wtforms

from personal_site import constants, db
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
    show_anon = wtforms.BooleanField("Show as anonymous to classmates?")
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
            show_anon=self.show_anon.data,
        )

        db.session.add(self.post)
        db.session.commit()
        return True


class EditPostForm(flask_wtf.Form):
    body = wtforms.TextAreaField(
        "Body",
        render_kw={"class": "form-control", "rows": 20, "style": "resize: vertical"},
    )
    show_anon = wtforms.BooleanField("Show as anonymous to classmates?")
    submit = wtforms.SubmitField("Submit")

    def __init__(self, post, *args, **kwargs):
        super(EditPostForm, self).__init__(*args, **kwargs)
        self.post = post

    def validate(self):
        if not super(EditPostForm, self).validate():
            return False

        if self.post.author.id != flask_login.current_user.id:
            self.body.errors.append("You don't have permission to edit this post")
            self.body.errors.append("Are you sure you're logged in?")
            return False

        self.post.edit(self.body.data, self.show_anon.data)
        db.session.commit()
        return True


class NewCommentForm(flask_wtf.Form):
    body = wtforms.TextAreaField(
        "Body",
        render_kw={"class": "form-control", "rows": 10, "style": "resize: vertical"},
    )
    show_anon = wtforms.BooleanField("Show as anonymous to classmates?")
    submit = wtforms.SubmitField("Save")

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
            show_anon=self.show_anon.data,
        )

        self.post.num_comments += 1
        self.post.last_activity = datetime.datetime.utcnow()

        db.session.add(self.comment)
        db.session.commit()
        return True


class EditCommentForm(flask_wtf.Form):
    body = wtforms.TextAreaField(
        "Body",
        render_kw={"class": "form-control", "rows": 20, "style": "resize: vertical"},
    )
    show_anon = wtforms.BooleanField("Show as anonymous to classmates?")
    submit = wtforms.SubmitField("Submit")

    def __init__(self, post, comment, *args, **kwargs):
        super(EditCommentForm, self).__init__(*args, **kwargs)
        self.post = post
        self.comment = comment

    def validate(self):
        if not super(EditCommentForm, self).validate():
            return False

        if self.comment.parent_post.id != self.post.id:
            flask.current_app.logger.error("comment doesn't belong to post")
            self.body.errors.append("You can't move this comment to another post")
            self.body.errors.append("I'm really not sure how this even happened.")
            return False

        if self.comment.author.id != flask_login.current_user.id:
            self.body.errors.append("You don't have permission to edit this comment")
            self.body.errors.append("Are you sure you're logged in?")
            return False

        self.comment.edit(self.body.data, self.show_anon.data)
        self.post.last_activity = datetime.datetime.utcnow()

        db.session.commit()
        return True
