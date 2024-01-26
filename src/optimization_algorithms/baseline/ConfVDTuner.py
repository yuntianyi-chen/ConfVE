import random
# import itertools as it


class ConfVDTuner:
    id_list: list

    def __init__(self, config_file_obj, range_analyzer):
        # self.id_index = 0
        self.config_file_obj = config_file_obj
        # self.range_analyzer = range_analyzer
        # self.id_list = self.generate_id_list()

    # def decide_positions(self):
    #     position_tuple = self.id_list[self.id_index]
    #     self.id_index += 1
    #     return position_tuple


    def tune_individual(self, individual, range_analyzer):
        tuned_id = random.randint(0, self.config_file_obj.option_count - 1)
        # position_tuple = self.decide_positions()
        # for position in position_tuple:
        range_analyzer.tune_one_value(individual, self.config_file_obj, tuned_id)
        return individual

    # def generate_id_list(self):
    #     id_list = []
    #     for e in it.combinations(range(self.config_file_obj.option_count), self.T):
    #         id_list.append(e)
    #     random.shuffle(id_list)
    #     return id_list
