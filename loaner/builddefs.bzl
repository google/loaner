"""Custom App Engine build rules for the Grab n Go Loaner Application."""

load(
    "@io_bazel_rules_appengine//appengine:py_appengine.bzl",
    "py_appengine_library",
    "py_appengine_test",
    _py_appengine_binary = "py_appengine_binary",
)

py_appengine_binary = _py_appengine_binary

def loaner_appengine_library(name, srcs = None, deps = [], data = [], testonly = 0):
    """Custom App Engine library for the Grab n Go Loaner Application."""
    py_appengine_library(
        name = name,
        srcs = srcs,
        deps = deps,
        data = data,
        testonly = testonly,
    )

def loaner_appengine_test(name, srcs, deps = [], data = [], size = "medium"):
    """Custom App Engine test for the Grab n Go Loaner Application."""
    py_appengine_test(
        name = name,
        srcs = srcs,
        deps = deps,
        data = data,
        size = size,
        libraries = {
            "jinja2": "2.6",
            "protorpc": "1.0",
            "webapp2": "2.5.2",
            "yaml": "3.10",
        },
    )
