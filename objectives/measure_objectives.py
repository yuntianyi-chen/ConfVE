import shutil
from config import MAGGIE_ROOT, APOLLO_ROOT, RECORDS_DIR
from objectives.violation_number.oracles import RecordAnalyzer
# from scenario_handling.run_scenario import replay_scenario


def measure_objectives(scenario_list):
    shutil.rmtree(f"{MAGGIE_ROOT}/data/records")
    shutil.copytree(f"{APOLLO_ROOT}/records", f"{MAGGIE_ROOT}/data/records")
    for scenario in scenario_list:
        record_path = f"{RECORDS_DIR}/{scenario.record_name}.00000"
        violation_number = measure_violation_number(record_path)
        # replay_scenario(record_path)
        code_coverage = measure_code_coverage()
        execution_time = measure_execution_time()
    return violation_number, code_coverage, execution_time

def measure_objectives_individually(scenario):
    # violation_number, code_coverage, execution_time = None, None, None
    # shutil.rmtree(f"{MAGGIE_ROOT}/data/records")
    # shutil.copytree(f"{APOLLO_ROOT}/records", f"{MAGGIE_ROOT}/data/records")
    # for scenario in scenario_list:
    record_path = f"{APOLLO_ROOT}/records/{scenario.record_name}.00000"
    violation_number = measure_violation_number(record_path)
    # replay_scenario(record_path)
    code_coverage = measure_code_coverage()
    execution_time = measure_execution_time()
    return violation_number, code_coverage, execution_time


def measure_code_coverage():
    return


def measure_execution_time():
    return


def measure_violation_number(record_path):
    ra = RecordAnalyzer(record_path)
    results = ra.analyze()
    print(f"     Violation Results: {results}")
    return results
