# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 17:05:46 2021

@author: prehr
"""
''' -------------------------------------------------------------- '''
''' Import all partfind stuff from TH
    For now, just sets/resets cwd and grabs code from scripts '''

import os

partfind_folder = "C:\\Users\\prehr\\OneDrive - University of Leeds\\__WORK SYNCED\\_Work\\_DCS project\\__ALL CODE\\_Repos\\partfind_old\\partfind for git"

cwd_old = os.getcwd()
os.chdir(partfind_folder)

import dgl

from partfind_search_gui import networkx_to_dgl
from partgnn import PartGNN
from main import parameter_parser
from step_to_graph import StepToGraph

# from utils import graphlet_pair_compare

''' Restore previous cwd '''
os.chdir(cwd_old)
''' -------------------------------------------------------------- '''



''' Adapted from TH's "partfind_search_gui_hr" (deleted, now part of "partfind_search_gui") and "step_to_graph"
    Minimal code to get graphs of parts '''
def load_from_step(step_file):
    print('Creating graph from STEP file...')
    s_load = StepToGraph(step_file)
    g_load = networkx_to_dgl(s_load.H)
    face_g = g_load.node_type_subgraph(['face'])
    g_out = dgl.to_homogeneous(face_g)
    return g_out



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





