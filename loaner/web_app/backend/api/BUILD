# Description:
#   BUILD file for //loaner/web_app/backend/api.

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
    name = "api",
    deps = [
        ":auth",
        ":bootstrap_api",
        ":chrome_api",
        ":config_api",
        ":datastore_api",
        ":device_api",
        ":permissions",
        ":root_api",
        ":search_api",
        ":shelf_api",
        ":survey_api",
        ":tag_api",
        ":user_api",
    ],
)

loaner_appengine_library(
    name = "auth",
    srcs = [
        "auth.py",
    ],
    deps = [
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/lib:user",
        "//loaner/web_app/backend/models:user_model",
        "@absl_archive//absl/logging",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "bootstrap_api",
    srcs = [
        "bootstrap_api.py",
    ],
    deps = [
        ":auth",
        ":permissions",
        ":root_api",
        "//loaner/web_app/backend/api/messages:bootstrap_messages",
        "//loaner/web_app/backend/lib:bootstrap",
    ],
)

loaner_appengine_library(
    name = "chrome_api",
    srcs = [
        "chrome_api.py",
    ],
    deps = [
        ":auth",
        ":permissions",
        ":root_api",
        "//loaner/web_app/backend/api/messages:chrome_messages",
        "//loaner/web_app/backend/lib:user",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/models:device_model",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "config_api",
    srcs = [
        "config_api.py",
    ],
    deps = [
        ":auth",
        ":permissions",
        ":root_api",
        "//loaner/web_app/backend/api/messages:config_messages",
        "//loaner/web_app/backend/lib:utils",
        "//loaner/web_app/backend/models:config_model",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "datastore_api",
    srcs = [
        "datastore_api.py",
    ],
    deps = [
        ":auth",
        ":permissions",
        ":root_api",
        "//loaner/web_app/backend/api/messages:datastore_messages",
        "//loaner/web_app/backend/lib:datastore_yaml",
    ],
)

loaner_appengine_library(
    name = "device_api",
    srcs = [
        "device_api.py",
    ],
    deps = [
        ":auth",
        ":permissions",
        ":root_api",
        ":shelf_api",
        "//loaner/web_app/backend/api/messages:device_messages",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/lib:api_utils",
        "//loaner/web_app/backend/lib:search_utils",
        "//loaner/web_app/backend/lib:user",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:user_model",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "permissions",
    srcs = [
        "permissions.py",
    ],
    data = [
        "//loaner/web_app:permissions",
    ],
)

loaner_appengine_library(
    name = "root_api",
    srcs = [
        "root_api.py",
    ],
    deps = [
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/lib:xsrf",
        "@absl_archive//absl/logging",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "search_api",
    srcs = [
        "search_api.py",
    ],
    deps = [
        ":auth",
        ":permissions",
        ":root_api",
        "//loaner/web_app/backend/api/messages:search_messages",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:shelf_model",
    ],
)

loaner_appengine_library(
    name = "shelf_api",
    srcs = [
        "shelf_api.py",
    ],
    deps = [
        ":auth",
        ":permissions",
        ":root_api",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/api/messages:shelf_messages",
        "//loaner/web_app/backend/lib:api_utils",
        "//loaner/web_app/backend/lib:search_utils",
        "//loaner/web_app/backend/lib:user",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:shelf_model",
        "@absl_archive//absl/logging",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "survey_api",
    srcs = [
        "survey_api.py",
    ],
    deps = [
        ":auth",
        ":permissions",
        ":root_api",
        "//loaner/web_app/backend/api/messages:survey_messages",
        "//loaner/web_app/backend/lib:api_utils",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/models:survey_models",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "tag_api",
    srcs = [
        "tag_api.py",
    ],
    deps = [
        ":auth",
        ":permissions",
        ":root_api",
        "//loaner/web_app/backend/api/messages:tag_messages",
        "//loaner/web_app/backend/lib:api_utils",
        "//loaner/web_app/backend/lib:user",
        "//loaner/web_app/backend/models:tag_model",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_library(
    name = "user_api",
    srcs = [
        "user_api.py",
    ],
    deps = [
        ":auth",
        ":permissions",
        ":root_api",
        "//loaner/web_app/backend/api/messages:user_messages",
        "//loaner/web_app/backend/lib:user",
        "//loaner/web_app/backend/models:user_model",
    ],
)

# ==============================================================================
# Tests
# ==============================================================================

loaner_appengine_test(
    name = "auth_test",
    srcs = [
        "auth_test.py",
    ],
    deps = [
        ":auth",
        ":permissions",
        ":root_api",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/lib:xsrf",
        "//loaner/web_app/backend/models:user_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@endpoints_archive//:endpoints",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "bootstrap_api_test",
    srcs = [
        "bootstrap_api_test.py",
    ],
    deps = [
        ":bootstrap_api",
        "//loaner/web_app/backend/api/messages:bootstrap_messages",
        "//loaner/web_app/backend/testing:loanertest",
    ],
)

loaner_appengine_test(
    name = "chrome_api_test",
    srcs = [
        "chrome_api_test.py",
    ],
    deps = [
        ":chrome_api",
        "//loaner/web_app/backend/api/messages:chrome_messages",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@endpoints_archive//:endpoints",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "config_api_test",
    srcs = [
        "config_api_test.py",
    ],
    deps = [
        ":config_api",
        "//loaner/web_app/backend/api/messages:config_messages",
        "//loaner/web_app/backend/lib:utils",
        "//loaner/web_app/backend/models:config_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "datastore_api_test",
    srcs = [
        "datastore_api_test.py",
    ],
    deps = [
        ":datastore_api",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/api/messages:bootstrap_messages",
        "//loaner/web_app/backend/testing:loanertest",
    ],
)

loaner_appengine_test(
    name = "device_api_test",
    srcs = [
        "device_api_test.py",
    ],
    deps = [
        ":device_api",
        ":root_api",
        "//loaner/web_app/backend/api/messages:device_messages",
        "//loaner/web_app/backend/api/messages:shared_messages",
        "//loaner/web_app/backend/api/messages:shelf_messages",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/lib:api_utils",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@endpoints_archive//:endpoints",
    ],
)

loaner_appengine_test(
    name = "root_api_test",
    srcs = [
        "root_api_test.py",
    ],
    deps = [
        ":root_api",
        "//loaner/web_app/backend/lib:xsrf",
        "//loaner/web_app/backend/testing:loanertest",
        "@endpoints_archive//:endpoints",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "search_api_test",
    srcs = [
        "search_api_test.py",
    ],
    deps = [
        ":search_api",
        "//loaner/web_app/backend/api/messages:search_messages",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:shelf_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "shelf_api_test",
    srcs = [
        "shelf_api_test.py",
    ],
    deps = [
        ":root_api",
        ":shelf_api",
        "//loaner/web_app/backend/api/messages:shared_messages",
        "//loaner/web_app/backend/api/messages:shelf_messages",
        "//loaner/web_app/backend/models:device_model",
        "//loaner/web_app/backend/models:shelf_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@endpoints_archive//:endpoints",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "survey_api_test",
    srcs = [
        "survey_api_test.py",
    ],
    deps = [
        ":root_api",
        ":survey_api",
        "//loaner/web_app/backend/api/messages:survey_messages",
        "//loaner/web_app/backend/models:survey_models",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@endpoints_archive//:endpoints",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "tag_api_test",
    srcs = [
        "tag_api_test.py",
    ],
    deps = [
        ":tag_api",
        "//loaner/web_app/backend/api/messages:tag_messages",
        "//loaner/web_app/backend/models:tag_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@endpoints_archive//:endpoints",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "user_api_test",
    srcs = [
        "user_api_test.py",
    ],
    deps = [
        ":user_api",
        "//loaner/web_app/backend/api/messages:user_messages",
        "//loaner/web_app/backend/models:user_model",
        "//loaner/web_app/backend/testing:loanertest",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":auth_test",
        ":bootstrap_api_test",
        ":chrome_api_test",
        ":config_api_test",
        ":datastore_api_test",
        ":device_api_test",
        ":root_api_test",
        ":search_api_test",
        ":shelf_api_test",
        ":survey_api_test",
        ":tag_api_test",
        ":user_api_test",
    ],
)
