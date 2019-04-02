import inspect
import json
import functools
import rq

import flask
import flask_shelve

from personal_site import create_app, db, email_util

import personal_site.base.models as base_models
import personal_site.auth.models as auth_models
import personal_site.learn.models as learn_models

import personal_site.learn.utils as learn_utils


REGISTERED_TASKS = set()


app = create_app()
app.app_context().push()


def register_task(f):
    REGISTERED_TASKS.add(f.__name__)

    @functools.wraps(f)
    def _wrap(*args, **kwargs):
        job = rq.get_current_job()
        _set_progress(job, 0)
        task = base_models.Task.query.get(job.get_id())

        # Task was created from some other context -> add a new object to db
        if task is None:
            # Get caller's function name
            name = inspect.stack()[1].function
            description = "(Called from unknown context)"
            task = base_models.Task(id=job.get_id(), name=name, description=description, user=None)
            db.session.add(task)
            db.session.commit()

        res = f(*args, **kwargs)
        _set_progress(job, 100)
        task.meta = json.dumps(job.meta)
        db.session.commit()
        return res
    return _wrap


def _set_progress(job, progress_pct):
    job.meta["progress"] = progress_pct
    job.save_meta()
    task = base_models.Task.query.get(job.get_id())
    if progress_pct >= 100:
        task.complete = True
    db.session.commit()


@register_task
def send_email(email_props):
    job = rq.get_current_job()
    email_util.send_email(**email_props)

@register_task
def record_view(username, page_name):
    with app.test_request_context("/"):
        job = rq.get_current_job()

        page_stats = learn_models.LearnPageStats.get_or_create(page_name)
        shelve_db = flask_shelve.get_shelve("c")
        shelve_key = f"{username}-{page_name}"

        if learn_utils.is_last_view_expired(shelve_db, shelve_key):
            page_stats.views += 1
            db.session.commit()

        # Update last seen time to now
        # It is INTENTIONAL that this updates even if we don't increment views
        learn_utils.update_shelve_expiration_time(shelve_db, shelve_key)


@register_task
def clear_old_shelve_objects():
    with app.test_request_context("/"):
        job = rq.get_current_job()
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


@register_task
def email_daily_bug_reports(start, end):
    new_reports = base_models.BugReport.query.filter(
            (base_models.BugReport.submitted_at > start)
            & (base_models.BugReport.submitted_at <= end)).all()

    print(f"Detected {len(new_reports)} new reports")
    if len(new_reports) > 0:
        email_props = {
            "subject": "Daily Bug Reports on logangore.dev",
            "sender": flask.current_app.config["ADMIN"],
            "recipients": [flask.current_app.config["EXT_ADMIN"]],
            "text_body": flask.render_template(
                "tasks/daily_bug_reports.txt",
                bug_reports=new_reports,
            ),
            "html_body": flask.render_template(
                "tasks/daily_bug_reports.html",
                bug_reports=new_reports,
            ),
        }

        email_util.send_email(**email_props)


@register_task
def record_error500(tb, user_id):
    user = auth_models.User.query.get(user_id)
    print(type(tb))
    bug_report = base_models.BugReport(
        user=user,
        report_type=base_models.REPORT_TYPES_INVERSE["BUG_REPORT"],
        text_response=str(tb),
    )
    db.session.add(bug_report)
    db.session.commit()
