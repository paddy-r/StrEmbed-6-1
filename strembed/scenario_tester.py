# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 11:19:55 2022

@author: prehr
"""

''' HR 31/03/23 Refactoring after total overhaul
    1. Removed all hard file paths -> relative paths
    2. Created BoM dictionary and folder search functionality so just need to specify BoM IDs (e.g. P1, P2)
'''

import pickle
import time
import strembed.step_parse as sp
import networkx as nx
import numpy as np

# from step_parse import StepParse
import copy
# from OCC.Core.TopoDS import TopoDS_Shape
import os
from os.path import dirname as up


''' Set here and all references below are relative to this '''
DATA_FOLDER = os.path.join(up(up(up(up(up(__file__))))),
                           "_Data and models",
                           "_For BoM recon paper")

BOM_FOLDERS = ['_Puzzle BoMs',
               "_Railway carriage BoMs",
               "_Torch BoMs"]

BOM_DICT = {"P1": "P1.STEP", # Puzzle
            "P2": "P2.STEP",
            "P3": "P3.STEP",
            "P4": "P4.STEP",
            "P5": "P5.STEP",
            "P6": "P6.STEP",
            "P7": "P7.STEP",
            "P8": "P8.STEP",
            "T1": "T1.STEP", # Torch
            "T2": "T2.STEP",
            "T3": "T3.STEP",
            "T4": "T4.STEP",
            "T5": "T5.STEP",
            "T6": "T6.STEP",
            "T7": "T7.STEP",
            "T8": "T8.STEP",
            "RE": "Trailer car TC (EBOM).STEP", # Railway carriage
            "RG": "Trailer car TC (G-SBOM).STEP",
            "RM": "Trailer car TC (MBOM).STEP",
            }


def bom_path(bom_id):
    # Check BoM is in dict
    bom_file = BOM_DICT.get(bom_id, None)
    if not bom_file:
        print('BoM not known')
        return None
    # Cycle through folders to look for BoM
    for folder in BOM_FOLDERS:
        bom_folder = os.path.join(DATA_FOLDER, folder)
        bom_path = os.path.join(bom_folder, bom_file)
        if os.path.isfile(bom_path):
            print('BoM file', bom_file, 'not found in folder', bom_folder)
            print('Returning path:', bom_path)
            return bom_path
        else:
            print('BoM file', bom_file, 'NOT found in folder', bom_folder)
            continue

    print('BoM file not found anywhere')
    return None


def save_matching_results(results, filename = None):
    if not filename:
        filename = str(time.strftime("%Y-%m-%d %H:%M")) + '.pkl'
        filename = filename.replace(':','-')

    try:
        with open(filename, 'wb') as handle:
            pickle.dump(results, handle)
    except Exception as e:
        print('Could not save results file; exception follows')
        print(e)

    print('Saved file: ', filename)



def load_matching_results(filename):
    try:
        with open(filename, 'rb') as handle:
            results_loaded = pickle.load(handle)
            print('Loaded file:', filename)
            return results_loaded
    except:
        print('Could not load file, returning None: ', filename)
        return None


# def load_stuff(file1,file2):
#     am = sp.AssemblyManager()

#     id1, ass1 = am.new_assembly()
#     ass1.load_step(file1)
#     # am.AddToLattice(id1)

#     id2, ass2 = am.new_assembly()
#     ass2.load_step(file2)
#     # am.AddToLattice(id2)
#     return am



# def run_scenario(am, id1, id2, strategy = None):
#     ''' Specify matching strategy '''
#     strategy = None

#     ''' Get matching results '''
#     results = am.matching_strategy(id1, id2)
#     # save_file = save_matching_results(results)


''' HR 31/03/23 Not necessary since summer 2022 as not doing scenarios by removing nodes
                Instead all BoMs are clearly specified and were created by HHC '''
# ''' Remove random set of nodes and true matches for e.g. scenario 2
#     If "delete_nodes", delete nodes from assembly;
#     if not, just remove from matches
#     Return removed nodes and corrected set of matches '''
# def remove_some(assembly, number, matches, delete_nodes = False):
#     picks = list(np.random.choice(list(assembly.leaves), number))
#     removed = []

#     ''' Get all ancestors (parents up to root) so can remove matches containing them '''
#     ancestors = []
#     for pick in picks:
#         ancestors.extend(nx.ancestors(assembly,pick))

#     ''' If specified, delete nodes from assembly '''
#     if delete_nodes:
#         for pick in picks:
#             try:
#                 print('  Removing node ', pick)
#                 print('  ', assembly.nodes[pick]['screen_name'])
#                 assembly.remove_node(pick)
#                 removed.append(pick)
#             except Exception as e:
#                 print('  EXCEPTION:', e)
#                 continue

#     items = list(picks) + ancestors
#     for item in items:
#         for match in matches.copy():
#             if match[0] == item:
#                 try:
#                     matches.remove(match)
#                 except Exception as e:
#                     print('  EXCEPTION:', e)
#     return assembly, picks, removed, matches


'''
ALL CORRECT PAIR MATCHES FOR TEST CASES/CASE STUDIES ARE BELOW
'''

''' HR 20/07/22 To compile all matches for puzzle and torch;
                (a) Puzzle BoMs are P1 to P8, one for each scenario
                (b) Torch BoMs are T1 to T8, one for each scenario
                Scenarios as defined in "List of BoMs for reconciliation scenarios" document, at version 3 currently '''

''' French names from older script; retaining here '''
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

''' Dictionary for true matches, produced by inspection of BoMs '''
M = {}



''' Older BoM pairs, used during testing: puzzle_1a, 1b and 1c from HHC '''
# '''                                        name    A     B     C     D     E '''
# M[('puzzle_1b.STEP', 'puzzle_1c.STEP')] = {(2,2),(3,9),(4,4),(5,8),(6,7),(7,5)}
# M[('puzzle_1c.STEP', 'puzzle_1d.STEP')] = {(2,2),(4,3),(5,7),(7,4),(8,8),(9,6)}
# M[('puzzle_1b.STEP', 'puzzle_1d.STEP')] = {(2,2),(3,6),(4,3),(5,8),(6,4),(7,7)}


'''
RAILWAY CARRIAGES
'''
''' 22/04/22 All NOTIONAL matches, i.e. NOT just combinatorial matches '''
# M[('RE', 'RG')] = {(3, 3),
#                    (4, 4),
#                    (5, 5),
#                    (7, 6),
#                    (8, 7),
#                    (9, 8),
#                    (10, 9),
#                    (11, 10),
#                    (12, 11),
#                    (13, 13),
#                    (14, 14),
#                    (16, 12),
#                    (17, 15),
#                    (18, 16),
#                    (28, 17),
#                    (30, 19),
#                    (31, 20),
#                    (32, 21),
#                    (33, 22),
#                    (34, 23),
#                    (35, 24),
#                    (36, 25),
#                    (37, 26),
#                    (38, 27)}
# M[('RG', 'RM')] = {(),
#                    (),
#                    }
# M[('RE', 'RM')] = {(),
#                    }

''' 25/04/22 COMBINATORIAL matches only, i.e. no solely NOTIONAL matches '''
M[('RE', 'RG')] = {(3, 3),  # Drawing of trailer body
                   (5, 5),  # Bogie frame GJ
                   (7, 6),  # Wheelset and axle box LZ-31582111
                   (8, 7),
                   (9, 8),
                   (10, 9),
                   (11, 10),
                   (12, 11),
                   (13, 13),
                   (14, 15),
                   (16, 12),  # Wheelset and axle box LZ-3159219
                   (17, 14),
                   (18, 16),
                   (28, 17),
                   (30, 19),  # Equipment under vehicle CA
                   (31, 20),
                   (32, 21),
                   (33, 22),
                   (34, 23),
                   (35, 24),
                   (36, 25),
                   (37, 26),
                   (38, 27),  # ALL CHECKED
                   }
M[('RG', 'RM')] = {(5, 8),  # Bogie frame GJ
                   (6, 11),  # Wheelset and axle box LZ-31582111
                   (7, 12),
                   (8, 16),
                   (9, 15),
                   (10, 13),
                   (11, 14),
                   (12, 17),  # Wheelset and axle box LZ-3159219
                   (13, 18),
                   (14, 19),
                   (15, 20),
                   (16, 21),
                   (17, 23),
                   (19, 24),  # Equipment under vehicle CA
                   (20, 25),
                   (21, 26),
                   (22, 27),
                   (23, 28),
                   (24, 29),
                   (25, 30),
                   (26, 31),
                   (27, 32),  # ALL CHECKED
                   }
M[('RE', 'RM')] = {(5, 8),  # Bogie frame GJ
                   (7, 11),  # Axle end accessories LF
                   (8, 12),
                   (9, 16),
                   (10, 15),
                   (11, 13),
                   (12, 14),
                   (13, 18),
                   (14, 20),
                   (16, 17),  # Wheelset and axle box LZ-3159219
                   (17, 19),
                   (18, 21),
                   (28, 23),
                   (30, 24),  # Equipment under vehicle CA
                   (31, 25),
                   (32, 26),
                   (33, 27),
                   (34, 28),
                   (35, 29),
                   (36, 30),
                   (37, 31),
                   (38, 32),  # ALL CHECKED
                   }


'''
FIVE-PIECE PUZZLE
'''
'''' COMBINATORIAL matches only, i.e. no solely NOTIONAL matches '''
M[('P1', 'P2')] = {(2,2),#P1, P2
                             (3,3),#{ABC},D, {part1part2,part3},part4
                             (4,4),
                             (5,5),
                             (6,6),#A, part1
                             (7,7),
                             (8,8),
                             (9,9),
                             (10,10)#E, part5
                             }
M[('P1', 'P3')] = {(2,2),#P1, P3
                             (4,3),#AB,C, ABC
                             (6,4),#A
                             (7,5),
                             (8,6),
                             (9,8),
                             (10,9)
                             }
M[('P1', 'P4')] = {(2,2),
                             (3,3),
                             (4,4),
                             (5,5),
                             (6,6),
                             (7,7),
                             (8,8),
                             (9,9),
                             (10,10)
                             }
M[('P1', 'P5')] = {(3,2),#{AB,C},D, P5
                             (6,4),#A, A
                             (7,4),
                             (8,5),
                             (9,8)
                             }
M[('P1', 'P6')] = {(2,2),#P1, P6
                             (4,3),#AB,C, part1part2part3
                             (6,4),#A, part1
                             (7,5),
                             (8,6),
                             (9,8),
                             (10,9)
                             }
M[('P1', 'P7')] = {(2,2),#P1, P7
                             (3,3),#{AB,C},D, {part1part2,part3},part4
                             (4,4),
                             (5,5),#AB, part1part2
                             (6,6),#A, part1
                             (7,7),
                             (8,8),
                             (9,9),
                             (10,10)
                             }
M[('P1', 'P8')] = {(2,2),#P1, P8
                             (4,3),#AB,C, ABC
                             (6,4),#A,A
                             (7,5),
                             (8,6),
                             (9,8),
                             (10,9)
                             }


'''
TORCH
'''

''' 'COMBINATORIAL matches only, i.e. no solely NOTIONAL matches '''
M[('T1', 'T2')] = {(2, 2),  # ASSEMBLY BOM, Torch ASSEMBLY BOM
                   (3, 3),
                   (4, 4),
                   (5, 5),  # BULB ASSEMBLY, Ensemblage d_ampoule
                   (6, 6),
                   (7, 7),
                   (8, 8),
                   (9, 9),
                   (10, 10),  # FASTENERS, Attaches
                   (11, 11),
                   (12, 14),
                   (13, 12),
                   (14, 13)
                   }
M[('T1', 'T3')] = {(2, 2),  # ASSEMBLY BOM, DISASSEMBLY BOM
                   (3, 4),
                   (4, 5),
                   (5, 10),  # BULB ASSEMBLY, BULB ASSEMBLY
                   (6, 11),
                   (7, 12),
                   (8, 13),
                   (9, 14),
                   (11, 6),
                   (12, 8),
                   (13, 7),
                   (14, 9)
                   }
# M[('T1', 'T3_agg')] = {(),#
#                              }
M[('T1', 'T4')] = {(2, 2),  # ASSEMBLY BOM, ASSEMBLY BOM (T4)
                   (3, 3),
                   (4, 4),
                   (5, 5),  # BULB ASSEMBLY, BULB HOUSING ASSEMBLY (T4)
                   (6, 6),
                   (7, 8),
                   (8, 9),
                   (9, 7),
                   (10, 10),  # FASTENERS, FASTENERS
                   (11, 11),
                   (12, 12),
                   (13, 13),
                   (14, 14)
                   }
M[('T1', 'T5')] = {(3, 4),  # TORCH BODY - LOWER, TORCH BODY - LOWER
                   (4, 5),
                   (6, 11),
                   (9, 12),
                   (11, 6),
                   (12, 8),
                   (13, 7),
                   (14, 9)
                   }
# M[('T1', 'T5_agg')] = {(),#
#                              }
M[('T1', 'T6')] = {(2, 2),  # ASSEMBLY BOM, Torche DISASSEMBLY BOM
                   (3, 4),
                   (4, 5),
                   (5, 10),
                   (6, 11),
                   (7, 12),
                   (8, 13),
                   (9, 14),
                   (11, 6),
                   (12, 8),
                   (13, 7),
                   (14, 9)
                   }
# M[('T1.STEP', 'T6_agg.STEP')] = {(),#
#                              }
M[('T1', 'T7')] = {(2, 2),  # ASSEMBLY BOM, Torche ASSEMBLY BOM (T7)
                   (3, 3),
                   (4, 4),
                   (5, 5),
                   (6, 6),
                   (7, 9),
                   (8, 8),
                   (9, 7),
                   (10, 10),
                   (11, 11),
                   (12, 14),
                   (13, 12),
                   (14, 13)
                   }
M[('T1', 'T8')] = {(2, 2),  # ASSEMBLY, DISASSEMBLY BOM (T8) (TORCH BODY has six parts)
                   (3, 4),
                   (4, 5),
                   (5, 10),  # BULB ASSEMBLY, BULB HOUSING ASSEMBLY (T4)
                   (6, 11),
                   (7, 13),
                   (8, 14),
                   (9, 12),
                   (11, 6),
                   (12, 8),
                   (13, 7),
                   (14, 9)
                   }
# M[('T1', 'T8_agg')] = {(),#
#                              }


''' All code below is for running BoM reconciliation strategies
    and assessing their matching success '''
if __name__ == "__main__":

    # suffixes = ('.stp', '.step', '.STP', '.STEP')

    ''' Older BoMs used during testing '''
    # file1 = '5 parts_{3,1},1.STEP'
    # file1 = 'Steam Engine STEP.STEP'
    # file1 = 'cakestep.stp'
    # file1 = 'PARKING_TROLLEY.STEP'
    # file1 = 'puzzle_1b.STEP'
    # file1 = 'puzzle_1c.STEP'
    # file2 = 'puzzle_1d.STEP'

    # file2 = 'Trailer car TC (EBOM).STEP'
    # file2 = 'Trailer car TC (G-SBOM).STEP'
    # file2 = 'Trailer car TC (MBOM).STEP'
    # file2 = 'puzzle_1b.STEP'
    # file2 = 'puzzle_1c.STEP'
    # file2 = 'puzzle_1d.STEP'


    '''
    HR 22/06/22 To standardise method for producing results for BoM recon paper
    '''


    ''' Puzzle BoMs '''

    # file1 = 'P1.STEP'
    # file2 = 'P2.STEP'
    # file2 = 'P3.STEP'
    # file2 = 'P4.STEP'
    # file2 = 'P5.STEP'
    # file2 = 'P6.STEP'
    # file2 = 'P7.STEP'
    # file2 = 'P8.STEP'
    # file2 = file1

    ''' Torch BoMs '''

    # file1 = 'T1.STEP'
    # # file2 = 'T2.STEP'
    # # file2 = 'T3.STEP'
    # # file2 = 'T3_agg.STEP'
    # file2 = 'T4.STEP'
    # file2 = 'T5.STEP'
    # file2 = 'T5_agg.STEP'
    # file2 = 'T6.STEP'
    # file2 = 'T6_agg.STEP'
    # file2 = 'T7.STEP'
    # file2 = 'T8.STEP'
    # file2 = 'T8_agg.STEP'
    # file2 = file1

    ''' Railway carriage BoMs '''

    # file1 = 'Trailer car TC (EBOM).STEP'
    # file1 = 'Trailer car TC (G-SBOM).STEP'
    # file1 = 'Trailer car TC (MBOM).STEP'
    # file2 = 'Trailer car TC (EBOM).STEP'
    # file2 = 'Trailer car TC (G-SBOM).STEP'
    # file2 = 'Trailer car TC (MBOM).STEP'
    # file2 = file1


    '''
    ASSEMBLE FULL PATHs
    '''
    # filefull1 = os.path.join(bom_dir, file1)
    # filefull2 = os.path.join(bom_dir, file2)
    bom1 = "T1"
    bom2 = "T2"
    path1 = bom_path(bom1)
    path2 = bom_path(bom2)


    ''' HR 22/07/22 To merge with "parse_tester"; block below from there '''

    ''' --- '''
    am = sp.AssemblyManager()

    id1, ass1 = am.new_assembly()
    ass1.load_step(path1)
    # ass1.remove_redundants()
    am.AddToLatticeSimple(id1)

    id2,ass2 = am.new_assembly()
    ass2.load_step(path2)
    # ass2.remove_redundants()

    weights = [1,0,0,0]
    structure_weights = [1,1,1,1]
    results = am.matching_strategy(id1 = id1, id2 = id2, stages = [((None, {}), ('mb', {'weights': weights, 'structure_weights': structure_weights}))])
    # results = am.matching_strategy(id1 = id1, id2 = id2, stages = [((None, {}), ('mb', {'weights': weights, 'structure_weights': structure_weights}))], match_subs = True)

    print('Matching results:\n', results)
    print('\nFinished "OnRecon"\n')

    mu = results[1][0]
    am.AddToLattice(id1, id2, mu)

    ''' Older strategies before fetching results and adding to lattice were separated as methods '''
    # am.AddToLattice(id2, stages = [((None, {}), ('mb', {'weights': [1,1,1,1]}))])
    # am.AddToLattice(id2, stages = [(('bb', {}), ('mb', {'weights': [1,0,1,0]}))])
    # am.AddToLattice(id2, stages = [(('bb', {}), ('mb', {'weights': [0,1,0,0]}))])
    # am.AddToLattice(id2, stages = [((None, {}), ('mb', {'weights': [0,1,0,1], 'structure_weights': [0,1,1,1]}))])
    # am.AddToLattice(id2, stages = [((None, {}), ('mb', {'weights': [1,0,0,0]}))])
    ''' --- '''

    ''' Alternative (older) way of getting matches in two stages: leaf matches then subs, then add them;
        retaining as could be useful '''
    # results = am.match_block(id1, id2, nodes1 = n1, nodes2 = n2, weights = [1,0,0,0], structure_weights = [1,0,1,1], scale = True)
    # results_subs = am.match_by_comb(id1,id2,results[0])

    # all_matches = results[0] + results_subs[0]
    # mu = set(all_matches)


    ''' Prepare true matches '''
    if bom1 == bom2:
        # nodes = set(ass1.nodes) - {ass1.head}
        ''' No need to remove head if all redundants removed '''
        nodes = set(ass1.nodes)
        M_ = {(node,node) for node in nodes}
    else:
        if (bom1, bom2) in M:
            ''' If found, direct access '''
            M_ = M[(bom1, bom2)]
        elif (bom2, bom1) in M:
            ''' If found in reverse, copy and flip entries, i.e. (a,b) -> (b,a) '''
            M_ = M[(bom2, bom1)]
            M_ = {(el[1],el[0]) for el in M_}
        else:
            print('True matches not found; aborting')


    ''' Obsolete as refers to older BoMs contrived to have nodes removed on the fly;
        current ones were created to order by HHC '''
    # ''' Remove/disregard nodes and matches containing them '''
    # delete_nodes = False
    # number_to_remove = 0
    # ass1, picks, removed, M_ = remove_some(ass1, number_to_remove, M_, delete_nodes = delete_nodes)

    # ''' Ignore nodes that have been removed/are to be disregarded '''
    # for pick in picks:
    #     try:
    #         n1.remove(pick)
    #     except:
    #         pass


    '''
    MATCHING SUCCESS
    '''

    # n_a = len(ass1.nodes) - 1
    # n_b = len(ass2.nodes) - 1
    ''' No need to subtract 1 if redundants removed '''
    n_a = len(ass1.nodes)
    n_b = len(ass2.nodes)

    ''' M = true matches
        mu = found matches '''
    P,R,S = sp.get_matching_success(n_a,n_b,M_,mu)

    def print_names(group):
        if group:
            for match in group:
                n1,n2 = match[0],match[1]
                print(' ', n1, ass1.nodes[n1]['screen_name'], '--', n2, ass2.nodes[n2]['screen_name'])
        else:
            print('None!')

    ''' Report on matches '''
    print('P,R,S:')
    print(' ', P,R,S)

    print('FN:')
    print_names((M_ - mu))
    print('FP:')
    print_names((mu - M_))
    print('|FN|:', len(M_ - mu))
    print('|FP|:', len(mu - M_))
