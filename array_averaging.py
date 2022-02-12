# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 11:09:36 2021

@author: prehr
"""
import numpy as np
from hungarian_algorithm import get_optimal_values

# a = np.full((3,2), fill_value = 1)
# b = np.full((3,2), fill_value = 10)
# c = np.full((3,2), fill_value = 100)

n1 = [0,1,2,3,4]
n2 = [10,20,30,40]
tol = 0.6

a = np.full((len(n1), len(n2)), fill_value = 0, dtype = float)
b = np.full((len(n1), len(n2)), fill_value = 0, dtype = float)
c = np.full((len(n1), len(n2)), fill_value = 0, dtype = float)

for i in range(len(n1)):
    for j in range(len(n2)):
        a[i,j] = np.random.rand()
        b[i,j] = np.random.rand()
        c[i,j] = np.random.rand()

w = np.array([2,4,6])

scores = np.average([a,b,c], axis = 0, weights = w)

rows, cols, best = get_optimal_values(scores)

pairs = list(zip(rows, cols))
print('\nPairs before tolerance: ', pairs)
pairs = [pair for pair in pairs if scores[pair] > tol]
print('\nPairs after tolerance: ', pairs)

total_score = sum([scores[pair] for pair in pairs])

''' Get actual pairs from n1, n2, i.e. get matches '''
matches = [(n1[pair[0]], n2[pair[1]]) for pair in pairs]

print('\nInputs:')
print(a,'\n',b,'\n',c)
print('\nWeights:')
print(w)
print('\nOutput:')
print(scores)

print('\nBest and sum of scores from cols/rows; should be the same:')
print(best, total_score)
