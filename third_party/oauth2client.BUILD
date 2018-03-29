# Description:
#   BUILD file for @oauth2client_archive//:oauth2client.

licenses(["notice"])  # Apache2

py_library(
    name = "oauth2client",
    srcs = glob(["oauth2client/**"]),
    visibility = ["//visibility:public"],
    deps = [
        "@fasteners_archive//:fasteners",
        "@httplib2_archive//:httplib2",
        "@pyasn1_archive//:pyasn1",
        "@pyasn1_modules_archive//:pyasn1_modules",
        "@rsa_archive//:rsa",
        "@six_archive//:six",
    ],
)
