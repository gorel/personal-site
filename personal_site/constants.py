import os
import re

# Basepath constants
__basepath = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(__basepath, "templates")

# Tasks
TASK_ID_LEN = 36
TASK_NAME_MAX_LEN = 128
TASK_DESC_MAX_LEN = 128
TASK_PREFIX = "personal_site.tasks."

# Admin
ADMIN_USERS_PER_PAGE = 50
WARNING_MAX_LEN = 200
WARNING_ICON = "fas fa-exclamation-triangle"
WARNING_TEXT_CLASS = "text-warning"

# Auth
USERNAME_MAX_LEN = 64
EMAIL_MAX_LEN = 64
PW_HASH_LEN = 64
PASSWORD_MIN_LEN = 8
VERIFY_ACCOUNT_TOKEN_STR = "verify_account"
RESET_PASSWORD_TOKEN_STR = "reset_password"
EMAIL_SUBJ_LEAD = "[logangore.dev]"
VERIFY_ACCOUNT_SUBJECT_STR = f"{EMAIL_SUBJ_LEAD} Verify your email"
RESET_PASSWORD_SUBJECT_STR = f"{EMAIL_SUBJ_LEAD} Reset your password",

# Profile
NOTIFICATION_MAX_LEN = 140
ICON_MAX_LEN = 64
TEXT_CLASS_MAX_LEN = 64
NOTIFICATIONS_PER_PAGE = 25
NOTIFICATION_URL_LINK_MAX_LEN = 256

# Learn
LEARN_PAGE_TEMPLATE_DIR = os.path.join("learn", "pages")
LEARNPAGE_MAX_LEN = 64
PAGE_IDNAME_REGEX = "^([a-zA-Z0-9]+-?)+[a-zA-Z0-9]+$"
PAGE_IDNAME_REGEX_MSG = ("idname can only contain alphanumeric characters plus "
                         "`-` and cannot start with, end with, or have "
                         "multiple successive `-` characters")
# Time required for a shelve_db key to expire for incrementing views
LEARN_VIEW_EXPIRED_HOURS = 1
SHELVE_TIMEOUT_SECS = 0.1
QUESTIONS_PER_PAGE = 20

# Forum
POST_TITLE_MAX_LEN = 100
POSTS_PER_PAGE = 20
COMMENTS_PER_PAGE = 10
POST_MAX_LEN = 10000
NEW_COMMENT_NOTIF_STR = "There is a new comment on a post you're following"

# Other
ES_PAGE_SIZE = 25
MARKDOWN_CODE_PATTERN = re.compile("```((.|\n)*?)```")
