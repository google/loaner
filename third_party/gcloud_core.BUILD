# Description:
#   BUILD file for @gcloud_core_archive//:gcloud_core.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "gcloud_core",
    srcs = glob(["google/**"]),
    srcs_version = "PY2AND3",
    # Include the .egg-info in order to make the package discoverable to
    # python. This is necessary because the library dynamically sets its
    # '__version__' property from the detected package installation's version.
    data = glob(["*.egg-info/**"]),
    visibility = ["//visibility:public"],
    deps = [
        "@httplib2_archive//:httplib2",
        "@gapi_protos_archive//:gapi_protos",
        "@protobuf_archive//:protobuf",
        "@gcloud_auth_archive//:gcloud_auth",
        "@google_auth_httplib2_archive//:google_auth_httplib2",
        "@six_archive//:six",
    ],
)
