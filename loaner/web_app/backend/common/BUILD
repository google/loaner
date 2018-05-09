# Description:
#   BUILD file for //loaner/web_app/backend/common.

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
