# Description:
#   BUILD file for @pyjwkest_archive//:jwkest.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "jwkest",
    srcs = glob(["jwkest/*.py"]),
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@requests_archive//:requests",
        "@six_archive//:six",
    ],
)
