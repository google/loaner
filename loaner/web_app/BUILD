# Description:
#   BUILD file for //loaner/web_app.

package(
    default_visibility = [
        "//loaner:__subpackages__",
    ],
)

load(
    "//loaner:builddefs.bzl",
    "loaner_appengine_library",
    "py_appengine_binary",
)

# ==============================================================================
# Files
# ==============================================================================

filegroup(
    name = "config_defaults_yaml",
    srcs = [
        "config_defaults.yaml",
    ],
)

filegroup(
    name = "permissions",
    srcs = [
        "permissions.json",
    ],
)

# ==============================================================================
# Libraries
# ==============================================================================

loaner_appengine_library(
    name = "constants",
    srcs = ["constants.py"],
    deps = [
        "//loaner/web_app/backend/models:template_model",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "chrome_api",
    srcs = [
        "chrome_api.py",
    ],
    deps = [
        "//loaner/web_app/backend/api:chrome_api",
        "//loaner/web_app/backend/api:root_api",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "endpoints_api",
    srcs = [
        "endpoints_api.py",
    ],
    deps = [
        "//loaner/web_app/backend/api:bootstrap_api",
        "//loaner/web_app/backend/api:config_api",
        "//loaner/web_app/backend/api:datastore_api",
        "//loaner/web_app/backend/api:device_api",
        "//loaner/web_app/backend/api:root_api",
        "//loaner/web_app/backend/api:shelf_api",
        "//loaner/web_app/backend/api:tag_api",
        "//loaner/web_app/backend/api:user_api",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "loaner",
    deps = [
        ":chrome_api",
        ":endpoints_api",
        ":main",
        "//loaner/web_app/backend",
    ],
)

loaner_appengine_library(
    name = "main",
    srcs = [
        "main.py",
    ],
    deps = [
        ":constants",
        "//loaner/web_app/backend/handlers:frontend",
        "//loaner/web_app/backend/handlers:maintenance",
        "//loaner/web_app/backend/handlers/cron:run_custom_events",
        "//loaner/web_app/backend/handlers/cron:run_reminder_events",
        "//loaner/web_app/backend/handlers/cron:run_shelf_audit_events",
        "//loaner/web_app/backend/handlers/cron:sync_user_roles",
        "//loaner/web_app/backend/handlers/task:process_action",
        "//loaner/web_app/backend/handlers/task:stream_to_bigquery",
    ],
)

# ==============================================================================
# Binary
# ==============================================================================

py_appengine_binary(
    name = "runfiles",
    srcs = ["main.py"],
    configs = [
        "action_system.yaml",
        "app.yaml",
        "chrome.yaml",
        "cron.yaml",
        "endpoints.yaml",
        "index.yaml",
        "queue.yaml",
    ],
    deps = [":loaner"],
)

# ==============================================================================
# Tests
# ==============================================================================

test_suite(
    name = "all_tests",
    tests = [
        "//loaner/web_app/backend:all_tests",
    ],
)
