# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 16:08:05 2021

@author: prehr
"""
from scipy.optimize import linear_sum_assignment as lsa
import numpy as np
import random

''' HR 27/10/21
    To do for full implementation:
        1. Create full (not triangular) square/rectangular matrix from similarity scores dictionary - DONE
        2. Allow user to specify tolerance that can be applied to scores either:
            a. Before LSA calculation, if below tolerance -> set to default (i.e. negative) value then do LSA and accept all matches, or
            b. After LSA calculations, if below tolerance -> nullify match, if present
        3. Needs work overall (see example 4) to ensure array columns/rows are right way round - DONE '''

''' HR 13/10/21
    Linear sum assignment problem
    solved using "modified Jonker-Volgenant algorithm with no initialization"
    1. scipy: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html
    2. Crouse (2016) paper on which scipy alg is based: https://doi.org/10.1109/TAES.2016.140952 '''
def get_optimal_values(arr, greedy = None, maximize = True, tol = 0, default = -1):
    
    ''' If "greedy" specified, proceed by either row (1) or column (2), matching by local highest score
        i.e. greedy matching; "by_row" -> by items in first input list, "by_column" -> by second
        NOT FINISHED: 
            1. Returns too many results if n != m
            2. Does not check for duplicate by row/column (as can only be max of one match in each) '''
    if greedy == "by_row":
        row_ind = np.arange(len(arr))
        col_ind = np.argmax(arr, axis = 1)

    elif greedy == "by_column":
        col_ind = np.arange(len(arr[0]))
        row_ind = np.argmax(arr, axis = 0)

    else:
        ''' ...else find globally optimal set of matches '''
        # cost = np.array([[4, 1, 3], [2, 0, 5], [3, 2, 2]])
        row_ind, col_ind = lsa(arr, maximize = maximize)

    best = arr[row_ind, col_ind].sum()
    return row_ind, col_ind, best



''' Return rectangular numpy (np) array from scores dictionary
    for use with "get_optimal_values" method '''
def scores_to_array(scores, default = -1.0):

    ''' Get all labels '''
    l1 = list(set([k[0] for k in scores.keys()]))
    l2 = list(set([k[1] for k in scores.keys()]))
    print('l1: ', l1)
    print('l2: ', l2)

    ''' Populate array with scores '''
    arr = np.full((len(l1),len(l2)), fill_value = default)
    for j,lab1 in enumerate(l1):
        for i,lab2 in enumerate(l2):
            if (lab1,lab2) in scores:
                val = scores[(lab1,lab2)]
                # print('Found: ', val)
                arr[j,i] = val

    return l1,l2,arr


# if __name__ == "__main__":
        
#     # ''' Example 1 '''
#     # arr = np.array([[4, 1, 3], [2, 0, 5], [3, 2, 2]])
#     # best = get_optimal_values(arr)[2]
#     # print('Optimal sum = ', best)
    
#     # ''' Example 2 '''
#     # arr = np.random.rand(100,100)
#     # best = get_optimal_values(arr)[2]
#     # print('Optimal sum = ', best)
    
#     # ''' Example 3 '''
#     # for i in ('a1', 'a2', 'a3'):
#     #     for j in ('b1', 'b2', 'b3'):
#     #         scores[(j,i)] = random.random()
    
#     ''' Example 4 '''
#     labels = ('a_','b_')
#     n = 5
#     m = 10
#     scores = {}
    
#     for i in range(n):
#         for j in range(m):
#             k = (labels[1] + str(j+1), labels[0] + str(i+1))
#             scores[k] = random.random()
    
#     l1,l2,arr = scores_to_array(scores)
#     opts = get_optimal_values(arr)
    
#     opts_ind = list(zip(opts[0],opts[1]))
    
#     pairs = []
#     for ind in opts_ind:
#         pair = (l2[ind[1]],l1[ind[0]])
#         pairs.append(pair)
#         print(pair)
