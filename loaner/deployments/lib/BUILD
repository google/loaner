# Description:
#   BUILD file for //loaner/deployments/lib.

package(
    default_visibility = [
        "//loaner:__subpackages__",
    ],
)

#############
# Libraries #
#############

py_library(
    name = "app_engine_lib",
    srcs = [
        "app_engine.py",
    ],
    deps = [
        ":auth_lib",
        "@absl_archive//absl/logging",
        "@googleapiclient_archive//:googleapiclient",
    ],
)

py_library(
    name = "auth_lib",
    srcs = [
        "auth.py",
    ],
    deps = [
        "@absl_archive//absl/flags",
        "@absl_archive//absl/logging",
        "@gcloud_auth_archive//:gcloud_auth",
        "@google_auth_httplib2_archive//:google_auth_httplib2",
        "@googleapiclient_archive//:googleapiclient",
        "@oauth2client_archive//:oauth2client",
    ],
)

py_library(
    name = "common_lib",
    srcs = [
        "common.py",
    ],
    data = [
        "//loaner/deployments:configs",
    ],
    deps = [
        "@absl_archive//absl/flags",
        "@absl_archive//absl/logging",
        "@yaml_archive//:yaml",
    ],
)

py_library(
    name = "datastore_lib",
    srcs = [
        "datastore.py",
    ],
    deps = [
        ":auth_lib",
        "//loaner/web_app/backend/common:google_cloud_lib_fixer",
        "@absl_archive//absl/logging",
        "@gcloud_datastore_archive//:gcloud_datastore",
    ],
)

py_library(
    name = "directory_lib",
    srcs = [
        "directory.py",
    ],
    deps = [
        ":auth_lib",
        "@absl_archive//absl/logging",
        "@googleapiclient_archive//:googleapiclient",
    ],
)

py_library(
    name = "storage_lib",
    srcs = [
        "storage.py",
    ],
    deps = [
        ":auth_lib",
        "@absl_archive//absl/logging",
        "@googleapiclient_archive//:googleapiclient",
    ],
)

#########
# Tests #
#########

py_test(
    name = "app_engine_test",
    size = "small",
    srcs = [
        "app_engine_test.py",
    ],
    deps = [
        ":app_engine_lib",
        ":auth_lib",
        ":common_lib",
        "@absl_archive//absl/testing:absltest",
        "@googleapiclient_archive//:googleapiclient",
        "@mock_archive//:mock",
    ],
)

py_test(
    name = "auth_test",
    size = "small",
    srcs = [
        "auth_test.py",
    ],
    deps = [
        ":auth_lib",
        ":common_lib",
        "@absl_archive//absl/flags",
        "@absl_archive//absl/testing:absltest",
        "@absl_archive//absl/testing:parameterized",
        "@gcloud_auth_archive//:gcloud_auth",
        "@google_auth_httplib2_archive//:google_auth_httplib2",
        "@mock_archive//:mock",
        "@oauth2client_archive//:oauth2client",
        "@pyfakefs_archive//:pyfakefs",
    ],
)

py_test(
    name = "common_test",
    size = "small",
    srcs = [
        "common_test.py",
    ],
    deps = [
        ":common_lib",
        "@absl_archive//absl/flags",
        "@absl_archive//absl/logging",
        "@absl_archive//absl/testing:absltest",
        "@absl_archive//absl/testing:parameterized",
        "@mock_archive//:mock",
        "@pyfakefs_archive//:pyfakefs",
    ],
)

py_test(
    name = "datastore_test",
    size = "small",
    srcs = [
        "datastore_test.py",
    ],
    deps = [
        ":auth_lib",
        ":common_lib",
        ":datastore_lib",
        "@absl_archive//absl/testing:absltest",
        "@gcloud_datastore_archive//:gcloud_datastore",
        "@mock_archive//:mock",
    ],
)

py_test(
    name = "directory_test",
    size = "small",
    srcs = [
        "directory_test.py",
    ],
    deps = [
        ":auth_lib",
        ":common_lib",
        ":directory_lib",
        "@absl_archive//absl/testing:absltest",
        "@absl_archive//absl/testing:parameterized",
        "@googleapiclient_archive//:googleapiclient",
        "@mock_archive//:mock",
    ],
)

py_test(
    name = "storage_test",
    size = "small",
    srcs = [
        "storage_test.py",
    ],
    deps = [
        ":auth_lib",
        ":common_lib",
        ":storage_lib",
        "@absl_archive//absl/testing:absltest",
        "@googleapiclient_archive//:googleapiclient",
        "@mock_archive//:mock",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":app_engine_test",
        ":auth_test",
        ":common_test",
        ":datastore_test",
        ":directory_test",
        ":storage_test",
    ],
)
