import datetime
import json
import os
import requests
import schedule
import time

import personal_site

from dli_app.mod_admin.models import ErrorReport
from dli_app.mod_auth.models import PasswordReset


app = personal_site.create_app()


def clear_old_shelf_objects():
    with app.app_context():
        personal_site.tasks.clear_old_shelf_objects()


############################
## BEGIN SCHEDULE SECTION ##
############################

schedule.every().day.at("23:59").do(clear_old_shelf_objects)

##########################
## END SCHEDULE SECTION ##
##########################


# Run all scheduled jobs forever
while True:
    schedule.run_pending()
    time.sleep(60)
