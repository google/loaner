# Description:
#   BUILD file for //loaner/web_app/backend/common.

load(
    "//loaner:builddefs.bzl",
    "loaner_appengine_library",
    "loaner_appengine_test",
)

package(
    default_visibility = [
        "//loaner:__subpackages__",
    ],
)

# ==============================================================================
# Libraries
# ==============================================================================

loaner_appengine_library(
    name = "common",
    deps = [
        ":google_cloud_lib_fixer",
    ],
)

loaner_appengine_library(
    name = "fake_monotonic",
    srcs = [
        "fake_monotonic.py",
    ],
)

loaner_appengine_library(
    name = "google_cloud_lib_fixer",
    srcs = [
        "google_cloud_lib_fixer.py",
    ],
    deps = [
        ":fake_monotonic",
        "@gcloud_auth_archive//:gcloud_auth",
        "@requests_toolbelt_archive//:requests_toolbelt",
    ],
)

# PY3 Migration Tests
# =========================================================

loaner_appengine_test(
    name = "fake_monotonic_test",
    srcs = [
        "fake_monotonic_test.py",
    ],
    deps = [
        ":fake_monotonic",
        "@absl_archive//absl/testing:absltest",
    ],
)

loaner_appengine_test(
    name = "google_cloud_lib_fixer_test",
    srcs = [
        "google_cloud_lib_fixer_test.py",
    ],
    deps = [
        ":google_cloud_lib_fixer",
        "@absl_archive//absl/testing:absltest",
        "@mock_archive//:mock",
    ],
)
