'''
HR 11/02/21
Algorithm 515 (Buckles_77, DOI: https://doi.org/10.1145/355732.355739)
For indexing combinations -> lexicographic ordering for ranking/unranking
Taken from Github repo of sleeepyjack here:
https://github.com/sleeepyjack/alg515/blob/master/python/alg515.py
'''

from scipy.special import binom

def comb(N, P, L):
    C = [0] * P
    print(C)
    X = 1
    R = int(binom(N-X, P-1))
    K = R

    while (K <= L):
        X += 1
        R  = int(binom(N-X, P-1))
        K += R
    K -= R
    C[0] = X-1

    for I in range(2, P):
        X += 1
        R  = int(binom(N-X, P-I))
        K += R
        while (K <= L):
            X += 1
            R  = int(binom(N-X, P-I))
            K += R
        K -= R
        C[I-1] = X-1
    C[P-1] = X + L - K
    return C

################################################

n, r = 10,5


nCr = int(binom(n, r))

print('n =', n, '\tr =', r, '\tnCr =', nCr)

# for i in range(nCr):
#     print(comb(n, r, i))