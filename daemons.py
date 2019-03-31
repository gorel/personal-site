import datetime
import sys
import time

import schedule

from personal_site import constants, create_app

app = create_app()


def clear_old_shelf_objects():
    print("clear_old_shelf_objects running", file=sys.stderr)
    app.task_queue.enqueue(constants.TASK_PREFIX + "clear_old_shelf_objects")
    print("clear_old_shelf_objects enqueued", file=sys.stderr)


def email_daily_bug_reports():
    print("email_daily_bug_reports", file=sys.stderr)
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(days=1)
    app.task_queue.enqueue(
        constants.TASK_PREFIX + "email_daily_bug_reports",
        start,
        end,
    )
    print("email_daily_bug_reports enqueued", file=sys.stderr)



############################
## BEGIN SCHEDULE SECTION ##
############################

schedule.every().day.at("23:59").do(clear_old_shelf_objects)
schedule.every().day.at("23:59").do(email_daily_bug_reports)

##########################
## END SCHEDULE SECTION ##
##########################


# Run all scheduled jobs forever
if __name__ == "__main__":
    while True:
        now = datetime.datetime.utcnow()
        now = now - datetime.timedelta(microseconds=now.microsecond)
        print(f"Run pending ({now}Z)", file=sys.stderr)
        sys.stdout.flush()
        schedule.run_pending()
        time.sleep(60)
