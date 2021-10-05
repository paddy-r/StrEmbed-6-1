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

import os
from OCC.Extend import DataExchange as dex

from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
# from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.TopoDS import TopoDS_Solid, TopoDS_Compound, TopoDS_Shell

import xlsxwriter
from step_parse_5_7 import StepParse, remove_suffixes

''' -------------------------------------------------------------- '''
''' Import all partfind stuff from TH
    For now, just sets/resets cwd and grabs code from scripts '''

# partfind_folder = "C:\_Work\_DCS project\__ALL CODE\_Repos\partfind\partfind for git"
partfind_folder = "C:\\Users\\prehr\\OneDrive - University of Leeds\\__WORK SYNCED\\_Work\\_DCS project\\__ALL CODE\\_Repos\\partfind\\partfind for git"
# sys.path.append(partfind_folder)

cwd_old = os.getcwd()
os.chdir(partfind_folder)

import dgl
from partfind_search_gui import networkx_to_dgl
from partgnn import PartGNN
from main import parameter_parser
from step_to_graph import StepToGraph

from utils import graphlet_pair_compare

''' Restore previous cwd '''
os.chdir(cwd_old)
''' -------------------------------------------------------------- '''



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



''' Get geometric absolute value
    i.e. min of a/b and b/a '''
def geo_abs(a,b):
    if a<b:
        return a/b
    else:
        return b/a



def get_bb_score(ar1, ar2):

    r1 = geo_abs(ar1[0], ar2[0])
    r2 = geo_abs(ar1[1], ar2[1])
    r3 = geo_abs(ar1[2], ar2[2])
    score = (r1+r2+r3)/3
    print('Score: ', score)
    return score



def get_aspect_ratios(shape, tol = 1e-6, use_mesh = True):
    ''' To get sorted list of aspect ratios of shape from bounding box
        Adapted from PythonOCC here:
        https://github.com/tpaviot/pythonocc-demos/blob/master/examples/core_geometry_bounding_box.py
        Copyright information below
        --- '''
    #Copyright 2017 Thomas Paviot (tpaviot@gmail.com)
    ##
    ##This file is part of pythonOCC.
    ##
    ##pythonOCC is free software: you can redistribute it and/or modify
    ##it under the terms of the GNU Lesser General Public License as published by
    ##the Free Software Foundation, either version 3 of the License, or
    ##(at your option) any later version.
    ##
    ##pythonOCC is distributed in the hope that it will be useful,
    ##but WITHOUT ANY WARRANTY; without even the implied warranty of
    ##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    ##GNU Lesser General Public License for more details.
    ##
    ##You should have received a copy of the GNU Lesser General Public License
    ##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

    print('Getting aspect ratios for ', shape)
    bbox = Bnd_Box()
    bbox.SetGap(tol)
    if use_mesh:
        mesh = BRepMesh_IncrementalMesh()
        mesh.SetParallelDefault(True)
        mesh.SetShape(shape)
        mesh.Perform()
        if not mesh.IsDone():
            raise AssertionError("Mesh not done.")
    brepbndlib_Add(shape, bbox, use_mesh)

    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    dx,dy,dz = xmax-xmin, ymax-ymin, zmax-zmin

    ar = sorted((dx/dy, dy/dz, dz/dx))
    print('Done BB calcs for ', shape)
    return ar



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



