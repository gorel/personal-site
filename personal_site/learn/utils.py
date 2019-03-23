import contextlib
import datetime
import signal

import flask_shelve

from personal_site import constants


def is_last_view_expired(db, shelve_key):
    now = datetime.datetime.utcnow()
    key_expiry_time = db.get(shelve_key, now)

    # Returns True if the shelve_key expired some time before now
    return key_expiry_time < now


def update_shelve_expiration_time(db, shelve_key):
    now = datetime.datetime.utcnow()
    new_expiry = now + datetime.timedelta(hours=constants.LEARN_VIEW_EXPIRED_HOURS)
    db[shelve_key] = new_expiry



class timeout(contextlib.ContextDecorator):
    def __init__(self, seconds, suppress_timeout_error=False):
        self.seconds = seconds
        self.suppress = suppress_timeout_error

    def _timeout_handler(self, _1, _2):
        raise TimeoutError("The operation timed out")

    def __enter__(self):
        signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)
        if self.suppress and exc_type is TimeoutError:
            return True
