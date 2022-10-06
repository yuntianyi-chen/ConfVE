load("@rules_python//python:defs.bzl", "py_binary")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "run_automation",
    srcs = ["run_automation.py"],
    deps = [
        "//cyber/python/cyber_py3:cyber",
        "//cyber/python/cyber_py3:cyber_time",
        "//modules/routing/proto:routing_py_pb2",
        "//apollo_v7_testing/auxiliary/record:read_record",
        "//apollo_v7_testing/auxiliary/routing:send_routing_request",
        "//apollo_v7_testing/grading_metrics:acceleration",
        "//apollo_v7_testing/grading_metrics:collision",
        "//apollo_v7_testing/grading_metrics:speeding",
        "//apollo_v7_testing/auxiliary/map:map_tools",
    ],
)
