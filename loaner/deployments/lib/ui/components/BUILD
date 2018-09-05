# Description:
#   BUILD file for //loaner/deployments/lib/ui/components.

package(
    default_visibility = [
        "//loaner:__subpackages__",
    ],
)

#############
# Libraries #
#############

py_library(
    name = "text_lib",
    srcs = [
        "text.py",
    ],
    deps = [
        "@urwid_archive//:urwid",
    ],
)

#########
# Tests #
#########

py_test(
    name = "text_test",
    size = "small",
    srcs = [
        "text_test.py",
    ],
    deps = [
        ":text_lib",
        "@absl_archive//absl/testing:absltest",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":text_test",
    ],
)
