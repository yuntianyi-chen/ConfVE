from config import APOLLO_ROOT, MAX_RECORD_TIME
from objectives.violation_number.oracles import RecordAnalyzer

def measure_objectives_individually(scenario):
    record_path = f"{APOLLO_ROOT}/records/{scenario.record_name}.00000"
    violation_number = measure_violation_number(record_path)
    # replay_scenario(record_path)
    code_coverage = measure_code_coverage()
    execution_time = measure_execution_time()
    return violation_number, code_coverage, execution_time


def measure_code_coverage():
    return 1


def measure_execution_time():
    return 1


def measure_violation_number(record_path):
    ra = RecordAnalyzer(record_path)
    results = ra.analyze()
    print(f"     Violation Results: {results}")
    return len(results)
