import flask
import redis
import rq

from personal_site import constants, db


class Task(db.Model):
    id = db.Column(db.String(constants.TASK_ID_LEN), primary_key=True)
    name = db.Column(db.String(constants.TASK_NAME_MAX_LEN), index=True)
    description = db.Column(db.String(constants.TASK_DESC_MAX_LEN))
    meta = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            return rq.job.Job.fetch(self.id, connection=flask.current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