''' To combine all similarity calculation functionality in single class for ease '''
class PartCompare():

    def __init__(self):

        ''' 1. Change to partfind directory '''
        cwd_old = os.getcwd()
        os.chdir(partfind_folder)

        ''' 2. Initialise ML model '''
        args = parameter_parser()
        # self.model = PartGNN(args, save_folder = os.path.join(partfind_folder, "./trained_models/"))
        self.model = PartGNN(args)
        self.model.load_model()

        ''' 3. Change back to previous directory '''
        os.chdir(cwd_old)

        # if not step_folder:
        #     # step_folder = "C:\_Work\_DCS project\__ALL CODE\_Repos\StrEmbed-5-6\StrEmbed-5-6 for git\gears"
        #     # step_folder = "C:\\_Work\\_DCS project\\__ALL CODE\\_Repos\StrEmbed-5-6\\StrEmbed-5-6 for git\\assorted"
        #     # step_folder = "C:\\_Work\\_DCS project\\__ALL CODE\\_Repos\\StrEmbed-5-6\\StrEmbed-5-6 for git\\Torch Assembly"
        #     step_folder = "C:\\_Work\\_DCS project\\__ALL CODE\\_Repos\\StrEmbed-5-6\\StrEmbed-5-6 for git\\cakestep"
        #     # step_folder = "C:\\_Work\\_DCS project\\__ALL CODE\\_Repos\\StrEmbed-5-6\\StrEmbed-5-6 for git\\77170325_1"
        # self.step_folder = step_folder



    ''' Adapted from TH's "partfind_search_gui_hr" (deleted, now part of "partfind_search_gui") and "step_to_graph"
        Minimal code to get graphs of parts '''
    def load_from_step(self, step_file):
        s_load = StepToGraph(step_file)
        g_load = networkx_to_dgl(s_load.H)
        face_g = g_load.node_type_subgraph(['face'])
        g_out = dgl.to_homogeneous(face_g)
        return g_out



    ''' HR June 21 Unused method for computation of similarities for arbitrary pair of STEP files
        Keep as might be useful '''
    # ''' Adapted from old "graph_compare" script
    #     Takes two STEP files (full path) and returns BB, ML and GR similarities '''
    # def simple_sims(self, f1, f2):

    #     sh1 = list(dex.read_step_file_with_names_colors(f1))[0]
    #     sh2 = list(dex.read_step_file_with_names_colors(f2))[0]

    #     ar1 = get_aspect_ratios(sh1)
    #     ar2 = get_aspect_ratios(sh2)

    #     g1 = self.load_from_step(f1)
    #     g2 = self.load_from_step(f2)

    #     score_bb = get_bb_score(ar1,ar2)
    #     score_ml = self.model.test_pair(g1,g2)
    #     score_gr = graphlet_pair_compare(g1,g2)

    #     print('ML score: ', score_ml)
    #     print('GR score: ', score_gr)

    #     return score_bb, score_ml, score_gr



    def do_all_sims(self, step_folder):

        if not os.path.isdir(step_folder):
            print('Folder not found; aborting...')
            return

        files = [file for file in os.listdir(step_folder) if file.endswith('STEP')]
        if not files:
            print('No STEP files found in folder ', step_folder, '; aborting...')
            return

        ''' Populate file dicts '''
        shape_dict = {file:list(dex.read_step_file_with_names_colors(os.path.join(step_folder, file)))[0] for file in files}

        graph_dict = {}
        for file in files:
            try:
                print('\nCreating graph for file ', file)
                graph_dict[file] = self.load_from_step(os.path.join(step_folder, file))
                print('Graph created ', file)
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
                        scores[(file,file2)] = self.model.test_pair(g1,g2)
                    except Exception as e:
                        print(e)
                        scores[(file,file2)] = default_value

                if (file,file2) in scores_graphlet_loaded:
                    print('Score GR found')
                    scores_graphlet[(file,file2)] = scores_graphlet_loaded[(file,file2)]
                else:
                    print('Score GR not found; calculating...')
                    try:
                        # score = graphlet_pair_compare(g1,g2)
                        scores_graphlet[(file,file2)] = graphlet_pair_compare(g1,g2)
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

    step_folder = remove_suffixes(step_file)

    ''' (a) '''
    sp = StepParse()
    sp.load_step(step_file)
    sp.split_and_render()

    ''' (b) '''
    pc = PartCompare()
    pc.do_all_sims(step_folder)

    ''' (c) '''
    scores_to_excel(step_folder)


