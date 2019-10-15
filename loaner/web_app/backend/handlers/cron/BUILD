# Description:
#   BUILD file for //loaner/web_app/backend/handlers/cron.

load(
    "//loaner:builddefs.bzl",
    "loaner_appengine_library",
    "loaner_appengine_test",
)

package(
    default_visibility = [
        "//loaner:__subpackages__",
    ],
)

# ==============================================================================
# Libraries
# ==============================================================================

loaner_appengine_library(
    name = "cron",
    srcs = [
        ":cloud_datastore_export",
        ":run_custom_events",
        ":run_reminder_events",
        ":sync_user_roles",
    ],
)

loaner_appengine_library(
    name = "cloud_datastore_export",
    srcs = [
        "cloud_datastore_export.py",
    ],
    deps = [
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/models:config_model",
    ],
)

loaner_appengine_library(
    name = "run_custom_events",
    srcs = [
        "run_custom_events.py",
    ],
    deps = [
        "//loaner/web_app/backend/lib:events",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:event_models",
        "//loaner/web_app/backend/models:shelf_model",
    ],
)

loaner_appengine_library(
    name = "run_reminder_events",
    srcs = [
        "run_reminder_events.py",
    ],
    deps = [
        "//loaner/web_app/backend/lib:events",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:event_models",
        "@absl_archive//absl/logging",
    ],
)

loaner_appengine_library(
    name = "run_shelf_audit_events",
    srcs = [
        "run_shelf_audit_events.py",
    ],
    deps = [
        "//loaner/web_app/backend/lib:events",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/models:shelf_model",
    ],
)

loaner_appengine_library(
    name = "sync_user_roles",
    srcs = [
        "sync_user_roles.py",
    ],
    deps = [
        "//loaner/web_app/backend/lib:sync_users",
    ],
)

# ==============================================================================
# Tests
# ==============================================================================

loaner_appengine_test(
    name = "cloud_datastore_export_test",
    srcs = [
        "cloud_datastore_export_test.py",
    ],
    deps = [
        ":cloud_datastore_export",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/testing:handlertest",
        "@absl_archive//absl/testing:parameterized",
        "@freezegun_archive//:freezegun",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "run_custom_events_test",
    srcs = [
        "run_custom_events_test.py",
    ],
    deps = [
        ":run_custom_events",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/lib:events",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:event_models",
        "//loaner/web_app/backend/models:shelf_model",
        "//loaner/web_app/backend/testing:handlertest",
        "//loaner/web_app/backend/testing:loanertest",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "run_reminder_events_test",
    srcs = [
        "run_reminder_events_test.py",
    ],
    deps = [
        ":run_reminder_events",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/lib:events",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:event_models",
        "//loaner/web_app/backend/testing:handlertest",
        "//loaner/web_app/backend/testing:loanertest",
    ],
)

loaner_appengine_test(
    name = "run_shelf_audit_events_test",
    srcs = [
        "run_shelf_audit_events_test.py",
    ],
    deps = [
        ":run_reminder_events",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/lib:events",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/models:event_models",
        "//loaner/web_app/backend/models:shelf_model",
        "//loaner/web_app/backend/testing:handlertest",
        "//loaner/web_app/backend/testing:loanertest",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":run_custom_events_test",
        ":run_reminder_events_test",
        ":run_shelf_audit_events_test",
    ],
)
