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

'''
HR 31/03/23 Onwards, refactoring for StrEmbed-6-1 version 2 (see Github releases)
            Aim is to overhaul for producing results for BoM recon paper
'''


# # Regular expression module
# import re

# Natural Language Toolkit module, for Levenshtein distance
import nltk

import numpy as np
from scipy.special import binom
# from math import log
from math import exp
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

''' For data exchange export '''
import xlsxwriter

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
from OCC.Core.TCollection import TCollection_ExtendedString

# from OCC.Extend.TopologyUtils import (discretize_edge, get_sorted_hlr_edges,
                                      # list_of_shapes_to_compound)

from OCC.Extend import DataExchange
from OCC.Core.Graphic3d import Graphic3d_BufferType

from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
# from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Display import OCCViewer

''' HR 28/06/22 These are the three files that must be modified to allow deep-copying '''
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_WHITE, Quantity_TOC_RGB
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TDF import TDF_LabelSequence, TDF_Label

# ''' HR 30/01/23 Modify OCC classes to allow deep-copying '''
# import occ_patch
# occ_patch.patch([Quantity_Color,
#                  TopLoc_Location,
#                  TDF_LabelSequence])

''' HR 24/03/23 Moved OCC patch to main.py '''
# ''' HR 16/03/23 Manually patch classes in library to allow deep-copying '''
# from . import occ_patch_manual
# try:
#     print("Trying to run OCC patch...")
#     occ_patch_manual.patch(klasses = [Quantity_Color,
#                                       TopLoc_Location,
#                                       TDF_LabelSequence])
# except Exception as e:
#     print("Could not run OCC patch, exception follows...")
#     print(e)
#     print("If you encounter this error while running an executable created by Pyinstaller, do the following:")
#     print("1. Run occ_patch_manual; this will do the patch by manually modifying some OCC library files")
#     print("2. Rerun Pyinstaller, i.e. create a new executable")


''' HR 28/07/22 For mass/volume computation of objects '''
from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop_VolumeProperties


''' HR 09/12/21 Adding PartCompare import to allow shape-based similarity scores '''
from .part_compare import PartCompare, load_from_step

''' HR 12/12/21 For pickling graphs of shapes for faster retrieval in similarity scoring '''
import pickle
''' HR 17/03/22 For duplicating assemblies '''
import copy

from . import hungarian_algorithm as hungalg


''' HR 08/04/22 NOT WORKING; HACKED CLASS DEFINITIONS IN SOURCE FILES '''
# ''' HR 07/04/22 For overriding method common to several PythonOCC classes;
#                 single line causes problems, index [3] gives error,
#                 works well when changed to [-1] '''
# def _dumps_object(klass):
#     """ Overwrite default string output for any wrapped object.
#     By default, __repr__ method returns something like:
#     <OCC.Core.TopoDS.TopoDS_Shape; proxy of <Swig Object of type 'TopoDS_Shape *' at 0x02BB0758> >
#     This is too much verbose.
#     We prefer :
#     <class 'gp_Pnt'>
#     or
#     <class 'TopoDS_Shape'>
#     """
#     print('\n  LINE IN "Quantity": ', str(klass.__class__), '\n')
#     klass_name = str(klass.__class__).split(".")[-1].split("'")[0]
#     # klass_name = str(klass.__class__).split(".")[3].split("'")[0]
#     repr_string = "<class '" + klass_name + "'"
# # for TopoDS_Shape, we also look for the base type
#     if klass_name == "TopoDS_Shape":
#         if klass.IsNull():
#             repr_string += ": Null>"
#             return repr_string
#         st = klass.ShapeType()
#         types = {OCC.Core.TopAbs.TopAbs_VERTEX: "Vertex",
#                  OCC.Core.TopAbs.TopAbs_SOLID: "Solid",
#                  OCC.Core.TopAbs.TopAbs_EDGE: "Edge",
#                  OCC.Core.TopAbs.TopAbs_FACE: "Face",
#                  OCC.Core.TopAbs.TopAbs_SHELL: "Shell",
#                  OCC.Core.TopAbs.TopAbs_WIRE: "Wire",
#                  OCC.Core.TopAbs.TopAbs_COMPOUND: "Compound",
#                  OCC.Core.TopAbs.TopAbs_COMPSOLID: "Compsolid"}
#         repr_string += "; Type:%s" % types[st]
#     elif hasattr(klass, "IsNull"):
#         if klass.IsNull():
#             repr_string += "; Null"
#     repr_string += ">"
#     print('\n  FULL CLASS NAME: ', repr_string, '\n')
#     return repr_string


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


def get_dimensions(shape, tol = 1e-6, use_mesh = True, get_centre = False):
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
    # bbox.SetGap(0)
    if use_mesh:
        mesh = BRepMesh_IncrementalMesh()
        mesh.SetParallelDefault(True)
        mesh.SetShape(shape)
        mesh.Perform()
        if not mesh.IsDone():
            raise AssertionError("Mesh not done.")
    brepbndlib_Add(shape, bbox, use_mesh)

    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    if get_centre:
        return xmin, ymin, zmin, xmax, ymax, zmax

    dx,dy,dz = xmax-xmin, ymax-ymin, zmax-zmin
    dim = dx,dy,dz
    ar = sorted((dx/dy, dy/dz, dz/dx))
    print('Done BB calcs for ', shape)
    return dim, ar


''' Get geometric absolute value
    i.e. min of a/b and b/a '''
def geo_abs(a,b):
    if a<b:
        return a/b
    else:
        return b/a


def get_bb_score(ar1, ar2, phi = 1):

    r1 = geo_abs(ar1[0], ar2[0])
    r2 = geo_abs(ar1[1], ar2[1])
    r3 = geo_abs(ar1[2], ar2[2])
    score = (r1+r2+r3)/(3*phi)

    # print('Score: ', score)
    return score


''' HR 28/07/22 To get mass/volume properties of object,
                alternative to BB as that sometimes gives wrong answer
                Adapted from here: https://github.com/tpaviot/pythonocc-demos/blob/master/examples/core_shape_properties.py
                and here: https://stackoverflow.com/questions/66929762/extract-volume-from-a-step-file '''
def get_mass_properties(shape):

    props = GProp_GProps()
    brepgprop_VolumeProperties(shape, props)

    mass = props.Mass()
    print("Mass = %s" % mass)

    com = props.CentreOfMass()
    com_x, com_y, com_z = com.Coord()
    print("Center of mass: x = %f;y = %f;z = %f;" % (com_x, com_y, com_z))

    # matrix_of_inertia = props.MatrixOfInertia()
    # print("Matrix of inertia", matrix_of_inertia)

    com = com_x, com_y, com_z
    # return com, matrix_of_inertia, mass
    return com, mass


''' HR 03/08/22 To get similarity score based on two shape masses/volumes
                Options are:
                    (a) Divide by sum (default)
                    (b) Divide by max '''
def get_mass_score(mass1, mass2, *args, **kwargs):

    # if 'do_max' in kwargs:
    #     do_max = kwargs['do_max']
    # else:
    #     do_max = True
    do_max = kwargs.get('do_max', True)

    if do_max:
        score = 1 - abs(mass1 - mass2)/max(mass1, mass2)
    else:
        score = 1 - abs(mass1 - mass2)/(mass1 + mass2)
    return score


''' HR 03/08/22 To get similarity score based on Euclidean distance '''
def get_distance_score(pos1, pos2, *args, **kwargs):

    # if 'scale' in kwargs:
    #     scale = kwargs['scale']
    # else:
    #     scale = 1

    # if 'exponential' in kwargs:
    #     exponential = kwargs['exponential']
    # else:
    #     exponential = False

    scale = kwargs.get('scale', 1)
    exponential = kwargs.get('exponential', False)

    dist = euclidean_distance(pos1, pos2, *args, **kwargs)

    if not exponential:
        score = 1.0/(1.0 + dist/scale)
    else:
        score = exp(-(dist/scale))
    return score


''' HR 01/08/22 To get distance from n-dimensional coordinates
                Takes list of any length '''
def distance_magnitude(coords, *args, **kwargs):

    # if 'n' in kwargs:
    #     n = kwargs['n']
    # else:
    #     n = 2
    n = kwargs.get('n', 2)

    if not type(coords) == list:
        coords = list(coords)
    result = sum([el**n for el in coords])**(1.0/n)

    return result


''' HR 01/08/22 To get Euclidean distance between two n-dimensional vectors '''
def euclidean_distance(vector1, vector2, *args, **kwargs):

    if not type(vector1) == list:
        vector1 = list(vector1)
    if not type(vector2) == list:
        vector2 = list(vector2)

    # if 'n' in kwargs:
    #     n - kwargs['n']
    # else:
    #     n = 2
    n = kwargs.get('n', 2)

    vectors = [el for el in zip(vector1, vector2)]
    result = sum([(el[1]-el[0])**n for el in vectors])**(1.0/n)

    return result


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
def get_matching_success(n_a, n_b, M, mu):

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


''' HR 06/04/22 UPDATE ON DEEPCOPY OF SWIG OBJECTS, SEE PYTHONOCC ISSUE HERE: https://github.com/tpaviot/pythonocc-core/issues/1097
                1. First tried wrapping classes causing problems (Quantity_Color, TDF_Label, TopLoc_Location) -> (Quantity_ColorSWIG, etc., see commented code below)
                    with PicklableSWIG, below, but failed in two ways:
                    - TopLoc_LocationSWIG.Multiplied(loc) during STEP parsing generates TopLoc_Location, not TopLoc_LocationSWIG, so prevents deepcopying
                    - Error then also produced during __repr__ (??) of wrapped classes; index [3] is wrong (should be [-1] or something suitable)
                        in "_dumps_object" method that's common to all three classes
                2. Eventually hacked source code for all three classes (actually TopLoc, Quantity and TDF) to add self.args to __init__ and __set_state__ and __get_state__;
                    as in SO answer (see 17/03/22), but __get_state__ as follows, as was getting AttributeError for "args", very hacky but now works

                    if not hasattr(self, 'args'):
                        self.args = {} '''

''' HR 17/03/22
    Workaround to allow picking/deep-copying of StepParse;
    solves problem of error when attempting copy.deepcopy of StepParse:
        "TypeError: cannot pickle 'SwigPyObject' object"
    i.e. deepcopy uses pickle, which cannot serialise StepParse,
    presumably because of PythonOCC contents
    ---
    Solution from here: https://stackoverflow.com/questions/9310053/how-to-make-my-swig-extension-module-work-with-pickle
    --
    Important bits copied below and adapted into StepParse
    ---
    class PickalableC(C, PickalableSWIG):

        def __init__(self, *args):
            self.args = args
            C.__init__(self)

    where PickalableSWIG is as in class, below
    --- '''
class PicklableSWIG:

    def __setstate__(self, state):
        self.__init__(*state['args'])

    def __getstate__(self):
        return {'args': self.args}


''' HR summer 2022, the below does not work '''
# ''' All classes that need to be copy-enabled '''
# class TopLoc_LocationSWIG(TopLoc_Location, PicklableSWIG):
#     def __init__(self, *args):
#         self.args = args
#         TopLoc_Location.__init__(self)

# class Quantity_ColorSWIG(Quantity_Color, PicklableSWIG):
#     def __init__(self, *args):
#         self.args = args
#         Quantity_Color.__init__(self)

# class TDF_LabelSWIG(TDF_Label, PicklableSWIG):
#     def __init__(self, *args):
#         self.args = args
#         TDF_Label.__init__(self)

