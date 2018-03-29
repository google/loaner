# Description:
#   BUILD file for @fasteners_archive//:fasteners.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "fasteners",
    srcs = glob(["fasteners/*.py"]),
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@monotonic_archive//:monotonic",
        "@six_archive//:six",
    ],
)
