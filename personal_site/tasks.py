import contextlib
import inspect
import json
import functools
import rq

import flask
import flask_shelve

from personal_site import create_app, db, email_util, models

import personal_site.learn.utils as learn_utils


REGISTERED_TASKS = set()


app = create_app()
app.app_context().push()


def register_task(f):
    REGISTERED_TASKS.add(f.__name__)

    @functools.wraps(f)
    def _wrap(*args, **kwargs):
        job = rq.get_current_job()
        task = models.Task.query.get(job.get_id())

        # Task was created from some other context -> add a new object to db
        if task is None:
            # Get caller's function name
            name = inspect.stack()[1].function
            description = "(Called from unknown context)"
            task = models.Task(id=job.get_id(), name=name, description=description, user=None)
            db.session.add(task)
            db.session.commit()

        res = f(*args, **kwargs)
        job = rq.get_current_job()
        task.meta = json.dumps(job.meta)
        db.session.commit()
        return res
    return _wrap


@contextlib.contextmanager
def fake_request_context(*args, **kwargs):
    ctx = None
    try:
        ctx = flask.current_app.test_request_context("")
        ctx.push()
        yield
    finally:
        if ctx is not None:
            ctx.pop()


def _set_progress(job, progress_pct):
    job.meta["progress"] = progress_pct
    job.save_meta()
    task = models.Task.query.get(job.get_id())
    if progress_pct >= 100:
        task.complete = True
    db.session.commit()


@register_task
def send_email(email_props):
    job = rq.get_current_job()
    _set_progress(job, 0)
    email_util.send_email(**email_props)
    _set_progress(job, 100)


@register_task
def clear_old_shelve_objects():
    with fake_request_context():
        job = rq.get_current_job()
        _set_progress(job, 0)
        job.meta["expired_keys"] = 0
        job.save_meta()

        shelve_db = flask_shelve.get_shelve("c")
        keys = shelve_db.keys()
        for i, key in enumerate(keys):
            _set_progress(job, i / len(keys))
            if learn_utils.is_last_view_expired(shelve_db, key):
                del shelve_db[key]
                job.meta["expired_keys"] += 1
                job.save_meta()
        _set_progress(job, 100)
