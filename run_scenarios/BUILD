load("@rules_python//python:defs.bzl", "py_binary")

#package(default_visibility = ["//visibility:public"])


# Add your own section here
py_binary(
    name = "creating_scenarios",
    srcs = ["creating_scenarios.py"],
    deps = [
        "//cyber/python/cyber_py3:cyber",
		"//apollo_v7_testing/auxiliary/map:map_tools",
    ],
)

# py_binary(
#     name = "main",
#     srcs = ["main.py"],
#     deps = [
#         "//cyber/python/cyber_py3:cyber",
#         "//apollo_v7_testing/AV_Config_Testing/objectives/violation_number/oracles:__init__"
#     ],
# )

py_binary(
    name = "toggle_sim_control",
    srcs = ["toggle_sim_control.py"],
    deps = [
    ],
)

py_binary(
    name = "obstacle_generator",
    srcs = ["obstacle_generator.py"],
    deps = [
		"//apollo_v7_testing/auxiliary/map:map_tools",
    ],
)
