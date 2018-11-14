# Description:
#   BUILD file for //loaner/web_app/backend/clients.

package(default_visibility = ["//loaner:__subpackages__"])

load(
    "//loaner:builddefs.bzl",
    "loaner_appengine_library",
    "loaner_appengine_test",
)

# ==============================================================================
# Libraries
# ==============================================================================

loaner_appengine_library(
    name = "clients",
    deps = [
        ":bigquery",
        ":directory",
    ],
)

loaner_appengine_library(
    name = "bigquery",
    srcs = [
        "bigquery.py",
    ],
    deps = [
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/common:google_cloud_lib_fixer",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:shelf_model",
        "//loaner/web_app/backend/models:survey_models",
        "@gcloud_bigquery_archive//:gcloud_bigquery",
    ],
)

loaner_appengine_library(
    name = "directory",
    srcs = [
        "directory.py",
    ],
    deps = [
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/common:google_cloud_lib_fixer",
        "@gcloud_auth_archive//:gcloud_auth",
        "@google_auth_httplib2_archive//:google_auth_httplib2",
        "@googleapiclient_archive//:googleapiclient",
    ],
)

# ==============================================================================
# Tests
# ==============================================================================

loaner_appengine_test(
    name = "bigquery_test",
    srcs = [
        "bigquery_test.py",
    ],
    deps = [
        ":bigquery",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/common:google_cloud_lib_fixer",
        "//loaner/web_app/backend/models:bigquery_row_model",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@gcloud_bigquery_archive//:gcloud_bigquery",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "directory_test",
    srcs = [
        "directory_test.py",
    ],
    deps = [
        ":directory",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@googleapiclient_archive//:googleapiclient",
        "@mock_archive//:mock",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":bigquery_test",
        ":directory_test",
    ],
)
