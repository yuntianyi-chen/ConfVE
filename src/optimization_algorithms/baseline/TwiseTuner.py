from config_file_handler.option_handling import tune_one_value


class TwiseTuner:
    def __init__(self, config_file_obj, range_analyzer, T):
        self.config_file_obj = config_file_obj
        self.range_analyzer = range_analyzer
        self.T = T

    def decide_positions(self):
        position_list = []
        return position_list

    def tune_individual(self, individual):
        position_list = self.decide_positions()
        for position in position_list:
            tune_one_value(individual, self.config_file_obj, self.range_analyzer, position)
        return individual
