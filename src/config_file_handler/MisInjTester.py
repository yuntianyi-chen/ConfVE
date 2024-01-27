import random
import string

from config import OPT_MODE


class MisInjTester:
    def __init__(self):
        self.letters_list = [c for c in string.ascii_letters + string.digits]
        self.str_operator_func_list = [self.char_substitute,
                                       self.char_add,
                                       self.char_delete,
                                       self.convert_case,
                                       self.disorder,
                                       self.cut_out,
                                       self.repeat]
        self.number_operator_func_list = [self.generate_new_number
            # , self.change_digit_type
                                          ]

    def apply_one_operator(self, option_type, option_value, option_range):
        if option_type in ["float", "integer"]:
            generated_value = random.choice(self.number_operator_func_list)(option_type, option_value, option_range)
        elif option_type == "boolean":
            generated_value = "true" if option_value == "false" else "false"
        elif option_type == "e_number":
            exp = random.randint(option_range[0], option_range[1])
            forward = option_value.split("e")[0]
            generated_value = f"{forward}e{exp}"
        elif option_type == "string":
            if option_value in ["min", "max"]:
                generated_value = "min" if option_value == "max" else "min"
            elif option_value in ["yes", "no"]:
                generated_value = "yes" if option_value == "no" else "min"
            else:
                generated_value = random.choice(self.str_operator_func_list)(option_value)
        elif option_type == "enum":
            generated_value = random.choice(self.str_operator_func_list)(option_value)
        else:
            generated_value = option_value
        return str(generated_value)

    def char_substitute(self, value):
        random_position = random.randint(0, len(value) - 1)
        new_char = random.choice(self.letters_list)
        char_list = [c for c in value]

        char_list[random_position] = new_char
        generated_value = "".join(char_list)
        return generated_value

    def char_add(self, value):
        random_position = random.randint(0, len(value) - 1)
        new_char = random.choice(self.letters_list)
        char_list = [c for c in value]

        char_list.insert(random_position, new_char)
        generated_value = "".join(char_list)
        return generated_value

    def char_delete(self, value):
        random_position = random.randint(0, len(value) - 1)
        char_list = [c for c in value]

        char_list.pop(random_position)
        generated_value = "".join(char_list)
        return generated_value

    def convert_case(self, value):
        temp_value = value.upper()
        if temp_value == value:
            generated_value = value.lower()
        else:
            generated_value = temp_value
        return generated_value

    def disorder(self, value):
        if len(value) > 1:
            random_position_1 = random.randint(0, len(value) - 1)
            random_position_2 = 0
            is_equal = False
            while not is_equal:
                random_position_2 = random.randint(0, len(value) - 1)
                if random_position_2 == random_position_1:
                    is_equal = True
            char_list = [c for c in value]
            temp_char = char_list[random_position_1]
            char_list[random_position_1] = char_list[random_position_2]
            char_list[random_position_2] = temp_char
            generated_value = "".join(char_list)
        else:
            generated_value = value
        return generated_value

    def cut_out(self, value):
        if len(value) > 0:
            random_position = random.randint(0, len(value) - 1)
            generated_value = random.choice([value[:random_position], value[random_position:]])
        else:
            generated_value = value
        return generated_value

    def repeat(self, value):
        generated_value = value + value
        return generated_value

    def change_digit_type(self, option_type, option_value, option_range):
        if option_type == "float":
            generated_value = option_value.split(".")[0]
        else:
            generated_value = option_value + ".5"
        return generated_value

    def generate_new_number(self, option_type, option_value, option_range):
        if OPT_MODE == "ConfVD":
            # Enable beyond range
            engative_or_positive = random.choice([-1, 1])
            if engative_or_positive == -1:
                temp = option_range[0]
                option_range[0] = option_range[0] * 1000
                option_range[1] = temp
            else:
                temp = option_range[1]
                option_range[1] = option_range[1] * 1000
                option_range[0] = temp
        if option_type == "float":
            round_bit = len(option_value.split(".")[1])
            generated_value = round(random.uniform(option_range[0], option_range[1]), round_bit)
        else:
            generated_value = random.randint(option_range[0], option_range[1])
        return generated_value
