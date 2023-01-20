from objectives.Objectives import Objectives
from objectives.violation_number.oracles import RecordAnalyzer


def measure_objectives_individually(scenario):
    violation_results = measure_violation_number(scenario)
    code_coverage = measure_code_coverage()
    execution_time = measure_execution_time()
    objectives = Objectives(violation_results, code_coverage, execution_time)
    return objectives


def measure_code_coverage():
    return 1


def measure_execution_time():
    return 1


def measure_violation_number(scenario):
    ra = RecordAnalyzer(scenario.record_path)
    results = ra.analyze()
    if len(results) > 0:
        print(f"  Record Path: {scenario.record_path}")
        print(f"    Violation Results: {results}")
    return results


def measure_violation_number_by_path(record_path):
    ra = RecordAnalyzer(record_path)
    results = ra.analyze()
    if len(results) > 0:
        print(f"  Record Path: {record_path}")
        print(f"    Violation Results: {results}")
    return results