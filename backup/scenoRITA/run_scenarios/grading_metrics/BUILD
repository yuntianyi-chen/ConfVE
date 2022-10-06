load("@rules_python//python:defs.bzl", "py_binary")

package(default_visibility = ["//visibility:public"])

py_binary(
	name = "collision",
	srcs = ["collision.py"],
	deps = [
		"//apollo_v7_testing/auxiliary/record:read_record",
		"//modules/tools/perception:replay_perception",
		"//apollo_v7_testing/auxiliary/oracles:speeding",
	],
)

py_binary(
	name = "acceleration",
	srcs = ["acceleration.py"],
	deps = [
		"//apollo_v7_testing/auxiliary/record:read_record",
		"//apollo_v7_testing/grading_metrics:speeding",
		"//apollo_v7_testing/auxiliary/oracles:speeding",
	],
)

py_binary(
	name = "speeding",
	srcs = ["speeding.py"],
	deps = [
		"//apollo_v7_testing/auxiliary/record:read_record",
		"//apollo_v7_testing/auxiliary/map:map_tools",
		"//apollo_v7_testing/grading_metrics:collision",
		"//apollo_v7_testing/auxiliary/oracles:speeding",
	],
)

py_binary(
	name = "run_oracles",
	srcs = ["run_oracles.py"],
	deps = [
		"//apollo_v7_testing/grading_metrics:acceleration",
		"//apollo_v7_testing/grading_metrics:collision",
		"//apollo_v7_testing/grading_metrics:off_road",
		"//apollo_v7_testing/grading_metrics:speeding",
	],
)
