# Description:
#   BUILD file for @endpoints_archive//:endpoints.

licenses(["notice"])  # Apache v2.0

py_library(
    name = "endpoints",
    srcs = glob(
        include = ["endpoints/*.py"],
        exclude = ["endpoints/test/**"],
    ),
    data = ["endpoints/proxy.html"],
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "@attr_archive//:attr",
        "@google_endpoints_api_management_archive//:endpoints_management",
        "@semver_archive//:semver",
        "@setup_tools_archive//:setup_tools",
    ],
)
