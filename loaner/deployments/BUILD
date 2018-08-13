# Description:
#   BUILD file for //loaner/deployments.

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
        ":deploy_impl_test",
        "//loaner/deployments/lib:all_tests",
    ],
)
