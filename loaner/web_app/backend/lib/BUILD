# Description:
#   BUILD file for //loaner/web_app/backend/lib.

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
    name = "lib",
    deps = [
        ":action_loader",
        ":api_utils",
        ":bootstrap",
        ":datastore_yaml",
        ":events",
        ":send_email",
        ":user",
        ":utils",
        ":xsrf",
    ],
)

loaner_appengine_library(
    name = "action_loader",
    srcs = [
        "action_loader.py",
    ],
    deps = ["//loaner/web_app/backend/actions"],
)

loaner_appengine_library(
    name = "api_utils",
    srcs = [
        "api_utils.py",
    ],
    deps = [
        "//loaner/web_app/backend/api/messages:device_messages",
        "//loaner/web_app/backend/api/messages:shelf_messages",
        "//loaner/web_app/backend/models:device_model",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "bootstrap",
    srcs = [
        "bootstrap.py",
    ],
    data = [
        "bootstrap.yaml",
    ],
    deps = [
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/clients:bigquery",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/lib:datastore_yaml",
        "//loaner/web_app/backend/lib:utils",
        "//loaner/web_app/backend/models:bootstrap_status_model",
        "//loaner/web_app/backend/models:config_model",
    ],
)

loaner_appengine_library(
    name = "datastore_yaml",
    srcs = [
        "datastore_yaml.py",
    ],
    deps = [
        ":user",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:event_models",
        "//loaner/web_app/backend/models:shelf_model",
        "//loaner/web_app/backend/models:survey_models",
        "//loaner/web_app/backend/models:template_model",
        "//loaner/web_app/backend/models:user_model",
    ],
)

loaner_appengine_library(
    name = "events",
    srcs = [
        "events.py",
    ],
    deps = [
        "//loaner/web_app/backend/models:event_models",
    ],
)

loaner_appengine_library(
    name = "search_utils",
    srcs = [
        "search_utils.py",
    ],
    deps = [
        "//loaner/web_app/backend/api/messages:shared_messages",
        "//loaner/web_app/backend/models:device_model",
    ],
)

loaner_appengine_library(
    name = "send_email",
    srcs = [
        "send_email.py",
    ],
    deps = [
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/models:config_model",
        "@html2text_archive//:html2text",
    ],
)

loaner_appengine_library(
    name = "sync_users",
    srcs = [
        "sync_users.py",
    ],
    deps = [
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/models:user_model",
    ],
)

loaner_appengine_library(
    name = "user",
    srcs = [
        "user.py",
    ],
    deps = [
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "utils",
    srcs = [
        "utils.py",
    ],
    data = [
        "//loaner/web_app:config_defaults_yaml",
    ],
    deps = [
        "//loaner/web_app:constants",
    ],
)

loaner_appengine_library(
    name = "xsrf",
    srcs = [
        "xsrf.py",
    ],
    deps = [
        ":user",
        "//loaner/web_app:constants",
        "@oauth2client_archive//:oauth2client",
    ],
)

# ==============================================================================
# Tests
# ==============================================================================

loaner_appengine_test(
    name = "action_loader_test",
    srcs = [
        "action_loader_test.py",
    ],
    deps = [
        ":action_loader",
        "//loaner/web_app/backend/actions",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "api_utils_test",
    srcs = [
        "api_utils_test.py",
    ],
    deps = [
        ":api_utils",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/api/messages:device_messages",
        "//loaner/web_app/backend/api/messages:shelf_messages",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:shelf_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_test(
    name = "bootstrap_test",
    srcs = [
        "bootstrap_test.py",
    ],
    deps = [
        ":bootstrap",
        "//loaner/web_app/backend/clients:bigquery",
        "//loaner/web_app/backend/lib:datastore_yaml",
        "//loaner/web_app/backend/lib:utils",
        "//loaner/web_app/backend/models:bootstrap_status_model",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@gcloud_auth_archive//:gcloud_auth",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "datastore_yaml_test",
    srcs = [
        "datastore_yaml_test.py",
    ],
    deps = [
        ":datastore_yaml",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:event_models",
        "//loaner/web_app/backend/models:shelf_model",
        "//loaner/web_app/backend/models:survey_models",
        "//loaner/web_app/backend/models:template_model",
        "//loaner/web_app/backend/models:user_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "events_test",
    srcs = [
        "events_test.py",
    ],
    deps = [
        ":events",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:event_models",
        "//loaner/web_app/backend/models:shelf_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "search_utils_test",
    srcs = [
        "search_utils_test.py",
    ],
    deps = [
        ":search_utils",
        "//loaner/web_app/backend/api/messages:device_messages",
        "//loaner/web_app/backend/api/messages:shared_messages",
        "//loaner/web_app/backend/api/messages:shelf_messages",
        "//loaner/web_app/backend/models:shelf_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "send_email_test",
    srcs = [
        "send_email_test.py",
    ],
    deps = [
        ":send_email",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:shelf_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "sync_users_test",
    srcs = [
        "sync_users_test.py",
    ],
    deps = [
        ":sync_users",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/models:user_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "user_test",
    srcs = [
        "user_test.py",
    ],
    deps = [
        ":user",
        "//loaner/web_app/backend/testing:loanertest",
        "@endpoints_archive//:endpoints",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "utils_test",
    srcs = [
        "utils_test.py",
    ],
    deps = [
        ":utils",
        "//loaner/web_app/backend/testing:loanertest",
    ],
)

loaner_appengine_test(
    name = "xsrf_test",
    srcs = [
        "xsrf_test.py",
    ],
    deps = [
        ":user",
        ":xsrf",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/testing:loanertest",
        "@mock_archive//:mock",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":action_loader_test",
        ":api_utils_test",
        ":bootstrap_test",
        ":datastore_yaml_test",
        ":events_test",
        ":search_utils_test",
        ":send_email_test",
        ":sync_users_test",
        ":user_test",
        ":utils_test",
        ":xsrf_test",
    ],
)
