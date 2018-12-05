# Description:
#   BUILD file for //loaner/web_app/backend/models.

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
    name = "models",
    deps = [
        ":base_model",
        ":bigquery_row_model",
        ":bootstrap_status_model",
        ":config_model",
        ":device_model",
        ":event_models",
        ":shelf_model",
        ":survey_models",
        ":tag_model",
        ":template_model",
        ":user_model",
    ],
)

loaner_appengine_library(
    name = "base_model",
    srcs = [
        "base_model.py",
    ],
    deps = [
        "//loaner/web_app/backend/lib:utils",
    ],
)

loaner_appengine_library(
    name = "bigquery_row_model",
    srcs = [
        "bigquery_row_model.py",
    ],
    deps = [
        ":base_model",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/clients:bigquery",
        "@absl_archive//absl/logging",
    ],
)

loaner_appengine_library(
    name = "bootstrap_status_model",
    srcs = [
        "bootstrap_status_model.py",
    ],
)

loaner_appengine_library(
    name = "config_model",
    srcs = [
        "config_model.py",
    ],
    deps = [
        "//loaner/web_app/backend/lib:utils",
    ],
)

loaner_appengine_library(
    name = "device_model",
    srcs = [
        "device_model.py",
    ],
    deps = [
        ":base_model",
        ":config_model",
        ":user_model",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/api:permissions",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/lib:events",
        "//loaner/web_app/backend/lib:user",
        "@absl_archive//absl/logging",
    ],
)

loaner_appengine_library(
    name = "event_models",
    srcs = [
        "event_models.py",
    ],
    deps = [
        "@absl_archive//absl/logging",
    ],
)

loaner_appengine_library(
    name = "shelf_model",
    srcs = [
        "shelf_model.py",
    ],
    deps = [
        ":base_model",
        ":config_model",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/lib:events",
        "@absl_archive//absl/logging",
    ],
)

loaner_appengine_library(
    name = "survey_models",
    srcs = [
        "survey_models.py",
    ],
    deps = [
        ":base_model",
        ":config_model",
        "//loaner/web_app:constants",
    ],
)

loaner_appengine_library(
    name = "tag_model",
    srcs = [
        "tag_model.py",
    ],
    deps = [
        ":base_model",
        "//loaner/web_app/backend/lib:api_utils",
    ],
)

loaner_appengine_library(
    name = "template_model",
    srcs = [
        "template_model.py",
    ],
)

loaner_appengine_library(
    name = "user_model",
    srcs = [
        "user_model.py",
    ],
    deps = [
        "//loaner/web_app/backend/api:permissions",
    ],
)

# ==============================================================================
# Tests
# ==============================================================================

loaner_appengine_test(
    name = "base_model_test",
    srcs = [
        "base_model_test.py",
    ],
    deps = [
        ":base_model",
        ":shelf_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "bigquery_row_model_test",
    srcs = [
        "bigquery_row_model_test.py",
    ],
    deps = [
        ":bigquery_row_model",
        ":device_model",
        ":shelf_model",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/clients:bigquery",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@freezegun_archive//:freezegun",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "bootstrap_status_model_test",
    srcs = [
        "bootstrap_status_model_test.py",
    ],
    deps = [
        ":bootstrap_status_model",
        "//loaner/web_app/backend/testing:loanertest",
    ],
)

loaner_appengine_test(
    name = "config_model_test",
    srcs = [
        "config_model_test.py",
    ],
    deps = [
        ":config_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:absltest",
        "@absl_archive//absl/testing:parameterized",
        "@pyfakefs_archive//:pyfakefs",
    ],
)

loaner_appengine_test(
    name = "device_model_test",
    srcs = [
        "device_model_test.py",
    ],
    deps = [
        ":config_model",
        ":device_model",
        ":shelf_model",
        ":user_model",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/lib:events",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@freezegun_archive//:freezegun",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "event_models_test",
    srcs = [
        "event_models_test.py",
    ],
    deps = [
        ":device_model",
        ":event_models",
        ":shelf_model",
        "//loaner/web_app/backend/clients:directory",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/logging",
    ],
)

loaner_appengine_test(
    name = "shelf_model_test",
    srcs = [
        "shelf_model_test.py",
    ],
    deps = [
        ":config_model",
        ":shelf_model",
        "//loaner/web_app:constants",
        "//loaner/web_app/backend/lib:events",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@freezegun_archive//:freezegun",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "survey_models_test",
    srcs = [
        "survey_models_test.py",
    ],
    deps = [
        ":survey_models",
        "//loaner/web_app/backend/testing:loanertest",
    ],
)

loaner_appengine_test(
    name = "tag_model_test",
    srcs = [
        "tag_model_test.py",
    ],
    deps = [
        ":base_model",
        ":tag_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@absl_archive//absl/testing:parameterized",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "template_model_test",
    srcs = [
        "template_model_test.py",
    ],
    deps = [
        ":template_model",
        "//loaner/web_app/backend/testing:loanertest",
        "@mock_archive//:mock",
    ],
)

loaner_appengine_test(
    name = "user_model_test",
    srcs = [
        "user_model_test.py",
    ],
    deps = [
        ":user_model",
        "//loaner/web_app/backend/api:permissions",
        "//loaner/web_app/backend/testing:loanertest",
    ],
)

test_suite(
    name = "all_tests",
    tests = [
        ":base_model_test",
        ":bigquery_row_model_test",
        ":bootstrap_status_model_test",
        ":config_model_test",
        ":device_model_test",
        ":event_models_test",
        ":shelf_model_test",
        ":survey_models_test",
        ":tag_model_test",
        ":template_model_test",
        ":user_model_test",
    ],
)
