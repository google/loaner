# Description:
#   BUILD file for @pyjwkest_archive//:jwkest.
load("@pip_deps//:requirements.bzl", "requirement")

licenses(["notice"])  # Apache v2.0

py_library(
    name = "jwkest",
    srcs = glob(["jwkest/*.py"]),
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        requirement("pycrypto"),
        "@requests_archive//:requests",
        "@six_archive//:six",
    ],
)
