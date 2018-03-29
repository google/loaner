# Description:
#   BUILD file for @pyasn1_modules_archive//:pyasn1_modules.

licenses(["notice"])  # BSD

py_library(
    name = "pyasn1_modules",
    srcs = glob(["pyasn1_modules/**"]),
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@pyasn1_archive//:pyasn1",
    ],
)
