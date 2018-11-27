# Description:
#   BUILD file for //loaner/deployments.

package(
    default_visibility = [
        "//loaner/deployments:__subpackages__",
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
    default_python_version = "PY3",
    srcs_version = "PY2AND3",
    deps = [
        ":deploy_impl_lib",
    ],
)

py_binary(
    name = "gng_impl",
    srcs = [
        "gng_impl.py",
    ],
    default_python_version = "PY3",
    deps = [
        ":gng_impl_lib",
    ],
)

#############
# Libraries #
#############

py_library(
    name = "deploy_impl_lib",
    srcs = [
        "deploy_impl.py",
    ],
    srcs_version = "PY2AND3",
    deps = [
        "@absl_archive//absl:app",
        "@absl_archive//absl/flags",
        "@absl_archive//absl/logging",
        "@six_archive//:six",
    ],
)

py_library(
    name = "gng_impl_lib",
    srcs = [
        "gng_impl.py",
    ],
    srcs_version = "PY2AND3",
    deps = [
        "//loaner/deployments/lib:app_constants_lib",
        "//loaner/deployments/lib:app_engine_lib",
        "//loaner/deployments/lib:auth_lib",
        "//loaner/deployments/lib:common_lib",
        "//loaner/deployments/lib:datastore_lib",
        "//loaner/deployments/lib:directory_lib",
        "//loaner/deployments/lib:menu_lib",
        "//loaner/deployments/lib:storage_lib",
        "//loaner/deployments/lib:utils_lib",
        "@absl_archive//absl:app",
        "@absl_archive//absl/flags",
        "@absl_archive//absl/logging",
        "@six_archive//:six",
    ],
)

#########
# Tests #
#########

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

py_test(
    name = "gng_impl_test",
    size = "small",
    srcs = [
        "gng_impl_test.py",
    ],
    deps = [
        ":gng_impl_lib",
        "//loaner/deployments/lib:app_constants_lib",
        "//loaner/deployments/lib:auth_lib",
        "//loaner/deployments/lib:common_lib",
        "//loaner/deployments/lib:storage_lib",
        "//loaner/deployments/lib:utils_lib",
        "@absl_archive//absl/logging",
        "@absl_archive//absl/testing:absltest",
        "@absl_archive//absl/testing:flagsaver",
        "@absl_archive//absl/testing:parameterized",
        "@freezegun_archive//:freezegun",
        "@gcloud_auth_archive//:gcloud_auth",
        "@mock_archive//:mock",
        "@pyfakefs_archive//:pyfakefs",
        "@six_archive//:six",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":deploy_impl_test",
        ":gng_impl_test",
        "//loaner/deployments/lib:all_tests",
    ],
)
