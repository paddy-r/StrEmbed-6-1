# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 12:29:57 2021

@author: prehr
"""
import step_parse_6_1
am = step_parse_6_1.AssemblyManager()
_id, _ass = am.new_assembly()
_ass.load_step('5 parts_{3,1},1.STEP')
am.AddToLattice(_id)

for node in _ass:
    print(node, _ass.nodes[node]['screen_name'])

am.assemble_in_lattice(_id, [8,9])

for node in am._lattice.nodes:
    try:
        active_node = am._lattice.nodes[node][_id]
        print('Node, name: ', node, am._mgr[_id].nodes[active_node]['screen_name'])
    except:
        print('Node ', node, 'not active or no name')