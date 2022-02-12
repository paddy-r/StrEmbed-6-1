# HR 19/08/2019 to 10/12/2019
# Added all extra code I've done up to this point

# TH: I am using this to turn the script into a module file to make it useable else where
# We can add functionally as new things are made.

# HR July 2019
# To parse STEP file

### ---
# HR 12/12/2019 onwards
# Version 5.2
### ---

### ---
# HR 23/03/2020 onwards
# Version 5.3
### ---
# Removed treelib entirely, now using networkx for all operations
# A lot of old functionality replaced with simpler networkx methods

'''HR 11/08/20 onwards
Version 5.5'''

'''HR 02/12/20 onwards
Version 5.6 '''

''' HR 07/07/21
Version 5.7 '''

''' HR 05/10/21
Version 6.1
Copy of 5.7, to draw line under version 5
Version 6 to include major upgrade of BoM reconciliation functionality '''



# # Regular expression module
# import re

# Natural Language Toolkit module, for Levenshtein distance
import nltk

import numpy as np
from scipy.special import binom
# from math import log
# import pandas as pd

# # For powerset construction
# from itertools import chain, combinations

# def powerset(iterable):
#     "e.g. powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
#     s = list(iterable)
#     return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

# Import networkx for plotting lattice
import networkx as nx

''' MPL for default viewer if run outside GUI '''
import matplotlib as mpl

#TH: useful for working with files
import os

# ''' For data exchange export '''
# import xlsxwriter

# HR 10/7/20 All python-occ imports for 3D viewer
# from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Solid, TopoDS_Compound, TopoDS_Shell, TopoDS_Face, TopoDS_Vertex, TopoDS_Edge, TopoDS_Wire, TopoDS_CompSolid
# from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
# from OCC.Core.StlAPI import stlapi_Read, StlAPI_Writer
# from OCC.Core.BRep import BRep_Builder
# from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pnt2d
# from OCC.Core.Bnd import Bnd_Box2d
# from OCC.Core.TopoDS import TopoDS_Compound
# from OCC.Core.IGESControl import IGESControl_Reader, IGESControl_Writer
# from OCC.Core.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
# from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone
# from OCC.Core.IFSelect import IFSelect_ItemsByEntity
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.XCAFDoc import (XCAFDoc_DocumentTool_ShapeTool,
                              XCAFDoc_DocumentTool_ColorTool)
from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
from OCC.Core.TDF import TDF_LabelSequence, TDF_Label
from OCC.Core.TCollection import TCollection_ExtendedString
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

# from OCC.Extend.TopologyUtils import (discretize_edge, get_sorted_hlr_edges,
                                      # list_of_shapes_to_compound)

from OCC.Display import OCCViewer
from OCC.Core.Quantity import (Quantity_Color, Quantity_NOC_WHITE, Quantity_TOC_RGB)
from OCC.Extend import DataExchange
from OCC.Core.Graphic3d import Graphic3d_BufferType

from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
# from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh

''' HR 09/12/21 Adding PartCompare import to allow shape-based similarity scores '''
from part_compare import PartCompare, load_from_step

''' HR 12/12/21 For pickling graphs of shapes for faster retrieval in similarity scoring '''
import pickle

import hungarian_algorithm as hungalg



def remove_suffixes(_str, suffixes = ('.stp', '.step', '.STP', '.STEP')):
    ''' "endswith" accept tuple etc.'''
    while _str.endswith(suffixes):
        _str = os.path.splitext(_str)[0]
    return _str



''' HR 26/04/21
    To get lines (e.g. in STEP file) with certain keywords present or not
    Adapted from earlier script
    Keep here for now but not best place for it '''
def step_search(file, keywords = None, exclusions = None, any_mode = True):

    if not file:
        print('File not found; aborting')
        return

    if not keywords:
        keywords = ['NEXT_']
        # keywords = ['MANIFOLD', 'PRODUCT ', 'CLOSED', 'ADVANCED']

    if not exclusions:
        exclusions = ['kevinphilipsbong']

    results = []

    # with open(file) as f:
    #     for i,line in enumerate(f):
    #         if any(word in line for word in keywords) and not any(_word in line for _word in exclusions):
    #             results.append(line)

    ''' HR 4/5/21 updated to account for lines running over '''
    with open(file) as f:
        ''' Create empty running line to append text to '''
        full_line = ''
        for i,line in enumerate(f):
            ''' Append to running line, removing trailing newline chars '''
            full_line += line.replace('\n', '')
            ''' If ending line, do actual search... '''
            if line.endswith(';\n'):
                if any_mode:
                    if any(word in full_line for word in keywords) and not any(_word in full_line for _word in exclusions):
                        results.append(full_line)
                else:
                    if all(word in full_line for word in keywords) and not any(_word in full_line for _word in exclusions):
                        results.append(full_line)
                ''' ...and make new empty running line '''
                full_line = ''

    keyword_dict = {}
    for keyword in keywords:
        keyword_dict[keyword] = []
        for line in results:
            if keyword in line:
                keyword_dict[keyword].append(line)

    return results, keyword_dict



def get_aspect_ratios(shape, tol = 1e-6, use_mesh = True, return_dims = False):
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

    if return_dims:
        print('Returning absolute dimensions')
        return dx,dy,dz

    ar = sorted((dx/dy, dy/dz, dz/dx))
    print('Done BB calcs for ', shape)
    return ar



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



'''
HR 14/01/22 To calculate P-R-S (precision, recall, specificity) of matches
            i.e. success of matched pairs, compared to known correct matches
            See user manual for set algebra/derivations
Notation:
    T: true (i.e. correct)
    F: false (i.e. incorrect)
    P: positive (i.e. match)
    N: negative (i.e. non-match)
    M: set of true matches
    mu: set of actual matches
    N: set of true matches
    nu: set of actual matches
    P = TP/(TP + FP)
    R = TP/(TP + FN)
    S = TN/(TN + FP)
'''
def get_matching_success(n_a, n_b, M = {}, mu = {}):

    ''' Get cardinalities of each set '''
    TP = len(mu & M)
    FP = len(mu - M)
    TN = n_a*n_b - len(mu | M)
    FN = len(M - mu)

    ''' Get P-R-S '''
    P = TP/(TP + FP)
    R = TP/(TP + FN)
    S = TN/(TN + FP)

    return P,R,S



"""
HR 26/08/2020
ShapeRenderer adapted from pythonocc script "wxDisplay"
https://github.com/tpaviot/pythonocc-core
"""
class ShapeRenderer(OCCViewer.Viewer3d):
    '''
    HR 17/7/20
    Adapted/simplified from OffScreenRenderer in OCCViewer <- OCC.Display
    Dumps render of shape to jpeg file
    '''
    def __init__(self, screen_size = (1000,1000)):
        super().__init__()
        self.Create()
        self.View.SetBackgroundColor(Quantity_Color(Quantity_NOC_WHITE))
        self.SetSize(screen_size[0], screen_size[1])
        # self.DisableAntiAliasing()
        self.SetModeShaded()
        # self.display_triedron()
        self.SetRaytracingMode(depth = 5)
        self._rendered = False





