# Description:
#   BUILD file for //loaner/oss/deployments.

package(
    default_visibility = [
        "//loaner:__subpackages__",
    ],
)

#########
# Files #
#########

filegroup(
    name = "configs",
    srcs = [
        "config.yaml",
    ],
)

############
# Binaries #
############

py_binary(
    name = "deploy_impl",
    srcs = [
        "deploy_impl.py",
    ],
    deps = [
        ":deploy_impl_lib",
    ],
)

#############
# Libraries #
#############

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
        ":configs",
    ],
    deps = [
        "@absl_archive//absl:app",
        "@absl_archive//absl/flags",
        "@absl_archive//absl/logging",
        "@yaml_archive//:yaml",
    ],
)

py_library(
    name = "deploy_impl_lib",
    srcs = [
        "deploy_impl.py",
    ],
    deps = [
        "@absl_archive//absl:app",
        "@absl_archive//absl/flags",
        "@absl_archive//absl/logging",
    ],
)

#########
# Tests #
#########

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
    name = "deploy_impl_test",
    size = "small",
    srcs = [
        "deploy_impl_test.py",
    ],
    deps = [
        ":deploy_impl",
        "@absl_archive//absl:app",
        "@absl_archive//absl/flags",
        "@absl_archive//absl/testing:absltest",
        "@freezegun_archive//:freezegun",
        "@mock_archive//:mock",
        "@pyfakefs_archive//:pyfakefs",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":auth_test",
        ":common_test",
        ":deploy_impl_test",
    ],
)
