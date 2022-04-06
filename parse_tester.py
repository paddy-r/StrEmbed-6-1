# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 10:33:32 2021

@author: prehr
"""
# sp = StepParse()
# sp.load_step('Torch Assembly_for parse testing2.STEP')
# sp.load_step('cakestep.STP')
# sp.load_step('PARKING_TROLLEY.STEP')

import step_parse_6_1 as sp
import networkx as nx
import time
import numpy as np
import nltk
import pandas as pd

suffixes = ('.stp', '.step', '.STP', '.STEP')



file1 = '5 parts_{3,1},1.STEP'
# file1 = 'Torch Assembly.STEP'
# file1 = 'Steam Engine STEP.STEP'
# file1 = 'Trailer car TC (EBOM).STEP'
# file2 = 'Trailer car TC (G-SBOM).STEP'
# file3 = 'Trailer car TC (MBOM).STEP'
# file1 = 'cakestep.stp'
# file1 = 'PARKING_TROLLEY.STEP'
file2 = file1

# file2 = 'Trailer car TC (G-SBOM).STEP'

am = sp.AssemblyManager()

id1, ass1 = am.new_assembly()
ass1.load_step(file1)
# am.AddToLattice(id1)

id2, ass2 = am.new_assembly(id_to_duplicate = id1)
# ass2.load_step(file2)
# am.AddToLattice(id2)

# id3, ass3 = am.new_assembly()
# ass3.load_step(file3)
# # am.AddToLattice(id3)

# # am.xlsx_write(save_file = 'cakebox.xlsx')
# # am.xlsx_write(save_file = '5puzzle.xlsx')
# # am.xlsx_write(save_file = 'torch.xlsx')
# am.xlsx_write(save_file = 'trains.xlsx')

# french_names = {6: "Torche avec lentille et corps modifiés",
#                 7: "Assemblage du boîtier d'ampoule",
#                 8: "Boîtier d'ampoule modifié",
#                 9: "Ampoule",
#                 10: "Lentille modifié",
#                 11: "Bague de retenue de lentille modifié",
#                 12: "Corps de torche modifié",
#                 13: "Corps de torche",
#                 14: "Écrou M6",
#                 15: "Écrou M6",
#                 16: "Vis à tête cylindrique M6 x 30",
#                 17: "Vis à tête cylindrique M6 x 30"}

# for k,v in french_names.items():
#     ass2.nodes[k]['occ_name'] = v

# # results1 = am.match_block(id1, id2, weights = [1,1,1,1])
# # results2 = am.match_block(id1, id2, weights = [0,1,1,0])

# # def to_excel(data, file):
# #     df = pd.DataFrame(data)
# #     df.to_excel(file, index=False)

# am.xlsx_write(save_file = 'torch_french.xlsx')


# ''' Get true matches
#     Only true if both BoMs are from the same STEP file and unmodified '''
# # mu = get_matches(am, id1, id2)
# mu = get_matches(am, id1)
# mu = set(mu.values())

# ''' Modify BoM2 '''
# mu.discard((10,10))
# mu.discard((13,13))
# mu.update([(10,13),(13,10)])

# ''' Remove head node first '''
# # nodes1 = [node for node in ass1]
# # nodes1.remove(ass1.head)
# # nodes2 = [node for node in ass2]
# # nodes2.remove(ass2.head)
# nodes1 = list(ass1.leaves)
# nodes2 = list(ass2.leaves)

# ''' Set up CPU timer '''
# start_time = time.process_time()

# ''' Get matches '''
# matches = am.match_block(id1, id2, nodes1 = nodes1, nodes2 = nodes2, weights = [1,0,0,0])
# # matches = am.match_block(id1, id2, nodes1 = nodes1, nodes2 = nodes2, weights = [0,1,0,0])
# # matches = am.match_block(id1, id2, nodes1 = nodes1, nodes2 = nodes2, weights = [0,0,1,0])
# # matches = am.match_block(id1, id2, nodes1 = nodes1, nodes2 = nodes2, weights = [0,0,0,1])

# ''' Get elapsed time and time per operation '''
# elapsed_time = time.process_time() - start_time
# N = len(nodes1)*len(nodes2)
# elapsed_per = elapsed_time/N
# print('Time per operation: ', elapsed_per, 's')

# print('\n### MATCHES AND NAMES ###\n')
# for match in matches[0]:
#     print(ass1.nodes[match[0]]['screen_name'])
#     print(ass2.nodes[match[1]]['screen_name'])
#     print('\n')

# # ''' Add to lattice based on matches above '''

# shapes = []
# for node in ass1.nodes:
#     d = ass1.nodes[node]
#     if 'shape_raw' in d:
#         shape = ass1.nodes[node]['shape_raw'][0]
#         if shape:
#             print('Found shape for node ', node)
#             if shape in shapes:
#                 print(' Shape already in list; not adding')
#             else:
#                 print(' Shape not in list; adding')
#                 shapes.append(shape)


# N = 10

# n1,n2 = 13,17
# sh1 = ass1.nodes[n1]['shape_raw'][0]
# sh2 = ass1.nodes[n2]['shape_raw'][0]
# sh3 = ass2.nodes[n1]['shape_raw'][0]
# sh4 = ass2.nodes[n2]['shape_raw'][0]

# tol1 = 1e-3
# start_time = time.process_time()
# for i in range(N):
#     ar1 = sp.get_aspect_ratios(sh1, tol = tol1)
#     # ar2 = sp.get_aspect_ratios(sh2, tol = tol1)
# elapsed_time = time.process_time() - start_time
# print('Time per BB calc with tol = ', tol1, ':', elapsed_time/N)


# tol2 = 1e-4
# start_time = time.process_time()
# for i in range(N):
#     ar3 = sp.get_aspect_ratios(sh3, tol = tol2)
#     # ar4 = sp.get_aspect_ratios(sh4, tol = tol2)
# elapsed_time = time.process_time() - start_time
# print('Time per BB calc with tol = ', tol2, ':', elapsed_time/N)


# print(ar1)
# # print(ar2)
# print(ar3)
# # print(ar4)

# groups = am.block_by_name(id1, id2)

# blocks_by_bb = am.block_by_bb(id1, id2)
# results = am.matching_strategy(id1, id2)

