# Description:
#   BUILD file for //loaner/web_app/backend/api/messages.

package(
    default_visibility = [
        "//loaner:__subpackages__",
    ],
)

load(
    "//loaner:builddefs.bzl",
    "loaner_appengine_library",
)

# ==============================================================================
# Libraries
# ==============================================================================

loaner_appengine_library(
    name = "config_messages",
    srcs = [
        "config_messages.py",
    ],
)

loaner_appengine_library(
    name = "bootstrap_messages",
    srcs = [
        "bootstrap_messages.py",
    ],
)

loaner_appengine_library(
    name = "chrome_messages",
    srcs = [
        "chrome_messages.py",
    ],
)

loaner_appengine_library(
    name = "datastore_messages",
    srcs = [
        "datastore_messages.py",
    ],
)

loaner_appengine_library(
    name = "device_messages",
    srcs = [
        "device_messages.py",
    ],
    deps = [
        ":shared_messages",
        ":shelf_messages",
    ],
)

loaner_appengine_library(
    name = "search_messages",
    srcs = [
        "search_messages.py",
    ],
)

loaner_appengine_library(
    name = "shared_messages",
    srcs = [
        "shared_messages.py",
    ],
)

loaner_appengine_library(
    name = "shelf_messages",
    srcs = [
        "shelf_messages.py",
    ],
    deps = [
        ":shared_messages",
    ],
)

loaner_appengine_library(
    name = "survey_messages",
    srcs = [
        "survey_messages.py",
    ],
)

loaner_appengine_library(
    name = "tag_messages",
    srcs = [
        "tag_messages.py",
    ],
)

loaner_appengine_library(
    name = "user_messages",
    srcs = [
        "user_messages.py",
    ],
)
