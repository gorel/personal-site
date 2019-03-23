import datetime

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
