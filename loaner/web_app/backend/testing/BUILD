# Description:
#   BUILD file for //loaner/web_app/backend/testing.

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
    name = "handlertest",
    testonly = 1,
    srcs = [
        "handlertest.py",
    ],
    deps = [
        ":loanertest",
        "//loaner/web_app:main",
        "@webtest_archive//:webtest",
    ],
)

loaner_appengine_library(
    name = "loanertest",
    testonly = 1,
    srcs = [
        "loanertest.py",
    ],
    deps = [
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/api:auth",
        "//loaner/web_app/backend/lib:action_loader",
        "//loaner/web_app/backend/lib:events",
        "//loaner/web_app/backend/models:user_model",
        "@absl_archive//absl/testing:absltest",
        "@endpoints_archive//:endpoints",
        "@mock_archive//:mock",
    ],
)

# ==============================================================================
# Tests
# ==============================================================================

loaner_appengine_test(
    name = "handlertest_test",
    srcs = [
        "handlertest_test.py",
    ],
    deps = [
        ":handlertest",
        "//loaner/web_app/backend/clients:directory",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "loanertest_test",
    srcs = [
        "loanertest_test.py",
    ],
    deps = [
        ":loanertest",
        "//loaner/web_app/backend/lib:action_loader",
        "@endpoints_archive//:endpoints",
        "@mock_archive//:mock",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":handlertest_test",
        ":loanertest_test",
    ],
)
