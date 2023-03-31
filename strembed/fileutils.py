# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 15:02:13 2021

@author: prehr
"""

''' HR June 21 Full update to consolidate sim dump to Excel
    and added "split_and_dump" to show example usage '''

''' HR 14/03/21
    To load arbitrary STEP files from folder
    and compute similarity scores based on:
        1. Bounding boxes (i.e. aspect ratios)
        2. Tom's ML methods
        3. Tom's graphlet-based "ground truth" method '''

''' HR 19/03/21
    Some file operation utils here for now '''

''' HR 31/03/23
    Adding to repo UNTESTED in case any useful scrap later
    Probably a lot of overlap with file operations in "step_parse" '''


import os
from OCC.Extend import DataExchange as dex

from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
# from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.TopoDS import TopoDS_Solid, TopoDS_Compound, TopoDS_Shell

import xlsxwriter
from step_parse import StepParse, remove_suffixes, get_aspect_ratios, get_bb_score
from part_compare import load_from_step, PartCompare


''' Read/write operations '''
def save_to_txt(data, file = None):
    if not file:
        file = os.path.join(os.getcwd(), 'data.txt')
    with open(file, 'w+') as f:
        f.write(str(data))

def load_from_txt(file):
    with open(file, 'r') as f:
        for line in f.readlines():
            data = line.replace('nan', '-1')
    return eval(data)


''' HR 11/04/21
    To load pre-calculated sim scores from file
    and add graphlet sim scores to Excel w/o using StepParse
    BB, ML and GR scores all in common semi-matrix format '''

''' Save all constituent parts in STEP file to individual STEP files
    "path" is for saving
    "model_folder" is path to STEP models and similarity scores '''
def scores_to_excel(step_folder, path = None, default_value = -1, suffixes = ('step', 'stp', 'STEP', 'STP')):

    ''' HR 11/08/21
        To add BoM info to Excel output; must load original STEP file
        and get number of instances of all items '''
    sp = StepParse()

    for suffix in suffixes:
        filename = step_folder + '.' + suffix
        loaded = False
        print('Trying to load file: ', filename)
        try:
            sp.load_step(filename)
            print('Loaded file: ', filename)
            loaded = True
            break
        except Exception as e:
            print('Could not find/load file: ', filename)
            print('Exception:\n', e)

    if not loaded:
        print('Aborting: no file loaded')
        return

    ''' Prepare BoM structure in list form for easy writing to Excel later '''
    level = [0]
    tree = []

    def get_children(node):
        children = [el for el in sp.successors(node)]
        level[0] += 1
        for child in children:
            print(str(level[0]*'_'), sp.nodes[node]['screen_name'], sp.nodes[child]['screen_name'], level[0])
            tree.append((level[0], sp.nodes[child]['screen_name']))
            get_children(child)
        level[0] -= 1

        return tree

    head = sp.get_root()
    root_node = [el for el in sp.successors(head)][0]
    print('Root node: ', sp.nodes[root_node])

    print(str(level[0]*'_'), 'Head', sp.nodes[root_node]['screen_name'], level[0])
    tree_list = [(level[0], sp.nodes[root_node]['screen_name'])]

    tree_list.extend(get_children(root_node))


    if not path:
        path = step_folder

    ''' Get all STEP files/part names in folder '''
    files = [file for file in os.listdir(step_folder) if file.endswith(suffixes)]
    files_sorted = sorted(files)
    # print('Got list of unique/distinct parts')
    # print('Number: ', len(files_sorted))
    # file_dict = {i:file for i,file in enumerate(files_sorted)}

    parts_sorted = [el.rsplit('.', 1)[0] for el in files_sorted]

    ''' Initialise Excel file for dumping data '''
    bb_data = {}
    ml_data = {}
    gr_data = {}

    data_file = os.path.join(path, 'data_all.xlsx')
    print('Full data file path: ', data_file)
    workbook = xlsxwriter.Workbook(data_file)


    ''' Get pre-calculated sim scores from file '''
    try:
        bb_dict = load_from_txt(os.path.join(step_folder, 'scores_bb.txt'))
    except:
        bb_dict = {}

    try:
        ml_dict = load_from_txt(os.path.join(step_folder, 'scores.txt'))
    except:
        ml_dict = {}

    try:
        gr_dict = load_from_txt(os.path.join(step_folder, 'scores_graphlet.txt'))
    except:
        gr_dict = {}


    '''
    Meta sheet and headers for all other sheets
    '''
    meta_sheet = workbook.add_worksheet('Information')
    meta_fields = ['Item ID', 'Part name/label', 'Type', 'Instances']
    for i,el in enumerate(meta_fields):
        meta_sheet.write(0, i, el)
    for i,file in enumerate(files_sorted):
        text = file.rsplit('.', 1)[0]
        if text in parts_sorted:
            print('Part found: ', text)
            ty = 'Part'
        else:
            print('Part NOT found; item is assembly: ', text)
            ty = 'Assembly'
        instances = sp.name_root_counter[text]

        meta_sheet.write(i+1, 0, i)
        meta_sheet.write(i+1, 1, text)
        meta_sheet.write(i+1, 2, ty)
        meta_sheet.write(i+1, 3, instances)

    '''
    BoM sheet with structure in cell-indented list format
    '''
    bom_sheet = workbook.add_worksheet('BoM tree')
    bom_fields = ['BoM structure with cell indentations to represent parent-child relationship']
    for i,el in enumerate(bom_fields):
        bom_sheet.write(0, i, el)
    y_off = 2
    x_off = 1
    for el in tree_list:
        y_off += 1
        bom_sheet.write(i+y_off, el[0]+x_off, el[1])


    ''' Bounding box/aspect ratio (BB) sim scores sheet '''
    bb_fields = files_sorted
    bb_sheet = workbook.add_worksheet('BB sim score data')
    for i,el in enumerate(bb_fields):
        bb_sheet.write(0, i+1, i)
        bb_sheet.write(i+1, 0, i)

    ''' Machine learning (ML) sim scores sheet '''
    ml_fields = files_sorted
    ml_sheet = workbook.add_worksheet('ML sim score data')
    for i,el in enumerate(ml_fields):
        ml_sheet.write(0, i+1, i)
        ml_sheet.write(i+1, 0, i)

    ''' Graphlet-based (GR) sim scores sheet '''
    gr_fields = files_sorted
    gr_sheet = workbook.add_worksheet('GR sim score data')
    for i,el in enumerate(gr_fields):
        gr_sheet.write(0, i+1, i)
        gr_sheet.write(i+1, 0, i)


    ''' Load sim scores and dump to Excel file '''
    y = 0
    _done = []
    '''
    Get similarity score data
    '''
    for f1 in files_sorted:

        bb_data[f1] = []
        ml_data[f1] = []
        gr_data[f1] = []

        for f2 in files_sorted:
            if f2 in _done:
                # print('Skipping...')
                continue

            if (f1,f2) in bb_dict:
                bb_score = bb_dict[(f1,f2)]
                # print('Found')
            elif (f2,f1) in bb_dict:
                bb_score = bb_dict[(f2,f1)]
                # print('Found')
            else:
                bb_score = default_value
                # print('Not found: ', (f1,f2))

            if (f1,f2) in ml_dict:
                ml_score = ml_dict[(f1,f2)]
                # print('Found')
            elif (f2,f1) in ml_dict:
                ml_score = ml_dict[(f2,f1)]
                # print('Found')
            else:
                ml_score = default_value
                # print('Not found: ', (f1,f2))

            if (f1,f2) in gr_dict:
                gr_score = gr_dict[(f1,f2)]
                # print('Found')
            elif (f2,f1) in gr_dict:
                gr_score = gr_dict[(f2,f1)]
                # print('Found')
            else:
                gr_score = default_value
                # print('Not found: ', (f1,f2))

            bb_data[f1].append(bb_score)
            ml_data[f1].append(ml_score)
            gr_data[f1].append(gr_score)

        '''
        Dump all scores to Excel file
        offsetting by number of skipped entries to give triangular matrix
        '''
        for i,el in enumerate(bb_data[f1]):
            bb_sheet.write(y+1, i+y+1, el)
            ml_el = ml_data[f1][i]
            ml_sheet.write(y+1, i+y+1, ml_el)
            gr_el = gr_data[f1][i]
            gr_sheet.write(y+1, i+y+1, gr_el)

        _done.append(f1)
        # print(_done)

        ''' Counter to ensure triangular matrix '''
        y += 1


    ''' Must close workbook! '''
    workbook.close()

    # return (files_sorted, bb_dict, ml_dict, gr_dict, bb_data, ml_data, gr_data)
    return tree_list


''' HR 28/10/21 From PartCompare but needs to go here '''
def do_all_sims(step_folder):

    ''' HR 28/10/21 Initialise PartCompare here '''
    pc = PartCompare()

    if not os.path.isdir(step_folder):
        print('Folder not found; aborting...')
        return

    files = [file for file in os.listdir(step_folder) if file.endswith('STEP')]
    print('STEP files found:\n')
    print(files)

    if not files:
        print('No STEP files found in folder ', step_folder, '; aborting...')
        return

    ''' Populate file dicts '''
    shape_dict = {file:list(dex.read_step_file_with_names_colors(os.path.join(step_folder, file)))[0] for file in files}

    graph_dict = {}
    for file in files:
        try:
            full_file = os.path.join(step_folder, file)
            print('\nCreating graph for file ', full_file)
            graph_dict[file] = load_from_step(full_file)
            print('Graph created ', full_file)
        except:
            graph_dict[file] = None
            print('\nCould not create graph for ', file)

    print('Done all graphs')

    ar_dict = {}
    for file in files:
        ar_dict[file] = get_aspect_ratios(shape_dict[file])
    print('Got aspect ratios')


    try:
        scores_bb_loaded = load_from_txt(os.path.join(step_folder, 'scores_bb.txt'))
    except:
        scores_bb_loaded = {}
    print('BB load done')

    try:
        scores_loaded = load_from_txt(os.path.join(step_folder, 'scores.txt'))
    except:
        scores_loaded = {}
    print('ML load done')

    try:
        scores_graphlet_loaded = load_from_txt(os.path.join(step_folder, 'scores_graphlet.txt'))
    except:
        scores_graphlet_loaded = {}
    print('GR load done')

    # self.loaded = [scores_bb_loaded, scores_loaded, scores_graphlet_loaded]

    default_value = -1
    buffer_size = 10

    done = []
    scores = {}
    scores_graphlet = {}
    scores_bb = {}


    count = 0

    for file in files:
        try:
            # g1 = load_from_step(os.path.join(step_folder, file))
            g1 = graph_dict[file]
        except:
            g1 = None

        ''' Get OCC shape 1 '''
        # sh1 = dex.read_step_file_with_names_colors(os.path.join(step_folder, file))
        # sh1 = list(sh1)[0]
        # sh1 = shape_dict[file]
        ar1 = ar_dict[file]

        to_do = [el for el in files if el not in done]
        for file2 in to_do:
            try:
                # g2 = load_from_step(os.path.join(step_folder, file2))
                g2 = graph_dict[file2]
            except:
                g2 = None

            ''' Get OCC shape 2 '''
            # sh2 = dex.read_step_file_with_names_colors(os.path.join(step_folder, file2))
            # sh2 = list(sh2)[0]
            # sh2 = shape_dict[file2]
            ar2 = ar_dict[file2]

            if (file,file2) in scores_loaded:
                print('Score ML found')
                scores[(file,file2)] = scores_loaded[(file,file2)]
            else:
                print('Score ML not found; calculating...')
                try:
                    score = pc.model.test_pair(g1,g2)
                    scores[(file,file2)] = score
                    print('ML score: ', score)
                except Exception as e:
                    print(e)
                    print('ML score not calculated, setting default value')
                    scores[(file,file2)] = default_value

            if (file,file2) in scores_graphlet_loaded:
                print('Score GR found')
                scores_graphlet[(file,file2)] = scores_graphlet_loaded[(file,file2)]
            else:
                print('Score GR not found; calculating...')
                try:
                    # score = graphlet_pair_compare(g1,g2)
                    scores_graphlet[(file,file2)] = pc.gpc(g1, g2)
                except Exception as e:
                    print(e)
                    scores_graphlet[(file,file2)] = default_value

            if (file,file2) in scores_bb_loaded:
                print('Score BB found')
                scores_bb[(file,file2)] = scores_bb_loaded[(file,file2)]
            else:
                print('Score BB not found; calculating...')
                try:
                    scores_bb[(file,file2)] = get_bb_score(ar1,ar2)
                except:
                    scores_bb[(file,file2)] = default_value

            count += 1
            print('Count = ', count)

            ''' Save if buffer limit reached '''
            if (count % buffer_size == 0) or (file2 == to_do[-1]):
                print('Saving buffer...')
                save_to_txt(scores, os.path.join(step_folder, 'scores.txt'))
                save_to_txt(scores_graphlet, os.path.join(step_folder, 'scores_graphlet.txt'))
                save_to_txt(scores_bb, os.path.join(step_folder, 'scores_bb.txt'))

        done.append(file)


''' HR June 21 Example usage to:
        (a) Split and render all images and STEP files from assembly;
        (b) Calculate all similarity scores; and
        (c) Dump all similarity data to Excel '''
def dump_all(step_file):

    # step_folder = remove_suffixes(step_file)
    step_folder = step_file

    ''' (a) '''
    sp = StepParse()
    sp.load_step(step_file)
    sp.split_and_render()

    ''' (b) '''
    # pc = PartCompare()
    step_folder = remove_suffixes(step_folder)
    do_all_sims(step_folder)

    ''' (c) '''
    scores_to_excel(step_folder)

