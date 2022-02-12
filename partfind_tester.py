# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 15:13:51 2021

@author: prehr
"""

''' HR 07/12/21 To get newest PartFind running with minimal example:
        Two STEP files -> similarity score '''

import pandas as pd
import os
import cv2
import torch
from torch_geometric.data import DataLoader

''' -------------------------------------------------------------- '''
''' Import all necessary PartFind stuff
    Sets/resets cwd and grabs code from scripts '''

partfind_folder = "C:\\Users\\prehr\\OneDrive - University of Leeds\\__WORK SYNCED\\_Work\\_DCS project\\__ALL CODE\\_Repos\\partfind"
# model_folder = "C:\\Users\\prehr\\OneDrive - University of Leeds\\__WORK SYNCED\\_Work\\_DCS project\\__ALL CODE\\_Repos\\partfind\\Model"

cwd_old = os.getcwd()

os.chdir(partfind_folder)
from CADDataset import CADDataset
from Model.model import GCNTriplet
from step2graph import StepToGraph

''' Restore previous cwd '''
os.chdir(cwd_old)
''' -------------------------------------------------------------- '''



seed = 0
torch.manual_seed(seed)
if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")



''' Set up model and data loader '''
convtype="GraphConv"
model, loader = load_model(convtype = convtype)

''' Get graphs from STEP files '''
file1 = 'MODIFIED TORCH BODY - LOWER.STEP.STEP.STEP.STEP.STEP'
step1 = StepToGraph(tmp_file)
step1.compute_faces_surface()

file2 = 'MODIFIED TORCH BODY - LOWER.STEP.STEP.STEP.STEP.STEP'
step2 = StepToGraph(tmp_file)
step2.compute_faces_surface()



# ''' Calculate scores '''
# out0, out1, out2, correct, score_p, score_n, correct_s = model(**kwargs)



''' Everything in class form #'''
class PartFinder():
    def __init__(self):
        pass
    
    def g_from_step(self, file):
        pass