import random
from copy import deepcopy
from optimization_algorithms.genetic_algorithm.fitness_func import get_fitness_list


# from src.data_processing.generate_csv import dflist2csv
# from src.transfer_algorithm.transfer_func import transfer, get_trans_df


def ga_config(source_train, target_train, train_model, generation_limit, generation_loop, new_chrom_num,
              experiment_name, string_bit, topk, real_topk,
              rank_index, map_scale, dataset_choose, select_num):
    # init_pop = 10
    init_pop = 20

    s_col = source_train.shape[1] - 4
    t_col = target_train.shape[1] - 4
    chrom_length = s_col * t_col * string_bit

    # 初始化种群
    chrom_list = generate_chrome(init_pop, chrom_length)

    # 开始GA
    generation = 0
    temp_fitness = 100000000  # a large number
    gen_count = 0
    while generation < generation_limit:
        # print("Generation:  " + str(generation))
        # time_start = time.time()
        generation = generation + 1

        if generation == 1:
            select_chrome_list = chrom_list
        else:
            select_chrome_list, least_fitness = select(chrom_list, s_col, string_bit, target_train, train_model, topk,
                                                       real_topk, map_scale, select_num)
            if temp_fitness == least_fitness:
                gen_count += 1
                # print(gen_count, end=' ')
                if gen_count == generation_loop:
                    break
            else:
                # print("\ngeneration:", generation, end="  , ")
                # print("fitness:", least_fitness, end="  -- ")
                temp_fitness = least_fitness
                gen_count = 0

        new_chrom_list = generate_chrome(new_chrom_num, chrom_length)
        select_chrome_list += new_chrom_list

        cross_chrom_list = crossover(select_chrome_list)
        mutant_chrom_list = mutate(cross_chrom_list)

        chrom_list = mutant_chrom_list

        random.shuffle(chrom_list)

        # time_end = time.time()
        # print('total time-cost', time_end - time_start)

    print("End generation:", generation, end="  ")
    select_chrome_list, least_fitness = select(chrom_list, s_col, string_bit, target_train, train_model, topk,
                                               real_topk, map_scale, select_num)
    final_select_chrome_list = select_chrome_list[:1]
    # trans_test_list = transfer(final_select_chrome_list, target_train, s_col, string_bit, train_model, map_scale)
    # dflist2csv(trans_test_list, experiment_name, topk, rank_index, dataset_choose, map_scale, generation_limit, string_bit, resultorprocess='p')
    return final_select_chrome_list


def select(chrom_list, s_col, string_bit, target_train, train_model, topk, real_topk, map_scale, select_num):
    # trans_df_list = get_trans_df(chrom_list, s_col, string_bit, target_train, map_scale)
    fitness_list = get_fitness_list(trans_df_list, topk, train_model, real_topk)

    result_list = [i for i in zip(chrom_list, fitness_list)]
    result_list.sort(key=lambda x: x[-1])
    sorted_chrom_list = [i[0] for i in result_list]
    sorted_fitness_list = [i[-1] for i in result_list]

    if select_num == 1:
        return sorted_chrom_list[0:1], sorted_fitness_list[0]
    else:
        select_chrom_list = select_unduplicated_list(sorted_chrom_list, select_num)
        # trans_df_list2 = get_trans_df(select_chrom_list, s_col, string_bit, target_train, map_scale)
        # fitness_list2 = get_fitness_list(trans_df_list2, topk, train_model, real_topk)
        # print('\n',fitness_list2[:20],fitness_list2[20:])
        return select_chrom_list, sorted_fitness_list[0]


def select_unduplicated_list(element_list, select_num):
    select_list = []
    count = 0
    num = 0
    for element in element_list:
        num = num + 1
        if count < select_num / 2:
            if element not in select_list:
                select_list.append(element)
                count = count + 1
        else:
            break
    list_length = len(element_list)
    while count < select_num:
        id = random.randint(num, list_length - 1)
        if element_list[id] not in select_list:
            select_list.append(element_list[id])
            count = count + 1
    return select_list


def crossover(chrom_list):
    cross_chrome_list = []
    copy_chrom_list = deepcopy(chrom_list)
    chrom_length = len(copy_chrom_list[0])
    chrom_list_length = len(copy_chrom_list)

    # crossover(随机选择chrom_length次配对法)
    for i in range(chrom_list_length):  # 若个体数为奇数，则最后单着的那一个跳过
        # if random.random() < crossover_poss:
        randa = random.randint(0, chrom_list_length - 1)
        randb = random.randint(0, chrom_list_length - 1)
        while randb == randa:
            randb = random.randint(0, chrom_list_length - 1)
        chrom_A = copy_chrom_list[randa]
        chrom_B = copy_chrom_list[randb]

        position = random.randint(1, chrom_length - 2)
        chrom_a = ''.join([chrom_A[:position], chrom_B[position:]])
        chrom_b = ''.join([chrom_B[:position], chrom_A[position:]])
        cross_chrome_list.append(chrom_a)
        cross_chrome_list.append(chrom_b)
    chrom_list = chrom_list + cross_chrome_list
    return chrom_list


def mutate(chrom_list):
    mutant_chrom_list = deepcopy(chrom_list)
    chrom_length = len(mutant_chrom_list[0])
    chrom_list_length = len(mutant_chrom_list)

    # mutation
    for i in range(chrom_list_length):
        position = random.randint(0, chrom_length - 1)
        chrom2list = list(mutant_chrom_list[i])
        chrom2list[position] = '0' if chrom2list[position] == '1' else '1'
        mutant_chrom_list[i] = ''.join(chrom2list)
    chrom_list = chrom_list + mutant_chrom_list

    return chrom_list


def generate_chrome(chrom_num, chrom_length):
    chrom_list = []
    for i in range(chrom_num):
        chrom = []
        for i in range(chrom_length):
            chrom.append(random.choice("01"))
        chrom = ''.join(chrom)
        chrom_list.append(chrom)
    return chrom_list
