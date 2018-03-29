# Description:
#   BUILD file for @freezegun_archive//:freezegun.

licenses(["notice"])  # Apache 2.0

py_library(
    name = "freezegun",
    srcs = glob(["**/*.py"]),
    data = ["PKG-INFO"],
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@dateutil_archive//:dateutil",
        "@six_archive//:six",
    ],
)
