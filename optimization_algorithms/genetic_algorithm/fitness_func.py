import math
import random


# from src.machine_learning_algorithm.regression_model import cart


def fitness_g1(real_rank, real_topk):
    count = 0
    for rank in real_rank:
        if rank < real_topk:
            count = count + 1
    g1 = 1 - count / real_topk
    return g1


def fitness_g2(real_rank):
    g2 = sum(real_rank)
    return g2


def fitness_g3(real_rank):
    count = 0
    length = len(real_rank)
    for i in range(length - 1):
        for rank_b in real_rank[i + 1:]:
            if real_rank[i] < rank_b:
                count = count + 1
    comp_num = length * (length - 1) / 2
    g3 = round(1 - count / comp_num, 2)
    return g3


def get_fitness_list(trans_df_list, topk, train_model, real_topk):
    fitness_list = []
    # i = 0
    # for trans_test_df in trans_df_list:
    #     predicted = cart(train_model, trans_test_df)
    #     trans_test_df['predicted'] = predicted
    #     trans_test_df.sort_values(by=["predicted"], inplace=True)
    #     # trans_test_df['predicted_rank'] = range(len(trans_test_df)) # no_use in this function
    #
    #     real_rank_list = trans_test_df['real_rank'].tolist()
    #     predicted_list = trans_test_df['predicted'].tolist()
    #     mean_fitness = fitness_calcu(topk, real_rank_list, predicted_list, real_topk)
    #     fitness_list.append(mean_fitness)
    #     i = i + 1
    return fitness_list


def fitness_calcu(topk, real_rank_list, predicted_list, real_topk):
    mean_fitness = get_mean_fitness(real_rank_list, predicted_list, topk, real_topk)
    return mean_fitness


def get_mean_fitness(real_rank_list, predicted_list, topk, real_topk):
    random_times = 10
    fitness_list = []
    for i in range(random_times):
        rerank_real_rank_list = get_topk_real_rank_list(real_rank_list, predicted_list, topk)
        # fitness = fitness_g1(real_rank_list, real_topk) * (real_topk + 1) + fitness_g2(real_rank_list)
        # fitness = fitness_g1(rerank_real_rank_list, real_topk)
        # fitness = fitness_g2(rerank_real_rank_list)
        fitness = fitness_g1(rerank_real_rank_list, real_topk) * 100000 + fitness_g2(
            rerank_real_rank_list) + fitness_g3(rerank_real_rank_list)
        fitness_list.append(fitness)
    mean_fitness = round(math.fsum(fitness_list) / random_times, 4)
    return mean_fitness


def get_topk_real_rank_list(real_rank_list, predicted_list, topk):
    if topk >= len(real_rank_list):
        return real_rank_list[0:topk]
    else:
        topk = topk - 1
        if predicted_list[topk] == predicted_list[topk + 1]:
            up_id = down_id = 0
            for j in range(len(predicted_list)):
                if topk == 0:
                    up_id = 0
                elif predicted_list[j] == predicted_list[topk] and predicted_list[j - 1] != predicted_list[topk]:
                    up_id = j
                if j + 1 < len(predicted_list):
                    if predicted_list[j] == predicted_list[topk] and predicted_list[j + 1] != predicted_list[topk]:
                        down_id = j
                        break
                else:
                    down_id = j
            temp_rank_list = real_rank_list[up_id:down_id + 1]
            random.shuffle(temp_rank_list)
            rank_list = real_rank_list[0:up_id] + temp_rank_list
        else:
            rank_list = real_rank_list
        topk = topk + 1
        return rank_list[0:topk]
