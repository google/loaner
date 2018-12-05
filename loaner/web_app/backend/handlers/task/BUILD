# Description:
#   BUILD file for //loaner/web_app/backend/handlers/task.

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
    name = "task",
    srcs = [
        ":process_action",
        ":stream_to_bigquery",
    ],
)

loaner_appengine_library(
    name = "process_action",
    srcs = [
        "process_action.py",
    ],
    deps = [
        "//loaner/web_app/backend/lib:action_loader",
        "@absl_archive//absl/logging",
    ],
)

loaner_appengine_library(
    name = "stream_to_bigquery",
    srcs = [
        "stream_to_bigquery.py",
    ],
    deps = [
        "//loaner/web_app/backend/models:bigquery_row_model",
    ],
)

# ==============================================================================
# Tests
# ==============================================================================

loaner_appengine_test(
    name = "process_action_test",
    srcs = [
        "process_action_test.py",
    ],
    deps = [
        ":process_action",
        "//loaner/web_app/backend/lib:action_loader",
        "//loaner/web_app/backend/testing:handlertest",
        "@absl_archive//absl/logging",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "stream_to_bigquery_test",
    srcs = [
        "stream_to_bigquery_test.py",
    ],
    deps = [
        ":stream_to_bigquery",
        "//loaner/web_app/backend/testing:handlertest",
        "@absl_archive//absl/testing:parameterized",
        "@mock_archive//:mock",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":process_action_test",
        ":stream_to_bigquery_test",
    ],
)
