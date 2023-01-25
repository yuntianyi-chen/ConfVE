from copy import deepcopy
from config import FITNESS_MODE


class IndividualWithFitness:

    def __init__(self, value_list):
        self.value_list = value_list
        self.pre_value_list = []
        self.option_tuning_tracking_list = []
        self.reset_default()

    def configuration_reverting(self, do_reverting):
        if do_reverting:
            temp = deepcopy(self.value_list)
            self.value_list = deepcopy(self.pre_value_list)
            self.pre_value_list = temp
            self.option_tuning_tracking_list.pop()
            self.reset_default()

    def calculate_fitness(self):
        self.violation_number = self.accumulated_objectives[0]
        self.code_coverage = self.accumulated_objectives[1]
        self.execution_time = self.accumulated_objectives[2]

        if FITNESS_MODE == "emerge":
            self.fitness = self.violation_emerged
        else:
            self.fitness = self.violation_number * self.code_coverage * self.execution_time

    def update_accumulated_objectives(self, objectives):
        self.accumulated_objectives[0] += len(objectives.violation_results)
        self.accumulated_objectives[1] += objectives.code_coverage
        self.accumulated_objectives[2] += objectives.execution_time

        self.violation_results_list.append(objectives.violation_results)

    def update_allow_selection(self, contain_module_violation):
        self.allow_selection = not contain_module_violation

    def update_id(self, id):
        self.id = id

    def get_fitness(self):
        return self.fitness

    def reset_default(self):
        self.fitness = 0
        self.violation_number = 0
        self.code_coverage = 0
        self.execution_time = 0
        self.accumulated_objectives = [0, 0, 0]

        self.violation_emerged = 0

        self.violation_results_list = []

        self.violations_emerged_results = []
        self.violations_emerged_results_list = []

        self.allow_selection = True

    def update_violation_emerged_with_sid(self, violations_emerged_results, scenario):
        violations_emerged_results_with_sid = [(scenario.record_id, v) for v in violations_emerged_results]
        self.violations_emerged_results_list.append(violations_emerged_results_with_sid)
        self.violations_emerged_results += violations_emerged_results_with_sid
        self.violation_emerged += len(violations_emerged_results_with_sid)
