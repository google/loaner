# Description:
#   BUILD file for @gcloud_bigquery_archive//:gcloud_bigquery.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "gcloud_bigquery",
    srcs = glob(["google/**"]),
    srcs_version = "PY2AND3",
    # Include the .egg-info in order to make the package discoverable to
    # python. This is necessary because the library dynamically sets its
    # '__version__' property from the detected package installation's version.
    data = glob(["*.egg-info/**"]),
    visibility = ["//visibility:public"],
    deps = [
        "@gcloud_core_archive//:gcloud_core",
        "@gcloud_auth_archive//:gcloud_auth",
        "@gcloud_resumable_media_archive//:gcloud_resumable_media",
        "@requests_archive//:requests",
    ],
)
