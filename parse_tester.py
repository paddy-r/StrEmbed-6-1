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
import time
import numpy as np
import nltk

suffixes = ('.stp', '.step', '.STP', '.STEP')



# ''' HR 19/01/22
#     To  (1) grab existing matches from lattice nodes for specified assemblies, or
#         (2) grab notional matches from one BoM, for when it is to be duplicated,
#             i.e. assume same nodes IDs in BoM1 as in notional BoM2
#     Returns dictionary of master_node: (node1,node2) in case master node needed later '''
# def grab_matches(lattice, id1, id2 = None):
#     matches = {}
#     for latt_node in lattice._lattice.nodes:
#         node_dict = lattice._lattice.nodes[latt_node]
#         if (id1 in node_dict):
#             node1 = node_dict[id1]
#             if id2 and (id2 in node_dict):
#                 ''' Case (1): get all matches found with id1, id2 in lattice '''
#                 node2 = node_dict[id2]
#                 matches[latt_node] = (node1,node2)
#                 print('Added actual pair:', node1, node2)
#             elif not id2:
#                 ''' Case (2): duplicate BoM1 node IDs '''
#                 node2 = node1
#                 matches[latt_node] = (node1,node2)
#                 print('Added notional pair:', node1, node2)
#     return matches



# '''
# HR 27/01/22
# To group items by name including inexactly via Levenshtein distance
# NOT FULLY TESTED AND MULTIPLE ISSUES IF 'screen_name' USED AS QUERY FIELD:
#     1. Endings (e.g. "_1") not accounted for when multiple instances of item exist;
#     2. The above complicated further if suffixes exists (e.g. ".STEP" -> ".STEP_1") as cannot then be removed consistently;
#     3. Cannot deal with non-product names (e.g. if default names present for "SOLID" or other shape types) or empty name fields
# Correctly groups parking trolley items if text_tol = 1e-2; this is small b/c some very long names, e.g. beginning with "Colson"
# '''
# def group_by_text(a1, a2, nodes1 = None, nodes2 = None, text_tol = 5e-2, suffixes = [], field = 'occ_name'):

#     groups = {}
#     grouped = False

#     if not nodes1:
#         nodes1 = a1.nodes
#     if not nodes2:
#         nodes2 = a2.nodes

#     for n1 in nodes1:
#         text = a1.nodes[n1][field]
#         if not text:
#             print('No name found at node ', n1)
#             continue
#         print('Name found at node ', n1)
#         ''' Remove suffixes '''
#         if suffixes:
#             text = remove_suffixes(text, suffixes = suffixes)
#         if text in groups:
#             print('Adding to existing group (exact match)')
#             groups[text][0].append(n1)
#             continue
#         for k in groups.keys():
#             lev_dist = nltk.edit_distance(text, k)
#             sim = 1 - lev_dist/max(len(text), len(k))

#             if sim > 1-text_tol:
#                 print('Adding to existing group (inexact match), score = ', sim)
#                 groups[k][0].append(n1)
#                 grouped = True
#                 break
#         if grouped:
#             grouped = False
#             continue
#         print('Creating new group: ', text)
#         groups[text] = ([n1], [])

#     for n2 in nodes2:
#         text = a2.nodes[n2][field]
#         if not text:
#             print('No name found at node ', n2)
#             continue
#         print('Name found at node ', n2)
#         ''' Remove suffixes '''
#         if suffixes:
#             text = remove_suffixes(text, suffixes = suffixes)
#         if text in groups:
#             print('Adding to existing group (exact match)')
#             groups[text][1].append(n2)
#             continue
#         for k in groups.keys():
#             lev_dist = nltk.edit_distance(text, k)
#             sim = 1 - lev_dist/max(len(text), len(k))

#             if sim > 1-text_tol:
#                 print('Adding to existing group (inexact match), score = ', sim)
#                 groups[k][1].append(n2)
#                 grouped = True
#                 break
#         if grouped:
#             grouped = False
#             continue
#         # print('Creating new group: ', text)
#         groups[text] = ([], [n2])

#     return groups



# '''
# HR 25/01/22
# To group items by bounding box (BB) dimensions (specifically sum of aspect ratios)
# Groups if (a) exact match or (b) inexact match (within tolerance) according to sim score
# '''
# def group_by_bb(a1, a2, nodes1 = None, nodes2 = None, bb_tol = 1e-4, group_tol = 1e-3):

#     groups = {}
#     grouped = False

#     if not nodes1:
#         nodes1 = a1.nodes
#     if not nodes2:
#         nodes2 = a2.nodes

#     for n1 in nodes1:
#         shape = a1.nodes[n1]['shape_raw'][0]
#         if not shape:
#             print('No shape found at node ', n1)
#             continue
#         print('Shape found at node ', n1, '; computing BB...')
#         bb_sum = np.sum(sp.get_aspect_ratios(shape, tol = bb_tol))
#         if bb_sum in groups:
#             print('Adding to existing group (exact match)')
#             groups[bb_sum][0].append(n1)
#             continue
#         for k in groups.keys():
#             if np.isclose(k, bb_sum, rtol = group_tol):
#                 print('Adding to existing group (inexact match)')
#                 groups[bb_sum][0].append(n1)
#                 grouped = True
#                 break
#             continue
#         if grouped:
#             grouped = False
#             continue
#         print('Creating new group')
#         groups[bb_sum] = ([n1], [])

#     for n2 in nodes2:
#         shape = a2.nodes[n2]['shape_raw'][0]
#         if not shape:
#             print('No shape found at node ', n2)
#             continue
#         print('Shape found at node ', n2, '; computing BB...')
#         bb_sum = np.sum(sp.get_aspect_ratios(shape, tol = bb_tol))
#         if bb_sum in groups:
#             print('Adding to existing group (exact match)')
#             groups[bb_sum][1].append(n2)
#             continue
#         for k in groups.keys():
#             if np.isclose(k, bb_sum, rtol = group_tol):
#                 print('Adding to existing group (inexact match)')
#                 groups[bb_sum][1].append(n2)
#                 grouped = True
#                 break
#             continue
#         if grouped:
#             grouped = False
#             continue
#         print('Creating new group')
#         groups[bb_sum] = ([], [n2])

#     return groups



# file1 = 'Torch Assembly.STEP'
# file1 = 'Steam Engine STEP.STEP'
# file1 = '5 parts_{3,1},1.STEP'
# file1 = 'Trailer car TC (EBOM).STEP'
# file1 = 'Trailer car TC (G-SBOM).STEP'
file1 = 'Trailer car TC (MBOM).STEP'
# file1 = 'cakestep.stp'
# file1 = 'PARKING_TROLLEY.STEP'
# file2 = file1

file2 = 'Trailer car TC (G-SBOM).STEP'

am = sp.AssemblyManager()

id1, ass1 = am.new_assembly()
ass1.load_step(file1)
am.AddToLattice(id1)

id2, ass2 = am.new_assembly()
ass2.load_step(file2)
# am.AddToLattice(id2)

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

groups_by_bb = am.block_by_bb(id1, id2)
# results = am.matching_strategy(id1, id2)
