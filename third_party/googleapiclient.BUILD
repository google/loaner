# Description:
#   BUILD file for @googleapiclient//:googleapiclient.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "googleapiclient",
    srcs = glob(["googleapiclient/**"]),
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@oauth2client_archive//:oauth2client",
        "@six_archive//:six",
        "@uritemplate_archive//:uritemplate",
    ],
)
