# Description:
#   BUILD file for //loaner/web_app/backend/api/messages.

package(
    default_visibility = [
        "//loaner:internal",
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
    name = "shelf_message",
    srcs = [
        "shelf_message.py",
    ],
)

loaner_appengine_library(
    name = "config_message",
    srcs = [
        "config_message.py",
    ],
)

loaner_appengine_library(
    name = "bootstrap_message",
    srcs = [
        "bootstrap_message.py",
    ],
)

loaner_appengine_library(
    name = "chrome_message",
    srcs = [
        "chrome_message.py",
    ],
)

loaner_appengine_library(
    name = "datastore_message",
    srcs = [
        "datastore_message.py",
    ],
)

loaner_appengine_library(
    name = "device_message",
    srcs = [
        "device_message.py",
    ],
    deps = [
        ":shelf_message",
    ],
)

loaner_appengine_library(
    name = "survey_messages",
    srcs = [
        "survey_messages.py",
    ],
)

loaner_appengine_library(
    name = "user_message",
    srcs = [
        "user_message.py",
    ],
)
