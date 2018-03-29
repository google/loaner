# Description:
#   BUILD file for @gcloud_auth_archive//:gcloud_auth.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "gcloud_auth",
    srcs = glob(["google/**"]),
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@cachetools_archive//:cachetools",
        "@pyasn1_archive//:pyasn1",
        "@pyasn1_modules_archive//:pyasn1_modules",
        "@rsa_archive//:rsa",
        "@six_archive//:six",
    ],
)
