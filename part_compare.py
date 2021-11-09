# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 17:05:46 2021

@author: prehr
"""
''' -------------------------------------------------------------- '''
''' Import all partfind stuff from TH
    For now, just sets/resets cwd and grabs code from scripts '''

import os

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


    def gpc(self, g1, g2):
        ''' TO BE FINISHED
            Called from fileutils '''
        pass


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

