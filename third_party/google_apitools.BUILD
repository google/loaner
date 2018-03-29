# Description:
#   BUILD file for @google_apitools_archive//:apitools.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "apitools",
    srcs = glob(["**/*.py"]),
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@fasteners_archive//:fasteners",
        "@httplib2_archive//:httplib2",
        "@oauth2client_archive//:oauth2client",
        "@six_archive//:six",
    ],
)
