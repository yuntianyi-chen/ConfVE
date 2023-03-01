from config import CURRENT_CONFIG_FILE_PATH, CONFIG_FILE_NAME


class ApolloTranslator:
    @staticmethod
    def save2file(output_string_list):
        with open(CURRENT_CONFIG_FILE_PATH, 'w') as processed_config_file:
            processed_config_file.writelines(output_string_list)

    @staticmethod
    def option_obj_translator(option_obj_list):
        output_string_list = list()
        last_position_list = None
        indent_length_rate = 0
        for option_item in option_obj_list:
            position_list = option_item.position
            layer_list = option_item.layers
            if not last_position_list:
                for layer in layer_list:
                    output_string_list.append("  " * indent_length_rate + layer + ": {\n")
                    indent_length_rate += 1
                output_string_list.append(
                    "  " * indent_length_rate + option_item.option_key + ": " + option_item.option_value + "\n")
            else:
                if len(position_list) >= len(last_position_list):
                    long_position_list = position_list
                    short_position_list = last_position_list
                else:
                    long_position_list = last_position_list
                    short_position_list = position_list
                first_diff_position = None
                for i in range(len(short_position_list)):
                    if short_position_list[i] != long_position_list[i]:
                        first_diff_position = i
                        break
                pop_count = len(last_position_list) - first_diff_position - 1
                push_count = len(position_list) - first_diff_position - 1

                for i in range(pop_count):
                    indent_length_rate -= 1
                    output_string_list.append("  " * indent_length_rate + "}\n")
                for i in range(push_count):
                    output_string_list.append("  " * indent_length_rate + layer_list[first_diff_position + i] + ": {\n")
                    indent_length_rate += 1
                output_string_list.append(
                    "  " * indent_length_rate + option_item.option_key + ": " + option_item.option_value + "\n")
            last_position_list = position_list
        pop_count = len(last_position_list) - 1
        for i in range(pop_count):
            indent_length_rate -= 1
            output_string_list.append("  " * indent_length_rate + "}\n")

        if CONFIG_FILE_NAME == "planning_config.pb.txt":
            output_string_list.insert(17, "  planner_public_road_config: {\n")
            output_string_list.insert(18, "  }\n")
            output_string_list.insert(14, "# NO_LEARNING / E2E / HYBRID / RL_TEST / E2E_TEST / HYBRID_TEST")
        return output_string_list

    @staticmethod
    def option_tuple_translator(option_tuple_list):
        output_string_list = list()
        last_position_list = None
        indent_length_rate = 0
        for item in option_tuple_list:
            position_list = item[-2]
            layer_list = item[-1]
            if not last_position_list:
                for layer in layer_list:
                    output_string_list.append("  " * indent_length_rate + layer + ": {\n")
                    indent_length_rate += 1
                output_string_list.append("  " * indent_length_rate + item[1] + ": " + item[2] + "\n")
            else:
                if len(position_list) >= len(last_position_list):
                    long_position_list = position_list
                    short_position_list = last_position_list
                else:
                    long_position_list = last_position_list
                    short_position_list = position_list
                first_diff_position = None
                for i in range(len(short_position_list)):
                    if short_position_list[i] != long_position_list[i]:
                        first_diff_position = i
                        break
                pop_count = len(last_position_list) - first_diff_position - 1
                push_count = len(position_list) - first_diff_position - 1

                for i in range(pop_count):
                    indent_length_rate -= 1
                    output_string_list.append("  " * indent_length_rate + "}\n")
                for i in range(push_count):
                    output_string_list.append("  " * indent_length_rate + layer_list[first_diff_position + i] + ": {\n")
                    indent_length_rate += 1
                output_string_list.append("  " * indent_length_rate + item[1] + ": " + item[2] + "\n")
            last_position_list = position_list
        pop_count = len(last_position_list) - 1
        for i in range(pop_count):
            indent_length_rate -= 1
            output_string_list.append("  " * indent_length_rate + "}\n")
        return output_string_list