# # class TopoDS_CompoundSWIG(TopoDS_Compound, PicklableSWIG):
# #     def __init__(self, *args):
# #         self.args = args
# #         TopoDS_Compound.__init__(self)

# # class TopoDS_SolidlSWIG(TopoDS_Solid, PicklableSWIG):
# #     def __init__(self, *args):
# #         self.args = args
# #         TopoDS_Solid.__init__(self)


"""
HR 26/08/2020
ShapeRenderer adapted from pythonocc script "wxDisplay"
https://github.com/tpaviot/pythonocc-core
"""
class ShapeRenderer(OCCViewer.Viewer3d, PicklableSWIG):
    '''
    HR 17/7/20
    Adapted/simplified from OffScreenRenderer in OCCViewer <- OCC.Display
    Dumps render of shape to jpeg file
    '''
    def __init__(self, screen_size = (1000,1000), *args):
        self.args = args
        OCCViewer.Viewer3d.__init__(self)

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

    def __init__(self,
                 viewer = None,
                 axes = None,
                 ic = None,
                 dc = None,
                 sc = None,
                 lc = None,
                 lattice_plot_mode = True):
        ''' Dict of all assembly IDs to SP instances '''
        self._mgr = {}
        ''' List of IDs of all assemblies in lattice '''
        self._assemblies_in_lattice = []

        self._lattice = StepParse('lattice')
        self.pc = PartCompare()

        ''' -----------------------------
        ALL MATCHING/RECONCILIATION STUFF
        ----------------------------- '''
        ''' Weights, constants, etc. '''
        self.MATCHING_WEIGHTS_DEFAULT = [0,1,1,1]
        self.MATCHING_WEIGHTS_STRUCTURE_DEFAULT = [0,1,1,1]
        self.MATCHING_C1_DEFAULT = 0
        self.MATCHING_C2_DEFAULT = 0
        self.MATCHING_FIELD_DEFAULT = 'occ_name'
        self.MATCHING_FIELD_DEFAULT_2 = 'screen_name'
        self.MATCHING_BB_SCALE_DEFAULT = False
        self.MATCHING_TOLERANCE_DEFAULT = 0
        self.MATCHING_SCORE_DEFAULT = -1
        self.MATCHING_BB_TOL_DEFAULT = 1e-4
        self.MATCHING_BB_GROUP_TOL_DEFAULT = 1e-3
        self.MATCHING_MASS_TOL_DEFAULT = 1e-3
        self.MATCHING_MASS_GROUP_TOL_DEFAULT = 1e-3

        self.MATCHING_TEXT_SUFFIXES_DEFAULT = ('.STEP', '.STP', '.step', 'stp')
        self.MATCHING_TEXT_TOL_DEFAULT = 5e-2

        self.MATCH_BY_COMB_DEFAULT = True

        ''' Basic matching strategy:
        1. Block ('b') by item name
        2. Match ('m') within each block with weights [0,1,1,0], i.e.
            ignore item names and shapes,
            equal weights for local structure and bounding box-based metrics
        3. Second part of each sub-stage is for kwargs to method, for specs,
            e.g. 'weights = [0,1,1,0]' '''
        self.MATCHING_STRATEGY_METHODS = {'bn': self.block_by_name,
                                          'bb': self.block_by_bb,
                                          'bm': self.block_by_mass,
                                          'mb': self.match_block}

        # self.MATCHING_STRATEGY_STAGES_DEFAULT = [(('bb', {}), ('mb', {'weights': [0,1,1,1]}))]
        # self.MATCHING_STRATEGY_STAGES_DEFAULT = [(('bm', {}), ('mb', {'weights': [1,1,1,1], 'structure_weights': [1,1,1,1]}))]
        self.MATCHING_STRATEGY_STAGES_DEFAULT = [((None, {}), ('mb', {'weights': [1,1,1,1], 'structure_weights': [1,1,1,1]}))]
        # self.MATCHING_STRATEGY_STAGES_DEFAULT = [(('bn', {}), ('mb', {'weights': [0,1,1,1]}))]
        ''' ----------------------------- '''

        self.SAVE_PATH_DEFAULT = os.getcwd()
        self.SAVE_FILENAME_DEFAULT = 'project.xlsx'
        self.ASSEMBLY_EXTENSION_DEFAULT = 'asy'

        # self.new_assembly_text = 'Unnamed item'
        # self.new_part_text     = 'Unnamed item'

        self.NUMBER_DISAGGREGATE_DEFAULT = 2
        self.ENFORCE_BINARY_DEFAULT = True
        self.DO_ALL_LATTICE_LINES = True

        self.NODE_NAME_OUTPUT_FIELD_DEFAULT = 'screen_name'

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


    def get_new_assembly_name(self, new_id):
        name = 'Assembly ' + str(new_id)
        ''' Check name doesn't exist; create new name by increment if so '''
        names = [a.assembly_name for a in self._mgr.values()]
        # names.remove(name)
        while name in names:
            print('Name already exists')
            new_id += 1
            name = 'Assembly ' + str(new_id)
            continue
        return name


    @property
    def new_assembly_id(self):
        if not hasattr(self, "assembly_id_counter"):
            self.assembly_id_counter = 0
        self.assembly_id_counter += 1
        return self.assembly_id_counter


    # @property
    # def get_assembly_name(self):
    #     if not hasattr(self, '_assembly_name'):
    #         name = 'Assembly ' + str(self.assembly_id)
    #         names = [el._assembly_name for el in self._mgr]
    #         self._assembly_name = name
    #     return self._assembly_name


    ''' Create new assembly (StepParse), with auto name and ID generation '''
    def new_assembly(self, dominant = None, *args, **kwargs):

        ''' Get assembly ID and name '''
        assembly_id = self.new_assembly_id
        # assembly_name = self.get_new_assembly_name(assembly_id)
        assembly = StepParse(assembly_id)

        ''' Add to manager '''
        self._mgr[assembly_id] = assembly
        print('Created new assembly with ID: ', assembly_id)

        if 'enforce_binary' in kwargs:
            assembly.enforce_binary = kwargs['enforce_binary']
        else:
            assembly.enforce_binary = self.ENFORCE_BINARY_DEFAULT

        return assembly_id, assembly


    ''' HR 08/04/22 To create new assembly based on existing one;
                    functionality requires copy.deepcopy of SWIG objects,
                    see PythonOCC issue: https://github.com/tpaviot/pythonocc-core/issues/1097;
                    returns same as "new_assembly", for consistency '''
    def duplicate_assembly(self, id_to_duplicate):

        if id_to_duplicate not in self._mgr:
            print('Assembly not present, returning None')
            return None

        ass_old = self._mgr[id_to_duplicate]

        ''' Create mew name/ID to overwrite... '''
        id_new, ass_new = self.new_assembly()
        name_new = ass_new.assembly_name

        ''' ...then copy everything wholesale, via deepcopy of __dict__... '''
        ass_new.__dict__ = copy.deepcopy(ass_old.__dict__)

        ''' DEBUGGING BLOCK: COPY EACH DICT ENTRY AND CHECK FOR EXCEPTIONS '''
        # ''' Try copying each dict entry individually '''
        # new_dict = {}
        # for k,v in ass_old.__dict__.items():
        #     try:
        #         new_dict[k] = copy.deepcopy(v)
        #         print('Copied ', k,v)
        #         print( 'to: ', k,new_dict[k])
        #     except Exception as e:
        #         print(' Could not copy ', k,v, '; exception follows')
        #         print(e)
        # ''' Copy everything over '''
        # ass_new.__dict__.update(new_dict)

        ''' ...lastly, overwrite name and ID with new ones,
            as will have been written over during __dict__ duplication above '''
        ass_new.assembly_name = name_new
        ass_new.assembly_id = id_new

        return id_new, ass_new


    ''' HR 11/04/22 To import pickled StepParse file '''
    def import_assembly(self, filename):
        print('Trying to import assembly from file: ', filename)

        try:
            with open(filename, 'rb') as handle:
                ass_imported = pickle.load(handle)
                print('Assembly imported')
        except Exception as e:
            print('Could not import assembly, returning None; exception follows')
            print(e)

        ''' Overwrite assembly ID in file in line with manager IDs '''
        old_id = ass_imported.assembly_id
        new_id = self.new_assembly_id
        new_name = self.get_new_assembly_name(new_id)
        ass_imported.assembly_id = new_id
        ass_imported.assembly_name = new_name

        ''' Add to manager '''
        self._mgr[new_id] = ass_imported
        print('Imported assembly with new ID: ', new_id, '(was', old_id, 'in file)')

        ''' Return ID and name, in common with "new_assembly" and "duplicate_assembly" '''
        return new_id, ass_imported


    ''' HR 12/04/22 To export StepParse via pickle '''
    def save_assembly(self, filename, ID):
        print('Trying to export assembly ', ID, 'to file: ', filename)
        if not ID in self._mgr:
            print('Assembly not found, returning False')
            return False

        assembly_to_save = self._mgr[ID]

        try:
            with open(filename, 'wb') as handle:
                pickle.dump(assembly_to_save, handle, protocol = pickle.HIGHEST_PROTOCOL)
            print('Assembly exported, returning True')
            return True

        except Exception as e:
            print('Could not export file, returning False; exception follows')
            print(e)
            return False


    ''' Get lattice node corresponding to node in given assembly
        Return lattice node if present, otherwise None '''
    def get_master_node(self, assembly_id, item):
        for node in self._lattice.nodes:
            for k,v in self._lattice.nodes[node].items():
                if k == assembly_id:
                    if v == item:
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
        self._lattice.add_node(nodem, populate = False)
        self._lattice.nodes[nodem].update({_id:node})

        self.add_edge_in_lattice(_id, parent, node)

        return node, nodem


    ''' HR 14/06/22 Superceded for now by "remove_redundants_in_lattice"
                    which should be called after every operation
                    that might produce redundant nodes;
                    and by "remove_redundants" in StepParse;
                    also a bad name for method, as same as StepParse attribute '''
    # def enforce_binary(self, _id, node):

    #     ass = self._mgr[_id]

    #     ''' Abort if not enforced '''
    #     if not ass.enforce_binary:
    #         print('Not enforcing binary relations; disallowed for assembly ', _id)
    #         return

    #     parent = ass.get_parent(node)
    #     children = [el for el in ass.successors(node)]

    #     ''' Abort if more than one child '''
    #     if not len(children) == 1:
    #         return

    #     print('Single child; removing and linking past node')
    #     print('Assembly ', _id, '; node ', node)

    #     ''' Reparent orphans-to-be '''
    #     for child in children:
    #         self.move_node_in_lattice(_id, child, parent)

    #     ''' Finally, remove redundant node '''
    #     print('  Removing node', node, ' in lattice in "enforce_binary"')
    #     self.remove_node_in_lattice(_id, node)


    def remove_node_in_lattice(self, _id, node):

        print('Running "remove_node_in_lattice"')
        ass = self._mgr[_id]
        nm = self.get_master_node(_id, node)

        parent = ass.get_parent(node)
        leaves = ass.leaves

        print('Trying to remove node', node, 'in assembly ', ass.assembly_name)

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

        ''' Remove now-redundant edges (lattice) '''
        ins = list(ass.in_edges(node))
        outs = list(ass.out_edges(node))
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

        # ''' If original node is leaf, enforce binary relations if necessary '''
        # if node in leaves:
        #     self.enforce_binary(_id, parent)


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

        # ''' Enforce binary relations if necessary '''
        # if not veto_binary:
        #     self.enforce_binary(_id, old_parent)

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
        # ass.remove_redundants()
        # if not new_sub in ass.nodes:
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


    def disaggregate_in_lattice(self, _id, node, num_disagg = None, **attr):

        if not num_disagg:
            num_disagg = self.NUMBER_DISAGGREGATE_DEFAULT

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


    ''' HR 13/06/22 To remove redundants from assembly; avoids problems
                    when using "enforce_binary" related to deletions of
                    already-deleted nodes '''
    def remove_redundants_in_lattice(self, _id):

        ass = self._mgr[_id]
        ''' Remove/add then return affected nodes and edges in target assembly '''
        redundant_nodes, removed_edges, added_edges = ass.remove_redundants()
        print('Nodes to remove: ', redundant_nodes)
        print('Edges to remove: ', removed_edges)
        print('Edges to add: ', added_edges)

        ''' Find corresponding nodes in lattice '''
        redundant_node_map = {node:self.get_master_node(_id, node) for node in redundant_nodes}

        # for node in nodes_to_remove:
        #     failed = []
        #     try:
        #         self.remove_node_in_lattice(_id, node)
        #     except Exception as e:
        #         print('Could not remove node', node,'; exception follows')
        #         print(e)
        #         failed.append(node)

        # removed = [el for el in nodes_to_remove if el not in failed]
        # print('Removed assembly/lattice nodes:')
        # for node in removed:
        #     print(' ', node, '/', node_map[node])

        ''' Rewmove references/nodes in lattice '''
        for node in redundant_nodes:
            latt_node = redundant_node_map[node]
            ''' Remove node completely if only one reference to assembly;
                else remove reference to assembly in question '''
            latt_node_dict = self._lattice.nodes[latt_node]
            if len(latt_node_dict) == 1 and _id in latt_node_dict:
                print('Only one reference (to assembly', _id ,') found in lattice node', latt_node, '; removing entire node (and all connected edges)')
                self._lattice.remove_node(latt_node)
            else:
                print('Multiple references (including to assembly', _id ,') found in lattice node', latt_node, '; removing reference but retaining node')
                latt_node_dict.pop(_id)

        ''' Find corresponding edges in lattice '''
        edge_dict = {}

        for edge in removed_edges | added_edges:
            u = self.get_master_node(_id, edge[0])
            v = self.get_master_node(_id, edge[1])
            ''' Ignore edges connected to already-deleted nodes '''
            if u and v:
                edge_dict[edge] = (u,v)
                print('Assembly edge: ', edge)
                print('Lattice edge:', u,v)

        ''' Delete/update all removed edges in lattice '''
        for edge in removed_edges:
            ''' Skip edges connected to alread-deleted nodes '''
            if edge not in edge_dict:
                continue
            latt_edge = edge_dict[edge]
            ''' Remove edge completely if only one reference to assembly;
                else remove reference to assembly in question '''
            latt_edge_dict = self._lattice.edges[latt_edge]
            if len(latt_edge_dict) == 1 and _id in latt_edge_dict:
                print('Only one reference (to assembly', _id ,') found in lattice edge', latt_edge, '; removing entire edge (and all connected edges)')
                try:
                    self._lattice.remove_edge(latt_edge)
                except:
                    print(' Could not remove edge; may have already been removed during node deletion')
            else:
                print('Multiple references (including to assembly', _id ,') found in lattice edge', latt_edge, '; removing reference but retaining edge')
                latt_edge_dict.pop(_id)

        ''' Add/update all added edges in lattice '''
        for edge in added_edges:
            ''' Skip edges connected to alread-deleted nodes '''
            if edge not in edge_dict:
                continue
            latt_edge = edge_dict[edge]
            ''' Update existing edge with reference to assembly if edge present in lattice;
                else add new edge with reference to assembly '''
            if _id in latt_edge_dict:
                print('Lattice edge', latt_edge, 'already exists; adding reference to assembly', _id)
            else:
                print('Lattice edge', latt_edge, 'not found; creating edge and adding reference to assembly', _id)
                self._lattice.add_edge(*latt_edge)
            latt_edge_dict = self._lattice.edges[latt_edge][_id] = edge


    ''' ----------------------------------------------------------------------
        ADD TO/REMOVE FROM LATTICE
        ----------------------------------------------------------------------
    '''


    ''' HR 05/07/22 To split into separate method from AddToLattice for ease;
                    to be used for (e.g.) first assembly to be added to lattice '''
    def AddToLatticeSimple(self, id1, *args, **kwargs):

        ''' Some basic checks '''
        if id1 not in self._mgr:
            print('ID: ', id1)
            print('Assembly not in manager; returning False')
            return

        if id1 in self._assemblies_in_lattice:
            print('Assembly', id1, 'already in lattice; returning False')
            return

        print('"Simple add": Adding first assembly to lattice')
        a1 = self._mgr[id1]

        for node in a1.nodes:
            new_node = self._lattice.new_node_id
            self._lattice.add_node(new_node, populate = False)
            self._lattice.nodes[new_node].update({id1:node})

        ''' Nodes must exist as edges require "get_master_node" '''
        for n1,n2 in a1.edges:
            u = self.get_master_node(id1, n1)
            v = self.get_master_node(id1, n2)
            self._lattice.add_edge(u,v)
            self._lattice.edges[(u,v)].update({id1:(n1,n2)})

        ''' HR 13/04/22 Added this list everywhere to track IDs present in lattice '''
        self._assemblies_in_lattice.append(id1)
        print('Done AddToLatticeSimple for assembly ID', id1)


    ''' HR 05/07/22 Refactored to pass matches to method
                    ultimately this is to allow user choice before adding to lattice
                    - id1: assembly to compare to
                    - id2: assembly to be added to lattice '''
    ''' HR 14/03/22 New version to use new reconciliation code,
                    including PartFind shape comparison (optionally) '''
    def AddToLattice(self, id1, id2, matches, *args, **kwargs):

        ''' Some basic checks '''
        if id2 not in self._mgr:
            print('ID: ', id2)
            print('Assembly not in manager; returning')
            return

        if id2 in self._assemblies_in_lattice:
            print('Assembly', id2, 'already in lattice; returning')
            return


        ''' Assemblies to be compared established by this point '''
        print('ID of assembly to compare to:         ', id1)
        print('ID of assembly to be added to lattice:', id2)

        a1 = self._mgr[id1]
        a2 = self._mgr[id2]
        ''' HR 05/07/22 Workaround to avoid passing tau to method '''
        # mu1 = [el[0] for el in matches]
        mu2 = [el[1] for el in matches]
        tau2 = [el for el in a2.nodes if el not in mu2]


        print('Matches to add to lattice: ')
        if 'field' in kwargs:
            f = kwargs['field']
        else:
            f = self.MATCHING_FIELD_DEFAULT_2
        # for k,v in matches.items():
        for k,v in matches:
            print('a1 node: ', k, a1.nodes[k][f], 'a2 node: ', v, a2.nodes[v][f])

        '''
            NODES
        '''

        ''' Append to existing master node dict if already present... '''
        # for n1,n2 in matches.items():
        for n1,n2 in matches:
            ''' Returns None if not present... '''
            master_node = self.get_master_node(id1, n1)
            ''' ...but if already present, add... '''
            if master_node:
                self._lattice.nodes[master_node].update({id2:n2})

        ''' ...else create new master node entry '''
        for n2 in tau2:
            node = self._lattice.new_node_id
            self._lattice.add_node(node, populate = False)
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

        ''' Add to lattice list '''
        self._assemblies_in_lattice.append(id2)
        print('Done AddToLattice for assembly ID', id2)

        return matches, id1, id2


    def RemoveFromLattice(self, _id):

        print('Running "RemoveFromLattice"')

        ''' ----------------------- '''
        ''' Preparatory stuff '''

        # if not self._mgr:
        #     print('Cannot remove assembly from lattice: no assembly in manager')
        #     return False

        if _id not in self._assemblies_in_lattice:
            print('ID: ', _id)
            print('Cannot remove assembly from lattice list as not present')
            return False

        ''' ----------------------- '''

        # ''' Remove from manager '''
        # self._mgr.pop(_id)

        ''' CASE 1: Lattice only contains single assembly '''
        if len(self._assemblies_in_lattice) == 1:
            print("Only one assembly in lattice, removing all nodes and edges")
            nodes = [node for node in self._lattice.nodes]
            ''' Edges will be removed automatically when their nodes are removed '''
            for node in nodes:
                self._lattice.remove_node(node)
            return True

        ''' CASE 2: Lattice has more than one assembly in it '''
        nodes = list(self._lattice.nodes)
        edges = list(self._lattice.edges)

        for edge in edges:
            edge_dict = self._lattice.edges[edge]
            if _id in edge_dict:
                ''' Remove entry for assembly in lattice dict... '''
                edge_dict.pop(_id)
                if not any(ass in edge_dict for ass in self._assemblies_in_lattice):
                    ''' ...and remove entirely if no other assemblies in dict '''
                    self._lattice.remove_edge(edge[0],edge[1])

        for node in nodes:
            node_dict = self._lattice.nodes[node]
            if _id in node_dict:
                ''' Remove entry for assembly in lattice dict... '''
                node_dict.pop(_id)
                if not any(ass in node_dict for ass in self._assemblies_in_lattice):
                    ''' ...and remove entirely if no other assemblies in dict '''
                    self._lattice.remove_node(node)

        ''' HR 13/04/22 Must not remove from _mgr!
                        That is covered by "DeleteAssembly '''
        # ''' Remove from manager '''
        # try:
        #     print('Removing assembly from manager...')
        #     self._mgr.pop(_id)
        #     print('Done')
        # except Exception as e:
        #     print('Could not remove assembly from manager; exception follows')
        #     print(e)

        ''' Remove from _mgr and lattice list '''
        self._assemblies_in_lattice.remove(_id)
        self._mgr.pop(_id)

        return True


    ''' HR 18/03/22 To duplicate existing assembly in lattice
                    - id1 = ID of existing (old) assembly being duplicated
                    - id2 = ID of duplicate (new) assembly being added '''
    def DuplicateInLattice(self, id1, id2):
        ''' Duplicate all node references '''
        for node in self._lattice.nodes:
            node_dict = self._lattice.nodes[node]
            if id1 in node_dict:
                print('Found node; duplicating...')
                node_dict[id2] = node_dict[id1]

        ''' Duplicate all edge references '''
        for edge in self._lattice.edges:
            edge_dict = self._lattice.edges[edge]
            if id1 in edge_dict:
                print('Found edge, duplicating...')
                edge_dict[id2] = edge_dict[id1]

        print('Duplicated assembly ', id1, ' in lattice; assembly ', id2, 'now present')
        print('Nodes, edges:')
        for node in self._lattice.nodes:
            print(self._lattice.nodes[node])
        for edge in self._lattice.edges:
            print(self._lattice.edges[edge])

        ''' Append to lattice list '''
        self._assemblies_in_lattice.append(id2)



    ''' HR 13/04/22 Extra method to differentiate between "delete" and "remove from lattice",
                    as second can happen without the first '''
    def DeleteAssembly(self, _id):
        print('Running DeleteAssembly')
        self.RemoveFromLattice(_id)
        self._mgr.pop(_id)


    ''' ---------------------------------------------------------
        ALL NEWER RECONCILIATION CODE
        JAN 2022 ONWARDS
        --------------------------------------------------------- '''


    ''' HR 20/07/22 Modified to allow choice of whether to:
                    (a) Allow matching of sub-assemblies with parts, or
                    (b) Only allow sub-assemblies to be matched combinatorially '''

    ''' HR 20/01/22
        Matching strategy set-up, to return set of matches based on series of blocking/matching stages
        Matched, unmatched and non-matches pairs passed from one stage to next
        Stages differ in terms of:  (a) Metrics used for comparison (via weight vectors)
                                    (b) Whether blocking or matching '''
    def matching_strategy(self, id1, id2, nodes1 = None,
                                          nodes2 = None,
                                          stages = None,
                                          match_subs = False,
                                          *args,
                                          **kwargs):

        a1 = self._mgr[id1]
        a2 = self._mgr[id2]

        ''' Default to all nodes if none specified '''
        if not nodes1:
            nodes1 = a1.nodes
        if not nodes2:
            nodes2 = a2.nodes

        nodes1 = set(nodes1)
        nodes2 = set(nodes2)

        ''' Get leaves and sub-assemblies within node sets '''
        leaves1 = set(a1.leaves)
        leaves2 = set(a2.leaves)
        leaves1 = leaves1 & nodes1
        leaves2 = leaves2 & nodes2

        subs1 = nodes1 - leaves1
        subs2 = nodes2 - leaves2

        print('leaves1:', leaves1)
        print('leaves2:', leaves2)
        print('subs1:', subs1)
        print('subs2:', subs2)

        # ''' Check for/set defaults '''
        # # if not nodes1:
        # #     nodes1 = [node for node in a1.nodes]
        # # if not nodes2:
        # #     nodes2 = [node for node in a2.nodes]
        # if not nodes1:
        #     nodes1 = leaves1
        # if not nodes2:
        #     nodes2 = leaves2


        ''' Get stages specification '''
        if not stages:
            stages = self.MATCHING_STRATEGY_STAGES_DEFAULT


        ''' 04/02/22 For pickling '''
        inputs = (id1, id2, nodes1, nodes2, a1.step_filename, a2.step_filename, stages)



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
        # tau = set()

        mu1 = []
        mu2 = []
        # nu1 = []
        # nu2 = []
        # ''' HR 28/06/22 Very important! This means non-leaves are accounted for '''
        # tau1 = [node for node in a1.nodes]
        # tau2 = [node for node in a2.nodes]

        ''' HR 20/07/22 Create nodes list for matching with option to include sub-assemblies '''
        tau1 = leaves1
        tau2 = leaves2
        if match_subs:
            tau1 = tau1 | subs1
            tau2 = tau2 | subs2


        for i, stage in enumerate(stages):

            ''' Grab all blocking sub-stage information and do blocking '''
            blocking_method, blocking_kwargs = stage[0]
            if (not blocking_method) or (blocking_method not in self.MATCHING_STRATEGY_METHODS):
                print('Blocking stage method not found or specified; skipping stage and defaulting to all unmatched nodes')
                blocks = {0:(tau1, tau2)}
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
            # non_matches = set()

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
                    if block_v[0] and block_v[1]:
                        matches_in_block, non_matches_in_block = matching_method(id1, id2, block_v[0], block_v[1], **matching_kwargs)[0:2]
                        print('Matches in block {} of {} and stage {} of {}:\n'.format(
                            j+1, len(blocks), i+1, len(stages)), matches_in_block)

                        ''' Update set of matches within current stage '''
                        print('Matches: ', matches)
                        print('Matches in block: ', matches_in_block)
                        matches = matches | set(matches_in_block)
                    else:
                        print('No nodes found in one half of block; not proceeding with matching...')

            '''
            UPDATE GLOBAL MATCHES ETC.
            '''

            '''Add matches within stage (matches) to master set/lists of matches (mu) and unmatches (tau) '''
            mu = matches | mu
            print('Matches: ', matches)
            print('mu:      ', mu)
            # ''' Remove matches from unmatched sets '''
            # nu = nu - mu

            matches1 = [el[0] for el in matches]
            matches2 = [el[1] for el in matches]
            mu1.extend(matches1)
            mu2.extend(matches2)

            tau1 = [el for el in tau1 if el not in mu1]
            tau2 = [el for el in tau2 if el not in mu2]

            ''' -- '''

        print('\nLEAF MATCHES:\n', mu)


        ''' HR 14/06/22 To integrate combinatorial sub-assembly matching '''
        if 'match_by_comb' in kwargs:
            match_by_comb = kwargs['match_by_comb']
        else:
            match_by_comb = self.MATCH_BY_COMB_DEFAULT

        ''' HR 20/07/22 Added second "match_subs" condition here to prevent subs being compared both above and here'''
        if match_by_comb and not match_subs:
            matches = self.match_by_comb(id1, id2, mu, subs1, subs2)[0]
            print('\nSUBS MATCHES:\n', matches)

            '''
            UPDATE GLOBAL MATCHES ETC.
            '''

            '''Add matches within stage (matches) to master set/lists of matches (mu) and unmatches (tau) '''
            mu = matches | mu
            print('Matches: ', matches)
            print('mu:      ', mu)
            # ''' Remove matches from unmatched sets '''
            # nu = nu - mu

            matches1 = [el[0] for el in matches]
            matches2 = [el[1] for el in matches]
            mu1.extend(matches1)
            mu2.extend(matches2)

            tau1 = [el for el in tau1 if el not in mu1]
            tau2 = [el for el in tau2 if el not in mu2]

            ''' -- '''

        else:
            print('\nNot matching subs combinatorially\n')


        ''' 04/2/22 For pickling '''
        outputs = (mu, mu1, mu2, tau1, tau2)

        # return mu, mu1, mu2
        return inputs, outputs


    # ''' HR 19/01/22
    #     To  (1) grab existing matches from lattice nodes for specified assemblies, or
    #         (2) grab notional matches from one BoM, for when it is to be duplicated,
    #             i.e. assume same nodes IDs in BoM1 as in notional BoM2
    #     Returns dictionary of master_node: (node1,node2) in case master node needed later '''
    # def grab_matches(self, id1, id2 = None):
    #     matches = {}
    #     for latt_node in self._lattice.nodes:
    #         node_dict = self._lattice.nodes[latt_node]
    #         if (id1 in node_dict):
    #             print('Assembly ID in latt node dict...')
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


    '''
    HR 27/01/22
    To group items by name including inexactly via Levenshtein distance
    NOT FULLY TESTED AND MULTIPLE ISSUES IF 'screen_name' USED AS QUERY FIELD:
        1. Endings (e.g. "_1") not accounted for when multiple instances of item exist;
        2. The above complicated further if suffixes exists (e.g. ".STEP" -> ".STEP_1") as cannot then be removed consistently;
        3. Cannot deal with non-product names (e.g. if default names present for "SOLID" or other shape types) or empty name fields
    Correctly groups parking trolley items if text_tol = 1e-2; this is small b/c some very long names, e.g. beginning with "Colson"
    '''
    def block_by_name(self, id1, id2, nodes1 = None,
                                      nodes2 = None,
                                      text_tol = None,
                                      suffixes = None,
                                      field = None,
                                      field2 = None):

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
        if not field2:
            field2 = self.MATCHING_FIELD_DEFAULT_2

        groups = {}
        grouped = False

        for n1 in nodes1:
            text = a1.nodes[n1][field]
            if not text:
                print('No name found at node ', n1, '; defaulting to "', str(field2), '"')
                text = a1.nodes[n1][field2]
                # continue
            print('Name: ', text)
            ''' Remove suffixes '''
            if suffixes:
                # print(' TEXT: ', text)
                text = remove_suffixes(text, suffixes = suffixes)
            if text in groups:
                # print('Adding to existing group (exact match)')
                groups[text][0].append(n1)
                continue
            for k in groups.keys():
                lev_dist = nltk.edit_distance(text, k)
                sim = 1 - lev_dist/max(len(text), len(k))

                if sim > 1-text_tol:
                    # print('Adding to existing group (inexact match), score = ', sim)
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
                print('No name found at node ', n2, '; defaulting to "', str(field2), '"')
                text = a2.nodes[n2][field2]
                # continue
            print('Name found: ', text)
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
    def block_by_bb(self, id1, id2, nodes1 = None,
                                    nodes2 = None,
                                    bb_tol = None,
                                    group_tol = None):

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
            try:
                bb_ar = self.get_dims(id1, n1)[1]
            except:
                continue

            if bb_ar:
                # print('Retrieved AR, trying to group...')
                bb_sum = np.sum(bb_ar)
            else:
                # print('Retrieved None as AR; skipping...')
                continue
            if bb_sum in groups:
                # print('Adding to existing group (exact match)')
                groups[bb_sum][0].append(n1)
                continue
            for k in groups.keys():
                if np.isclose(k, bb_sum, rtol = group_tol):
                    # print('Adding to existing group (inexact match)')
                    groups[k][0].append(n1)
                    grouped = True
                    break
                continue
            if grouped:
                grouped = False
                continue
            # print('Creating new group')
            groups[bb_sum] = ([n1], [])

        for n2 in nodes2:
            try:
                bb_ar = self.get_dims(id2, n2)[1]
            except:
                continue

            if bb_ar:
                # print('Retrieved AR, trying to group...')
                bb_sum = np.sum(bb_ar)
            else:
                # print('Retrieved None as AR; skipping...')
                continue
            if bb_sum in groups:
                # print('Adding to existing group (exact match)')
                groups[bb_sum][1].append(n2)
                continue
            for k in groups.keys():
                if np.isclose(k, bb_sum, rtol = group_tol):
                    # print('Adding to existing group (inexact match)')
                    groups[k][1].append(n2)
                    grouped = True
                    break
                continue
            if grouped:
                grouped = False
                continue
            # print('Creating new group')
            groups[bb_sum] = ([], [n2])

        return groups


    '''
    HR 01/08/22
    To group items by volume ("mass" in Open Cascade, with density = 1 by default)
    Groups if (a) exact match or (b) inexact match (within tolerance) according to sim score
    '''
    def block_by_mass(self, id1, id2, nodes1 = None,
                                      nodes2 = None,
                                      mass_tol = None,
                                      group_tol = None):

        ''' Check for/set defaults '''
        if not nodes1:
            a1 = self._mgr[id1]
            nodes1 = a1.nodes
        if not nodes2:
            a2 = self._mgr[id2]
            nodes2 = a2.nodes

        if not mass_tol:
            mass_tol = self.MATCHING_MASS_TOL_DEFAULT
        if not group_tol:
            group_tol = self.MATCHING_MASS_GROUP_TOL_DEFAULT

        groups = {}
        grouped = False

        for n1 in nodes1:
            try:
                mass = self.get_mass_data(id1, n1)[1]
            except:
                continue

            if mass:
                print('Retrieved volume, trying to group...')
            else:
                print('Retrieved None as volume; skipping...')
                continue
            if mass in groups:
                print('Adding to existing group (exact match)')
                groups[mass][0].append(n1)
                continue
            for k in groups.keys():
                if np.isclose(k, mass, rtol = group_tol):
                    print('Adding to existing group (inexact match)')
                    groups[k][0].append(n1)
                    grouped = True
                    break
                continue
            if grouped:
                grouped = False
                continue
            print('Creating new group')
            groups[mass] = ([n1], [])

        for n2 in nodes2:
            try:
                mass = self.get_mass_data(id2, n2)[1]
            except:
                continue

            if mass:
                print('Retrieved AR, trying to group...')
            else:
                print('Retrieved None as AR; skipping...')
                continue
            if mass in groups:
                print('Adding to existing group (exact match)')
                groups[mass][1].append(n2)
                continue
            for k in groups.keys():
                if np.isclose(k, mass, rtol = group_tol):
                    print('Adding to existing group (inexact match)')
                    groups[k][1].append(n2)
                    grouped = True
                    break
                continue
            if grouped:
                grouped = False
                continue
            print('Creating new group')
            groups[mass] = ([], [n2])

        return groups


    ''' HR 03/08/22 Added option to compute mass-/volume- and distance-based similarities as alternative to BB '''
    ''' HR 10/12/21 To grab all similarity scores
        For testing integration with PartFind '''
    def get_sims(self, id1, id2, node1, node2, field = None,
                                               weights = None,
                                               structure_weights = None,
                                               C1 = None,
                                               C2 = None,
                                               scale_bb = None,
                                               by_mass = True,
                                               *args,
                                               **kwargs):

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
        if not scale_bb:
            scale_bb = self.MATCHING_BB_SCALE_DEFAULT

        # print('weights =', weights)

        ''' Get name-based similarity '''
        if weights[0] > 0:
            sim_name = self.similarity_strings(id1, id2, node1, node2, field = field)[1]
        else:
            sim_name = 0
        # print('Name sim: ', sim_name)

        ''' Get local assembly structure-based score '''
        if weights[1] > 0:
            sim_str = self.similarity_structure(id1, id2, node1, node2, structure_weights = structure_weights, C1 = C1, C2 = C2)[0]
            # sim_str = sum(x*y for x,y in zip(sims, structure_weights))/sum(structure_weights)
        else:
            sim_str = 0
        # print('Struct sim: ', sim_str)

        ''' Get size-based score '''
        if by_mass:
            if weights[2] > 0:
                print('Getting mass/distance-based score')
                sim_size = self.similarity_mass(id1, id2, node1, node2, *args, **kwargs)
            else:
                sim_size = 0
        else:
            if weights[2] > 0:
                print('Getting BB-based score')
                sim_size = self.similarity_bb(id1, id2, node1, node2, scale = scale_bb)
            else:
                sim_size = 0
        # print('Size sim: ', sim_size)

        ''' Get shape-based score '''
        if weights[3] > 0:
            sim_sh = self.similarity_shape(id1, id2, node1, node2)
        else:
            sim_sh = 0
        # print('Shape sim: ', sim_sh)

        sims = (sim_name, sim_str, sim_size, sim_sh)
        sim_total = sum([s*w for s,w in zip(sims,weights)])/sum(weights)

        return sim_total, sims, weights


    ''' HR 10/21/12 To get all local assembly structure-based similarity scores
        All copied/adapted from older "node_sim" method below '''
    def similarity_structure(self, id1, id2, node1, node2, structure_weights = None,
                                                           C1 = None,
                                                           C2 = None,
                                                           field = None):

        ''' Check for/set defaults '''
        if not structure_weights:
            structure_weights = self.MATCHING_WEIGHTS_STRUCTURE_DEFAULT
        if not C1:
            C1 = self.MATCHING_C1_DEFAULT
        if not C2:
            C2 = self.MATCHING_C2_DEFAULT
        if not field:
            field = self.MATCHING_FIELD_DEFAULT

        # print('Structure weights:', structure_weights)

        a1 = self._mgr[id1]
        a2 = self._mgr[id2]

        # print('Structure weights:', structure_weights)

        ''' Get parents, where None is default if no parent... '''
        if structure_weights[0] > 0:
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


        ''' Get number of children... '''
        if structure_weights[1] > 0:
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


        ''' Get tree-depth similarity '''
        if structure_weights[3] > 0:
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


        sims = (sim_parent, sim_children, sim_sibs, sim_depth)
        sim_str = sum([s*w for s,w in zip(sims,structure_weights)])/sum(structure_weights)

        # print("Returning structure sims:", sim_str, sims, structure_weights)
        return sim_str, sims, structure_weights


    ''' HR 31/01/22 To automate/abstract all BB dimensions retrieval '''
    def get_dims(self, assembly_id, node, field = None,
                                          save_path = None):

        ''' Check for/set defaults '''
        if not field:
            field = self.MATCHING_FIELD_DEFAULT
        if not save_path:
            save_path = self.SAVE_PATH_DEFAULT

        assembly = self._mgr[assembly_id]
        node_dict = assembly.nodes[node]
        name = node_dict[field]
        if not name:
            # print('No name found; returning None')
            return None
        folder = remove_suffixes(assembly.step_filename)
        # print('Folder, name: ', folder, name)

        file = os.path.join(save_path, folder, name)
        # print('File:\n ', file)

        dimsfile = file + '.dims'
        got_dims = False

        ''' Create pickled dims if not already present '''
        if not os.path.isfile(dimsfile):
            print('Pickled aspect ratio (AR) data not found; getting shape and computing dimensions of bounding box (BB)...')
            # print('Retrieving shape...\n ')
            shape = node_dict['shape_loc'][0]
            if not shape:
                # print('Shape not found; returning None')
                return None
            ''' Create folder if not present '''
            if not os.path.isdir(folder):
                # print('Folder not present; creating...')
                os.mkdir(folder)
            # print('Computing and pickling AR data...\n ', dimsfile)
            dims = get_dimensions(shape)
            got_dims = True
            dims_writer = open(dimsfile,"wb")
            pickle.dump(dims, dims_writer)
            dims_writer.close()

        ''' Load pickled BB data '''
        if not got_dims:
            # print('Opening pickled BB data...\n ', arfile)
            dims_loader = open(dimsfile,"rb")
            dims = pickle.load(dims_loader)

        return dims


    ''' HR 28/07/22 To get mass and centre of mass info
                    Some duplication with "get_dims", probably acceptable '''
    def get_mass_data(self, assembly_id, node, field = None,
                                               save_path = None):

        ''' Check for/set defaults '''
        if not field:
            field = self.MATCHING_FIELD_DEFAULT
        if not save_path:
            save_path = self.SAVE_PATH_DEFAULT

        assembly = self._mgr[assembly_id]
        node_dict = assembly.nodes[node]
        name = node_dict[field]
        if not name:
            print('No name found; returning None')
            return None
        folder = remove_suffixes(assembly.step_filename)
        # print('Folder, name: ', folder, name)

        file = os.path.join(save_path, folder, name)
        print('File:\n ', file)

        massfile = file + '.mass'
        got_mass = False

        ''' Create pickled data if not already present '''
        if not os.path.isfile(massfile):
            print('Pickled volume data not found; getting volume data...')
            # print('Retrieving shape...\n ')
            shape = node_dict['shape_loc'][0]
            if not shape:
                print('Shape not found; returning None')
                return None
            ''' Create folder if not present '''
            if not os.path.isdir(folder):
                print('Folder not present; creating...')
                os.mkdir(folder)
            print('Computing and pickling volume data...\n ', massfile)
            mass = get_mass_properties(shape)
            got_mass = True
            mass_writer = open(massfile,"wb")
            pickle.dump(mass, mass_writer)
            mass_writer.close()

        ''' Load pickled volume data '''
        if not got_mass:
            print('Opening pickled volume data...\n ', massfile)
            mass_loader = open(massfile,"rb")
            mass = pickle.load(mass_loader)

        return mass


    ''' HR 31/01/22
        To replace older method by abstracting more: just pass shape and retrieve ARs
        Incorporates (a) retrieval from file and/or (b) pickling to file if necessary '''
    def similarity_bb(self, id1, id2, node1, node2, field = None,
                                                    scale = None,
                                                    *args,
                                                    **kwargs):

        ''' Check for/set defaults '''
        if not field:
            field = self.MATCHING_FIELD_DEFAULT
        if not scale:
            scale = self.MATCHING_BB_SCALE_DEFAULT

        try:
            ar1,dim1 = self.get_dims(id1, node1)
        except:
            # print('Could not get AR: exception')
            ar1,dim1 = None,None
        try:
            ar2,dim2 = self.get_dims(id2, node2)
        except:
            # print('Could not get AR: exception')
            ar2,dim2 = None,None

        ''' HR 29/04/22 To account for scale variation between shapes '''
        if scale:
            # print('  SCALE!')
            vol1 = np.prod(dim1)
            vol2 = np.prod(dim2)
            phi = vol1/vol2
        else:
            # print('   DO NOT SCALE!')
            phi = 1

        ''' Calculate similarity '''
        if ar1 and ar2:
            sim_bb = get_bb_score(ar1, ar2, phi = phi)
            return sim_bb
        else:
            return self.MATCHING_SCORE_DEFAULT


    ''' HR 02/08/22
        To retrieve item mass/volume and centre of mass (COM), as alternative to BB
        Incorporates (a) retrieval from file and/or (b) pickling to file if necessary
        Calculate similarity based on:
            - Volume by default (centre_of_mass = False), else
            - Centre of mass (centre_of_mass = True) '''
    def similarity_mass(self, id1, id2, node1, node2, field = None,
                                                      centre_of_mass = False,
                                                      *args,
                                                      **kwargs):

        ''' Check for/set defaults '''
        if not field:
            field = self.MATCHING_FIELD_DEFAULT

        try:
            com1, mass1 = self.get_mass_data(id1, node1)
        except:
            print('Could not get mass data: exception')
            com1, mass1 = None, None
        try:
            com2, mass2 = self.get_mass_data(id2, node2)
        except:
            print('Could not get mass data: exception')
            com2, mass2 = None, None

        ''' Calculate similarity '''
        if not centre_of_mass:
            if mass1 and mass2:
                sim_mass = get_mass_score(mass1, mass2, *args, **kwargs)
                print('Returning mass-based similarity...', sim_mass)
                return sim_mass
            else:
                print('Exception; returning default score...')
                return self.MATCHING_SCORE_DEFAULT
        else:
            if com1 and com2:
                sim_com = get_distance_score(com1, com2, *args, **kwargs)
                print('Returning distance-based similarity...', sim_com)
                return sim_com
            else:
                print('Exception; returning default score...')
                return self.MATCHING_SCORE_DEFAULT


    ''' HR 31/01/22 To automate/abstract all shape-thing retrieval,
        where a shape thing is shape representation used in PartFind
        (graph in older PF versions, vector in newer versions) '''
    def get_shape_thing(self, assembly_id, node, field = None,
                                                 save_path = None):

        ''' Check for/set defaults '''
        if not field:
            field = self.MATCHING_FIELD_DEFAULT
        if not save_path:
            save_path = self.SAVE_PATH_DEFAULT

        assembly = self._mgr[assembly_id]
        node_dict = assembly.nodes[node]
        name = node_dict[field]
        folder = remove_suffixes(assembly.step_filename)

        file = os.path.join(save_path, folder, name)
        # print('File:\n ', file)

        pickle_file = file + '.pickle'
        thing_in_memory = False

        ''' Create pickled thing if not already present '''
        if not os.path.isfile(pickle_file):
            # print('Pickled graph not found...')
            step_file = file + '.STEP'
            ''' Create STEP file for part if not already present '''
            if not os.path.isfile(step_file):
                # print('Getting shape and writing to STEP file...')
                shape = node_dict['shape_loc'][0]
                if not shape:
                    # print('Shape not found; returning None')
                    return None
                ''' Create folder if not present '''
                if not os.path.isdir(folder):
                    # print('Folder not present; creating...')
                    os.mkdir(folder)
                # print('shape, full file path:\n ', shape, step_file)
                DataExchange.write_step_file(shape, step_file)
            # print('Creating graph from STEP file...\n ', step_file)
            try:
                thing = load_from_step(step_file)
            except:
                # print('Could not create graph; returning None')
                return None
            # print('Pickling graph...\n ', pickle_file)
            pickle_writer = open(pickle_file,"wb")
            pickle.dump(thing, pickle_writer)
            pickle_writer.close()
            thing_in_memory = True

        ''' Load pickled thing if not already in memory '''
        if not thing_in_memory:
            # print('Opening pickled shape thing...\n ', pickle_file)
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
            # print('Could not get shape thing: exception')
            thing1 = None

        try:
            thing2 = self.get_shape_thing(id2, node2, field = field)
        except:
            # print('Could not get shape thing: exception')
            thing2 = None

        ''' Calculate similarity '''
        if thing1 and thing2:
            sim_sh = self.pc.model.test_pair(thing1, thing2)
            # print("Similarity score:", sim_sh)
            return sim_sh
        else:
            return self.MATCHING_SCORE_DEFAULT


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

        # print("String similarity stuff:", str1, str2)
        # print(lev_dist, sim)
        return lev_dist, sim


    ''' HR 15/12/21 General-purpose method for returning set of optimal matches from specific block '''
    def match_block(self, id1, id2, nodes1 = None,
                                    nodes2 = None,
                                    weights = None,
                                    structure_weights = None,
                                    tol = None,
                                    default_value = None,
                                    C1 = None,
                                    C2 = None,
                                    scale = None):
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
        else:
            nodes1 = list(nodes1)
        if not nodes2:
            a2 = self._mgr[id2]
            nodes2 = [node for node in a2.nodes]
        else:
            nodes2 = list(nodes2)

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
        if not scale:
            scale = self.MATCHING_BB_SCALE_DEFAULT

        ''' Get all similarity scores:
            1. Fill with default values
            (must define arrays as floats here,
             else numpy assumes int and updates values wrongly) '''
        np_kwargs = {'fill_value': default_value, 'dtype': 'float'}
        scores_name = np.full((len(nodes1), len(nodes2)), **np_kwargs)
        scores_str = np.full((len(nodes1), len(nodes2)), **np_kwargs)
        scores_size = np.full((len(nodes1), len(nodes2)), **np_kwargs)
        scores_sh = np.full((len(nodes1), len(nodes2)), **np_kwargs)

        '''
        HR 15/03/22 N.B. ARE WEIGHTS APPLIED TWICE HERE?
        i.e. once when calling get_sims and again when doing np.average?
        '''

        ''' 2. Populate with scores '''
        for i,n1 in enumerate(nodes1):
            for j,n2 in enumerate(nodes2):
                sim_name, sim_str, sim_size, sim_sh = self.get_sims(id1, id2, n1, n2, weights = weights,
                                                                                      structure_weights = structure_weights,
                                                                                      C1 = C1,
                                                                                      C2 = C2,
                                                                                      scale = scale)[1]
                # print('Nodes:', n1,n2, '\nSims: ', sim_name, sim_str, sim_size, sim_sh)
                scores_name[i,j] = sim_name
                scores_str[i,j] = sim_str
                scores_size[i,j] = sim_size
                scores_sh[i,j] = sim_sh

        ''' Multiply by weights to get aggregate scores...
            (alternative is to scale by weights within "get_sims" method, then set weights to 1 here) '''
        scores = np.average([scores_name, scores_str, scores_size, scores_sh], axis = 0, weights = weights)

        ''' ...then compute indices in array of globally optimal matches via Hungarian algorithm... '''
        rows, cols, best = hungalg.get_optimal_values(scores)
        pairs = list(zip(rows, cols))
        # print('Pairs by index: ', pairs)
        # print('Nodes1: ', nodes1)
        # print('Nodes2: ', nodes2)

        ''' ...find any pairs with scores below the threshold ("tol")... '''
        excluded = [pair for pair in pairs if scores[pair] < tol]

        ''' ...and convert to matches in terms of node IDs '''
        matches = [(nodes1[pair[0]], nodes2[pair[1]]) for pair in pairs]
        excluded = [(nodes1[pair[0]], nodes2[pair[1]]) for pair in pairs if scores[pair] < tol]

        scores_out = (scores_name, scores_str, scores_size, scores_sh, scores)

        return matches, excluded, scores_out


    ''' HR 15/06/22 TO DO
                    Rewrite to match sub-assemblies via lattice,
                    rather than through assembly 1, as otherwise may miss some,
                    e.g. loading ass1, ass2, ass2 misses common sub-assemblies in ass2
                    -> duplicated nodes and edges in lattice '''
    ''' --- '''

    ''' HR 26/04/22 To get all matches of sub-assemblies combinatorially,
                    i.e. match subs by IDs of leaves they contain;
                    simple comparison of sets of IDs
                    - id1, id2: IDs of assemblies whose nodes are being compared
                    - leaf_matches: IDs of leaves in each assembly that have already been matched
                    - subs1, subs2: sub-assemblies in each assembly to be compared '''
    def match_by_comb(self, id1, id2, leaf_matches, subs1 = None,
                                                    subs2 = None):
        ass1 = self._mgr[id1]
        ass2 = self._mgr[id2]

        ''' Default to all non-leaves '''
        if not subs1:
            subs1 = set(ass1.nodes) - ass1.leaves - {ass1.head}
            # subs1 = set(ass1.nodes) - ass1.leaves
        if not subs2:
            subs2 = set(ass2.nodes) - ass2.leaves - {ass2.head}
            # subs2 = set(ass2.nodes) - ass2.leaves

        ''' Convert matches to dict for easy lookup '''
        m_dict = dict(leaf_matches)

        print('subs1:', subs1)
        print('subs2:', subs2)
        print('m_dict:', m_dict)

        ''' Get dict of leaves for each non-leaf; assembly IDs '''
        leaves_in1 = ass1.get_leaves_in(subs1)
        leaves_in2 = ass2.get_leaves_in(subs2)

        ''' Get exact sub-assembly matches combinatorially '''
        subs_matches = set()
        for s1 in subs1:
            c1 = leaves_in1[s1]
            print('sub1,c1:', s1, c1)
            if all (k in m_dict for k in c1):
                print('All nodes found in leaf map')
            else:
                print('All nodes NOT found in leaf map; going to next sub')
                continue

            ''' Get corresponding combinatorial ID of sub in second assembly... '''
            c1_mapped = {m_dict[el] for el in c1}
            ''' ...then see if it exists '''
            print('Mapped ', c1, ' to ', c1_mapped, '; looking through second assembly')
            for s2 in subs2:
                c2 = leaves_in2[s2]
                if c1_mapped == c2:
                    print('Found match! ', c1, c2)
                    subs_matches.add((s1,s2))
                    continue

        return subs_matches, subs1, subs2


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
        self.viewer.subplots_adjust(left = 0.01,
                                    bottom = 0.01,
                                    right = 0.99,
                                    top = 0.99)

        self.axes.axes.axis('off')
        self.axes.axes.get_xaxis().set_ticks([])
        self.axes.axes.get_yaxis().set_ticks([])


    def update_colours_selected(self, active, selected = [],
                                              to_select = [],
                                              to_unselect = [],
                                              called_by = None):

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


    def update_colours_active(self, to_activate = [],
                                    to_deactivate = [],
                                    called_by = None):

        print('Running "update_colours_active"')
        print('Called by: ', called_by)

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


    ''' HR 22/02/22 To grab list of node info for export etc. '''
    def get_node_info(self, _id = None, nodes = None, indent = True, field = None):

        ''' Get lattice node data if no ID given '''
        if _id:
            assembly = self._mgr[_id]
        else:
            assembly = self._lattice
        ''' Default to all nodes if none specified;
            Only specified nodes added to dict
            but whole graph must be traversed anyway '''
        if not nodes:
            nodes = assembly.nodes
        if not field:
            field = self.MATCHING_FIELD_DEFAULT

        ''' Initialise dict '''
        node_info = {}
        node_list = []
        level = [0]

        ''' Function called for each node '''
        def get_children(node):
            children = assembly.successors(node)
            level[0] += 1
            for child in children:
                if child in nodes:
                    parent = assembly.get_parent(child)
                    ''' If ID given, get screen names; else get all lattice node info '''
                    if _id:
                        try:
                            text = str(assembly.nodes[child][field])
                        except:
                            text = 'Unnamed item'
                    else:
                        text = str(assembly.nodes[child])
                    ''' Add tree-like indentation if "indent" true '''
                    if indent:
                        # if level[0]>0:
                        #     p_level = node_info[parent][1]
                        #     text = p_level*'  ' + '|' + (level[0] - p_level)*'__' + text
                        text = (level[0]-1)*'   ' + '|__' + text
                    data = (text, level[0], parent)
                    # print(data)
                    node_info[child] = data
                    node_list.append(child)
                ''' Recurse '''
                get_children(child)
            level[0] -= 1


        ''' Starts here: get head info then traverse graph recursively '''
        # try:
        #     head = assembly.head
        #     print('Found head node: ', head)
        # except:
        #     print('Could not find "head" node explcitly; returning all zero in-degree nodes if more than one, or usual node info if only one')
        #     heads = [node for node in assembly if assembly.in_degree(node) == 0]
        #     if len(heads) > 1:
        #         print(' Multiple head nodes found; returning head nodes:', heads)
        #         return heads
        #     else:
        #         print(' Found one head node; returning node info')
        #         head = heads[0]
        ''' HR 16/06/22 Rewritten to allow for assemblies with no node called "head";
                        also accounts for any assembly that's had original head removed,
                        e.g. via removing redundants '''
        head = assembly.get_root()

        if head in nodes:
            if _id:
                try:
                    text = str(assembly.nodes[head][field])
                except:
                    text = ('Head node (no name)')
            else:
                text = str(assembly.nodes[head])
            data = (text, level[0], 'None')
                # print(data)
            node_info[head] = data
            node_list.append(head)
        get_children(head)

        return node_info, node_list


    ''' HR June 21 Method removed from StrEmbed
        Dumps all basic project/lattice, assembly and node info:
            Node ID, label/text, parent
        Keep for now, can reuse for larger "save" functionality later '''
    ''' HR 25/02/21
        Basic XLSX output for whole lattice (i.e. all assemblies) '''
    def xlsx_write(self, _ids = None, name_field = None, save_file = None, indent = True):

        if not save_file:
            save_file = self.SAVE_FILENAME_DEFAULT

        try:
            print('Trying to create Excel file at...')
            print(save_file)
            workbook = xlsxwriter.Workbook(save_file)
            print('Done')
        except:
            print('...could not create Excel file; creating default file name')
            save_file = self.SAVE_FILENAME_DEFAULT
            try:
                workbook = xlsxwriter.Workbook(save_file)
            except:
                print('Could not create Excel file; returning False...')
                return False

        ''' Get all assembly IDs if none specified '''
        if not _ids:
            _ids = [el for el in self._mgr]

        if not name_field:
            name_field = self.NODE_NAME_OUTPUT_FIELD_DEFAULT

        def get_header(_id):
            assembly = self._mgr[_id]
            header = []
            header.append(assembly.assembly_id)
            if hasattr(assembly, 'assembly_name'):
                header.append(assembly.assembly_name)
            else:
                header.append('-')
            if hasattr(assembly, 'step_filename'):
                header.append(assembly.step_filename)
            else:
                header.append(-'No STEP filename')
            return header

        ''' Create summary sheet '''
        sheet_dict = {}
        sheet_dict['summary'] = workbook.add_worksheet('Summary')
        summary_fields = ['Assembly ID', 'Assembly name', 'STP/STEP file', 'Sheet number']
        for i,el in enumerate(summary_fields):
            sheet_dict['summary'].write(0, i, el)
        ''' Dump summary of all assemblies to summary sheet '''
        for i,_id in enumerate(_ids):
            assembly = self._mgr[_id]
            assembly_name = assembly.assembly_name
            step_file = assembly.step_filename
            sheet_number = i+2
            assembly_data = [_id, assembly_name, step_file, sheet_number]
            for j,el in enumerate(assembly_data):
                x = j
                y = i+1
                sheet_dict['summary'].write(y, x, el)

        ''' Set up formatting of headers '''
        header_fields = ['Assembly ID', 'Assembly name', 'STP/STEP file']
        y_offset = len(header_fields) + 2
        fields = ['Node ID', 'Name', 'Level', 'Parent ID', ]

        ''' Create worksheet for each assembly to be exported '''
        for j,_id in enumerate(_ids):
            assembly = self._mgr[_id]
            # assembly_name = assembly.assembly_name
            # sheet_name = str(assembly_name)
            # # sheet_name = re.sub('[^a-zA-Z0-9 \n\.]', '', my_str)
            ''' Write main header... '''
            # sheet_dict[_id] = workbook.add_worksheet(sheet_name)
            sheet_dict[_id] = workbook.add_worksheet()
            header_data = get_header(_id)
            for i,el in enumerate(header_fields):
                sheet_dict[_id].write(i, 0, el)
                sheet_dict[_id].write(i, 1, header_data[i])

            ''' ...and node fields header '''
            for i,el in enumerate(fields):
                sheet_dict[_id].write(y_offset-1,i,el)

            node_info, node_list = self.get_node_info(_id, indent = indent, field = name_field)

            # counter = 0
            # for node in assembly:
            #     node_data = [node]
            #     node_data.extend([el for el in node_info[node]])
            #     print(node_data)
            #     for i,el in enumerate(node_data):
            #         x = i
            #         y = counter + y_offset
            #         sheet_dict[_id].write(y, x, el)
            #     counter += 1

            ''' HR 17/06/22 Rewritten to print/dump in order found in assembly,
                            i.e. from head downwards, instead of node-wise
                            as was the case previously,
                            as this garbles the order if any changes have been made
                            to the assembly structure '''
            counter = 0
            for node in node_list:
                node_data = [node]
                node_data.extend([el for el in node_info[node]])
                print(node_data)
                for i,el in enumerate(node_data):
                    x = i
                    y = counter + y_offset
                    sheet_dict[_id].write(y, x, el)
                counter += 1

        try:
            workbook.close()
            print('Closed Excel file')
            return True
        except:
            print('Could not close Excel file; returning False...')
            return False


