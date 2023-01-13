from objectives.violation_number.oracles import RecordAnalyzer


def measure_objectives_individually(scenario):
    violation_results = measure_violation_number(scenario.record_path)
    code_coverage = measure_code_coverage()
    execution_time = measure_execution_time()
    return violation_results, code_coverage, execution_time


def measure_code_coverage():
    return 1


def measure_execution_time():
    return 1


def measure_violation_number(record_path):
    ra = RecordAnalyzer(record_path)
    results = ra.analyze()
    print(f"      Violation Results: {results}")
    if len(results) > 0:
        print(f"          Record Path: {record_path}")
    return results



