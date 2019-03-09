import argparse
import os

from personal_site import db

import personal_site.account.models as account_models
import personal_site.admin.models as admin_models
import personal_site.auth.models as auth_models
import personal_site.forum.models as forum_models
import personal_site.wiki.models as wiki_models

parser = argparse.ArgumentParser(description="DB initial setup utility")
parser.add_argument(
    "-d", "--drop", action="store_true",
    help="Drop existing DB tables before recreation",
)
parser.add_argument(
    "-v", "--verbose", action="store_true",
    help="Show extra output about which stage the script is executing",
)


if __name__ == "__main__":
    args = parser.parse_args()
    print("create_db.py script loaded")

    if args.drop:
        db.session.close()
        db.drop_all()
        if args.verbose:
            print("Dropped all database models")

    db.create_all()
    print("All successful")
