# Description:
#   BUILD file for @dateutil_archive//:dateutil.

licenses(["notice"])  # BSD

py_library(
    name = "dateutil",
    srcs = glob(["**/*.py"]),
    data = ["PKG-INFO"],
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@six_archive//:six",
    ],
)
