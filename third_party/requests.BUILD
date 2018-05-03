# Description:
#   BUILD file for @requests_archive//:requests.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "requests",
    srcs = glob(["requests/**"]),
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@chardet_archive//:chardet",
        "@idna_archive//:idna",
        "@urllib3_archive//:urllib3",
        "@certifi_archive//:certifi",
    ],
)
