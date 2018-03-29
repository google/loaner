# Description:
#   BUILD file for @gapi_protos_archive//:gapi_protos.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "gapi_protos",
    srcs = glob(["google/**"]),
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@protobuf_archive//:protobuf",
    ],
)
