import datetime
import sys
import time

import schedule

from personal_site import create_app, tasks

app = create_app()


def clear_old_shelf_objects():
    print("clear_old_shelf_objects running", file=sys.stderr)
    with app.app_context():
        tasks.clear_old_shelf_objects()
    print("clear_old_shelf_objects done", file=sys.stderr)


############################
## BEGIN SCHEDULE SECTION ##
############################

schedule.every().day.at("23:59").do(clear_old_shelf_objects)

##########################
## END SCHEDULE SECTION ##
##########################


# Run all scheduled jobs forever
while True:
    now = datetime.datetime.utcnow()
    now = now - datetime.timedelta(microseconds=now.microsecond)
    print(f"Run pending ({now}Z)", file=sys.stderr)
    sys.stdout.flush()
    schedule.run_pending()
    time.sleep(60)
