# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 14:58:53 2022

@author: prehr
"""

''' HR 27/07/22 To test bounding box calculations as possible error
                Start with setting "gap" to zero in "get_dimensions" method in SP '''

''' HR 31/03/23
    Adding to repo UNTESTED in case any useful scrap later
'''


import step_parse as sp
from scenario_tester import bom_path
import os

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop_VolumeProperties, brepgprop_SurfaceProperties, brepgprop_LinearProperties

from OCC.Extend.TopologyUtils import TopologyExplorer


def get_mass_props(shape):
    # """Compute the inertia properties of a shape"""
    # # Create and display cube
    # print("Creating a cubic box shape (50*50*50)")
    # cube_shape = BRepPrimAPI_MakeBox(50.0, 50.0, 50.0).Shape()
    # Compute inertia properties
    props = GProp_GProps()
    # brepgprop_VolumeProperties(cube_shape, props)
    brepgprop_VolumeProperties(shape, props)
    # Get inertia properties
    mass = props.Mass()
    cog = props.CentreOfMass()
    matrix_of_inertia = props.MatrixOfInertia()
    # Display inertia properties
    # print("Volume = %s" % volume)
    print("Cube mass = %s" % mass)
    cog_x, cog_y, cog_z = cog.Coord()
    print("Center of mass: x = %f;y = %f;z = %f;" % (cog_x, cog_y, cog_z))
    print("Matrix of inertia", matrix_of_inertia)

    cog = cog_x, cog_y, cog_z
    return cog, matrix_of_inertia, mass


def get_all_dimensions(manager, _id, tol = 0):
    ass = manager._mgr[_id]
    bb_dict = {}
    for node in ass.leaves:
        print('Getting dimensions of node', node, 'in assembly', _id)
        bb_dict[node] = {'name': ass.nodes[node]['screen_name']}
        shape = ass.nodes[node]['shape_loc'][0]
        dims = sp.get_dimensions(shape, get_centre = True, tol = tol)
        bb_dict[node]['dims'] = dims
        xmin, ymin, zmin, xmax, ymax, zmax = dims
        bb_dict[node]['volume'] = (xmax-xmin)*(ymax-ymin)*(zmax-zmin)
    return bb_dict


if __name__ == "__main__":

    ''' HR 04/04/23
        Commented out most of what's below
        Just need to test mass/volume calculation and that it works in pipeline
    '''
    am = sp.AssemblyManager()

    file1 = bom_path("T1")
    file2 = bom_path("T2")
    # file3 = bom_path("P3")

    id1, ass1 = am.new_assembly()
    ass1.load_step(file1)

    id2,ass2 = am.new_assembly()
    ass2.load_step(file2)

    d1 = get_all_dimensions(am, 1)
    print(d1)
    d2 = get_all_dimensions(am, 2)
    print(d2)

    # id3,ass3 = am.new_assembly()
    # ass3.load_step(file3)

    # com1, mass1 = am.get_mass_data(1, 6)
    # com2, mass2 = am.get_mass_data(1, 7)
    # com3, mass3 = am.get_mass_data(1, ass1.get_root())
    #
    # ass = ass1
    # com_dict = {}
    # for node in ass.nodes:
    #     shape = ass.nodes[node]['shape_loc'][0]
    #     name = ass.nodes[node]['screen_name']
    #     if name:
    #         print(node, name)
    #         com_dict[node] = sp.get_mass_properties(shape)[0]
    #
    # ''' Testing for distance score based on centre of mass, with and without scaling '''
    # _scale = mass3**(1/3)
    #
    # res = sp.get_distance_score(com1, com2)
    # print(res)
    #
    # res = sp.get_distance_score(com1, com2, scale = _scale)
    # print(res)
    #
    # res = sp.get_distance_score(com1, com2, exponential = True)
    # print(res)
    #
    # res = sp.get_distance_score(com1, com2, exponential = True, scale = _scale)
    # print(res)
    #
    # ''' Testing for score based on volume, with sum vs. max value as divisor '''
    # ref_node = 8
    # compare_nodes = list(ass1.nodes)
    # compare_nodes.remove(ref_node)
    #
    # for node in compare_nodes:
    #     print('\n')
    #     shape1 = ass1.nodes[ref_node]['shape_loc'][0]
    #     data1 = sp.get_mass_properties(shape1)
    #     shape2 = ass1.nodes[node]['shape_loc'][0]
    #     data2 = sp.get_mass_properties(shape2)
    #
    #     print('Ref node:', ref_node, ass1.nodes[ref_node]['screen_name'])
    #     print('Compare node:', node, ass1.nodes[node]['screen_name'])
    #
    #     res = sp.get_mass_score(data1[1],data2[1])
    #     print(res)
    #     res = sp.get_mass_score(data1[1],data2[1], do_max = False)
    #     print(res)