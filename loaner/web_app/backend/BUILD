# Description:
#   BUILD file for //loaner/web_app/backend.

package(
    default_visibility = [
        "//loaner:__subpackages__",
    ],
)

load(
    "//loaner:builddefs.bzl",
    "loaner_appengine_library",
)

# ==============================================================================
# Libraries
# ==============================================================================

loaner_appengine_library(
    name = "backend",
    deps = [
        "//loaner/web_app/backend/actions",
        "//loaner/web_app/backend/api",
        "//loaner/web_app/backend/clients",
        "//loaner/web_app/backend/common",
        "//loaner/web_app/backend/handlers",
        "//loaner/web_app/backend/lib",
        "//loaner/web_app/backend/models",
    ],
)

# ==============================================================================
# Tests
# ==============================================================================

test_suite(
    name = "all_tests",
    tests = [
        "//loaner/web_app/backend/actions:all_tests",
        "//loaner/web_app/backend/api:all_tests",
        "//loaner/web_app/backend/clients:all_tests",
        "//loaner/web_app/backend/handlers:all_tests",
        "//loaner/web_app/backend/lib:all_tests",
        "//loaner/web_app/backend/models:all_tests",
        "//loaner/web_app/backend/testing:all_tests",
    ],
)
