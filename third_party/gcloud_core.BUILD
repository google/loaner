# Description:
#   BUILD file for @gcloud_core_archive//:gcloud_core.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "gcloud_core",
    srcs = glob(["google/**"]),
    # Include the .egg-info in order to make the package discoverable to
    # python. This is necessary because the library dynamically sets its
    # '__version__' property from the detected package installation's version.
    data = glob(["*.egg-info/**"]),
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@gapi_protos_archive//:gapi_protos",
        "@gcloud_auth_archive//:gcloud_auth",
        "@google_auth_httplib2_archive//:google_auth_httplib2",
        "@httplib2_archive//:httplib2",
        "@protobuf_archive//:protobuf",
        "@six_archive//:six",
    ],
)