''' To contain lattice structure that manages/contains all assemblies '''
class AssemblyManager():

    def __init__(self, viewer = None, axes = None, ic = None, dc = None, sc = None, lc = None, lattice_plot_mode = True, *args, **kwargs):
        self._mgr = {}
        self._lattice = StepParse('lattice')

        self.pc = PartCompare()

        ''' -----------------------------
        ALL MATCHING/RECONCILIATION STUFF
        ----------------------------- '''
        ''' Weights, constants, etc. '''
        self.MATCHING_WEIGHTS_DEFAULT = [1,1,1,1]
        self.MATCHING_WEIGHTS_STRUCTURE_DEFAULT = [1,1,1,1]
        self.MATCHING_C1_DEFAULT = 0
        self.MATCHING_C2_DEFAULT = 0
        self.MATCHING_FIELD_DEFAULT = 'occ_name'
        self.MATCHING_TOLERANCE_DEFAULT = 0
        self.MATCHING_SCORE_DEFAULT = -1
        self.MATCHING_BB_TOL_DEFAULT = 1e-4
        self.MATCHING_BB_GROUP_TOL_DEFAULT = 1e-3
        self.MATCHING_TEXT_SUFFIXES_DEFAULT = ('.STEP', '.STP', '.step', 'stp')
        self.MATCHING_TEXT_TOL_DEFAULT = 5e-2
        ''' ----------------------------- '''

        # self.new_assembly_text = 'Unnamed item'
        # self.new_part_text     = 'Unnamed item'

        self.ENFORCE_BINARY_DEFAULT = False
        self.DO_ALL_LATTICE_LINES = True

        '''
            Set up lattice plot viewer
            Default is MPL viewer
        '''
        if viewer:
            self.viewer = viewer
        else:
            self.viewer = mpl.pyplot.figure()
        if axes:
            self.axes = axes
        else:
            self.axes = self.viewer.add_subplot(111)

        ''' Turn off all axis lines and ticks '''
        self.axes.axis('off')
        self.axes.axes.get_xaxis().set_ticks([])
        self.axes.axes.get_yaxis().set_ticks([])

        self._lattice.origin = (0,0)

        self.lattice_plot_mode = lattice_plot_mode

        ''' Set up colouring '''
        self.INACTIVE_COLOUR_DEFAULT = 'darkgray'
        self.DEFAULT_COLOUR_DEFAULT = 'red'
        self.SELECTED_COLOUR_DEFAULT = 'blue'
        self.LINE_COLOUR_DEFAULT = 'lightgray'

        if not ic:
            self.ic = self.INACTIVE_COLOUR_DEFAULT
        else:
            self.ic = ic
        if not dc:
            self.dc = self.DEFAULT_COLOUR_DEFAULT
        else:
            self.dc = dc
        if not sc:
            self.sc = self.SELECTED_COLOUR_DEFAULT
        else:
            self.sc = sc
        if not lc:
            self.lc = self.LINE_COLOUR_DEFAULT
        else:
            self.lc = lc



    @property
    def new_assembly_id(self):
        if not hasattr(self, "assembly_id_counter"):
            self.assembly_id_counter = 0
        self.assembly_id_counter += 1
        return self.assembly_id_counter



    def new_assembly(self, dominant = None):
        assembly_id = self.new_assembly_id
        assembly = StepParse(assembly_id)
        self._mgr.update({assembly_id:assembly})
        print('Created new assembly with ID: ', assembly_id)

        assembly.enforce_binary = self.ENFORCE_BINARY_DEFAULT

        return assembly_id, assembly



    def remove_assembly(self, _id):
        if _id in self._mgr:
            print('Assembly ', _id, 'found in and removed from manager')
            ''' Try and remove from lattice '''
            self.RemoveFromLattice(_id)
            self._mgr.pop(_id)
            return True
        else:
            print('Assembly ', _id, 'not found in manager; could not be removed')
            return False



    ''' Get lattice node corresponding to node in given assembly
        Return lattice node if present, otherwise None '''
    def get_master_node(self, assembly_id, item):
        for node in self._lattice.nodes:
            for k,v in self._lattice.nodes[node].items():
                if k == assembly_id and v == item:
                    return node
        return None





    ''' ----------------------------------------------------------------------
        ----------------------------------------------------------------------
        HR JAN 2021 ASSEMBLY OPERATIONS TO BE REFERRED TO IN GUI
        Plan:
        - Copy existing methods from GUI and check they're working
        - Goal is to remove any reference to individual assemblies in GUI,
            all interactions in GUI should be with assembly manager here
        - COMPLETE FEB 2021! I am a neat guy!
    '''



    def add_edge_in_lattice(self, _id, u, v):

        '''
        Assembly-specific operations
        '''
        ass = self._mgr[_id]
        ass.add_edge(u, v)

        '''
        Lattice operations
        '''
        um = self.get_master_node(_id, u)
        vm = self.get_master_node(_id, v)

        if (um,vm) in self._lattice.edges:
            print('Edge already exists; adding entry')
        else:
            print('Edge does not exist in lattice; creating new edge and entry')
            print(' ', um,vm)
            self._lattice.add_edge(um,vm)
        self._lattice.edges[(um,vm)].update({_id:(u,v)})




    def remove_edge_in_lattice(self, _id, u, v):

        '''
        Assembly-specific operations
        '''
        ass = self._mgr[_id]
        ass.remove_edge(u, v)

        '''
        Lattice operations
        '''
        um = self.get_master_node(_id, u)
        vm = self.get_master_node(_id, v)

        _len = len(self._lattice.edges[(um,vm)])
        if _len == 1:
            print('Edge dict has len = 1; removing whole edge')
            self._lattice.remove_edge(um,vm)
        else:
            print('Edge dict has len > 1; removing edge dict entry for assembly')
            self._lattice.edges[(um,vm)].pop(_id)



    def add_node_in_lattice(self, _id, parent, disaggregate = False, **attr):

        ass = self._mgr[_id]
        leaves = ass.leaves

        ''' Allow node to be added to leaf if "disaggregate" flag is true '''
        if parent not in leaves:
            print('ID of node to add node to: ', parent)
        else:
            if not disaggregate:
                print('Cannot add node: item is a leaf node/irreducible part')
                print('To add node, disaggregate part first')
                return

        node = ass.new_node_id

        '''
        Assembly-specific operations
        '''
        ass.add_node(node, **attr)

        '''
        Lattice operations
        '''
        nodem = self._lattice.new_node_id
        self._lattice.add_node(nodem)
        self._lattice.nodes[nodem].update({_id:node})

        self.add_edge_in_lattice(_id, parent, node)

        return node, nodem



    def enforce_binary(self, _id, node):

        ass = self._mgr[_id]

        ''' Abort if not enforced '''
        if not ass.enforce_binary:
            print('Not enforcing binary relations; disallowed for assembly ', _id)
            return

        parent = ass.get_parent(node)
        children = [el for el in ass.successors(node)]

        ''' Abort if more than one child '''
        if not len(children) == 1:
            return

        print('Single child; removing and linking past node')
        print('Assembly ', _id, '; node ', node)

        ''' Reparent orphans-to-be '''
        for child in children:
            self.move_node_in_lattice(_id, child, parent)

        ''' Finally, remove redundant node '''
        print('  Removing node in lattice in "enforce_binary"')
        self.remove_node_in_lattice(_id, node)



    def remove_node_in_lattice(self, _id, node):

        ass = self._mgr[_id]
        nm = self.get_master_node(_id, node)

        parent = ass.get_parent(node)
        leaves = ass.leaves

        '''
        NOTES
        - Order of operations is unusual here, to avoid missing edges
        1. Reparent (move) children, if node is sub-assembly,
            with veto of binary enforcement (as not necessary if sub-ass)
        2. Other redundant edges are then removed in lattice first
        3. Then node/edges removed in assembly
        4. Then remaining node/edge references removed in lattice dicts
        5. Last, binary relations enforced if necessary
        '''

        ''' Reparent orphans to node parent if node is sub-assembly '''
        if node not in leaves:
            orphans = [el for el in ass.successors(node)]
            for orphan in orphans:
                self.move_node_in_lattice(_id, orphan, parent, veto_binary = True)

        ins = list(ass.in_edges(node))
        outs = list(ass.out_edges(node))

        ''' Remove now-redundant edges (lattice) '''
        edges = ins + outs
        for edge in edges:
            print('Removing edge: ', edge[0], edge[1])
            self.remove_edge_in_lattice(_id, edge[0], edge[1])

        ''' Remove node and edges (assembly) '''
        ass.remove_node(node)

        ''' Remove node (dicts in lattice) '''
        _len = len(self._lattice.nodes[nm])
        if _len == 1:
            print('Node dict has len = 1; removing whole node')
            self._lattice.remove_node(nm)
        else:
            print('Node dict has len > 1; removing node dict entry for assembly')
            self._lattice.nodes[nm].pop(_id)

        ''' If original node is leaf, enforce binary relations if necessary '''
        if node in leaves:
            self.enforce_binary(_id, parent)



    def move_node_in_lattice(self, _id, node, parent, veto_binary = False):

        ass = self._mgr[_id]
        old_parent = ass.get_parent(node)

        if old_parent == parent:
            return

        ''' Check if is root, i.e. has no parent '''
        if (old_parent is None):
            print('Root node cannot be moved; not proceeding')
            return False

        ''' Remove old edge '''
        self.remove_edge_in_lattice(_id, old_parent, node)

        ''' Create new edge '''
        self.add_edge_in_lattice(_id, parent, node)

        ''' Enforce binary relations if necessary '''
        if not veto_binary:
            self.enforce_binary(_id, old_parent)

        return True



    def assemble_in_lattice(self, _id, nodes, **attr):

        ass = self._mgr[_id]

        ''' Check root is not present in nodes '''
        root = ass.get_root()
        if root in nodes:
            nodes.remove(root)
            print('Removed root from items to assemble')

        '''
        MAIN "ASSEMBLE" ALGORITHM
        '''

        ''' Get selected item that is highest up tree (i.e. lowest depth) '''
        depths = {}
        for node in nodes:
            depths[node] = ass.node_depth(node)
            print('ID = ', node, '; parent depth = ', depths[node])
        highest_node = min(depths, key = depths.get)
        new_parent = ass.get_parent(highest_node)
        print('New parent = ', new_parent)

        ''' Get valid ID for new node then create '''
        new_sub, _ = self.add_node_in_lattice(_id, new_parent, **attr)

        ''' Move all selected items to be children of new node '''
        for node in nodes:
            self.move_node_in_lattice(_id, node, new_sub)

        # ''' HR 03/12/21 To try and resolve wrong node positioning '''
        # _ass.remove_redundants()
        # if not new_sub in _ass.nodes:
        #     new_sub = None

        return new_sub



    def flatten_in_lattice(self, _id, node):

        ass = self._mgr[_id]
        leaves = ass.leaves
        print('Leaves: ', leaves)

        if node not in leaves:
            print('ID of item to flatten = ', node)
        else:
            print('Cannot flatten: item is a leaf node/irreducible part\n')
            return

        '''
        MAIN "FLATTEN" ALGORITHM
        '''

        ''' Get all children of item '''
        ch = nx.descendants(ass, node)
        ch_parts = [el for el in ch if el in leaves]
        print('Children parts = ', ch_parts)
        ch_ass = [el for el in ch if not el in leaves]
        print('Children assemblies = ', ch_ass)

        ''' Move all children that are indivisible parts '''
        for child in ch_parts:
            self.move_node_in_lattice(_id, child, node)

        ''' Delete all children that are assemblies '''
        for child in ch_ass:
            self.remove_node_in_lattice(_id, child)

        return True



    def disaggregate_in_lattice(self, _id, node, num_disagg = 2, **attr):

        ass = self._mgr[_id]
        leaves = ass.leaves

        if node in leaves:
            print('ID of item to disaggregate = ', node)
        else:
            print('Cannot disaggregate: item is not a leaf node/irreducible part\n')
            return

        '''
        MAIN "DISAGGREGATE" ALGORITHM
        '''

        ''' Get valid ID for new node then create '''
        new_nodes = []
        for i in range(num_disagg):
            new_node, _ = self.add_node_in_lattice(_id, node, disaggregate = True, **attr)
            new_nodes.append(new_node)

        return new_nodes



    def aggregate_in_lattice(self, _id, node):

        ass = self._mgr[_id]
        leaves = ass.leaves

        if not node in leaves:
            print('ID of item to aggregate = ', node)
        else:
            print('Cannot aggregate: item is a leaf node/irreducible part\n')
            return

        '''
        MAIN "AGGREGATE" ALGORITHM
        '''

        ''' Get children of node and remove '''
        removed_nodes = []
        ch = nx.descendants(ass, node)
        print('Children aggregated: ', ch)
        for child in ch:
            try:
                self.remove_node_in_lattice(_id, child)
                print('Removed node ', child)
                removed_nodes.append(child)
            except:
                print('Could not delete node')

        return removed_nodes



    ''' ----------------------------------------------------------------------
        ADD TO/REMOVE FROM LATTICE
        ----------------------------------------------------------------------
    '''



    def AddToLattice(self, _id, dominant = None):

        if not self._mgr:
            print('Cannot add assembly to lattice: no assembly in manager')
            return False

        if _id not in self._mgr:
            print('ID: ', _id)
            print('Assembly not in manager; not proceeding')
            return False

        ''' If first assembly being added, just map nodes and edges directly
            No need to do any similarity calculations '''
        if len(self._mgr) == 1:

            print('Adding first assembly to lattice')
            a1 = self._mgr[_id]

            for node in a1.nodes:
                new_node = self._lattice.new_node_id
                self._lattice.add_node(new_node)
                self._lattice.nodes[new_node].update({_id:node})

            ''' Nodes must exist as edges require "get_master_node" '''
            for n1,n2 in a1.edges:
                u = self.get_master_node(_id, n1)
                v = self.get_master_node(_id, n2)
                self._lattice.add_edge(u,v)
                self._lattice.edges[(u,v)].update({_id:(n1,n2)})

            return True



        ''' If no dominant assembly specified/not found
            get the one with lowest ID '''
        if (not dominant) or (dominant not in self._mgr):
            print('Dominant assembly not specified or not found in manager; defaulting to assembly with lowest ID')
            idlist = sorted([el for el in self._mgr])
            idlist.remove(_id)
            dominant = idlist[0]



        ''' Assemblies to be compared established by this point '''
        print('ID of dominant assembly in manager: ', dominant)
        print('ID of assembly to be added:         ', _id)

        id1 = dominant
        id2 = _id

        a1 = self._mgr[id1]
        a2 = self._mgr[id2]
        print('a1 nodes: ', a1.nodes)
        print('a2 nodes: ', a2.nodes)



        '''
        MAIN SECTION:
            1. DO NODE COMPARISON AND COMPUTE PAIR-WISE SIMILARITIES
            2. GET NODE MAP BETWEEN DOMINANT AND NEW ASSEMBLIES
            3. ADD NEW ASSEMBLY TO LATTICE GRAPH
        '''
        results = self.map_nodes(a1, a2)

        ''' Get node map (n1:n2) and lists of unmapped nodes in a1 and a2 '''
        _map = results[0]
        u1, u2 = results[1]

        ''' Show results '''
        print('Mapping results: ')
        f = 'screen_name'
        for k,v in results[0].items():
            print('a1 node: ', a1.nodes[k][f], 'a2 node: ', a2.nodes[v][f])

        '''
            NODES
        '''

        ''' Append to existing master node dict if already present... '''
        for n1,n2 in _map.items():
            ''' Returns None if not present... '''
            master_node = self.get_master_node(id1, n1)
            ''' ...but if already present, add... '''
            if master_node:
                self._lattice.nodes[master_node].update({id2:n2})

        ''' ...else create new master node entry '''
        for n2 in u2:
            node = self._lattice.new_node_id
            self._lattice.add_node(node)
            self._lattice.nodes[node].update({id2:n2})


        '''
            EDGES
        '''

        for n1,n2 in a2.edges:
            m1 = self.get_master_node(id2, n1)
            m2 = self.get_master_node(id2, n2)
            if m1 and m2:
                ''' Create master edge if not present '''
                if (m1,m2) not in self._lattice.edges:
                    self._lattice.add_edge(m1,m2)
                ''' Lastly, create new entry '''
                self._lattice.edges[(m1,m2)].update({id2:(n1,n2)})

        return True



    def RemoveFromLattice(self, _id):

        if not self._mgr:
            print('Cannot remove assembly from lattice: no assembly in manager')
            return False

        if _id not in self._mgr:
            print('ID: ', _id)
            print('Assembly not in manager; not proceeding')
            return False

        ''' CASE 1: Lattice only contains single assembly '''
        if len(self._mgr) == 1:
            nodes = [node for node in self._lattice.nodes]
            ''' Edges will be removed automatically when their nodes are removed '''
            for node in nodes:
                self._lattice.remove_node(node)
            return True

        ''' CASE 2: Lattice has more than one assembly in it '''
        nodes = list(self._lattice.nodes)
        edges = list(self._lattice.edges)

        for edge in edges:
            _dict = self._lattice.edges[edge]
            if _id in _dict:
                ''' Remove entry for assembly in lattice dict... '''
                _dict.pop(_id)
                if not any(ass in _dict for ass in self._mgr):
                    ''' ...and remove entirely if no other assemblies in dict '''
                    self._lattice.remove_edge(edge[0],edge[1])

        for node in nodes:
            dict = self._lattice.nodes[node]
            if _id in _dict:
                ''' Remove entry for assembly in lattice dict... '''
                dict.pop(_id)
                if not any(ass in dict for ass in self._mgr):
                    ''' ...and remove entirely if no other assemblies in dict '''
                    self._lattice.remove_node(node)

        return True



    ''' ----------------------------------------------------------------------
        HR June 21: All similarity/assembly matching methods here,
            refactored from StepParse class methods
        ----------------------------------------------------------------------
    '''



    '''
    HR June 21 Must refactor this, moved from StepParse class method
    NOT TESTED
    '''
    # ''' ---------------
    # TREE RECONCILIATION
    # HR 3/6/20
    # Based on Networkx "optimal_edit_paths" method

    # a1 and a2 are assemblies 1 and 2
    # Call as "paths, cost = StepParse.Reconcile(a1, a2)"
    # ----------------'''

    def Reconcile(self, id1, id2, lev_tol = 0.1):

        ''' -------------------------------------------
        STAGE 1: MAP NODES/EDGES B/T THE TWO ASSEMBLIES

        Currently done simply via tags
        More sophisticated metrics to be implemented in future

        Method of assembly class (StepParse) to set item tags to their IDs
        --------------------------------------------'''
        a1 = self._mgr[id1]
        a2 = self._mgr[id2]

        a1.set_all_tags()
        a2.set_all_tags()



        def similarity(str1, str2):

            _lev_dist  = nltk.edit_distance(str1, str2)
            _sim = 1 - _lev_dist/max(len(str1), len(str2))

            return _lev_dist, _sim



        # def remove_special_chars(_str):

        #     # Strip out special characters
        #     _str = re.sub('[!@#$_]', '', _str)

        #     return _str



        ''' Comparing nodes directly gives equality simply if both are NX nodes...
            ...i.e. same object type, but this isn't good enough...'
            ...so equality in this context defined as having same tags '''
        def return_eq(item1, item2):

            _eq = False

            tag1 = item1['tag']
            tag2 = item2['tag']

            ''' 1. Simple equality test based on tags
                (which are just IDs copied to "tag" field)... '''
            _eq = tag1 == tag2
            if _eq:
                print('Mapped ', tag1, 'to ', tag2)

            # ''' 2. ...then do test based on parts contained by nodes... '''
            # if tag1 and tag2 in (a1.nodes or a2.nodes) and not _eq:
            #     try:
            #         _eq = item1['parts'] == item2['parts']
            #     except:
            #         pass

            # ''' 3. ...then do test based on Levenshtein distance b/t items, if leaves '''
            # if not _eq and (tag1 and tag2 in (a1.leaves or a2.leaves)):

            #     tag1_ = remove_special_chars(tag1)
            #     tag2_ = remove_special_chars(tag2)

            #     try:
            #         dist = similarity(tag1_, tag2_)
            #         _eq  = dist < lev_tol
            #     except:
            #         pass

            # if _eq:
            #     print('Nodes/edges mapped:     ', tag1, tag2)
            # else:
            #     pass

            return _eq
            # return item1 == item2




        def MyReconcile(a1, a2, node_match = None, edge_match = None):

            a1.set_all_tags()
            a2.set_all_tags()

            n1 = set(a1.nodes)
            n2 = set(a2.nodes)
            e1 = set(a1.edges)
            e2 = set(a2.edges)

            node_deletions = []
            node_additions = []
            edge_deletions = []
            edge_additions = []

            ''' Find additions and deletions by set difference (relative complement) '''
            #
            for node in n1 - n2:
                node_deletions.append((node, None))
            print('Node deletions: ', node_deletions)

            for node in n2 - n1:
                node_additions.append((None, node))
            print('Node deletions: ', node_additions)

            for edge in e1 - e2:
                edge_deletions.append((edge, None))
            print('Edge deletions: ', edge_deletions)

            for edge in e2 - e1:
                edge_additions.append((None, edge))
            print('Edge additions: ', edge_additions)



            paths = [list(set(node_deletions + node_additions)), list(set(edge_deletions + edge_additions))]

            cost = len(node_deletions) + len(node_additions) + len(edge_deletions) + len(edge_additions)

            return paths, cost


        ''' -----------------------------------------------------
        STAGE 2: FIND EDIT PATHS VIA NETWORKX AND GENERATE REPORT
        ------------------------------------------------------'''

        # paths, cost_nx = nx.optimal_edit_paths(a1, a2, node_match = return_eq, edge_match = return_eq)
        # paths = paths[0]

        paths, cost = MyReconcile(a1, a2, node_match = return_eq, edge_match = return_eq)

        node_edits = [el for el in paths[0] if el[0] != el[1]]
        edge_edits = [el for el in paths[1] if el[0] != el[1]]
        cost_from_edits = len(node_edits) + len(edge_edits)

        print('Node edits: {}\nEdge edits: {}\nTotal cost (Networkx): {}\nTotal cost (no. of edits): {}'.format(
            node_edits, edge_edits, cost, cost_from_edits))

        return paths, cost, cost_from_edits, node_edits, edge_edits



    ''' ---------------------------------------------------------
        ALL NEWER RECONCILIATION CODE
        JAN 2022 ONWARDS
        --------------------------------------------------------- '''



    ''' HR 20/01/22
        Matching strategy set-up, to return set of matches based on series of blocking/matching stages
        Matched, unmatched and non-matches pairs passed from one stage to next
        Stages differ in terms of:  (a) Metrics used for comparison (via weight vectors)
                                    (b) Whether blocking or matching '''
    def matching_strategy(self, id1, id2, nodes1 = None, nodes2 = None, stages = None):

        ''' LEAVE THIS LOT HERE FOR NOW; MOVE LATER '''

        ''' Basic matching strategy:
        1. Block ('b') by item name
        2. Match ('m') within each block with weights [0,1,1,0], i.e.
            ignore item names and shapes,
            equal weights for local structure and bounding box-based metrics '''
        if not hasattr(self, 'MATCHING_STRATEGY_METHODS'):
            self.MATCHING_STRATEGY_METHODS = {'bn': self.block_by_name,
                                              'bb': self.block_by_bb,
                                              'mb': self.match_block}

        if not hasattr(self, 'MATCHING_STRATEGY_STAGES_DEFAULT'):
            self.MATCHING_STRATEGY_STAGES_DEFAULT = [(('bn', {}), ('mb', {'weights': [0,1,1,0]}))]



        ''' Check for/set defaults '''
        if not nodes1:
            a1 = self._mgr[id1]
            nodes1 = a1.nodes
        if not nodes2:
            a2 = self._mgr[id2]
            nodes2 = a2.nodes

        if not stages:
            stages = self.MATCHING_STRATEGY_STAGES_DEFAULT

        print('\n### Starting matching strategy with ', len(stages), ' stages... ###\n')

        ''' Initiate node lists, which are modified throughout the matching process
            and from which matches and non-matches can be derived at any point;
            definitions of node sets are:
                lambda = all possible node pairs
                mu     = matched pairs
                nu     = non-matched pairs
                tau    = (as-yet) unmatched pairs

            Notation below is used for node lists:
                e.g. nu1 and nu2 are node lists for nu assemblies 1 and 2 such that:
                nu = set(zip(nu1,nu2)) '''

        ''' Initiate node sets/lists '''
        mu = set()
        # nu = set()
        tau = set()

        mu1 = []
        mu2 = []
        # nu1 = []
        # nu2 = []
        tau1 = [el for el in nodes1]
        tau2 = [el for el in nodes2]

        for i, stage in enumerate(stages):

            ''' Grab all blocking sub-stage information and do blocking '''
            blocking_method, blocking_kwargs = stage[0]
            if (not blocking_method) or (blocking_method not in self.MATCHING_STRATEGY_METHODS):
                print('Blocking stage method not found; skipping stage and defaulting to all unmatched nodes')
                blocks = [(tau1, tau2)]
            else:
                ''' Do blocking sub-stage here and return list of blocks '''
                blocking_method = self.MATCHING_STRATEGY_METHODS[blocking_method]
                print('Running ', blocking_method.__name__,
                      '\n with assembly IDs ', id1, id2,
                      '\n node lists ', tau1, tau2,
                      '\n and kwargs: ', blocking_kwargs)
                blocks = blocking_method(id1, id2, tau1, tau2, **blocking_kwargs)

            print('Blocks: ', blocks)

            ''' Set up matching sub-stage '''
            matches = set()
            non_matches = set()

            ''' Grab all matching sub-stage information and do matching '''
            matching_method, matching_kwargs = stage[1]
            if (not matching_method) or (matching_method not in self.MATCHING_STRATEGY_METHODS):
                print('Matching stage method not found; skipping stage and defaulting to all unmatched nodes')
            else:
                ''' Execute matching function according to stage specification '''
                matching_method = self.MATCHING_STRATEGY_METHODS[matching_method]
                for j, (block_k, block_v) in enumerate(blocks.items()):
                    ''' Match within each block '''
                    print('Running ', matching_method.__name__,
                          '\n with assembly IDs ', id1, id2,
                          '\n in block with node lists ', block_v[0], block_v[1],
                          '\n and kwargs: ', matching_kwargs)
                    matches_in_block , non_matches_in_block = matching_method(id1, id2, block_v[0], block_v[1], **matching_kwargs)

                    print('Matches in block {} of {} and stage {} of {}:\n'.format(
                        j+1, len(blocks), i+1, len(stages)), matches_in_block)

                    ''' Update set of matches within current stage '''
                    print('Matches: ', matches)
                    print('Matches in block: ', matches_in_block)
                    matches = matches | set(matches_in_block)

            ''' Add to master set/lists of matches and unmatches '''
            print('Matches: ', matches)
            print('mu:      ', mu)
            mu = matches | mu
            # ''' Remove matches from unmatched sets '''
            # nu = nu - mu

            matches1 = [el[0] for el in matches]
            matches2 = [el[1] for el in matches]
            mu1.extend(matches1)
            mu2.extend(matches2)

            tau1 = [el for el in tau1 if el not in mu1]
            tau2 = [el for el in tau2 if el not in mu2]

            print('Matching stages done; returning set of matches: ', mu)

        return mu, mu1, mu2



    ''' HR 19/01/22
        To  (1) grab existing matches from lattice nodes for specified assemblies, or
            (2) grab notional matches from one BoM, for when it is to be duplicated,
                i.e. assume same nodes IDs in BoM1 as in notional BoM2
        Returns dictionary of master_node: (node1,node2) in case master node needed later '''
    def grab_matches(self, id1, id2 = None):
        matches = {}
        for latt_node in self._lattice.nodes:
            node_dict = self._lattice.nodes[latt_node]
            if (id1 in node_dict):
                node1 = node_dict[id1]
                if id2 and (id2 in node_dict):
                    ''' Case (1): get all matches found with id1, id2 in lattice '''
                    node2 = node_dict[id2]
                    matches[latt_node] = (node1,node2)
                    print('Added actual pair:', node1, node2)
                elif not id2:
                    ''' Case (2): duplicate BoM1 node IDs '''
                    node2 = node1
                    matches[latt_node] = (node1,node2)
                    print('Added notional pair:', node1, node2)
        return matches



    '''
    HR 27/01/22
    To group items by name including inexactly via Levenshtein distance
    NOT FULLY TESTED AND MULTIPLE ISSUES IF 'screen_name' USED AS QUERY FIELD:
        1. Endings (e.g. "_1") not accounted for when multiple instances of item exist;
        2. The above complicated further if suffixes exists (e.g. ".STEP" -> ".STEP_1") as cannot then be removed consistently;
        3. Cannot deal with non-product names (e.g. if default names present for "SOLID" or other shape types) or empty name fields
    Correctly groups parking trolley items if text_tol = 1e-2; this is small b/c some very long names, e.g. beginning with "Colson"
    '''
    def block_by_name(self, id1, id2, nodes1 = None, nodes2 = None, text_tol = None, suffixes = None, field = None):

        a1 = self._mgr[id1]
        a2 = self._mgr[id2]

        ''' Check for/set defaults '''
        if not nodes1:
            nodes1 = a1.nodes
        if not nodes2:
            nodes2 = a2.nodes

        if not text_tol:
            text_tol = self.MATCHING_TEXT_TOL_DEFAULT
        if not suffixes:
            suffixes = self.MATCHING_TEXT_SUFFIXES_DEFAULT
        if not field:
            field = self.MATCHING_FIELD_DEFAULT

        groups = {}
        grouped = False

        for n1 in nodes1:
            text = a1.nodes[n1][field]
            if not text:
                print('No name found at node ', n1)
                continue
            print('Name found at node ', n1)
            ''' Remove suffixes '''
            if suffixes:
                print(' TEXT: ', text)
                text = remove_suffixes(text, suffixes = suffixes)
            if text in groups:
                print('Adding to existing group (exact match)')
                groups[text][0].append(n1)
                continue
            for k in groups.keys():
                lev_dist = nltk.edit_distance(text, k)
                sim = 1 - lev_dist/max(len(text), len(k))

                if sim > 1-text_tol:
                    print('Adding to existing group (inexact match), score = ', sim)
                    groups[k][0].append(n1)
                    grouped = True
                    break
            if grouped:
                grouped = False
                continue
            print('Creating new group: ', text)
            groups[text] = ([n1], [])

        for n2 in nodes2:
            text = a2.nodes[n2][field]
            if not text:
                print('No name found at node ', n2)
                continue
            print('Name found at node ', n2)
            ''' Remove suffixes '''
            if suffixes:
                text = remove_suffixes(text, suffixes = suffixes)
            if text in groups:
                print('Adding to existing group (exact match)')
                groups[text][1].append(n2)
                continue
            for k in groups.keys():
                lev_dist = nltk.edit_distance(text, k)
                sim = 1 - lev_dist/max(len(text), len(k))

                if sim > 1-text_tol:
                    print('Adding to existing group (inexact match), score = ', sim)
                    groups[k][1].append(n2)
                    grouped = True
                    break
            if grouped:
                grouped = False
                continue
            # print('Creating new group: ', text)
            groups[text] = ([], [n2])

        return groups



    '''
    HR 25/01/22
    To group items by bounding box (BB) dimensions (specifically sum of aspect ratios)
    Groups if (a) exact match or (b) inexact match (within tolerance) according to sim score
    '''
    def block_by_bb(self, id1, id2, nodes1 = None, nodes2 = None, bb_tol = None, group_tol = None):

        ''' Check for/set defaults '''
        if not nodes1:
            a1 = self._mgr[id1]
            nodes1 = a1.nodes
        if not nodes2:
            a2 = self._mgr[id2]
            nodes2 = a2.nodes

        if not bb_tol:
            bb_tol = self.MATCHING_BB_TOL_DEFAULT
        if not group_tol:
            group_tol = self.MATCHING_BB_GROUP_TOL_DEFAULT

        groups = {}
        grouped = False

        for n1 in nodes1:
            # shape = a1.nodes[n1]['shape_raw'][0]
            # if not shape:
            #     print('No shape found at node ', n1)
            #     continue
            # print('Shape found at node ', n1, '; computing BB...')
            # bb_sum = np.sum(get_aspect_ratios(shape, tol = bb_tol))
            bb_ar = self.get_ar(id1, n1)
            if bb_ar:
                print('Retrieved AR, trying to group...')
                bb_sum = np.sum(bb_ar)
            else:
                print('Retrieved None as AR; skipping...')
                continue
            if bb_sum in groups:
                print('Adding to existing group (exact match)')
                groups[bb_sum][0].append(n1)
                continue
            for k in groups.keys():
                if np.isclose(k, bb_sum, rtol = group_tol):
                    print('Adding to existing group (inexact match)')
                    groups[bb_sum][0].append(n1)
                    grouped = True
                    break
                continue
            if grouped:
                grouped = False
                continue
            print('Creating new group')
            groups[bb_sum] = ([n1], [])

        for n2 in nodes2:
            # shape = a2.nodes[n2]['shape_raw'][0]
            # if not shape:
            #     print('No shape found at node ', n2)
            #     continue
            # print('Shape found at node ', n2, '; computing BB...')
            # bb_sum = np.sum(get_aspect_ratios(shape, tol = bb_tol))
            bb_ar = self.get_ar(id2, n2)
            if bb_ar:
                print('Retrieved AR, trying to group...')
                bb_sum = np.sum(bb_ar)
            else:
                print('Retrieved None as AR; skipping...')
                continue
            if bb_sum in groups:
                print('Adding to existing group (exact match)')
                groups[bb_sum][1].append(n2)
                continue
            for k in groups.keys():
                if np.isclose(k, bb_sum, rtol = group_tol):
                    print('Adding to existing group (inexact match)')
                    groups[k][1].append(n2)
                    grouped = True
                    break
                continue
            if grouped:
                grouped = False
                continue
            print('Creating new group')
            groups[bb_sum] = ([], [n2])

        return groups



    ''' HR 10/12/21 To grab all similarity scores
        For testing integration with PartFind '''
    def get_sims(self, id1, id2, node1, node2, field = None, weights = None, structure_weights = None, C1 = None, C2 = None):

        ''' Check for/set defaults '''
        if not field:
            field = self.MATCHING_FIELD_DEFAULT
        if not weights:
            weights = self.MATCHING_WEIGHTS_DEFAULT
        if not structure_weights:
            structure_weights = self.MATCHING_WEIGHTS_STRUCTURE_DEFAULT
        if not C1:
            C1 = self.MATCHING_C1_DEFAULT
        if not C2:
            C2 = self.MATCHING_C2_DEFAULT

        # a1 = self._mgr[id1]
        # a2 = self._mgr[id2]

        ''' Get name-based similarity '''
        if weights[0] > 0:
            sim_name = self.similarity_strings(id1, id2, node1, node2, field = field)[1]
        else:
            sim_name = 0
        print('Name sim: ', sim_name)

        ''' Get local assembly structure-based score '''
        if weights[1] > 0:
            sim_str = self.similarity_structure(id1, id2, node1, node2, structure_weights = structure_weights, C1 = C1, C2 = C2)[0]
            # sim_str = sum(x*y for x,y in zip(sims, structure_weights))/sum(structure_weights)
        else:
            sim_str = 0
        print('Struct sim: ', sim_str)

        ''' Get BB-based score '''
        if weights[2] > 0:
            sim_bb = self.similarity_bb(id1, id2, node1, node2)
        else:
            sim_bb = 0
        print('BB sim: ', sim_bb)

        ''' Get shape-based score '''
        if weights[3] > 0:
            sim_sh = self.similarity_shape(id1, id2, node1, node2)
        else:
            sim_sh = 0
        print('Shape sim: ', sim_sh)

        sims = (sim_name, sim_str, sim_bb, sim_sh)
        sim_total = sum([s*w for s,w in zip(sims,weights)])/sum(weights)

        return sim_total, sims, weights



    ''' HR 10/21/12 To get all local assembly structure-based similarity scores
        All copied/adapted from older "node_sim" method below '''
    def similarity_structure(self, id1, id2, node1, node2, structure_weights = None, C1 = None, C2 = None, field = None):

        ''' Check for/set defaults '''
        if not structure_weights:
            structure_weights = self.MATCHING_WEIGHTS_STRUCTURE_DEFAULT
        if not C1:
            C1 = self.MATCHING_C1_DEFAULT
        if not C2:
            C2 = self.MATCHING_C2_DEFAULT
        if not field:
            field = self.MATCHING_FIELD_DEFAULT

        a1 = self._mgr[id1]
        a2 = self._mgr[id2]

        ''' Get tree-depth similarity '''
        if structure_weights[0] > 0:
            root1 = a1.get_root()
            root2 = a2.get_root()

            d1 = nx.shortest_path_length(a1, root1, node1)
            d2 = nx.shortest_path_length(a2, root2, node2)
            if (d1 == 0) and (d2 == 0):
                c = C1
            elif (d1 == 0) != (d2 == 0):
                c = C2
            else:
                c = min(d1, d2)/max(d1, d2)
            sim_depth = c

        else:
            sim_depth = 0



        ''' Get parents, where None is default if no parent... '''
        if structure_weights[1] > 0:
            parent1 = next(a1.predecessors(node1), None)
            parent2 = next(a2.predecessors(node2), None)
            ''' ...then get parent label similarity, if both parents exist '''
            if (parent1 == None) and (parent2 == None):
                c = C1
            elif (parent1 == None) != (parent2 == None):
                c = C2
            else:
                try:
                    c = self.similarity_strings(a1.nodes[parent1][field], a2.nodes[parent2][field])[1]
                except:
                    c = 0
            sim_parent = c

        else:
            sim_parent = 0



        ''' Get number of siblings... '''
        if structure_weights[2] > 0:
            try:
                ns1 = len([el for el in a1.successors(parent1)]) - 1
                ns2 = len([el for el in a2.successors(parent2)]) - 1
            except:
                ns1 = 0
                ns2 = 0
            ''' ...then get similarity '''
            if (ns1 == 0) and (ns2 == 0):
                c = C1
            elif (ns1 == 0) != (ns2 == 0):
                c = C2
            else:
                c = min(ns1, ns2)/max(ns1, ns2)
            sim_sibs = c
        else:
            sim_sibs = 0



        ''' Get number of children... '''
        if structure_weights[3] > 0:
            nc1 = len([el for el in a1.successors(node1)])
            nc2 = len([el for el in a2.successors(node2)])
            ''' ...then get similarity '''
            if (nc1 == 0) and (nc2 == 0):
                c = C1
            elif (nc1 == 0) != (nc2 == 0):
                c = C2
            else:
                c = min(nc1, nc2)/max(nc1, nc2)
            sim_children = c

        else:
            sim_children = 0

        sims = (sim_depth, sim_parent, sim_sibs, sim_children)
        sim_str = sum([s*w for s,w in zip(sims,structure_weights)])/sum(structure_weights)

        return sim_str, sims, structure_weights



    # ''' HR 10/21/12 To get bounding box-based similarity scores
    #     To do later: pickle shapes where necessary '''
    # def similarity_bb(self, id1, id2, node1, node2):

    #     a1 = self._mgr[id1]
    #     a2 = self._mgr[id2]

    #     node_dict1 = a1.nodes[node1]
    #     node_dict2 = a2.nodes[node2]

    #     name1 = node_dict1['occ_name']
    #     name2 = node_dict2['occ_name']

    #     folder1 = remove_suffixes(a1.step_filename)
    #     folder2 = remove_suffixes(a2.step_filename)
    #     print('Folder 1:\n ', folder1)
    #     print('Folder 2:\n ', folder2)

    #     file1 = os.path.join(os.getcwd(), folder1, name1)
    #     file2 = os.path.join(os.getcwd(), folder2, name2)
    #     print('File 1:\n ', file1)
    #     print('File 2:\n ', file2)

    #     arfile1 = file1 + '.ar'
    #     arfile2 = file2 + '.ar'

    #     ''' Create pickled ARs if not already present '''
    #     if not os.path.isfile(arfile1):
    #         print('Pickled aspect ratio (AR) data not found; getting shape and computing ARs from bounding box (BB)...')
    #         shape1 = node_dict1['shape_loc'][0]
    #         ''' Create folder if not present '''
    #         if not os.path.isdir(folder1):
    #             print('Folder not present; creating...')
    #             os.mkdir(folder1)
    #         print('Retrieving shape...\n ')
    #         shape1 = node_dict1['shape_loc'][0]
    #         print('Computing and pickling AR data...\n ', arfile1)
    #         ar1 = get_aspect_ratios(shape1)
    #         ar_writer1 = open(arfile1,"wb")
    #         pickle.dump(ar1, ar_writer1)
    #         ar_writer1.close()

    #     if not os.path.isfile(arfile2):
    #         print('Pickled aspect ratio (AR) data not found; getting shape and computing ARs from bounding box (BB)...')
    #         shape2 = node_dict2['shape_loc'][0]
    #         ''' Create folder if not present '''
    #         if not os.path.isdir(folder2):
    #             print('Folder not present; creating...')
    #             os.mkdir(folder2)
    #         print('Retrieving shape...\n ')
    #         shape2 = node_dict2['shape_loc'][0]
    #         print('Computing and pickling AR data...\n ', arfile2)
    #         ar2 = get_aspect_ratios(shape2)
    #         ar_writer2 = open(arfile2,"wb")
    #         pickle.dump(ar2, ar_writer2)
    #         ar_writer2.close()

    #     ''' Load pickled BB data '''
    #     print('Opening pickled BB data...\n ', arfile1)
    #     ar_loader1 = open(arfile1,"rb")
    #     ar1 = pickle.load(ar_loader1)
    #     ar_loader2 = open(arfile2,"rb")
    #     ar2 = pickle.load(ar_loader2)

    #     sim_bb = get_bb_score(ar1, ar2)

    #     return sim_bb



    ''' HR 31/01/22 To automate/abstract all AR retrieval '''
    def get_ar(self, assembly_id, node, field = None):

        ''' Check for/set defaults '''
        if not field:
            field = self.MATCHING_FIELD_DEFAULT

        assembly = self._mgr[assembly_id]
        node_dict = assembly.nodes[node]
        name = node_dict[field]
        if not name:
            print('No name found; returning None')
            return None
        folder = remove_suffixes(assembly.step_filename)
        print('Folder, name: ', folder, name)

        file = os.path.join(os.getcwd(), folder, name)
        print('File:\n ', file)

        arfile = file + '.ar'

        ''' Create pickled ARs if not already present '''
        if not os.path.isfile(arfile):
            print('Pickled aspect ratio (AR) data not found; getting shape and computing ARs from bounding box (BB)...')
            print('Retrieving shape...\n ')
            shape = node_dict['shape_loc'][0]
            if not shape:
                print('Shape not found; returning None')
                return None
            ''' Create folder if not present '''
            if not os.path.isdir(folder):
                print('Folder not present; creating...')
                os.mkdir(folder)
            print('Computing and pickling AR data...\n ', arfile)
            ar = get_aspect_ratios(shape)
            ar_writer = open(arfile,"wb")
            pickle.dump(ar, ar_writer)
            ar_writer.close()

        ''' Load pickled BB data '''
        print('Opening pickled BB data...\n ', arfile)
        ar_loader = open(arfile,"rb")
        ar = pickle.load(ar_loader)

        return ar



    ''' HR 31/01/22
        To replace older method by abstracting more: just pass shape and retrieve ARs
        Incorporates (a) retrieval from file and/or (b) pickling to file if necessary '''
    def similarity_bb(self, id1, id2, node1, node2, field = None):

        ''' Check for/set defaults '''
        if not field:
            field = self.MATCHING_FIELD_DEFAULT

        try:
            ar1 = self.get_ar(id1, node1)
        except:
            print('Could not get AR: exception')
            ar1 = None
        try:
            ar2 = self.get_ar(id2, node2)
        except:
            print('Could not get AR: exception')
            ar2 = None

        ''' Calculate similarity '''
        if ar1 and ar2:
            sim_bb = get_bb_score(ar1, ar2)
            return sim_bb
        else:
            return self.MATCHING_SCORE_DEFAULT



    ''' HR 31/01/22 To automate/abstract all AR retrieval '''
    def get_shape_thing(self, assembly_id, node, field = None):

        ''' Check for/set defaults '''
        if not field:
            field = self.MATCHING_FIELD_DEFAULT

        assembly = self._mgr[assembly_id]
        node_dict = assembly.nodes[node]
        name = node_dict[field]
        folder = remove_suffixes(assembly.step_filename)

        file = os.path.join(os.getcwd(), folder, name)
        print('File:\n ', file)

        pickle_file = file + '.pickle'
        thing_in_memory = False

        ''' Create pickled thing if not already present '''
        if not os.path.isfile(pickle_file):
            print('Pickled graph not found...')
            step_file = file + '.STEP'
            ''' Create STEP file for part if not already present '''
            if not os.path.isfile(step_file):
                print('Getting shape and writing to STEP file...')
                shape = node_dict['shape_loc'][0]
                if not shape:
                    print('Shape not found; returning None')
                    return None
                ''' Create folder if not present '''
                if not os.path.isdir(folder):
                    print('Folder not present; creating...')
                    os.mkdir(folder)
                print('shape, full file path:\n ', shape, step_file)
                DataExchange.write_step_file(shape, step_file)
            print('Creating graph from STEP file...\n ', step_file)
            try:
                thing = load_from_step(step_file)
            except:
                print('Could not create graph; returning None')
                return None
            print('Pickling graph...\n ', pickle_file)
            pickle_writer = open(pickle_file,"wb")
            pickle.dump(thing, pickle_writer)
            pickle_writer.close()
            thing_in_memory = True

        ''' Load pickled thing if not already in memory '''
        if not thing_in_memory:
            print('Opening pickled shape thing...\n ', pickle_file)
            pickle_loader = open(pickle_file,"rb")
            thing = pickle.load(pickle_loader)

        return thing



    def similarity_shape(self, id1, id2, node1, node2, field = None):

        ''' Check for/set defaults '''
        if not field:
            field = self.MATCHING_FIELD_DEFAULT

        try:
            thing1 = self.get_shape_thing(id1, node1, field = field)
        except:
            print('Could not get shape thing: exception')
            thing1 = None

        try:
            thing2 = self.get_shape_thing(id2, node2, field = field)
        except:
            print('Could not get shape thing: exception')
            thing2 = None

        ''' Calculate similarity '''
        if thing1 and thing2:
            sim_sh = self.pc.model.test_pair(thing1, thing2)
            return sim_sh
        else:
            return self.MATCHING_SCORE_DEFAULT



    # def similarity_shape(self, id1, id2, node1, node2, field = None):

    #     ''' Check for/set defaults '''
    #     if not field:
    #         field = self.MATCHING_FIELD_DEFAULT

    #     a1 = self._mgr[id1]
    #     a2 = self._mgr[id2]

    #     node_dict1 = a1.nodes[node1]
    #     node_dict2 = a2.nodes[node2]

    #     name1 = node_dict1['occ_name']
    #     name2 = node_dict2['occ_name']

    #     folder1 = remove_suffixes(a1.step_filename)
    #     folder2 = remove_suffixes(a2.step_filename)
    #     print('Folder 1:\n ', folder1)

    #     file1 = os.path.join(os.getcwd(), folder1, name1)
    #     file2 = os.path.join(os.getcwd(), folder2, name2)
    #     print('File 1:\n ', file1)

    #     pickle1 = file1 + '.pickle'
    #     pickle2 = file2 + '.pickle'

    #     ''' Create pickled graphs if not already present '''
    #     if not os.path.isfile(pickle1):
    #         print('Pickled graph not found...')
    #         step1 = file1 + '.STEP'
    #         ''' Create STEP file for part if not already present '''
    #         if not os.path.isfile(step1):
    #             print('Getting shape and writing to STEP file...')
    #             shape1 = node_dict1['shape_loc'][0]
    #             ''' Create folder if not present '''
    #             if not os.path.isdir(folder1):
    #                 print('Folder not present; creating...')
    #                 os.mkdir(folder1)
    #             print('shape, full file path:\n ', shape1, step1)
    #             DataExchange.write_step_file(shape1, step1)
    #         print('Creating graph from STEP file...\n ', step1)
    #         try:
    #             graph1 = load_from_step(step1)
    #         except:
    #             print('Could not create graph; returning zero similarity')
    #             return 0
    #         print('Pickling graph...\n ', pickle1)
    #         pickle_writer1 = open(pickle1,"wb")
    #         pickle.dump(graph1, pickle_writer1)
    #         pickle_writer1.close()

    #     if not os.path.isfile(pickle2):
    #         print('Pickled graph not found...')
    #         step2 = file2 + '.STEP'
    #         ''' Create STEP file for part if not already present '''
    #         if not os.path.isfile(step2):
    #             print('Getting shape and writing to STEP file...')
    #             shape2 = node_dict2['shape_loc'][0]
    #             ''' Create folder if not present '''
    #             if not os.path.isdir(folder2):
    #                 print('Folder not present; creating...')
    #                 os.mkdir(folder2)
    #             print('shape, full file path:\n ', shape2, step2)
    #             DataExchange.write_step_file(shape2, step2)
    #         print('Creating graph from STEP file...\n ', step2)
    #         try:
    #             graph2 = load_from_step(step2)
    #         except:
    #             print('Could not create graph; returning zero similarity')
    #             return 0
    #         print('Pickling graph...\n ', pickle2)
    #         pickle_writer2 = open(pickle2,"wb")
    #         pickle.dump(graph2, pickle_writer2)
    #         pickle_writer2.close()

    #     ''' Load pickled graph '''
    #     print('Opening pickled graph...\n ', pickle1)
    #     pickle_loader1 = open(pickle1,"rb")
    #     graph1 = pickle.load(pickle_loader1)
    #     pickle_loader2 = open(pickle2,"rb")
    #     graph2 = pickle.load(pickle_loader2)

    #     ''' Calculate similarity '''
    #     sim_sh = self.pc.model.test_pair(graph1, graph2)

    #     return sim_sh



    ''' HR June 21 Must refactor this, moved from StepParse class method '''
    def similarity_strings(self, id1, id2, node1, node2, field = None):

        ''' Check for/set defaults '''
        if not field:
            field = self.MATCHING_FIELD_DEFAULT

        a1 = self._mgr[id1]
        a2 = self._mgr[id2]

        node_dict1 = a1.nodes[node1]
        node_dict2 = a2.nodes[node2]

        str1 = str(node_dict1[field])
        str2 = str(node_dict2[field])

        # if type(str1) != str:
        #     str1 = str(str1)
        # if type(str2) != str:
        #     str2 = str(str2)

        lev_dist = nltk.edit_distance(str1, str2)
        sim = 1 - lev_dist/max(len(str1), len(str2))

        return lev_dist, sim



    ''' HR 15/12/21 General-purpose method for returning set of optimal matches from specific block '''
    def match_block(self, id1, id2, nodes1 = None, nodes2 = None, weights = None, structure_weights = None, tol = None, default_value = None, C1 = None, C2 = None):
        ''' Returns:
                - Set of matched node pairs (matches = m1 x m2)
                - Lists of nodes in each assembly in pairs (m1, m2)
                - Matrix of all scores (scores)
                - Indices of elements in matrix corresponding to optimal scores (indices)
                - Best (i.e. optimal) total score (best) '''

        ''' Check for/set defaults '''
        if not nodes1:
            a1 = self._mgr[id1]
            nodes1 = [node for node in a1.nodes]
        if not nodes2:
            a2 = self._mgr[id2]
            nodes2 = [node for node in a2.nodes]

        if not weights:
            weights = self.MATCHING_WEIGHTS_DEFAULT
        if not structure_weights:
            structure_weights = self.MATCHING_WEIGHTS_STRUCTURE_DEFAULT
        if not tol:
            tol = self.MATCHING_TOLERANCE_DEFAULT
        if not default_value:
            default_value = self.MATCHING_SCORE_DEFAULT
        if not C1:
            C1 = self.MATCHING_C1_DEFAULT
        if not C2:
            C2 = self.MATCHING_C2_DEFAULT

        ''' Get all similarity scores:
            1. Fill with default values '''
        scores_name = np.full((len(nodes1), len(nodes2)), fill_value = default_value)
        scores_str = np.full((len(nodes1), len(nodes2)), fill_value = default_value)
        scores_bb = np.full((len(nodes1), len(nodes2)), fill_value = default_value)
        scores_sh = np.full((len(nodes1), len(nodes2)), fill_value = default_value)

        ''' 2. Populate with scores '''
        for i,n1 in enumerate(nodes1):
            for j,n2 in enumerate(nodes2):
                sim_name, sim_str, sim_bb, sim_sh = self.get_sims(id1, id2, n1, n2, weights = weights, structure_weights = structure_weights)[1]
                scores_name[i,j] = sim_name
                scores_str[i,j] = sim_str
                scores_bb[i,j] = sim_bb
                scores_sh[i,j] = sim_sh

        ''' Multiply by weights to get aggregate scores...
            (alternative is to scale by weights within "get_sims" method, then set weights to 1 here) '''
        scores = np.average([scores_name, scores_str, scores_bb, scores_sh], axis = 0, weights = weights)

        ''' ...then compute indices in array of globally optimal matches via Hungarian algorithm... '''
        rows, cols, best = hungalg.get_optimal_values(scores)
        pairs = list(zip(rows, cols))
        print('Pairs: ', pairs)
        print('Nodes1: ', nodes1)
        print('Nodes2: ', nodes2)

        ''' ...find any pairs with scores below the threshold ("tol")... '''
        excluded = [pair for pair in pairs if scores[pair] < tol]

        ''' ...and convert to matches in terms of node IDs '''
        matches = [(nodes1[pair[0]], nodes2[pair[1]]) for pair in pairs]

        return matches, excluded



    ''' ------------------------------------------------------------------
        ALL OLDER (PRE-2022) RECON STUFF BELOW THIS
        ------------------------------------------------------------------ '''



    def map_nodes(self, a1, a2, **kwargs):

        _mapped = {}



        '''
        1.  Easy part of mapping: exact 1:1 mappings
            and get dupe map for any unmapped exact matches
        '''
        _dupemap, _newitems = self.map_exact(a1,a2)
        _mapped.update(_newitems)



        ''' Then calculate similarity matrix for each duplicate group
            This effectively allows matching by similarity components
            other than (but also including) exact node-name matches,
            e.g. parent node names (or whatever the user specifies
            via "weight" values in "node_sim") '''

        _sim = {}
        for k,v in _dupemap.items():
            _sim[k] = self.node_sim(a1, a2, k, v)



        ''' Get total similarity (i.e. sum of all measures)
            "_sim" contains each separately; [0] element is total value '''
        _totals = {k:v[0] for k,v in _sim.items()}



        '''
        2.  Get all singular mappings within duplicate groupings,
            i.e. occurrence of max value is one, and remove from grouping
        '''

        _tomap = {k:v for k,v in _dupemap.items()}
        _totalscopy = {k:v for k,v in _totals.items()}

        for k,v in _tomap.items():

            ''' Get singular mappings and update global map '''
            _newlymapped = self.get_by_max(_totals[k])

            ''' Remove old/create new dict items if any mappings made above '''
            if _newlymapped:

                ''' Add new entries to master map '''
                _mapped.update(_newlymapped)

                ''' Get new entries with already-mapped items removed... '''
                _newdupe, _newtotals = self.remap_entries(k, v, _newlymapped, _totalscopy[k])

                ''' ...then update dicts with new entries '''
                if _newdupe:
                    _dupemap.update(_newdupe)
                if _newtotals:
                    _totals.update(_newtotals)

                ''' Remove old entries with "pop";
                    'None' default in "pop" avoids exception if item not found '''
                _dupemap.pop(k, None)
                _totals.pop(k, None)



        for k,v in _totals.items():

            ''' Reform sub-groupings within each duplicate grouping
                "_valuelen" should be two or more for all entries now,
                as all single-occurrence values removed above '''

            _newentries = self.reform_entries(k, _dupemap[k], _totals[k])
            _dupemap.pop(k, None)
            _dupemap.update(_newentries)



        '''
        3.  Map remaining exact duplicate groupings, which all now have v = 1 due to reforming above
        '''

        _tomap = {k:v for k,v in _dupemap.items()}

        for k,v in _tomap.items():

            ''' Remove from map of duplicates '''
            _dupemap.pop(k)

            _newones = self.map_multi_grouping(k, v)
            _mapped.update(_newones)



        ''' Put together all unmapped items '''
        _u1 = [el for el in a1.nodes if el not in _mapped]
        _u2 = [el for el in a2.nodes if el not in _mapped.values()]



        '''
        4.  Now need to continue mapping all nodes without exact label matches
        '''

        ''' Get total similarity (i.e. sum of all measures), currently element [0] '''
        if _u1 and _u2:
            _sim_u = self.node_sim(a1, a2, _u1, _u2, weight = [1,0,1,0,0])[0]

            ''' First job, as in previous sections: get any easy mappings where
                max sim value appears once, and remove from dict '''
            _newmap = self.get_by_max(_sim_u)
            if _newmap:
                _mapped.update(_newmap)

                for node1 in _newmap:
                    _u1.remove(node1)
                for node2 in _newmap.values():
                    _u2.remove(node2)

                _dupenew, _simnew = self.remap_entries(_u1, _u2, _newmap, _sim_u)
                _dupemap.update(_dupenew)

                # ''' Next stage is to get sim groupings
                #     i.e. where max sim value appears more than once '''
                # _newentries = self.reform_entries(tuple(_u1), tuple(_u2), _simnew)
                # print('New sim map by reforming: ', _newentries)



        # return _mapped, (_u1, _u2), _sim, _dupemap, _totals, _tomap, _simnew
        return _mapped, (_u1, _u2)



    def node_sim(self, a1, a2, nodes1 = None, nodes2 = None, weight = [1,0,1,0,0], C1 = 0, C2 = 0, field = 'occ_name'):
        ''' Weights apply to similarity of following metrics (by index):
            0. Depth of nodes in tree (i.e. from root)
            1. Number of siblings
            2. Number of children
            3. Name of parent '''

        print('Running "node_sim"')

        if not nodes1:
            nodes1 = a1.nodes
        if not nodes2:
            nodes2 = a2.nodes

        # if type(nodes1) is not list:
        #     nodes1 = [nodes1]
        # if type(nodes2) is not list:
        #     nodes2 = [nodes2]

        _r1 = a1.get_root()
        _r2 = a2.get_root()

        _sim_label = {}
        _sim_depth = {}
        _sim_sibs = {}
        _sim_children = {}
        _sim_parent = {}
        _sim = {}

        for n1 in nodes1:
            _sim_label[n1] = {}
            _sim_depth[n1] = {}
            _sim_sibs[n1] = {}
            _sim_children[n1] = {}
            _sim_parent[n1] = {}
            _sim[n1] = {}

            for n2 in nodes2:

                ''' Get node label similarity '''
                # print('n1, n2, field:')
                # print(n1, n2, field)

                # _sim_label[n1][n2] = self.similarity_strings(a1.nodes[n1][field], a2.nodes[n2][field])[1]
                _sim_label[n1][n2] = self.similarity_strings(a1.assembly_id, a2.assembly_id, n1, n2)[1]



                ''' Get tree-depth similarity '''
                _d1 = nx.shortest_path_length(a1, _r1, n1)
                _d2 = nx.shortest_path_length(a2, _r2, n2)
                if (_d1 == 0) and (_d2 == 0):
                    c = C1
                elif (_d1 == 0) != (_d2 == 0):
                    c = C2
                else:
                    c = min(_d1, _d2)/max(_d1, _d2)
                _sim_depth[n1][n2] = c



                ''' Get parents, where None is default if no parent... '''
                _p1 = next(a1.predecessors(n1), None)
                _p2 = next(a2.predecessors(n2), None)
                ''' ...then get parent label similarity, if both parents exist '''
                if (_p1 == None) and (_p2 == None):
                    c = C1
                elif (_p1 == None) != (_p2 == None):
                    c = C2
                else:
                    try:
                        c = self.similarity_strings(a1.nodes[_p1][field], a2.nodes[_p2][field])[1]
                    except:
                        c = 0
                _sim_parent[n1][n2] = c



                ''' Get number of siblings... '''
                try:
                    _ns1 = len([el for el in a1.successors(_p1)]) - 1
                    _ns2 = len([el for el in a2.successors(_p2)]) - 1
                except:
                    _ns1 = 0
                    _ns2 = 0
                ''' ...then get similarity '''
                if (_ns1 == 0) and (_ns2 == 0):
                    c = C1
                elif (_ns1 == 0) != (_ns2 == 0):
                    c = C2
                else:
                    c = min(_ns1, _ns2)/max(_ns1, _ns2)
                _sim_sibs[n1][n2] = c



                ''' Get number of children... '''
                _nc1 = len([el for el in a1.successors(n1)])
                _nc2 = len([el for el in a2.successors(n2)])
                ''' ...then get similarity '''
                if (_nc1 == 0) and (_nc2 == 0):
                    c = C1
                elif (_nc1 == 0) != (_nc2 == 0):
                    c = C2
                else:
                    c = min(_nc1, _nc2)/max(_nc1, _nc2)
                _sim_children[n1][n2] = c


                _norm = sum(weight)
                ''' Get total (aggregate) similarity '''
                _sim[n1][n2] = (_sim_label[n1][n2]*weight[0] \
                        + _sim_depth[n1][n2]*weight[1] \
                        + _sim_parent[n1][n2]*weight[2] \
                        + _sim_sibs[n1][n2]*weight[3] \
                        + _sim_children[n1][n2]*weight[4])/_norm

        return _sim, _sim_label, _sim_depth, _sim_parent, _sim_sibs, _sim_children



    ''' Get all mappings by exact matching of field '''
    def map_exact(self, a1, a2, nodes1 = None, nodes2 = None, _field = 'occ_name'):
        print('Running "map_exact"')

        if (not nodes1) and (not nodes2):
            nodes1 = a1.nodes
            nodes2 = a2.nodes
        elif (not nodes1) != (not nodes2):
            return None

        _map = {}

        _values = set([a1.nodes[el][_field] for el in a1.nodes if _field in a1.nodes[el]])
        _field_dict = {}

        for el in _values:
            _n1 = [_el for _el in a1.nodes if _field in a1.nodes[_el] and a1.nodes[_el][_field] == el]
            _n2 = [_el for _el in a2.nodes if _field in a2.nodes[_el] and a2.nodes[_el][_field] == el]
            if _n1 and _n2:
                if len(_n1) == 1 and len(_n2) == 1:
                    ''' If single-value mapping, then map... '''
                    if _n1[0] not in _map:
                        _map[_n1[0]] = _n2[0]
                else:
                    ''' ...else create dupe dict entry '''
                    _field_dict[tuple(_n1)] = tuple(_n2)

        return _field_dict, _map



    ''' Get mappings by max value
        If "singles_only" is true, only map for single-occurrence max sim values
        Else map anyway, which means first node2 found with max sim value is mapped '''
    def get_by_max(self, _sim, singles_only = True):
        print('Running "get_by_max"')

        _map = {}

        nodes1 = _sim.keys()

        ''' Loop over node1 items, which are contained in key of "_sim" '''
        for node1 in nodes1:
            _simdict = _sim[node1]
            ''' Remove already-mapped entries '''
            for _done2 in _map.values():
                _simdict.pop(_done2, None)
            ''' Short-circuit if _simdict empty
                This will happen when fewer n1 than n2 '''
            if not _simdict:
                return _map

            _max = max([el for el in _simdict.values()])
            _occ = sum(value == _max for value in _simdict.values())

            ''' Get valid (i.e. not already mapped) k-v pairs in simdict '''
            if (singles_only and _occ == 1) or not singles_only:
                node2 = [_k for _k,_v in _simdict.items() if _v == _max][0]
                _map[node1] = node2

        return _map



    def remap_entries(self, k, v, _dupe, _sim):
        print('Running "remap_entries"')

        ''' Start building new dupe map elements... '''
        _toremove1 = [el for el in _dupe]
        _toremove2 = [el for el in _dupe.values()]

        _n1 = tuple([el for el in k if el not in _toremove1])
        _n2 = tuple([el for el in v if el not in _toremove2])

        ''' ...and new total sim dict entry '''
        _newv = {_k:_v for _k,_v in _sim.items() if _k in _n1}
        _klist = list(_newv)
        for el in _klist:
            for _el in _toremove2:
                if _el in _newv[el]:
                    _newv[el].pop(_el, None)

        _dupenew = {}
        _simnew = {}
        ''' Check that n1 and n2 both have items in, otherwise would be redundant... '''
        if (len(_n1) > 0) and (len(_n2) > 0):
            ''' ...then actually create entries... '''
            _dupenew[_n1] = _n2
            _simnew[_n1] = _newv

        return _dupenew, _simnew



    ''' HR 24/11/20
        reform_entries not working as intended when tested with torch assembly
        and HHC's alternative assembly with four bulbs
        Problem is matching nodes within multiplicity groupings '''
    def reform_entries(self, nodes1, nodes2, _sim):
        print('Running "reform_entries"')

        nodes1 = list(nodes1)
        nodes2 = list(nodes2)

        ''' HR 26/11/20 Workaround to avoid problems for node sets with differing sizes
            Larger problems with this method remain, as described above '''
        if len(nodes1) != len(nodes2):
            return {tuple(nodes1):tuple(nodes2)}

        _first = nodes1[0]
        _firstdict = _sim[_first]
        _firstvalueset = set(_firstdict.values())

        if len(_firstvalueset) == 1:
            return {tuple(nodes1):tuple(nodes2)}

        _sims = list(_firstdict.values())

        _newentries = {}

        for el in _firstvalueset:

            _i = [i for i,val in enumerate(_sims) if val == el]
            _n1 = [nodes1[i] for i in _i]
            _n2 = [nodes2[i] for i in _i]

            ''' Reform grouping; no need to rebuild totals dict as not used after this '''
            _newentries[tuple(_n1)] = tuple(_n2)

        return _newentries



    ''' Map same-sim-value grouping
        (a) by same node IDs or
        (b) in numerical order '''
    def map_multi_grouping(self, k, v):
        print('Running "map_multi_grouping"')

        _toremove = []
        _newmap = {}

        _klist = sorted([el for el in k])
        _vlist = sorted([el for el in v])

        ''' First match any with the same IDs... '''
        for el in _klist:
            if el in _vlist:
                _newmap[el] = el
                _toremove.append(el)

        for el in _toremove:
            _klist.remove(el)
            _vlist.remove(el)

        ''' ...then match the remainder in numerical order
            N.B. "zip" truncates to length of smaller list '''
        if _klist and _vlist:
            _remainder = dict(zip(_klist, _vlist))
            for _k,_v in _remainder.items():
                _newmap[_k] = _v

        return _newmap



    ''' ----------------------------------------------------------------------
        ALL GRAPH/LATTICE PLOT METHODS HERE
        ----------------------------------------------------------------------
    '''



    ''' Create all plot objects from scratch '''
    def create_plot_elements(self):

        latt = self._lattice
        pos = latt.get_positions()

        # dc = self.dc
        # sc = self.sc
        lc = self.lc
        ic = self.ic

        ''' Bodge to set nodes/edges to one colour
            then recolour later (as most will not be selected, so quick) '''
        c = ic

        latt.line_dict = {}
        latt.node_dict = {}
        latt.edge_dict = {}

        ''' Draw outline of each (populated) level, with end points '''
        ''' HR 28/10/21 To add option to realise all lines, not just populated ones '''
        if self.DO_ALL_LATTICE_LINES:
            lines = latt.S_p_all
        else:
            lines = latt.S_p

        for k,v in lines.items():
            if v <= 1:
                line_pos = 0
            else:
                line_pos = np.log(v-1)
            latt.line_dict[k] = self.axes.plot([-0.5*line_pos, 0.5*line_pos], [k, k], c = lc, marker = 'o', mfc = lc, mec = lc, zorder = -1)

        ''' Draw nodes '''
        for node in latt.nodes:
            latt.node_dict[node] = self.axes.scatter(pos[node][0], pos[node][1], c = c, zorder = 1)

        ''' Draw edges '''
        for u,v in latt.edges:
            latt.edge_dict[(u,v)] = self.axes.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], c = c, zorder = 0)[0] # [0] index to get single list item

        ''' Create edges b/t infimum and leaves '''
        origin = latt.origin
        ''' Here set v in edge (u,v) to None if v is infimum '''
        for leaf in latt.leaves:
            latt.edge_dict[(leaf,None)] = self.axes.plot([origin[0], pos[leaf][0]], [origin[1], pos[leaf][1]], c = c, zorder = 0)[0] # [0] index to get single list item



        ''' Minimise white space around plot in panel '''
        self.viewer.subplots_adjust(left = 0.01, bottom = 0.01, right = 0.99, top = 0.99)

        self.axes.axes.axis('off')
        self.axes.axes.get_xaxis().set_ticks([])
        self.axes.axes.get_yaxis().set_ticks([])



    def update_colours_selected(self, active, selected = [], to_select = [], to_unselect = [], called_by = None):

        print('Running "update_colours_selected"')
        print('Called by: ', called_by)

        latt = self._lattice
        leaves = latt.leaves

        ''' Get active elements '''
        active_nodes = [node for node in latt.nodes if active in latt.nodes[node]]
        active_edges = [edge for edge in latt.edges if active in latt.edges[edge]]
        print('Active nodes: ', active_nodes)
        print('Active edges: ', active_edges)

        selected = [self.get_master_node(active, node) for node in selected]
        selected = [node for node in selected if node in active_nodes]

        to_select = [self.get_master_node(active, node) for node in to_select]
        to_select = [node for node in to_select if node in active_nodes]

        if to_unselect:
            # to_unselect = [self.get_master_node(active, node) for node in to_unselect if active in self._lattice.nodes[node]]
            to_unselect = [self.get_master_node(active, node) for node in to_unselect]
        else:
            to_unselect = [node for node in latt.nodes if node not in to_select]
        to_unselect = [node for node in to_unselect if active in latt.nodes[node]]

        print('selected: ', selected)
        print('to_select: ', to_select)
        print('to_unselect: ', to_unselect)

        dc = self.dc
        sc = self.sc

        ''' Selections '''
        for node in to_select:
            ''' Nodes '''
            latt.node_dict[node].set_facecolor(sc)
            ''' Edges '''
            for u,v in latt.in_edges(node):
                if ((u in selected) or (u in to_select)) and (u,v) in active_edges:
                    latt.edge_dict[(u,v)].set_color(sc)
            for u,v in latt.out_edges(node):
                if ((v in selected) or (v in to_select)) and (u,v) in active_edges:
                    latt.edge_dict[(u,v)].set_color(sc)

        ''' Deselections '''
        for node in to_unselect:
            ''' Nodes '''
            latt.node_dict[node].set_facecolor(dc)
            ''' Edges '''
            for u,v in latt.in_edges(node):
                if ((u not in selected) or (u not in to_select)) and (u,v) in active_edges:
                    latt.edge_dict[(u,v)].set_color(dc)
            for u,v in latt.out_edges(node):
                if ((v not in selected) or (v not in to_select)) and (u,v) in active_edges:
                    latt.edge_dict[(u,v)].set_color(dc)

        ''' Edges from leaves to infimum '''
        to_select_leaves = [el for el in to_select if el in leaves]
        to_unselect_leaves = [el for el in to_unselect if el in leaves]
        ''' Selections '''
        for leaf in to_select_leaves:
            latt.edge_dict[(leaf,None)].set_color(sc)
        ''' Deselections '''
        for leaf in to_unselect_leaves:
            latt.edge_dict[(leaf,None)].set_color(dc)



        ''' Minimise white space around plot in panel '''
        self.viewer.subplots_adjust(left = 0.01, bottom = 0.01, right = 0.99, top = 0.99)

        self.axes.axes.axis('off')
        self.axes.axes.get_xaxis().set_ticks([])
        self.axes.axes.get_yaxis().set_ticks([])



    def update_colours_active(self, to_activate = [], to_deactivate = []):

        latt = self._lattice
        nodes = latt.nodes
        edges = latt.edges
        leaves = latt.leaves

        ''' Active colour '''
        dc = self.dc
        ''' Inactive colour '''
        ic = self.ic

        ''' Nodes '''
        for node in nodes:
            _dict = nodes[node]
            # Activate
            if any(el in to_activate for el in _dict):
                latt.node_dict[node].set_facecolor(dc)
            # Deactivate
            elif any(el in to_deactivate for el in _dict):
                latt.node_dict[node].set_facecolor(ic)

        ''' Edges '''
        for edge in edges:
            _dict = edges[edge]
            # Activate
            if any(el in to_activate for el in _dict):
                latt.edge_dict[edge].set_color(dc)
            # Deactivate
            elif any(el in to_deactivate for el in _dict):
                latt.edge_dict[edge].set_color(ic)

        ''' Edges from leaves to infimum '''
        for leaf in leaves:
            _dict = nodes[node]
            # Activate
            if any(el in to_activate for el in _dict):
                latt.edge_dict[(leaf,None)].set_color(dc)
                # print('Activating leaf edge; node dict: ', _dict)
            # Deactivate
            elif any(el in to_deactivate for el in _dict):
                latt.edge_dict[(leaf,None)].set_color(ic)
                # print('Deactivating leaf edge; node dict: ', _dict)



        ''' Minimise white space around plot in panel '''
        self.viewer.subplots_adjust(left = 0.01, bottom = 0.01, right = 0.99, top = 0.99)

        self.axes.axes.axis('off')
        self.axes.axes.get_xaxis().set_ticks([])
        self.axes.axes.get_yaxis().set_ticks([])




    ''' ----------------------------------------------------------------------
        ALL PROJECT/LATTICE DATA EXCHANGE HERE
        ----------------------------------------------------------------------
    '''



    ''' HR June 21 Method removed from StrEmbed
        Dumps all basic project/lattice, assembly and node info:
            Node ID, label/text, parent
        Keep for now, can reuse for larger "save" functionality later '''
    # ''' HR 25/02/21
    #     Basic XLSX output for whole lattice (i.e. all assemblies) '''
    # def xlsx_write(self, _ids = None):

    #     def get_header(_id, page):
    #         mgr = self._assembly_manager._mgr
    #         header = []
    #         header.append(mgr[_id].assembly_id)
    #         header.append(page.name)
    #         header.append(page.filename_fullpath)
    #         return header

    #     def get_output_data(_id, node):
    #         ass = self._assembly_manager._mgr[_id]
    #         data = []
    #         data.append(node)
    #         try:
    #             data.append(ass.nodes[node]['label'])
    #         except:
    #             data.append('')
    #         try:
    #             data.append(ass.nodes[node]['text'])
    #         except:
    #             data.append('')
    #         try:
    #             data.append(ass.get_parent(node))
    #         except:
    #             data.append('None (root)')
    #         return data

    #     header_fields = ['Assembly ID', 'Assembly name', 'STP/STEP file']
    #     y_offset = len(header_fields) + 2

    #     fields = ['Node ID', 'Label', 'Text', 'Parent ID', ]

    #     save_file = 'torch_project.xlsx'

    #     excel_file = os.getcwd() + '\\' + save_file
    #     workbook = xlsxwriter.Workbook(excel_file)

    #     '''Export all assemblies if none specified '''
    #     if not _ids:
    #         _ids = [el for el in self._assembly_manager._mgr]

    #     ''' Create worksheet for each assembly to be exported '''
    #     sheet_dict = {}
    #     for _id in _ids:
    #         sheet_dict[_id] = workbook.add_worksheet()
    #         page = [k for k,v in self._notebook_manager.items() if v == _id][0]

    #         ''' Write main header... '''
    #         header_data = get_header(_id, page)
    #         for i,el in enumerate(header_fields):
    #             sheet_dict[_id].write(i, 0, el)
    #             sheet_dict[_id].write(i, 1, header_data[i])

    #         ''' ...and node fields header '''
    #         for i,el in enumerate(fields):
    #             sheet_dict[_id].write(y_offset-1,i,el)

    #         ''' Get all nodes still present in CTC '''
    #         nodes = list(page.ctc_dict)

    #         counter = 0
    #         for node in nodes:
    #             data = get_output_data(_id, node)
    #             for i,el in enumerate(data):
    #                 x = i
    #                 y = counter + y_offset
    #                 sheet_dict[_id].write(y, x, data[i])
    #             counter += 1

    #     workbook.close()




