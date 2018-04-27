# Description:
#   BUILD file for @google_endpoints_api_management_archive//:endpoints_management.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "endpoints_management",
    srcs = glob(
        include = ["**/*.py"],
        exclude = ["test/**"],
    ),
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@cachetools_archive//:cachetools",
        "@dogpile_cache_archive//:dogpile",
        "@enum_archive//:enum",
        "@google_apitools_archive//:apitools",
        "@oauth2client_archive//:oauth2client",
        "@ply_archive//:ply",
        "@pyjwkest_archive//:jwkest",
        "@pylru_archive//:pylru",
        "@requests_archive//:requests",
        "@strict_rfc3339_archive//:strict_rfc3339",
        "@urllib3_archive//:urllib3",
    ],
)
