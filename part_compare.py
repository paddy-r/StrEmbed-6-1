# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 17:05:46 2021

@author: prehr
"""
''' -------------------------------------------------------------- '''
''' Import all partfind stuff from TH
    For now, just sets/resets cwd and grabs code from scripts '''

import os
import dgl
import sys

''' HR 01/07/22 Refactored to remove absolute paths and replace with relative paths;
                partfindv1 folder now in common place to this script '''

partfind_folder = os.path.join(os.path.dirname(__file__), 'partfindv1_frozen')
sys.path.insert(0, partfind_folder)

print('partfind folder:', partfind_folder)
cwd_old = os.getcwd()
os.chdir(partfind_folder)
# print('current:', os.getcwd())

# from partfind_search_gui import networkx_to_dgl
from partgnn import PartGNN
from main import parameter_parser
from step_to_graph import StepToGraph

from utils import graphlet_pair_compare

''' Restore previous cwd '''
os.chdir(cwd_old)
''' -------------------------------------------------------------- '''

def networkx_to_dgl(A_nx):
    # need to convert it into something dgl can work with
    node_dict = {} # to convert from A_nx nodes to dgl nodes
    part_count = 0
    assembly_count = 0
    face_count = 0

    face_str = []
    face_dst = []
    link_str = []
    link_dst = []
    assembly1_str = []
    assembly1_dst = []
    assembly2_str = []
    assembly2_dst = []

    #print("edges",A_nx.edges(data=True,keys=True))

    for node_str, node_dst, key, data in A_nx.edges(data=True,keys=True):
      t = data['type']
      # get nodes in dict
      tn_str = A_nx.nodes[node_str]['type']
      if node_str not in node_dict:
        if tn_str == 'part':
          node_dict[node_str] = part_count
          part_count += 1
        elif tn_str == "assembly":
          node_dict[node_str] = assembly_count
          assembly_count += 1
        elif tn_str == "face":
          node_dict[node_str] = face_count
          face_count += 1

      tn_dst = A_nx.nodes[node_dst]['type']
      if node_dst not in node_dict:
        if tn_dst == 'part':
          node_dict[node_dst] = part_count
          part_count += 1
        elif tn_dst == "assembly":
          node_dict[node_dst] = assembly_count
          assembly_count += 1
        elif tn_dst == "face":
          node_dict[node_dst] = face_count
          face_count += 1
      # there are three edge types so sort which ever one we are dealing with into that one

      if t == "face":
        assert tn_str == "face"
        assert tn_dst == "face"
        face_str.append(node_dict[node_str])
        face_dst.append(node_dict[node_dst])
      elif t == "link":
        # print("node_str, node_dst, key, data")
        # print(node_str, node_dst, key, data)
        # print("tn_str: ",tn_str)
        # print("tn_dst: ",tn_dst)
        assert tn_str == "face"
        assert tn_dst == "part"
        link_str.append(node_dict[node_str])
        link_dst.append(node_dict[node_dst])
      elif t == "assembly":
        assert tn_str == "assembly"
        assert tn_dst in ["assembly","part"]
        if tn_dst == "assembly":
          assembly1_str.append(node_dict[node_str])
          assembly1_dst.append(node_dict[node_dst])
        elif tn_dst == "part":
          assembly2_str.append(node_dict[node_str])
          assembly2_dst.append(node_dict[node_dst])

    # make heterograph
    A_dgl = dgl.heterograph({
      ('face','face','face') : ( face_str, face_dst ),
      ('face','link','part') : ( link_str, link_dst ), # part -> face
      ('assembly','assembly','part') : ( assembly2_str, assembly2_dst ), # these may be swapped around at some point
      ('assembly','assembly','assembly') : ( assembly1_str, assembly1_dst ),
      ('assembly','layer','part') : ([],[]),
      ('part','layer','part') : ([],[]),
      ('assembly','layer','assembly') : ([],[]),
      ('part','layer','assembly') : ([],[])
    })
    return A_dgl


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

        # ''' 1. Change to partfind directory '''
        # cwd_old = os.getcwd()
        # os.chdir(partfind_folder)

        ''' 2. Initialise ML model '''
        args = parameter_parser()
        # self.model = PartGNN(args, save_folder = os.path.join(partfind_folder, "./trained_models/"))
        self.model = PartGNN(args)
        self.model.load_model()

        # ''' 3. Change back to previous directory '''
        # os.chdir(cwd_old)





