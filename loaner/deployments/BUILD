# Description:
#   BUILD file for //loaner/oss/deployments.

package(
    default_visibility = [
        "//loaner:__subpackages__",
    ],
)

py_binary(
    name = "deploy_impl",
    srcs = [
        "deploy_impl.py",
    ],
    deps = [
        ":deploy_impl_lib",
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
    ],
)
