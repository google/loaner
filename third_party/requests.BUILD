# Description:
#   BUILD file for @requests_archive//:requests.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "requests",
    srcs = glob(["requests/**"]),
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@certifi_archive//:certifi",
        "@chardet_archive//:chardet",
        "@idna_archive//:idna",
        "@urllib3_archive//:urllib3",
    ],
)