class StepParse(nx.DiGraph):

    def __init__(self, assembly_id = None, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.part_level = 1

        ''' Below is full range of shape types, according to Open Cascade documentation here:
            https://dev.opencascade.org/doc/refman/html/class_topo_d_s___shape.html '''
        self.topo_types = (TopoDS_Shape, TopoDS_Solid, TopoDS_Compound, TopoDS_Shell, TopoDS_Face, TopoDS_Vertex, TopoDS_Edge, TopoDS_Wire, TopoDS_CompSolid)
        # self.topo_types = (TopoDS_Solid, TopoDS_Compound)
        # self.topo_types = (TopoDS_Solid, TopoDS_Compound, TopoDS_Shell, TopoDS_Face)
        # self.topo_types = (TopoDS_Solid,)

        self.assembly_id = assembly_id
        # self.OCC_dict = {}

        self.default_label_part = 'Unnamed item'
        self.default_label_ass = 'Unnamed item'
        self.head_name = '== PROJECT =='

        ''' Mid-grey for default shape colour '''
        self.SHAPE_COLOUR_DEFAULT = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)

        self.enforce_unary = True

        self.renderer = ShapeRenderer()
        self.PARTFIND_FOLDER_DEFAULT = "C:\_Work\_DCS project\__ALL CODE\_Repos\partfind\partfind for git"

        self.node_dict = {}
        self.file_loaded = False



    @property
    def new_node_id(self):
        if not hasattr(self, 'id_counter'):
            self.id_counter = 0
        self.id_counter += 1
        while self.id_counter in self.nodes:
            self.id_counter += 1
        return self.id_counter



    ''' Overridden to add label to node upon creation '''
    def add_node(self, node, **attr):
        super().add_node(node, **attr)

        kwds = ['text', 'label']

        for kwd in kwds:
            if kwd in attr:
                value = self.nodes[node][kwd]
                if (value is not None):
                    try:
                        self.nodes[node][kwd] = self.remove_suffixes(value)
                    except:
                        pass
            else:
                self.nodes[node][kwd] = self.default_label_part



    # def print_all_items(self):
    #     print('\nAll nodes and edges:')
    #     for node in self.nodes:
    #         print(node, self.nodes[node])
    #     for edge in self.edges:
    #         print(edge, self.edges[edge])



    ''' Set node and edge labels to node identifier
        For use later in tree reconciliation '''
    def set_all_tags(self):
        for node in self.nodes:
            if not 'tag' in self.nodes[node]:
                self.nodes[node]['tag'] = node
        for edge in self.edges:
            if not 'tag' in self.edges[edge]:
                self.edges[edge]['tag'] = edge



    def get_screen_name(self, occ_name, shape):

        if not hasattr(self, 'name_root_counter'):
            self.name_root_counter = {}
        if not hasattr(self, 'type_counter'):
            self.type_counter = {}

        ''' HR 13/05/21
            If item is product -> name root = product name,
            which assumes all products have a name,
            otherwise root name is based on shape type;
            lastly, call it "item" '''
        if occ_name in self.product_names:
            nm_root = occ_name

        elif shape:
            # ''' Lower case, naive implementation '''
            # nm_root = str(type(shape).__name__).rsplit('_', 1)[1]
            ''' Upper case to match pythonocc behaviour
                e.g. TopoDS_Solid -> SOLID, SOLID_1, SOLID_2, etc. '''
            if not type(shape) in self.type_counter:
                self.type_counter[type(shape)] = 0
                nm_root = str(type(shape).__name__).rsplit('_', 1)[1].upper()
            else:
                nm_root = str(type(shape).__name__).rsplit('_', 1)[1].upper() + '_' + str(self.type_counter[type(shape)])
            self.type_counter[type(shape)] += 1

        else:
            nm_root = 'Item'

        if not nm_root in self.name_root_counter:
            self.name_root_counter[nm_root] = 0
            nm_full = nm_root
        else:
            nm_full = nm_root + '_' + str(self.name_root_counter[nm_root])

        self.name_root_counter[nm_root] += 1

        print(' Returning screen name: ', nm_full)
        return nm_full



    @property
    def product_names(self):

        ''' HR 01/11/21 To fix STEP product name parsing problems '''
        def get_product_name(line):
            ''' First strip off basic extraneous stuff; this should work universally '''
            line_corr = line.split("PRODUCT")[1].strip().rstrip(";").lstrip("(").strip().split("#")[0].strip().rstrip("(").strip().strip(",").strip()
            print('Stripped back text, first stage: ', line_corr)
            ''' Next, deal with remaining rightmost field
            #     Fine for all case studies so far, but might not be universal solution; would need to deal with text in field, if present
            #     Note: Currently yields wrong name if text present in rightmost field '''
            # line_corr = line_corr.rstrip("'").strip().rstrip("'").strip().rstrip(",")
            ''' HR 22/11/21
                Rewritten to allow for text in third field
                Still assumes no commas in third field, but improvement on previous '''
            line_corr = ','.join(line_corr.split(",")[:-1])
            print('Stripped back text, second stage: ', line_corr)

            chunks = line_corr.split(",")
            print('Chunks by comma: ', chunks)

            l = len(chunks)
            print('Length: ', l)

            if l == 2:
                ''' If only two chunks, first chunk must be name, even if two empty chunks '''
                name = chunks[0]
                print("Length = 2, name is first chunk: ", name)

            else:
                if (l % 2) != 0:
                    ''' If l > 2 and odd, last chunk must be empty => name is all chunks except last '''
                    name = ''.join(chunks[:-1])
                    print("Length = ", l, " and odd, name is all chunks except last: ", name)
                else:
                    ''' Last remaining case is that l > 2 and even, for which two possible outcomes '''
                    lh = int(l/2)
                    print('Half length = ', lh)
                    ''' Chop text into two halves '''
                    half1 = ','.join(chunks[0:lh]).strip()
                    half2 = ','.join(chunks[lh:]).strip()
                    print('Half 1: ', half1)
                    print('Half 2: ', half2)
                    if half1 == half2:
                        ''' Outcome 1: Both halves the same, i.e. name repeated in two fields '''
                        name = half1
                        print("Length > 2 and even and halves match, name is first half: ", name)
                    else:
                        ''' Outcome 2: Second field empty => name is all chunks except last '''
                        name = ','.join(chunks[:-1])
                        print("Length > 2 and even and halves do NOT match, name is all chunks except last: ", name)

            ''' HR 01/11/21 Workaround for problem of multiple apostropges being reduced to single one in OCC
                Address unresolved OCC bug 32421: https://tracker.dev.opencascade.org/view.php?id=32421
                Possibly fixed via 32310: https://tracker.dev.opencascade.org/view.php?id=32310
                but needs testing here after updating PythonOCC '''
            while "''" in name:
                name = name.replace("''", "'")

            ''' Remove double quotes if present; may be more elegant method for doing this '''
            name = name[1:-1]

            # return line_corr, name
            return name



        ''' HR May 21 To get all product names from STEP files
            This all assumes products have non-empty names,
            otherwise logic would have to be completely revised
            and would need to delve into OCC much further '''
        if not hasattr(self, '_product_names'):
            lines = step_search(file = self.step_filename, keywords = ['PRODUCT ', 'PRODUCT('], exclusions = ['kevinphillipsbong'])[0]
            ''' HR 03/06/21 Product name parsing corrected '''
            # self._product_names = [line.split(",")[0].split("(")[1].lstrip().rstrip().lstrip("'").rstrip("'").lstrip().rstrip() for line in lines]
            # self._product_names = [line.split("PRODUCT")[1].split(",")[0].rstrip().lstrip().lstrip("(").lstrip().lstrip("'").strip("'") for line in lines]

            self._product_names = []
            for line in lines:
                self._product_names.append(get_product_name(line))

        return self._product_names



    def load_step(self, filename, get_subshapes = False):
        ''' HR 11/05/21 Adapted from "read_step_file_with_names_colors"
            in OCC.Extend.DataExchange here:
            https://github.com/tpaviot/pythonocc-core/blob/master/src/Extend/DataExchange.py '''
        ##Copyright 2018 Thomas Paviot (tpaviot@gmail.com)
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
        """ Returns list of tuples (topods_shape, label, color)
        Use OCAF.
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError("%s not found." % filename)

        self.step_filename = filename

        doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))

        shape_tool = XCAFDoc_DocumentTool_ShapeTool(doc.Main())
        color_tool = XCAFDoc_DocumentTool_ColorTool(doc.Main())
        #layer_tool = XCAFDoc_DocumentTool_LayerTool(doc.Main())
        #mat_tool = XCAFDoc_DocumentTool_MaterialTool(doc.Main())

        step_reader = STEPCAFControl_Reader()
        step_reader.SetColorMode(True)
        step_reader.SetLayerMode(True)
        step_reader.SetNameMode(True)
        step_reader.SetMatMode(True)
        step_reader.SetGDTMode(True)

        status = step_reader.ReadFile(filename)
        if status == IFSelect_RetDone:
            step_reader.Transfer(doc)

        ''' loc tracks spatial transformation through each level of assembly structure
            i.e. for each IsAssembly level, but not for sub-shapes '''
        locs = []



        ''' Create graph structure for shape data '''
        head = self.new_node_id
        self.head = head
        self.add_node(head)
        self.nodes[head]['occ_label'] = None
        self.nodes[head]['occ_name'] = None
        self.nodes[head]['screen_name'] = self.head_name
        self.nodes[head]['shape_raw'] = (None, None)
        self.nodes[head]['shape_loc'] = (None, None)
        self.nodes[head]['is_subshape'] = False
        self.nodes[head]['is_product'] = False



        def _get_sub_shapes(lab, loc):
            #global cnt, lvl
            #cnt += 1
            #print("\n[%d] level %d, handling LABEL %s\n" % (cnt, lvl, _get_label_name(lab)))
            #print()
            #print(lab.DumpToString())
            #print()
            #print("Is Assembly    :", shape_tool.IsAssembly(lab))
            #print("Is Free        :", shape_tool.IsFree(lab))
            #print("Is Shape       :", shape_tool.IsShape(lab))
            #print("Is Compound    :", shape_tool.IsCompound(lab))
            #print("Is Component   :", shape_tool.IsComponent(lab))
            #print("Is SimpleShape :", shape_tool.IsSimpleShape(lab))
            #print("Is Reference   :", shape_tool.IsReference(lab))

            #users = TDF_LabelSequence()
            #users_cnt = shape_tool.GetUsers(lab, users)
            #print("Nr Users       :", users_cnt)

            name = lab.GetLabelName()
            # print("Name :", name)



            ''' Properties common to assemblies and shapes
                Assembly- and shape-specific properties added in if/else below '''
            node = self.new_node_id
            self.add_edge(self.parent, node)
            self.nodes[node]['occ_label'] = lab
            self.nodes[node]['occ_name'] = name
            self.nodes[node]['is_subshape'] = False
            if name in self.product_names:
                is_product = True
            else:
                is_product = False
            self.nodes[node]['is_product'] = is_product



            if shape_tool.IsAssembly(lab):

                ''' Get components -> l_c '''
                l_c = TDF_LabelSequence()
                shape_tool.GetComponents(lab, l_c)
                #print("Nb components  :", l_c.Length())
                #print()

                ''' Assembly-specific (i.e. non-shape) properties '''
                self.nodes[node]['screen_name'] = self.get_screen_name(name, None)
                self.nodes[node]['shape_raw'] = (None, None)
                self.nodes[node]['shape_loc'] = (None, None)


                for i in range(l_c.Length()):
                    label = l_c.Value(i+1)
                    if shape_tool.IsReference(label):
                        #print("\n########  reference label :", label)
                        label_reference = TDF_Label()
                        shape_tool.GetReferredShape(label, label_reference)
                        loc = shape_tool.GetLocation(label)

                        self.parent = node

                        ''' Append location for this level '''
                        locs.append(loc)
                        #print(">>>>")
                        #lvl += 1
                        _get_sub_shapes(label_reference, loc)
                        #lvl -= 1
                        #print("<<<<")
                        locs.pop()



            elif shape_tool.IsSimpleShape(lab):

                ''' Get sub-shapes-> l_subss '''
                l_subss = TDF_LabelSequence()
                shape_tool.GetSubShapes(lab, l_subss)
                #print("Nb subshapes   :", l_subss.Length())

                #print("\n########  simpleshape label :", lab)
                shape = shape_tool.GetShape(lab)
                #print("    all ass locs   :", locs)

                ''' Create location by applying all locations to that level in sequence
                    as they are applied in sequence '''
                loc = TopLoc_Location()
                for l in locs:
                    #print("    take loc       :", l)
                    loc = loc.Multiplied(l)

                ''' HR June 21 some code duplication for colour assignment
                    but didn't work when reduced to single block '''
                c = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)  # default color
                colorSet = False
                if (color_tool.GetInstanceColor(shape, 0, c) or
                        color_tool.GetInstanceColor(shape, 1, c) or
                        color_tool.GetInstanceColor(shape, 2, c)):
                    color_tool.SetInstanceColor(shape, 0, c)
                    color_tool.SetInstanceColor(shape, 1, c)
                    color_tool.SetInstanceColor(shape, 2, c)
                    colorSet = True
                    n = c.Name(c.Red(), c.Green(), c.Blue())
                    # print('    instance color Name & RGB: ', c, n, c.Red(), c.Green(), c.Blue())

                if not colorSet:
                    if (color_tool.GetColor(lab, 0, c) or
                            color_tool.GetColor(lab, 1, c) or
                            color_tool.GetColor(lab, 2, c)):
                        color_tool.SetInstanceColor(shape, 0, c)
                        color_tool.SetInstanceColor(shape, 1, c)
                        color_tool.SetInstanceColor(shape, 2, c)

                        n = c.Name(c.Red(), c.Green(), c.Blue())
                        # print('    shape color Name & RGB: ', c, n, c.Red(), c.Green(), c.Blue())



                ''' Shape-specific (i.e. non-assembly) properties '''
                self.nodes[node]['screen_name'] = self.get_screen_name(name, shape)
                self.nodes[node]['shape_raw'] = (shape, loc)
                self.nodes[node]['shape_loc'] = (BRepBuilderAPI_Transform(shape, loc.Transformation()).Shape(), c)
                self.parent = node



                # ''' Location (loc) is applied in sequence '''
                # shape_disp = BRepBuilderAPI_Transform(shape, loc.Transformation()).Shape()

                # if not shape_disp in output_shapes:
                #     output_shapes[shape_disp] = [lab.GetLabelName(), c]



                ''' Return if sub-shapes are not required '''
                if not get_subshapes:
                    return



                for i in range(l_subss.Length()):
                    lab_subs = l_subss.Value(i+1)
                    shape_sub = shape_tool.GetShape(lab_subs)
                    # print("\n########  simpleshape subshape label, type :", lab_subs.GetLabelName(), type(shape_sub))

                    c = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)  # default color
                    colorSet = False
                    if (color_tool.GetInstanceColor(shape_sub, 0, c) or
                            color_tool.GetInstanceColor(shape_sub, 1, c) or
                            color_tool.GetInstanceColor(shape_sub, 2, c)):
                        color_tool.SetInstanceColor(shape_sub, 0, c)
                        color_tool.SetInstanceColor(shape_sub, 1, c)
                        color_tool.SetInstanceColor(shape_sub, 2, c)
                        colorSet = True
                        # n = c.Name(c.Red(), c.Green(), c.Blue())
                        # print('    instance color Name & RGB: ', c, n, c.Red(), c.Green(), c.Blue())

                    if not colorSet:
                        if (color_tool.GetColor(lab_subs, 0, c) or
                                color_tool.GetColor(lab_subs, 1, c) or
                                color_tool.GetColor(lab_subs, 2, c)):
                            color_tool.SetInstanceColor(shape_sub, 0, c)
                            color_tool.SetInstanceColor(shape_sub, 1, c)
                            color_tool.SetInstanceColor(shape_sub, 2, c)

                            # n = c.Name(c.Red(), c.Green(), c.Blue())
                            # print('    shape color Name & RGB: ', c, n, c.Red(), c.Green(), c.Blue())

                    # ''' Location (loc) is common to all sub-shapes '''
                    # shape_to_disp = BRepBuilderAPI_Transform(shape_sub, loc.Transformation()).Shape()

                    # if not shape_to_disp in output_shapes:
                    #     output_shapes[shape_to_disp] = [lab_subs.GetLabelName(), c]



                    ''' Sub-shape-specific (i.e. non-shape, non-assembly) properties '''
                    name_sub = lab_subs.GetLabelName()

                    node = self.new_node_id
                    self.add_edge(self.parent, node)
                    self.nodes[node]['occ_label'] = lab_subs
                    self.nodes[node]['occ_name'] = name_sub
                    self.nodes[node]['shape_raw'] = (shape_sub, loc)
                    self.nodes[node]['shape_loc'] = (BRepBuilderAPI_Transform(shape_sub, loc.Transformation()).Shape(), c)
                    self.nodes[node]['screen_name'] = self.get_screen_name(name_sub, shape_sub)
                    self.nodes[node]['is_subshape'] = True
                    self.nodes[node]['is_product'] = False




        def _get_shapes():
            labels = TDF_LabelSequence()
            ''' Free shapes are those not referred to by any other
                1. If assembly structure present, this gets root item
                2. If not, all items in flat structure
                https://dev.opencascade.org/doc/refman/html/class_x_c_a_f_doc___shape_tool.html '''
            shape_tool.GetFreeShapes(labels)
            #global cnt
            #cnt += 1
            print("Number of shapes at root :", labels.Length())

            for i in range(labels.Length()):

                root_item = labels.Value(i+1)

                self.parent = head
                _get_sub_shapes(root_item, None)

        _get_shapes()
        # return output_shapes

        self.remove_redundants()
        self.file_loaded = True



    def get_image_data(self, node, default_colour = False):

        def render(nodes):

            try:
                self.renderer.EraseAll()

                for node in nodes:

                    if not default_colour:
                        ''' Render in correct colour... '''
                        shape, c = self.nodes[node]['shape_loc']
                        self.renderer.DisplayShape(shape, color = Quantity_Color(c.Red(),
                                                                                 c.Green(),
                                                                                 c.Blue(),
                                                                                 Quantity_TOC_RGB))
                    else:
                        ''' ...or in default colour (for better reference images), i.e. orange '''
                        self.renderer.DisplayShape(shape)

                self.renderer.View.FitAll()
                self.renderer.View.ZFitAll()

                # img = <DO IMAGE DATA GRAB HERE>
                W,H = self.renderer.GetSize()
                img_data = (W, H, self.renderer.GetImageData(W, H, Graphic3d_BufferType.Graphic3d_BT_RGB))
                # img = wx.Image(W, H, img_data)
                # ''' Then with "from PIL import Image"
                # via https://github.com/tpaviot/pythonocc-core/issues/976 '''
                # img = Image.frombytes('RGB', (W, H), img_data)
                # img = img.rotate(180, expand=True)

            except Exception as e:
                print('Could not create image; exception follows')
                print(e)
                img_data = None

            return img_data



        ''' Grab node dict, shorthand '''
        d = self.nodes[node]

        ''' If already rendered (and stored in node dict), just return it '''
        if 'image_data' in d:
            if d['image_data']:
                img_data = d['image_data']
                print('Image data found in node dict')
                return img_data
        else:
            print('Image not found in node dict; rendering...')

        ''' If shape exists in node dict, render node
            else (b/c node is assembly) get all non-sub-shapes and render all '''
        _to_render = []
        if 'shape_loc' in d:
            if d['shape_loc'][0]:
                _to_render.append(node)
            else:
                for el in nx.descendants(self, node):
                    d_sub = self.nodes[el]
                    ''' Add to render list if shape present and not sub-shape '''
                    if 'shape_loc' in d_sub:
                        if d_sub['shape_loc'][0] and not d_sub['is_subshape']:
                            _to_render.append(el)

        ''' Get image; default to "no image" png if not successful '''
        if _to_render:
            img_data = render(_to_render)
            if img_data:
                print('Successfully rendered image')
        else:
            img_data = None

        return img_data



    ''' Remove all single-child sub-assemblies as not compatible with lattice '''
    def remove_redundants(self, tree = None):

        ''' Operate on whole tree by default '''
        if not tree:
            tree = self.nodes

        ''' Get list of redundant nodes and link past them... '''
        to_remove = []
        for node in tree:
            if self.out_degree(node) == 1 and self.nodes[node]['screen_name'] != self.head_name:
                parent = self.get_parent(node)
                child  = self.get_child(node)
                ''' Don't remove if at head of tree (i.e. if in_degree == 0)...
                    ...as Networkx would create new "None" node as parent '''
                if self.in_degree(node) != 0:
                    self.add_edge(parent, child)
                to_remove.append(node)

        ''' ...then remove in separate loop to avoid list changing size during previous loop '''
        for node in to_remove:
            self.remove_node(node)
            print('Removing node ', node)
        print('  Total nodes removed: ', len(to_remove))

        print('Removed redundants')



    ''' Finds root of graph containing reference node, which is passed for speed;
        otherwise start with first in node list (as any random one will do) '''
    def get_root(self, node = None):

        # root = [el for el in self.nodes if self.in_degree(el) == 0][0]
        ''' Get random node if none given '''
        if node is None:
            node = list(self.nodes)[0]

        parent = self.get_parent(node)
        if parent is None:
            return node

        while parent is not None:
            child = parent
            parent = self.get_parent(child)

        return child



    def get_parent(self, node):
        ''' Get parent of node; return None if parent not present '''
        parent = [el for el in self.predecessors(node)]
        if parent:
            return parent[-1]
        else:
            return None



    def get_child(self, node):
        ''' Get (single) child of node; return None if parent not present
            Best used only when removing redundant (i.e. single-child) subassemblies '''
        child = [el for el in self.successors(node)]
        if child:
            return child[-1]
        else:
            return None



    @property
    def leaves(self):
        ''' Get leaf nodes '''
        leaves = {node for node in self.nodes if self.out_degree(node) == 0}
        # print('Leaves and names for assembly ID :', self.assembly_id, '')
        # for leaf in leaves:
        #     try:
        #         print(' NODE: ', leaf, ', NAME: ', self.nodes[leaf]['screen_name'], '\n')
        #     except:
        #         print(' no name\n')
        return leaves



    def node_depth(self, node):
        ''' Get depth of node(s) from root '''
        root = self.get_root(node)
        depth = nx.shortest_path_length(self, root, node)
        return depth



    def move_node(self, node, new_parent):
        old_parent = self.get_parent(node)
        self.remove_edge(old_parent, node)
        self.add_edge(new_parent, node)



    '''
    HR 15/01/21
    New method(s) to fetch "parts in" and node positions, rather than set them
    '''

    ''' Generate set of parts contained by node(s); node list optional argument '''
    def get_leaves_in(self, nodes = None):

        ''' If no nodes passed, default to all nodes in assembly '''
        if not nodes:
            nodes = self.nodes

        ''' Convert to list if only one item '''
        if type(nodes) == int:
            nodes = [nodes]

        ''' Get all leaves in specified nodes by set intersection '''
        leaves = set(nodes) & self.leaves
        subassemblies = set(nodes) - leaves

        leaves_in = {}

        for leaf in leaves:
            leaves_in[leaf] = {leaf}

        for sub in subassemblies:
            # print('sub = ', sub)
            leaves_in[sub] = nx.descendants(self, sub) - subassemblies

        return leaves_in



    ''' Memoise combinations '''
    def get_comb(self, n, k):
        if not hasattr(self, 'nCk'):
            print('Creating nCk dict for memoisation...')
            self.nCk = {}
        if (n,k) not in self.nCk:
            self.nCk[(n,k)] = binom(n,k)
        return self.nCk[(n,k)]



    def get_positions(self, nodes = None):

        ''' If no nodes passed, default to all nodes in assembly '''
        if not nodes:
            nodes = set(self.nodes)
        ''' HR 03/12/21 Workaround to remove (redundant) head node '''
        try:
            nodes = nodes - {self.head}
            print('Removed head node')
        except:
            print('Could not remove head node: not present')

        # ''' Convert to list if only one item '''
        # if type(nodes) == int:
        #     nodes = [nodes]

        ''' Get parts in each node '''
        parts_in = self.get_leaves_in(nodes)

        self.pos = {}

        ''' Get all levels, i.e. number of parts by inclusion '''
        levels = set([len(parts) for node,parts in parts_in.items()])

        ''' Get number of possible combinations for each level... '''
        leaves = self.leaves
        n = len(leaves)
        print('\n    Number of leaves: ', n,'\n')
        ''' ...but only needed for specified nodes '''
        ''' HR 28/10/21 To add option to display all lines, not just populated ones '''
        self.S_p_all = {level:self.get_comb(n,level) for level in range(int(n+1))}
        self.S_p = {level:self.get_comb(n,level) for level in levels}

        ''' Create map of leaves to combinatorial numbering starting at 1... '''
        leaves_list = list(leaves)
        leaf_map = {}
        ''' ...but only need to map specified nodes; do by index in list of all nodes '''
        for leaf in leaves:
            leaf_map[leaf] = leaves_list.index(leaf) + 1

        self.levels_map = {}
        for node in nodes:
            parts = parts_in[node]
            num_parts = len(parts)
            comb_parts = [leaf_map[part] for part in parts]
            rank = self.rank(comb_parts)
            S = self.S_p[num_parts]
            if num_parts in self.levels_map:
                self.levels_map[num_parts].append(node)
            else:
                self.levels_map[num_parts] = [node]
            if S <= 1:
                x = 0
            else:
                x = ((rank/(S-1))-0.5)*np.log(S-1)
            self.pos[node] = (x, num_parts)

        return self.pos

    ''' ----------
    '''




    '''
    HR 12/05/20
    -----------
    All combinatorial ranking/unranking methods here
    And all class methods '''



    def stirling_ln(self, n):
        # if n in (0, 1):
        #     _result = 0
        #     return _result

        result = (n+0.5)*np.log(n) - n + np.log(np.sqrt(2*np.pi)) + (1/(12*n)) - (1/(360*n**3)) + (1/(1260*n**5)) - (1/(1680*n**7))
        # result = (n+0.5)*np.log(n) - n + np.log(np.sqrt(2*np.pi)) + (1/(12*n))
        # print('Log Stirling approx. for n = ', n, ': ', result)
        return result



    def comb_ln(self, n, k):
        result = self.stirling_ln(n) - self.stirling_ln(k) - self.stirling_ln(n-k)
        # print('Log combination approx. for (n, k) = ', (n,k), ': ', result)
        return result



    # RANKING OF COMBINATION
    # --
    # Find position (rank) of combination in ordered list of all combinations
    # Items list argument consists of zero-based indices
    # --
    def rank(self, items):

        if not items:
            print('Item list empty or not conditioned: returning None')
            return None

        if 0 in items:
            print('Item list contains 0 element: returning None')
            return None

        if not all(isinstance(item, int) for item in items):
            print('One or more non-integers present in item list: returning None')
            return None

        if len(items) != len(set(items)):
            print('Item list contains duplicate(s): returning None')
            return None

        # if len(items) == 1:
        #     items = [items]

        if len(items) > 1:
            items.sort()

        rank = 0
        items.sort()
        for i, item in enumerate(items):
            comb = self.get_comb(item-1, i+1)
            rank += comb

        return rank



    '''
    UNRANKING OF COMBINATORIAL INDEX
    --
    Find combination of nCk items at position "rank" in ordered list of all combinations
    Ordering is zero-based
    '''
    def unrank(self, n, k, rank):

        ''' Check all arguments (except "self") are integers '''
        args = {k:v for k,v in locals().items() if k != 'self'}
        # print(['{} = {}'.format(k,v) for k,v in locals().items() if k != 'self'])
        print(['{} = {}'.format(k,v) for k,v in args.items()])

        if not all(isinstance(el, (int, float)) for el in args.values()):
        # if not all(isinstance(el, int) for el in (n, k, rank)):
            print('Not all arguments are integers: returning None')
            return None

        if rank < 0:
            print('Rank must be b/t 0 and (nCk-1); returning None')
            return None

        ''' Increase by one to satisfy zero-based indexing; check/resolve in future '''
        rank += 1

        ''' Check whether "rank" within nCk '''
        max_ln = self.comb_ln(n, k)

        ''' Check whether rank is massive; if so, calculate log(x) = log(x/a) + log(a)
            where x = rank and a = chop
            as np.log can't handle large numbers (actually x > 1e308 or so) '''
        chop = 1
        if rank > 1e100:
            print('Chopping rank for log')
            chop = 1000

        log_  = np.log(chop) + np.log(rank/chop)
        print('log_  = ', log_)

        if log_ > max_ln:
            print('Rank outside nCk bounds: returning None')
            return None

        ''' Convert to float to allow large n values '''
        rank = float(rank)



        ''' Optimisation as (n+1 k) = (n k)*(n+1)/(n+1-m) '''
        def next_comb(n, k, comb):
            _next = (comb*(n+1))/(n+1-k)
            return _next

        ''' Using scipy comb; can optimise in future, e.g. with Stirling approx. '''
        def comb_(n, k):
            result = self.get_comb(n, k)
            return result



        '''
        MAIN ALGORITHM
        '''
        items = []
        remainder = rank

        # print('Starting, k = {}'.format(k))
        ''' Find each of k items '''
        for i in range(k, 0, -1):

            ''' Initialise at 1 as kCk = 1 for all k '''
            c_i = 1
            count = i

            if c_i >= remainder:
                last_comb = c_i
            else:
                while c_i < remainder:
                    last_comb = c_i
                    c_i = next_comb(count, i, c_i)
                    count += 1

            # print('i   = {}'.format(i))
            # print('c_i = {}\n'.format(c_i))
            items.append(count)
            remainder -= last_comb

        return items



        ''' Alternative algorithm for unranking '''
        # '''
        # Algorithm 515 (Buckles_77, DOI: https://doi.org/10.1145/355732.355739)
        # For indexing combinations -> lexicographic ordering for ranking/unranking
        # Taken from Github repo of sleeepyjack here:
        # https://github.com/sleeepyjack/alg515/blob/master/python/alg515.py
        # '''

        # from scipy.special import binom

        # def comb(N, P, L):
        #     C = [0] * P
        #     X = 1
        #     R = int(binom(N-X, P-1))
        #     K = R

        #     while (K <= L):
        #         X += 1
        #         R  = int(binom(N-X, P-1))
        #         K += R
        #     K -= R
        #     C[0] = X-1

        #     for I in range(2, P):
        #         X += 1
        #         R  = int(binom(N-X, P-I))
        #         K += R
        #         while (K <= L):
        #             X += 1
        #             R  = int(binom(N-X, P-I))
        #             K += R
        #         K -= R
        #         C[I-1] = X-1
        #     C[P-1] = X + L - K
        #     return C



    '''
    SPLIT AND RENDER METHODS HERE
    '''



    ''' Image renderer (copied from StrEmbed) '''
    def quick_render(self, shape, colour = None, img_file = None):

        self.renderer.EraseAll()

        if colour:
            ''' Render in specified colour... '''
            c = colour
            self.renderer.DisplayShape(shape, color = Quantity_Color(c.Red(),
                                                                      c.Green(),
                                                                      c.Blue(),
                                                                      Quantity_TOC_RGB))
        else:
            ''' ...or in default colour (for better reference images), i.e. orange '''
            self.renderer.DisplayShape(shape)

        try:
            # print('Fitting and dumping image ', img_name)
            ''' Create directory if it doesn't already exist '''
            img_path = os.path.split(img_file)[0]
            if not os.path.isdir(img_path):
                os.mkdir(img_path)

            self.renderer.View.FitAll()
            self.renderer.View.ZFitAll()
            self.renderer.View.Dump(img_file)
            ''' Check if rendered and dumped, i.e. if image file exists '''
            if os.path.exists(img_file):
                # print('Image saved to ', img_file)
                image_saved_ok = True
            else:
                print('Could not save image')
                image_saved_ok = False

        except Exception as e:
            print('Could not dump image to file; exception follows')
            print(e)
            image_saved_ok = False

        return image_saved_ok



    ''' HR June 21 Updated to allow only products to be dumped '''
    def split_and_render(self, path = None, products_only = False, subshapes = False):

        # for node in self.nodes:
        #     print(node, self.nodes[node]['screen_name'])

        ''' Collect nodes to be checked, remove unwanted nodes (non-products, subshapes) '''
        nodes = self.nodes
        _to_remove = []
        if products_only:
            _to_remove.extend([el for el in nodes if not self.nodes[el]['is_product']])
        if not subshapes:
            _to_remove.extend([el for el in nodes if self.nodes[el]['is_subshape']])
        if _to_remove:
            for el in _to_remove:
                nodes.remove(el)

        ''' Collect unique shapes (i.e. avoid duplication) with names '''
        shapes = {}

        for node in nodes:
            d = self.nodes[node]

            ''' Skip if no shape '''
            if not d['shape_raw'][0]:
                continue
            shape = d['shape_raw'][0]

            ''' Skip rest if shape already grabbed or is sub-shape '''
            if (shape in shapes):
                print('Duplicate shape found; node ', node, shape)
                continue
            # if not subshapes and d['is_subshape']:
            #     # print('Sub-shape found; ignoring')
            #     continue

            ''' Else go through naming logic and add to shape map
                1. If product, get product name, as maps to shape,
                2. Otherwise get screen name '''
            if d['is_product']:
                name = d['occ_name']
            else:
                name = d['screen_name']
            shapes[shape] = name



        ''' Abort if no shapes '''
        if not shapes:
            print('No shapes found; aborting...')
            return


        ''' Get cwd as path if none given '''
        if not path:
            path = os.getcwd()

        ''' Create folder '''
        folder = os.path.join(path, remove_suffixes(self.step_filename))
        if not os.path.exists(folder):
            print('Creating folder...')
            os.makedirs(folder)

        ''' DO DUMP: Generate and save STEP and image files '''
        for k,v in shapes.items():
            step_file = os.path.join(folder, v + '.STEP')
            if os.path.isfile(step_file):
                print('Part model already exists; not saving')
            else:
                print('Saving STEP file for part: ', v)
                DataExchange.write_step_file(k, step_file)

            img_file = os.path.join(folder, v + '.jpg')
            if os.path.isfile(img_file):
                print('Part image file already exists; not saving')
            else:
                print('Saving image for part: ', v)
                self.quick_render(k, img_file = img_file)
