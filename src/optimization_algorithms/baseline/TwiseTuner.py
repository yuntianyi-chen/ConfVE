class TwiseTuner:
    def __init__(self, config_file_obj, range_analyzer, T):
        self.config_file_obj = config_file_obj
        self.range_analyzer = range_analyzer
        self.T = T

    def decide_positions(self):
        position_list = []
        return position_list

    def tune_individual(self, individual, range_analyzer):
        position_list = self.decide_positions()
        for position in position_list:
            range_analyzer.tune_one_value(individual, self.config_file_obj, position)
        return individual