class StepParse(nx.DiGraph):

    def __init__(self, assembly_id = None, *args, **kwargs):

        self.args = args
        super().__init__(*args, **kwargs)
        self.part_level = 1

        ''' Below is full range of shape types, according to Open Cascade documentation here:
            https://dev.opencascade.org/doc/refman/html/class_topo_d_s___shape.html '''
        self.topo_types = (TopoDS_Shape, TopoDS_Solid, TopoDS_Compound, TopoDS_Shell, TopoDS_Face, TopoDS_Vertex, TopoDS_Edge, TopoDS_Wire, TopoDS_CompSolid)
        # self.topo_types = (TopoDS_Solid, TopoDS_Compound)
        # self.topo_types = (TopoDS_Solid, TopoDS_Compound, TopoDS_Shell, TopoDS_Face)
        # self.topo_types = (TopoDS_Solid,)

        self.assembly_id = assembly_id
        if 'assembly_name' in kwargs:
            self.assembly_name = kwargs['assembly_name']
        else:
            self.assembly_name = 'Assembly ' + str(self.assembly_id)
        # self.OCC_dict = {}

        self.default_label_part = 'Unnamed item'
        self.default_label_ass = 'Unnamed item'
        if 'head_name_default' in kwargs:
            self.HEAD_NAME_DEFAULT = kwargs['head_name_default']
        else:
            self.HEAD_NAME_DEFAULT = '** PROJECT **'

        ''' Mid-grey for default shape colour '''
        self.SHAPE_COLOUR_DEFAULT = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)

        # self.enforce_unary = True

        self.renderer = ShapeRenderer()

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


    # ''' Overridden to add label to node upon creation '''
    # def add_node(self, node, **attr):
    #     super().add_node(node, **attr)

    #     kwds = ['text', 'label']

    #     for kwd in kwds:
    #         if kwd in attr:
    #             value = self.nodes[node][kwd]
    #             if (value is not None):
    #                 try:
    #                     self.nodes[node][kwd] = self.remove_suffixes(value)
    #                 except:
    #                     pass
    #         else:
    #             self.nodes[node][kwd] = self.default_label_part


    ''' HR 09/06/22 To avoid problem with lattice nodes not being deleted '''
    ''' Overridden to add label to node upon creation '''
    def add_node(self, node, populate = True, **attr):
        super().add_node(node, **attr)

        if not populate:
            return

        # kwds = ['text', 'label']
        kwds = []

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
            # print('Stripped back text, first stage: ', line_corr)
            ''' Next, deal with remaining rightmost field
            #     Fine for all case studies so far, but might not be universal solution; would need to deal with text in field, if present
            #     Note: Currently yields wrong name if text present in rightmost field '''
            # line_corr = line_corr.rstrip("'").strip().rstrip("'").strip().rstrip(",")
            ''' HR 22/11/21
                Rewritten to allow for text in third field
                Still assumes no commas in third field, but improvement on previous '''
            line_corr = ','.join(line_corr.split(",")[:-1])
            # print('Stripped back text, second stage: ', line_corr)

            chunks = line_corr.split(",")
            # print('Chunks by comma: ', chunks)

            l = len(chunks)
            # print('Length: ', l)

            if l == 2:
                ''' If only two chunks, first chunk must be name, even if two empty chunks '''
                name = chunks[0]
                # print("Length = 2, name is first chunk: ", name)

            else:
                if (l % 2) != 0:
                    ''' If l > 2 and odd, last chunk must be empty => name is all chunks except last '''
                    name = ''.join(chunks[:-1])
                    # print("Length = ", l, " and odd, name is all chunks except last: ", name)
                else:
                    ''' Last remaining case is that l > 2 and even, for which two possible outcomes '''
                    lh = int(l/2)
                    # print('Half length = ', lh)
                    ''' Chop text into two halves '''
                    half1 = ','.join(chunks[0:lh]).strip()
                    half2 = ','.join(chunks[lh:]).strip()
                    # print('Half 1: ', half1)
                    # print('Half 2: ', half2)
                    if half1 == half2:
                        ''' Outcome 1: Both halves the same, i.e. name repeated in two fields '''
                        name = half1
                        # print("Length > 2 and even and halves match, name is first half: ", name)
                    else:
                        ''' Outcome 2: Second field empty => name is all chunks except last '''
                        name = ','.join(chunks[:-1])
                        # print("Length > 2 and even and halves do NOT match, name is all chunks except last: ", name)

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


    ''' HR 25/02/22 New version to remove unnecessary head node if only one "free shape" at root;
                    and to grab all shapes, including sub-assemblies '''
    def load_step(self, filename, get_subshapes = False, *args, **kwargs):
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
            print('Returning...')
            return

        self.step_filename = filename
        print('Filename (full path): ', filename)

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
            shape = shape_tool.GetShape(lab)

            ''' Create location by applying all locations to that level in sequence
                as they are applied in sequence '''
            loc = TopLoc_Location()
            for l in locs:
                #print("    take loc       :", l)
                loc = loc.Multiplied(l)

            ''' Calculate correct location recursively '''
            shape_loc = BRepBuilderAPI_Transform(shape, loc.Transformation()).Shape()

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
                # n = c.Name(c.Red(), c.Green(), c.Blue())
                # print('    instance color Name & RGB: ', c, n, c.Red(), c.Green(), c.Blue())

            if not colorSet:
                if (color_tool.GetColor(lab, 0, c) or
                        color_tool.GetColor(lab, 1, c) or
                        color_tool.GetColor(lab, 2, c)):
                    color_tool.SetInstanceColor(shape, 0, c)
                    color_tool.SetInstanceColor(shape, 1, c)
                    color_tool.SetInstanceColor(shape, 2, c)
                    # n = c.Name(c.Red(), c.Green(), c.Blue())
                    # print('    shape color Name & RGB: ', c, n, c.Red(), c.Green(), c.Blue())


            # ''' Shape-specific (i.e. non-assembly) properties '''
            # # attr_dict = {'screen_name': self.get_screen_name(name, shape),
            # #              'shape_raw': [shape, loc],
            # #              'shape_loc': [BRepBuilderAPI_Transform(shape, loc.Transformation()).Shape(), c]}
            # attr_dict = {'shape_loc': [BRepBuilderAPI_Transform(shape, loc.Transformation()).Shape(), c]}
            # nx.set_node_attributes(self, {node: attr_dict})


            ''' Properties common to assemblies and shapes
                Assembly- and shape-specific properties added in if/else below '''
            node = self.new_node_id
            if name in self.product_names:
                is_product = True
            else:
                is_product = False
            attr_dict = {'occ_label': lab,
                         'occ_name': name,
                         'is_subshape': False,
                         'is_product': is_product,
                         'screen_name': self.get_screen_name(name, shape),
                         'shape_raw': [shape, loc],
                         'shape_loc': [shape_loc, c]}
            self.add_node(node, **attr_dict)
            self.add_edge(self.parent, node)


            if shape_tool.IsAssembly(lab):

                ''' Get components -> l_c '''
                l_c = TDF_LabelSequence()
                shape_tool.GetComponents(lab, l_c)
                #print("Nb components  :", l_c.Length())
                #print()

                # ''' Assembly-specific (i.e. non-shape) properties '''
                # attr_dict = {'screen_name': self.get_screen_name(name, None),
                #              'shape_raw': [None, None],
                #              'shape_loc': [None, None]}
                # nx.set_node_attributes(self, {node: attr_dict})

                # shape = shape_tool.GetShape(lab)

                # ''' Assembly-specific (i.e. non-shape) properties '''
                # # attr_dict = {'screen_name': self.get_screen_name(name, shape),
                # #              'shape_raw': [shape, loc],
                # #              'shape_loc': [None, None]}
                # attr_dict = {'shape_loc': [None, None]}
                # nx.set_node_attributes(self, {node: attr_dict})

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
                # shape = shape_tool.GetShape(lab)
                #print("    all ass locs   :", locs)

                # ''' Create location by applying all locations to that level in sequence
                #     as they are applied in sequence '''
                # loc = TopLoc_Location()
                # for l in locs:
                #     #print("    take loc       :", l)
                #     loc = loc.Multiplied(l)

                # ''' HR June 21 some code duplication for colour assignment
                #     but didn't work when reduced to single block '''
                # c = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)  # default color
                # colorSet = False
                # if (color_tool.GetInstanceColor(shape, 0, c) or
                #         color_tool.GetInstanceColor(shape, 1, c) or
                #         color_tool.GetInstanceColor(shape, 2, c)):
                #     color_tool.SetInstanceColor(shape, 0, c)
                #     color_tool.SetInstanceColor(shape, 1, c)
                #     color_tool.SetInstanceColor(shape, 2, c)
                #     colorSet = True
                #     # n = c.Name(c.Red(), c.Green(), c.Blue())
                #     # print('    instance color Name & RGB: ', c, n, c.Red(), c.Green(), c.Blue())

                # if not colorSet:
                #     if (color_tool.GetColor(lab, 0, c) or
                #             color_tool.GetColor(lab, 1, c) or
                #             color_tool.GetColor(lab, 2, c)):
                #         color_tool.SetInstanceColor(shape, 0, c)
                #         color_tool.SetInstanceColor(shape, 1, c)
                #         color_tool.SetInstanceColor(shape, 2, c)
                #         # n = c.Name(c.Red(), c.Green(), c.Blue())
                #         # print('    shape color Name & RGB: ', c, n, c.Red(), c.Green(), c.Blue())


                # ''' Shape-specific (i.e. non-assembly) properties '''
                # # attr_dict = {'screen_name': self.get_screen_name(name, shape),
                # #              'shape_raw': [shape, loc],
                # #              'shape_loc': [BRepBuilderAPI_Transform(shape, loc.Transformation()).Shape(), c]}
                # attr_dict = {'shape_loc': [BRepBuilderAPI_Transform(shape, loc.Transformation()).Shape(), c]}
                # nx.set_node_attributes(self, {node: attr_dict})

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

                    ''' Add node + attributes + edge '''
                    node = self.new_node_id
                    attr_dict = {'occ_label': lab_subs,
                                  'occ_name': name_sub,
                                  'shape_raw': [shape_sub, loc],
                                  'shape_loc': [BRepBuilderAPI_Transform(shape_sub, loc.Transformation()).Shape(), c],
                                  'screen_name': self.get_screen_name(name_sub, shape_sub),
                                  'is_subshape': True,
                                  'is_product': False}
                    self.add_node(node, **attr_dict)
                    self.add_edge(self.parent, node)


        ''' Create graph structure for shape data '''
        head = self.new_node_id
        self.head = head
        attr_dict = {'occ_label': None,
                     'occ_name': None,
                     'screen_name': self.HEAD_NAME_DEFAULT,
                     'shape_raw': [None, None],
                     'shape_loc': [None, None],
                     'is_subshape': False,
                     'is_product': False}
        self.add_node(head, **attr_dict)


        # def _get_shapes():
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

        # _get_shapes()
        # # return output_shapes


        ''' Correct colours in "args" of colour objects '''
        self.update_colour_objects()
        ''' ------------------------------------------- '''

        ''' HR 14/06/22 Remove all redundant nodes if specified '''
        if 'remove_redundants' in kwargs:
            remove = kwargs['remove_redundants']
        else:
            remove = self.enforce_binary
        if remove:
            self.remove_redundants()

        # self.remove_redundants()
        self.file_loaded = True


    ''' HR 21/04/22 Workaround to update "args" of Quantity_Color SWIG objects
                    otherwise colours not copied correctly if deep-copied
                    e.g. when assembly is duplicated or saved '''
    def update_colour_objects(self, nodes = None):
        if not nodes:
            nodes = self.nodes
        for node in nodes:
            colour_obj = self.nodes[node]['shape_loc'][1]
            if colour_obj:
                r = colour_obj.Red()
                g = colour_obj.Green()
                b = colour_obj.Blue()
                _end = colour_obj.args[-1]
                colour_obj.args = (r,g,b,_end)


    ''' HR 21/04/22 Refactored to render all leaves contained by node,
                    rather than node itself as this can cause colouring issues;
                    issue arose because:
                        (1) Shapes now present in sub-assemblies, but parts may vary in colour
                        (2) May be another colouring issue present; easier to just refactor '''
    def get_image_data(self, node, default_colour = False):

        def render(nodes):

            try:
                self.renderer.EraseAll()

                for node in nodes:

                    if not default_colour:
                        ''' Render in correct colour... '''
                        shape, c = self.nodes[node]['shape_loc']
                        # self.renderer.DisplayShape(shape, color = Quantity_Color(c.Red(),
                        #                                                           c.Green(),
                        #                                                           c.Blue(),
                        #                                                           Quantity_TOC_RGB))
                        self.renderer.DisplayShape(shape, color = c)
                    else:
                        ''' ...or in default colour (for better reference images), i.e. orange '''
                        self.renderer.DisplayShape(shape)

                self.renderer.View.FitAll()
                self.renderer.View.ZFitAll()

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

        ''' Old version for compiling "_to_render", keeping for reference '''
        # ''' If shape exists in node dict, render node
        #     else (b/c node is assembly) get all non-sub-shapes and render all '''
        # _to_render = []
        # if 'shape_loc' in d:
        #     if d['shape_loc'][0]:
        #         _to_render.append(node)
        #     else:
        #         for el in nx.descendants(self, node):
        #             d_sub = self.nodes[el]
        #             ''' Add to render list if shape present and not sub-shape '''
        #             if 'shape_loc' in d_sub:
        #                 if d_sub['shape_loc'][0] and not d_sub['is_subshape']:
        #                     _to_render.append(el)

        ''' Get all items to be rendered '''
        if self.out_degree(node) == 0:
            '''
            CASE 1: ITEM IS LEAF NODE => RENDER PART
            '''
            print('Item to be rendered is leaf: rendering item only')
            _to_render.append(node)

        else:
            '''
            CASE 2: ITEM IS SUB-ASSEMBLY => DO NOT RENDER ITS SHAPE,
            BUT GRAB AND RENDER EACH LEAF NODE IT CONTAINS
            '''
            print('Item is sub-assembly: rendering all leaf nodes within')
            for el in nx.descendants(self, node):
                if self.out_degree(el) == 0:
                    print(' Found leaf', el)
                    ''' Get node dict '''
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
            ''' Add to node dict for fast retrieval later '''
            d['image_data'] = img_data
        else:
            img_data = None

        return img_data


    ''' HR 13/06/22 To split off into separate method for use elsewhere '''
    def get_redundants(self, nodes = None):

        ''' Operate on whole assembly by default '''
        if not nodes:
            nodes = self.nodes

        redundants = []
        for node in nodes:
            if self.out_degree(node) == 1:
                redundants.append(node)

        print('Found redundant nodes: ', redundants)
        print(' in assembly', self.assembly_id)
        return redundants


    # ''' Remove all single-child sub-assemblies as not compatible with lattice '''
    # def remove_redundants(self, nodes = None):

    #     ''' Operate on whole assembly by default '''
    #     if not nodes:
    #         nodes = self.nodes

    #     ''' Get list of redundant nodes and link past them... '''
    #     to_remove = []
    #     for node in nodes:
    #         # if self.out_degree(node) == 1 and self.nodes[node]['screen_name'] != self.head_name:
    #         if self.out_degree(node) == 1 and self.nodes[node]['screen_name'] != self.nodes[self.head]['screen_name']:
    #             parent = self.get_parent(node)
    #             child = self.get_child(node)
    #             ''' Don't remove if at head of tree (i.e. if in_degree == 0)...
    #                 ...as Networkx would create new "None" node as parent '''
    #             if self.in_degree(node) != 0:
    #                 self.add_edge(parent, child)
    #             to_remove.append(node)

    #     ''' ...then remove in separate loop to avoid list changing size during previous loop '''
    #     for node in to_remove:
    #         self.remove_node(node)
    #         print('Removing node ', node)
    #     print('  Total redundant nodes removed: ', len(to_remove))

    #     # print('Removed redundants')
    #     return to_remove


    ''' HR 13/06/22 Refactored to integrate better with corresponding lattice method
                    Objective is to allow calling of "remove_redundants" from assembly manager
                    in consistent way without duplication of operations '''
    ''' --- '''
    ''' Remove all single-child sub-assemblies as not compatible with lattice representation '''
    def remove_redundants(self, nodes = None, remove_head = True):

        ''' Operate on whole assembly by default '''
        if not nodes:
            nodes = self.nodes

        ''' Get list of redundant nodes and link past them... '''
        redundant_nodes = self.get_redundants()
        redundant_edges = []
        new_edges = []

        edges_before = set(self.edges)

        # ''' To remove head but retain its single child, if possible '''
        # if remove_head:
        #     root = self.get_root()
        #     if root in redundant_nodes:
        #         root_child = self.get_child(root)
        #         redundant_nodes.remove(root_child)
        #         print('Removed root child from nodes to delete')

        ''' Link past each node, if parent present (not the case for the root node) '''
        for node in redundant_nodes:
            parent = self.get_parent(node)

            if parent:
                child = self.get_child(node)
                new_edge = (parent,child)
                self.add_edge(*new_edge)
                new_edges.append(new_edge)

        ''' ...then remove in separate loop to avoid list changing size during previous loop '''
        for node in redundant_nodes:
            ins = list(self.in_edges(node))
            outs = list(self.out_edges(node))
            redundant_edges.extend(ins + outs)

            self.remove_node(node)
            print('Removing node ', node)

        print('  Total redundant nodes removed: ', len(redundant_nodes))

        edges_after = set(self.edges)

        edges_removed = edges_before - edges_after
        edges_added = edges_after - edges_before

        # print('Removed redundants')
        # return redundant_nodes, redundant_edges, new_edges
        return redundant_nodes, edges_removed, edges_added


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


    ''' HR 09/06/22 New version to catch exception if node already removed '''
    def get_parent(self, node):
        ''' Get parent of node; return None if parent not present '''
        try:
            parent = [el for el in self.predecessors(node)][-1]
            # print('Found parent of ', node,': ', parent)
            return parent
        except:
            # print('Could not find parent of node ', node, '; returning None')
            return None


    # def get_child(self, node):
    #     ''' Get (single) child of node; return None if parent not present
    #         Best used only when removing redundant (i.e. single-child) subassemblies '''
    #     child = [el for el in self.successors(node)]
    #     if child:
    #         return child[-1]
    #     else:
    #         return None


    ''' HR 09/06/22 New version to catch exception if no child present '''
    def get_child(self, node):
        ''' Get (single) child of node; return None if parent not present
            Best used only when removing redundant (i.e. single-child) subassemblies '''
        try:
            child = [el for el in self.successors(node)][-1]
            print('Found single/last child of node ', node, ': ', child)
            return child
        except:
            print('Could not find single/last child of node ', node, '; returning None')
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
    def get_leaves_in(self, nodes = None, leaves = None):

        ''' If no nodes passed, default to all nodes in assembly '''
        if not nodes:
            nodes = self.nodes

        ''' Convert to list if only one item '''
        if type(nodes) == int:
            nodes = [nodes]

        ''' Get all leaves in specified nodes by set intersection '''
        if not leaves:
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
    All combinatorial ranking/unranking methods here '''


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


    '''
    RANKING OF COMBINATION
    --
    Find position (rank) of combination in ordered list of all combinations
    Items list argument consists of zero-based indices
    '''
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

    '''
    SPLIT AND RENDER METHODS HERE
    '''

    ''' Image renderer (copied from StrEmbed) '''
    def quick_render(self, shape, colour = None, img_file = None):

        self.renderer.EraseAll()

        if colour:
            ''' Render in specified colour... '''
            c = colour
            # self.renderer.DisplayShape(shape, color = Quantity_Color(c.Red(),
            #                                                           c.Green(),
            #                                                           c.Blue(),
            #                                                           Quantity_TOC_RGB))
            self.renderer.DisplayShape(shape, color = c)
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
    def split_and_render(self, path = None, products_only = False, subshapes = False, parts_only = False):

        # for node in self.nodes:
        #     print(node, self.nodes[node]['screen_name'])

        ''' Collect nodes to be checked, remove unwanted nodes (non-products, subshapes) '''
        if parts_only:
            nodes = self.leaves
        else:
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
                print(img_file)
                print('Part image file already exists; not saving')
            else:
                print('Saving image for part: ', v)
                self.quick_render(k, img_file = img_file)
