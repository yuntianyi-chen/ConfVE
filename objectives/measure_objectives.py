from datetime import date
from config import APOLLO_ROOT, MAX_RECORD_TIME, MAGGIE_ROOT
from environment.container_settings import init_settings
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
    # return MAX_RECORD_TIME


# Most important
def measure_violation_number(record_path):
    ra = RecordAnalyzer(record_path)
    results = ra.analyze()
    print(f"      Violation Results: {results}")

    if len(results) > 0:
        print(f"      Record Path: {record_path}")
        with open(f"{MAGGIE_ROOT}/data/violation_results/violation_results_{date.today()}.txt", "a") as f:
            f.write(f"Violation Results: {results}\n")
            f.write(f"  {record_path}\n")

    return len(results)


if __name__ == '__main__':
    init_settings()
    record_path = f"/home/cloudsky/Research/Apollo/Backup/DoppelTest_records/records_8.26/records/Generation_00074/Scenario_00003/yuqi_apollo_dev_ROUTE_3.Scenario_00003.00000"
    violation_number = 0
    for i in range(100):
        violation_number +=measure_violation_number(record_path)
    print(violation_number)