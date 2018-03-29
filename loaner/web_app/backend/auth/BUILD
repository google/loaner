# Description:
#   BUILD file for //loaner/web_app/backend/auth.

package(
    default_visibility = [
        "//loaner:internal",
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
    name = "auth",
    deps = [
        ":permissions",
    ],
)

loaner_appengine_library(
    name = "permissions",
    srcs = [
        "permissions.py",
    ],
    deps = [
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/lib:user",
        "//loaner/web_app/backend/models:user_model",
        "@endpoints_archive//:endpoints",
        "@enum_archive//:enum",
    ],
)

# ==============================================================================
# Tests
# ==============================================================================

loaner_appengine_test(
    name = "permissions_test",
    srcs = [
        "permissions_test.py",
    ],
    deps = [
        ":permissions",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/models:user_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@endpoints_archive//:endpoints",
        "@mock_archive//:mock",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":permissions_test",
    ],
)
