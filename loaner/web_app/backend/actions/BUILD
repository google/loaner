# Description:
#   BUILD file for //loaner/web_app/backend/actions.

package(
    default_visibility = [
        "//loaner:__subpackages__",
    ],
)

load(
    "//loaner:builddefs.bzl",
    "loaner_appengine_library",
    "loaner_appengine_test",
)

# ==============================================================================
# Libraries
# ==============================================================================

loaner_appengine_library(
    name = "actions",
    deps = [
        ":base_action",
        ":lock_device",
        ":request_shelf_audit",
        ":send_reminder",
        ":send_return_thanks",
        ":send_welcome",
    ],
)

loaner_appengine_library(
    name = "base_action",
    srcs = [
        "base_action.py",
    ],
)

loaner_appengine_library(
    name = "lock_device",
    srcs = [
        "lock_device.py",
    ],
    deps = [
        ":base_action",
        "//loaner/web_app:constants",
    ],
)

loaner_appengine_library(
    name = "request_shelf_audit",
    srcs = [
        "request_shelf_audit.py",
    ],
    deps = [
        ":base_action",
        "//loaner/web_app/backend/lib:send_email",
        "//loaner/web_app/backend/models:config_model",
    ],
)

loaner_appengine_library(
    name = "send_reminder",
    srcs = [
        "send_reminder.py",
    ],
    deps = [
        ":base_action",
        "//loaner/web_app/backend/lib:send_email",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/models:event_models",
        "@absl_archive//absl/logging",
    ],
)

loaner_appengine_library(
    name = "send_return_thanks",
    srcs = [
        "send_return_thanks.py",
    ],
    deps = [
        ":base_action",
        "//loaner/web_app/backend/lib:send_email",
    ],
)

loaner_appengine_library(
    name = "send_welcome",
    srcs = [
        "send_welcome.py",
    ],
    deps = [
        ":base_action",
        "//loaner/web_app/backend/lib:send_email",
    ],
)

# ==============================================================================
# Tests
# ==============================================================================

loaner_appengine_test(
    name = "base_action_test",
    srcs = [
        "base_action_test.py",
    ],
    deps = [
        ":base_action",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
    ],
)

loaner_appengine_test(
    name = "lock_device_test",
    srcs = [
        "lock_device_test.py",
    ],
    deps = [
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "request_shelf_audit_test",
    srcs = [
        "request_shelf_audit_test.py",
    ],
    deps = [
        "//loaner/web_app/backend/lib:send_email",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/models:shelf_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "send_reminder_test",
    srcs = [
        "send_reminder_test.py",
    ],
    deps = [
        "//loaner/web_app/backend/lib:send_email",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:event_models",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "send_return_thanks_test",
    srcs = [
        "send_return_thanks_test.py",
    ],
    deps = [
        "//loaner/web_app/backend/lib:send_email",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "send_welcome_test",
    srcs = [
        "send_welcome_test.py",
    ],
    deps = [
        "//loaner/web_app/backend/lib:send_email",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@mock_archive//:mock",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":base_action_test",
        ":lock_device_test",
        ":request_shelf_audit_test",
        ":send_reminder_test",
        ":send_return_thanks_test",
        ":send_welcome_test",
    ],
)
