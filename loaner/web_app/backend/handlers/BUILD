# Description:
#   BUILD file for //loaner/web_app/backend/handlers.

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
    name = "handlers",
    deps = [
        ":frontend",
        ":maintenance",
        "//loaner/web_app/backend/handlers/cron",
        "//loaner/web_app/backend/handlers/task",
    ],
)

loaner_appengine_library(
    name = "frontend",
    srcs = [
        "frontend.py",
    ],
    deps = [
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/lib:bootstrap",
        "//loaner/web_app/backend/lib:sync_users",
        "@absl_archive//absl/logging",
    ],
)

loaner_appengine_library(
    name = "maintenance",
    srcs = [
        "maintenance.py",
    ],
    data = [
        "//loaner/web_app/backend/static_content:maintenance",
    ],
    deps = [
        "//loaner/web_app:constants",
    ],
)

# ==============================================================================
# Tests
# ==============================================================================

loaner_appengine_test(
    name = "frontend_test",
    srcs = [
        "frontend_test.py",
    ],
    deps = [
        ":frontend",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/lib:bootstrap",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/testing:handlertest",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "maintenance_test",
    srcs = [
        "maintenance_test.py",
    ],
    deps = [
        ":maintenance",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/testing:handlertest",
        "@mock_archive//:mock",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":frontend_test",
        ":maintenance_test",
        "//loaner/web_app/backend/handlers/cron:all_tests",
        "//loaner/web_app/backend/handlers/task:all_tests",
    ],
)
