import os

# Basepath constants
__basepath = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(__basepath, "templates")

# Admin
ADMIN_USERS_PER_PAGE = 50
WARNING_MAX_LEN = 200

# Auth
USERNAME_MAX_LEN = 32
PASSWORD_MIN_LEN = 8

# Wiki
WIKIPAGE_MAX_LEN = 64

# Learn
LEARN_PAGE_TEMPLATE_DIR = os.path.join("learn", "pages")
LEARNPAGE_MAX_LEN = 64
PAGE_IDNAME_REGEX = "^([a-zA-Z0-9]+-?)+[a-zA-Z0-9]+$"
PAGE_IDNAME_REGEX_MSG = ("idname can only contain alphanumeric characters plus "
                         "`-` and cannot start with, end with, or have "
                         "multiple successive `-` characters")

# Forum
NOTIFICATION_MAX_LEN = 140
POST_TITLE_MAX_LEN = 100
POSTS_PER_PAGE = 25
COMMENTS_PER_PAGE = 20
POST_MAX_LEN = 10000

# Other
ES_PAGE_SIZE = 25
