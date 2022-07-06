# HR June 2019 onwards
# Version 5 to follow HHC's StrEmbed-4 in Perl
# User interface for lattice-based assembly configurations

### ---
# HR 17/10/19
# Version 5.1 to draw main window as panels within flexgridsizer
# Avoids confusing setup for staticbox + staticboxsizer
### ---

### ---
# HR 12/12/2019 onwards
# Version 5.2
### ---

### BUGS LOG
# 1 // 7/2/20
# Images in selector view does not update when resized until next resize
# e.g. when maximised, images remain small
# FIXED Feb 2020 with CallAfter
# ---
# 2 // 7/2/20
# Image rescaling (via ScaleImage method) may need correction
# Sometimes appears that images overlap border of toggle buttons partly
# ---
# 3 // 6/3/20
# Assembly operation methods (flatten, assemble, etc.) need compressing into fewer methods
# as currently a lot of repeated code

### ---
# HR 23/03/2020 onwards
# Version 5.3
### ---

"""
HR 11/08/20 onwards
Version 5.5
"""

''' HR 02/12/20
Version 5.6 '''

''' HR 07/07/21
Version 5.7
Abandoned '''

''' HR 05/10/21
Version 6.1
Copy of 5.7, to draw line under version 5
Version 6 to include major upgrade of BoM reconciliation functionality
and bug fixes:
    1. GUI changes being executed multiple times
    2. Node positioning error after change in graph structure '''



# WX stuff
import wx
# WX customtreectrl for parts list
import wx.lib.agw.customtreectrl as ctc
import wx.ribbon as RB

# # Allows inspection of app elements via Ctrl + Alt + I
# Use InspectableApp() in MainLoop()
# import wx.lib.mixins.inspection as wit

# For scrolled panel
import wx.lib.scrolledpanel as scr

# matplotlib stuff
import matplotlib as mpl
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar

# # Ordered dictionary
# from collections import OrderedDict as odict

# Regular expressions
import re

# OS operations for exception-free file checking
import os

# import shutil

# Import networkx for plotting lattice
import networkx as nx

# Gets rid of blurring throughout application by getting DPI info
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
except:
    pass

# For STEP import
# from step_parse_6_1 import StepParse, AssemblyManager, ShapeRenderer
from step_parse_6_1 import StepParse, AssemblyManager

# import matplotlib.pyplot as plt
import numpy as np
# from scipy.special import comb

import images

import time

# For 3D CAD viewer based on python-occ
from OCC.Display import OCCViewer
from OCC.Display import wxDisplay
from OCC.Core.Quantity import (Quantity_Color, Quantity_NOC_WHITE, Quantity_TOC_RGB)
# from OCC.Core.AIS import AIS_Shaded, AIS_WireFrame



''' Get bitmap from "images" script, which must itself be created
    via "embed_images" '''
def CreateBitmap(imgName, mask = wx.WHITE, size = None):
    if not size:
        size = (100,100)

    _bmp = getattr(images, imgName).GetBitmap()
    _im = _bmp.ConvertToImage()

    width, height = size
    _im = _im.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    _bmp = wx.Bitmap(_im)

    if mask:
        _mask = wx.Mask(_bmp, mask)
        _bmp.SetMask(_mask)

    return _bmp



class MyTree(ctc.CustomTreeCtrl):

    def __init__(self, parent, style):
        super().__init__(parent = parent, agwStyle = style)
        self.parent = parent
        self.reverse_sort = False
        self.alphabetical = True

    ''' Overridden method to allow sorting based on data other than text
        Can be sorted alphabetically or numerically, and in reverse
        ---
        This method is called by sorting methods
        ---
        NOTE the functionality necessary for this was added to the wxWidgets / Phoenix Github repo
        in 2018 in response to issue #774 here: https://github.com/wxWidgets/Phoenix/issues/774 '''
    def OnCompareItems(self, item1, item2):

        if self.alphabetical:
            t1 = self.GetItemText(item1)
            t2 = self.GetItemText(item2)
        else:
            t1 = self.GetPyData(item1)['sort_id']
            t2 = self.GetPyData(item2)['sort_id']

        if self.reverse_sort:
            reverse = -1
        else:
            reverse = 1

        if t1 < t2:
            return -1*reverse
        if t1 == t2:
            return 0
        return reverse



    def GetDescendants(self, item):

        '''
        Get all children of CTC item recursively
        Named "GetDescendants" as recursive children in Networkx are "descendants"
        ---
        MUST create shallow copy of children here to avoid strange behaviour
        According to ctc docs, "It is advised not to change this list
        i.e. returned list] and to make a copy before calling
        other tree methods as they could change the contents of the list."
        See: https://wxpython.org/Phoenix/docs/html/wx.lib.agw.customtreectrl.GenericTreeItem.html
        '''
        descendants = item.GetChildren().copy()
        # They mess you up, your mum and dad
        parents = descendants
        while parents:
            # They may not mean to, but they do
            children = []
            for parent in parents:
                # They fill you with the faults they had
                children = parent.GetChildren().copy()
                descendants.extend(children)
                # And add some extra, just for you
                parents = children
        return descendants



    def SortAllChildren(self, item):

        ''' Get all non-leaf nodes of parent CTC object (always should be MainWindow) '''
        nodes = self.GetDescendants(item)
        nodes = [el for el in nodes if el.HasChildren()]
        for node in nodes:
            count = self.GetChildrenCount(node, recursively = False)
            if count > 1:
                self.SortChildren(node)



''' HR 26/05/21
    New class with overridden constructor to reduce code here
    Only differences are:
        (1) Don't bind EVT_LEFT_UP as that is bound later, and
        (2) Apply style to panel
    Some code duplication from Pythonocc here:
    https://github.com/tpaviot/pythonocc-core '''
class MyBaseViewer(wxDisplay.wxBaseViewer):
    def __init__(self, parent = None):
        wx.Panel.__init__(self, parent, style = wx.BORDER_SIMPLE)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnLostFocus)
        self.Bind(wx.EVT_MAXIMIZE, self.OnMaximize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.OnMiddleDown)
        # self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_MIDDLE_UP, self.OnMiddleUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelScroll)

        self._display = None
        self._inited = False



''' HR 26/05/21
    New class with overridden constructor etc. to reduce code here
    Some code duplication from Pythonocc here:
    https://github.com/tpaviot/pythonocc-core '''
class MyViewer3d(wxDisplay.wxViewer3d):
    def __init__(self, *kwargs):
        MyBaseViewer.__init__(self, *kwargs)

        self._drawbox = False
        self._zoom_area = False
        self._select_area = False
        self._inited = False
        self._leftisdown = False
        self._middleisdown = False
        self._rightisdown = False
        self._selection = None
        self._scrollwheel = False
        self._key_map = {}
        self.dragStartPos = None

    def InitDriver(self):
        ''' HR 26/12/20 modified to pass window handle to "Create" rather than "__init__""
            If handle not passed, renderer is off-screen (see OCCViewer) '''
        # self._display = OCCViewer.Viewer3d(self.GetWinId())
        # self._display.Create()
        self._display = OCCViewer.Viewer3d()
        self._display.Create(self.GetWinId())
        self._display.SetModeShaded()
        self._inited = True

        # dict mapping keys to functions
        self._SetupKeyMap()

    def _SetupKeyMap(self):
        def set_shade_mode():
            self._display.DisableAntiAliasing()
            self._display.SetModeShaded()

        self._key_map = {ord('W'): self._display.SetModeWireFrame,
                         ord('S'): set_shade_mode,
                         ord('A'): self._display.EnableAntiAliasing,
                         ord('B'): self._display.DisableAntiAliasing,
                         ord('H'): self._display.SetModeHLR,
                         ord('G'): self._display.SetSelectionModeVertex,
                         # 306: lambda: print('Shift pressed')
                        }

    def OnKeyDown(self, evt):
        code = evt.GetKeyCode()
        try:
            self._key_map[code]()
            # print('Key pressed: %i' % code)
        except KeyError:
            # print('Unrecognized key pressed %i' % code)
            pass



''' Class to veto unsplit when sash is double-clicked '''
class MySplitter(wx.SplitterWindow):
    def __init__(self, parent):

        super().__init__(parent = parent)
        self.Bind(wx.EVT_SPLITTER_DCLICK, self.OnSashDoubleClick)

    def OnSashDoubleClick(self, event):
        event.Veto()



class NotebookPanel(wx.Panel):
    def __init__(self, parent, _id, border = 0, panel_style = None, name = None):

        super().__init__(parent = parent)

        self.name = name
        self._id = _id

        if panel_style:
            self.panel_style = panel_style
        else:
            self.panel_style = wx.BORDER_SIMPLE



        ''' OVERALL SIZER AND FIRST SPLITTER SETUP '''
        _splitter = MySplitter(self)

        self.part_panel = wx.Panel(_splitter, style = self.panel_style)
        self._view_splitter = MySplitter(_splitter)

        _splitter.SplitVertically(self.part_panel, self._view_splitter)
        _splitter.SetSashGravity(0.5)

        self_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self_sizer.Add(_splitter, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(self_sizer)

        _splitter_sizer = wx.BoxSizer(wx.HORIZONTAL)
        _splitter_sizer.Add(self.part_panel, wx.ALL|wx.EXPAND)
        _splitter_sizer.Add(self._view_splitter, wx.ALL|wx.EXPAND)
        _splitter.SetSizer(_splitter_sizer)



        ''' PARTS VIEW SETUP '''
        self.treeStyle = (ctc.TR_MULTIPLE | ctc.TR_EDIT_LABELS | ctc.TR_HAS_BUTTONS)
        self.partTree_ctc = MyTree(self.part_panel, style = self.treeStyle)

        part_sizer = wx.BoxSizer(wx.VERTICAL)
        part_sizer.Add(self.partTree_ctc, 1, wx.ALL|wx.EXPAND)
        self.part_panel.SetSizer(part_sizer)



        ''' GEOMETRY VIEWS SETUP '''
        # self.occ_panel = wxViewer3d(self._view_splitter)
        self.occ_panel = MyViewer3d(self._view_splitter)
        self.occ_panel.InitDriver()
        self.occ_panel._display.View.SetBackgroundColor(Quantity_Color(Quantity_NOC_WHITE))

        self.slct_panel = scr.ScrolledPanel(self._view_splitter, style = self.panel_style)
        self.slct_panel.SetupScrolling()
        self.slct_panel.SetBackgroundColour('white')

        ''' Set up image-view grid, where "rows = 0" means the sizer updates dynamically
            according to the number of elements it holds '''
        self.image_cols = 4
        self.slct_sizer = wx.FlexGridSizer(cols = self.image_cols,
                                           rows = 0,
                                           hgap = 5,
                                           vgap = 5)

        self.slct_panel.SetSizer(self.slct_sizer)

        self._view_splitter.SplitHorizontally(self.slct_panel, self.occ_panel)
        self._view_splitter.SetSashGravity(0.5)

        # _view_splitter_sizer = wx.BoxSizer(wx.VERTICAL)
        # _view_splitter_sizer.Add(_view_splitter, 1, wx.ALL|wx.EXPAND)
        # self.view_panel.SetSizer(_view_splitter_sizer)



        ''' Discard pile and alternative assembly '''
        # self.discarded = StepParse()
        self.alt = StepParse(1000)

        self.edge_alt_dict = {}
        self.node_alt_dict = {}

        self.ctc_dict     = {}
        self.ctc_dict_inv = {}

        ''' Toggle buttons '''
        # self.button_dict     = odict()
        # self.button_dict_inv = odict()
        self.button_dict     = {}
        self.button_dict_inv = {}
        self.button_img_dict = {}

        self.file_open = False

        # self.occ_panel.Refresh()



''' HR 13/10/21
    Dialog box for node data entry '''
class DataEntryDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Node data entry", size= (400,180))
        self.panel = wx.Panel(self,wx.ID_ANY)

        self.lblfield = wx.StaticText(self.panel,
                                      label = "Field name:",
                                      pos = (20,20))
        self.field = wx.TextCtrl(self.panel,
                                 value = "",
                                 pos = (110,20),
                                 size = (250,-1))
        self.lblvalue = wx.StaticText(self.panel,
                                      label = "Value:",
                                      pos = (20,60))
        self.value = wx.TextCtrl(self.panel,
                                 value = "",
                                 pos = (110,60),
                                 size = (250,-1))
        self.okButton = wx.Button(self.panel,
                                  label = "OK",
                                  pos = (110,100))
        self.closeButton = wx.Button(self.panel,
                                     label = "Cancel",
                                     pos = (210,100))
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.closeButton.Bind(wx.EVT_BUTTON, self.OnQuit)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Show()

    def OnQuit(self, event):
        self.result_field = None
        self.Destroy()

    def OnOK(self, event):
        self.result_field = self.field.GetValue()
        self.result_value = self.value.GetValue()
        self.Destroy()



class DecisionDialog(wx.MessageDialog):
    def __init__(self, parent = None, message = 'Decision dialog', caption = 'OK to proceed?', style = wx.OK | wx.CANCEL):
        super().__init__(parent = parent, message = message, caption = caption, style = style)



class ReconciliationSpecDialog(wx.Dialog):
    def __init__(self, parent, ids, blocking_modes, matching_properties, *args, **kwargs):
        super().__init__(parent = parent, title = 'Reconciliation specification')

        self.ids = ids
        self.blocking_modes = blocking_modes
        self.matching_properties = matching_properties

        ''' Main sizer '''
        vbox = wx.BoxSizer(wx.VERTICAL)



        ''' 1. Set up assembly selection section '''
        pnl1 = wx.Panel(self)

        sb = wx.StaticBox(pnl1, label = 'Choose assembly for comparison')
        sbs = wx.StaticBoxSizer(sb, orient = wx.VERTICAL)
        ''' Populate with all available assemblies '''
        self.assembly_dict = {}
        for i, id_present in enumerate(self.ids):
            label = 'Assembly ' + str(id_present)
            if i == 0:
                style = wx.RB_GROUP
            else:
                style = 0
            radio_button = wx.RadioButton(pnl1, label = label, style = style)
            sbs.Add(radio_button)
            self.assembly_dict[id_present] = radio_button

        pnl1.SetSizer(sbs)


        ''' 2. Set up blocking mode section '''
        pnl2 = wx.Panel(self)

        sb2 = wx.StaticBox(pnl2, label = 'Choose blocking mode')
        sbs2 = wx.StaticBoxSizer(sb2, orient = wx.VERTICAL)
        ''' Populate with all available assemblies '''
        self.blocking_dict = {}
        for i, mode in enumerate(self.blocking_modes):
            label = mode
            if i == 0:
                style = wx.RB_GROUP
            else:
                style = 0
            radio_button = wx.RadioButton(pnl2, label = label, style = style)
            sbs2.Add(radio_button)
            self.blocking_dict[mode] = radio_button

        pnl2.SetSizer(sbs2)



        ''' 3. Set up matching properties section '''
        pnl3 = wx.Panel(self)

        sb3 = wx.StaticBox(pnl3, label = 'Choose assembly properties to consider')
        sbs3 = wx.StaticBoxSizer(sb3, orient = wx.VERTICAL)
        ''' Populate with all available assemblies '''
        self.property_dict = {}
        for i, _property in enumerate(self.matching_properties):
            label = _property
            if i == 0:
                style = wx.RB_GROUP
            else:
                style = 0
            check_box = wx.CheckBox(pnl3, -1, label)
            sbs3.Add(check_box)
            self.property_dict[_property] = check_box

        pnl3.SetSizer(sbs3)



        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK)
        cancelButton = wx.Button(self, wx.ID_CANCEL)
        hbox2.Add(okButton)
        hbox2.Add(cancelButton)



        vbox.Add(pnl1, proportion = 1, flag = wx.ALL|wx.EXPAND, border = 5)
        vbox.Add(pnl2, proportion = 1, flag = wx.ALL|wx.EXPAND, border = 5)
        vbox.Add(pnl3, proportion = 1, flag = wx.ALL|wx.EXPAND, border = 5)
        vbox.Add(hbox2, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10)

        self.SetSizer(vbox)
        self.Fit()



    def get_spec(self):
        print('Running "get_spec"')
        ''' Grab ID of assembly for comparison, blocking mode and weights '''
        # assembly_id = [(v,k.GetValue()) for k,v in self.assembly_dict.items()]
        # blocking_mode = [(v,k.GetValue()) for k,v in self.blocking_dict.items()]
        # weights = [(v,k.GetValue()) for k,v in self.property_dict.items()]
        
        assembly_id = [_id for _id in self.ids if self.assembly_dict[_id].GetValue()][0]
        blocking_mode = [mode for mode in self.blocking_modes if self.blocking_dict[mode].GetValue()][0]
        weights = [int(self.property_dict[_property].GetValue()) for _property in self.matching_properties]
        return assembly_id, blocking_mode, weights



class ReconciliationResultsDialog(wx.Dialog):
    def __init__(self, parent, id1, id2, matches_text, *args, **kwargs):
        super().__init__(parent = parent, title = 'Reconciliation report: click OK to add to lattice')

        ''' Main sizer '''
        vbox = wx.BoxSizer(wx.VERTICAL)



        ''' List of matches in text box, for user to review '''
        panel = wx.Panel(self)
        panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        textctrl = wx.TextCtrl(panel,
                                value = matches_text,
                                size = (500,200),
                                style = wx.TE_MULTILINE | wx.TE_READONLY | wx.EXPAND | wx.HSCROLL)
        panel_sizer.Add(textctrl)
        panel.SetSizer(panel_sizer)



        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK)
        cancelButton = wx.Button(self, wx.ID_CANCEL)
        hbox.Add(okButton)
        hbox.Add(cancelButton)



        vbox.Add(panel, proportion = 1, flag = wx.ALL|wx.EXPAND, border = 5)
        vbox.Add(hbox, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10)

        self.SetSizer(vbox)
        self.Fit()



class MainWindow(wx.Frame):
    def __init__(self):

        super().__init__(parent = None, title = "StrEmbed-6-1")

        ''' All other app-wide initialisation '''
        self.SetBackgroundColour('white')
        # self.SetIcon(wx.Icon(wx.ArtProvider.GetBitmap(wx.ART_PLUS)))
        # self.SetIcon(wx.Icon(images.sb_icon3_bmp.GetBitmap()))
        self.SetIcon(wx.Icon(CreateBitmap("sb_icon3_grey_bmp",
                                          size = (20,20),
                                          mask = 'white')))

        self.no_image_ass  = images.no_image_ass_png.GetBitmap()
        self.no_image_part = images.no_image_part_png.GetBitmap()
        self.no_image      = images.no_image_png.GetBitmap()

        # self.im_folder = 'Temp'
        # self.im_path = os.path.join(os.getcwd(), self.im_folder)
        # if not os.path.exists(self.im_path):
        #     os.mkdir(self.im_path)
        #     print('Created temporary image folder at ', self.im_path)

        # ''' Off-screen renderer for producing static images for toggle buttons '''
        # self.renderer = ShapeRenderer()

        self.tight = 0.9
        self._border = 1
        self._default_size = (30,30)
        self._button_size = (50,50)

        ''' HR 25/11/21 New flags to prevent multiple event execution '''
        self.VETO_PARTS = False
        self.VETO_SELECTOR = False

        self._highlight_colour = wx.RED
        self.LATTICE_PLOT_MODE_DEFAULT = True
        self.COMMON_SELECTOR_VIEW = True
        self.SELECT_ALL_CHILDREN = False

        self.ADD_TO_LATTICE_DEFAULT = True

        self.origin = (0,0)
        self.click_pos = None

        ''' Themes for assembly suggestions in "Assistant" '''
        self.themes = ['Create maintenance bill',
                       'Create manufacturing bill',
                       'Create transport bill']



        ID_NEW = self.NewControlId()
        ID_DELETE = self.NewControlId()
        ID_FILE_OPEN = self.NewControlId()
        ID_FILE_SAVE = self.NewControlId()
        ID_EXPORT_ASSEMBLY = self.NewControlId()

        ID_ASSEMBLE = self.NewControlId()
        ID_FLATTEN = self.NewControlId()
        ID_DISAGGREGATE = self.NewControlId()
        ID_AGGREGATE = self.NewControlId()
        ID_ADD_NODE = self.NewControlId()
        ID_REMOVE_NODE = self.NewControlId()
        ID_SORT_MODE = self.NewControlId()
        ID_SORT_REVERSE = self.NewControlId()

        ID_CALC_SIM = self.NewControlId()
        ID_ASS_MAP = self.NewControlId()
        ID_RECON = self.NewControlId()
        ID_SUGGEST = self.NewControlId()

        ID_SETTINGS = self.NewControlId()
        ID_ABOUT = self.NewControlId()

        ID_LINE_VIEW = self.NewControlId()
        ID_COMMON_SELECTOR_VIEW = self.NewControlId()

        self.ID_ASSISTANT_PAGE = self.NewControlId()



        ''' Main panel containing everything '''
        panel_top = wx.Panel(self)

        ''' Ribbon with tools '''
        self._ribbon = RB.RibbonBar(panel_top,
                                    style = RB.RIBBON_BAR_DEFAULT_STYLE | RB.RIBBON_BAR_SHOW_PANEL_EXT_BUTTONS)



        home = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Home")

        file_panel = RB.RibbonPanel(home, wx.ID_ANY, "File",
                                    style=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)
        toolbar = RB.RibbonToolBar(file_panel, wx.ID_ANY)

        toolbar.AddTool(ID_FILE_OPEN,
                        wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN,
                                                 wx.ART_OTHER,
                                                 wx.Size(self._default_size)),
                        help_string = "File open")
        toolbar.AddTool(ID_FILE_SAVE,
                        wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE,
                                                 wx.ART_OTHER,
                                                 wx.Size(self._default_size)),
                        help_string = "Save project to Excel")
        toolbar.AddTool(ID_EXPORT_ASSEMBLY,
                        wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS,
                                                 wx.ART_OTHER,
                                                 wx.Size(self._default_size)),
                        help_string = "Save active assembly")
        toolbar.AddSeparator()
        toolbar.AddHybridTool(ID_NEW,
                              wx.ArtProvider.GetBitmap(wx.ART_NEW,
                                                       wx.ART_OTHER,
                                                       wx.Size(self._default_size)),
                              help_string = "Create new empty assembly")
        toolbar.AddHybridTool(ID_DELETE,
                              wx.ArtProvider.GetBitmap(wx.ART_DELETE,
                                                       wx.ART_OTHER,
                                                       wx.Size(self._default_size)),
                              help_string = "Delete assembly")
        toolbar.SetRows(2, 3)

        ass_panel = RB.RibbonPanel(home, wx.ID_ANY, "Assembly")

        ass_ops = RB.RibbonButtonBar(ass_panel)
        ass_ops.AddButton(ID_ADD_NODE, "Add node",
                          CreateBitmap("add_node_png",
                                       size = self._button_size),
                          help_string ="Add node at selected position")
        ass_ops.AddButton(ID_REMOVE_NODE, "Remove node",
                          CreateBitmap("remove_node_png",
                                       size = self._button_size),
                          help_string = "Remove selected node")
        ass_ops.AddButton(ID_ASSEMBLE, "Assemble",
                          CreateBitmap("assemble_png",
                                       size = self._button_size),
                          help_string = "Assemble parts into sub-assembly")
        ass_ops.AddButton(ID_FLATTEN, "Flatten",
                          CreateBitmap("flatten_png",
                                       size = self._button_size),
                          help_string = "Remove sub-assemblies")
        ass_ops.AddButton(ID_DISAGGREGATE, "Disaggregate",
                          CreateBitmap("disaggregate_png",
                                       size = self._button_size),
                          help_string = "Create sub-assembly with two parts")
        ass_ops.AddButton(ID_AGGREGATE, "Aggregate",
                          CreateBitmap("aggregate_png",
                                       size = self._button_size),
                          help_string = "Remove all contained parts and create single part")

        sort_panel = RB.RibbonPanel(home, wx.ID_ANY, "Sort")

        sort_ops = RB.RibbonButtonBar(sort_panel)
        sort_ops.AddButton(ID_SORT_MODE, "Sort mode",
                           CreateBitmap("sort_mode_png",
                                        size = self._button_size),
                           help_string = "Toggle alphabetical/numerical sort in parts list")
        sort_ops.AddButton(ID_SORT_REVERSE, "Sort reverse",
                           CreateBitmap("sort_reverse_png",
                                        size = self._button_size),
                           help_string = "Reverse sort order in parts list")



        assistant_tab = RB.RibbonPage(self._ribbon, self.ID_ASSISTANT_PAGE, "Assistant")



        selector_panel = RB.RibbonPanel(assistant_tab, wx.ID_ANY, "Selector")
        self.selector_1 = wx.Choice(selector_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, [])
        self.selector_2 = wx.Choice(selector_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, [])
        self.selector_1.SetMinSize(wx.Size(100, -1))
        self.selector_2.SetMinSize(wx.Size(100, -1))


        selector_sizer = wx.BoxSizer(wx.VERTICAL)
        # selector_sizer.AddStretchSpacer(1)
        selector_sizer.Add(self.selector_1, 0, wx.ALL|wx.EXPAND, border = 10)
        selector_sizer.Add(self.selector_2, 0, wx.ALL|wx.EXPAND, border = 10)
        # selector_sizer.AddStretchSpacer(1)
        selector_panel.SetSizer(selector_sizer)

        recon_panel = RB.RibbonPanel(assistant_tab, wx.ID_ANY, "Comparison tools")

        recon_ops = RB.RibbonButtonBar(recon_panel)
        recon_ops.AddButton(ID_CALC_SIM, "Calculate similarity",
                            CreateBitmap("compare_png",
                                         size = self._button_size),
                            help_string = "Calculate and report similarity between two assemblies")
        recon_ops.AddButton(ID_ASS_MAP, "Map assembly elements",
                            CreateBitmap("injection_png",
                                         size = self._button_size),
                            help_string = "Map elements in first assembly to those in second")
        recon_ops.AddButton(ID_RECON, "Reconcile assemblies",
                            CreateBitmap("tree_png",
                                         size = self._button_size),
                            help_string = "Calculate and report edit path(S) to transform one assembly into another")

        suggestions_panel = RB.RibbonPanel(assistant_tab, wx.ID_ANY, "Configuration suggestions")

        suggestions_ops = RB.RibbonButtonBar(suggestions_panel)
        suggestions_ops.AddHybridButton(ID_SUGGEST, "Suggest new assembly",
                                        CreateBitmap("bulb_sharp_small_png",
                                                     size = self._button_size))



        settings_tab = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Settings & help")

        info_panel = RB.RibbonPanel(settings_tab, wx.ID_ANY, "Info",
                                       style=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)

        info_tools = RB.RibbonToolBar(info_panel, wx.ID_ANY)
        info_tools.AddTool(ID_SETTINGS, wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_OTHER, wx.Size(self._default_size)))
        info_tools.AddTool(ID_ABOUT, wx.ArtProvider.GetBitmap(wx.ART_QUESTION, wx.ART_OTHER, wx.Size(self._default_size)))

        view_panel = RB.RibbonPanel(settings_tab, wx.ID_ANY, "View",
                                       style=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)

        view_tools = RB.RibbonToolBar(view_panel, wx.ID_ANY)
        view_tools.AddTool(ID_LINE_VIEW, wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_OTHER, wx.Size(self._default_size)))
        view_tools.AddTool(ID_COMMON_SELECTOR_VIEW, wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_OTHER, wx.Size(self._default_size)))

        self._ribbon.Realize()



        ''' Initialise main layout:
                (L) Assembly-specific notebook pages
                (R) Lattice view containing all assemblies '''

        _splitter = MySplitter(panel_top)

        self.latt_panel = wx.Panel(_splitter)
        self._notebook = wx.Notebook(_splitter)

        _splitter.SplitVertically(self._notebook,self.latt_panel)
        _splitter.SetSashGravity(0.5)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self._ribbon, 0, wx.EXPAND)
        s.Add(_splitter, 1, wx.ALL|wx.EXPAND, self._border)
        panel_top.SetSizer(s)

        ''' LATTICE VIEW SETUP
            Set up matplotlib FigureCanvas with toolbar for zooming and movement '''
        self.latt_figure = mpl.figure.Figure()
        self.latt_canvas = FigureCanvas(self.latt_panel, -1, self.latt_figure)
        self.latt_axes = self.latt_figure.add_subplot(111)
        self.latt_tb = NavigationToolbar(self.latt_canvas)

        # ''' Remove plot border/axes and tick marks '''
        # self.latt_axes.axes.axis('off')
        # self.latt_axes.axes.get_xaxis().set_ticks([])
        # self.latt_axes.axes.get_yaxis().set_ticks([])

        s2 = wx.BoxSizer(wx.HORIZONTAL)
        s2.Add(self._notebook, 1, wx.ALL|wx.EXPAND, self._border)
        s2.Add(self.latt_panel, 1, wx.ALL|wx.EXPAND, self._border)
        _splitter.SetSizer(s2)

        sb = wx.StaticBox(self.latt_panel, -1, label = 'Lattice view')
        self.latt_sizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        self.latt_sizer.Add(self.latt_canvas, 1, wx.EXPAND | wx.ALIGN_TOP | wx.ALL, self._border)
        self.latt_sizer.Add(self.latt_tb, 0, wx.ALL|wx.EXPAND, self._border)
        self.latt_panel.SetSizer(self.latt_sizer)

        ''' Can call Realize() and/or Hide(), to be shown later when file loaded/data updated '''
        # self.latt_canvas.Hide()
        # self.latt_tb.Realize()
        # self.latt_tb.Hide()



        ''' Status bar '''
        self.statbar = self.CreateStatusBar()



        ''' App-wide bindings '''
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnNewAssembly, id = ID_NEW)
        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnDeleteAssembly, id = ID_DELETE)
        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnFileOpen, id = ID_FILE_OPEN)
        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnFileSave, id = ID_FILE_SAVE)
        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnExportAssembly, id = ID_EXPORT_ASSEMBLY)

        ass_ops.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnAddNode, id = ID_ADD_NODE)
        ass_ops.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnRemoveNode, id = ID_REMOVE_NODE)
        ass_ops.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnAssemble, id = ID_ASSEMBLE)
        ass_ops.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnFlatten, id = ID_FLATTEN)
        ass_ops.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnDisaggregate, id = ID_DISAGGREGATE)
        ass_ops.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnAggregate, id = ID_AGGREGATE)

        sort_ops.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnSortMode, id = ID_SORT_MODE)
        sort_ops.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnSortReverse, id = ID_SORT_REVERSE)

        # recon_ops.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnCalcSim, id = ID_CALC_SIM)
        # recon_ops.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnMapAssemblies, id = ID_ASS_MAP)
        recon_ops.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnRecon, id = ID_RECON)

        suggestions_ops.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnSuggestionsButton, id = ID_SUGGEST)
        suggestions_ops.Bind(RB.EVT_RIBBONBUTTONBAR_DROPDOWN_CLICKED, self.OnSuggestionsDropdown, id = ID_SUGGEST)

        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnSettings, id = ID_SETTINGS)
        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnAbout, id = ID_ABOUT)

        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnLineViewMode, id = ID_LINE_VIEW)
        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnCommonSelectorMode, id = ID_COMMON_SELECTOR_VIEW)

        self.Bind(RB.EVT_RIBBONBAR_PAGE_CHANGING, self.OnRibbonTabChanging)

        self._notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnNotebookPageChanging)
        # self._notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChanged)
        self._notebook.Bind(wx.EVT_RIGHT_DOWN, self.OnNotebookRightDown)



        ''' Lattice view bindings: "mpl_connect" is equivalent of WX "Bind" '''
        self.latt_canvas.mpl_connect('button_press_event', self.GetLattPos)
        # self.latt_canvas.mpl_connect('button_release_event', self.LattNodeSelected)
        self.latt_canvas.mpl_connect('button_release_event', self.OnLatticeMouseRelease)
        # self.latt_canvas.mpl_connect('pick_event', self.OnNodePick)



        '''
            OBJECTS FOR ASSEMBLY MANAGEMENT
        '''
        self._notebook_manager = {}
        self._assembly_manager = AssemblyManager(viewer = self.latt_figure, axes = self.latt_axes)



        ''' Starter assembly '''
        self.MakeNewAssemblyPage()



    # def get_selected_assemblies(self):

    #     self.AddText('Trying to get selected assemblies...')

    #     if self.selector_1.GetSelection() == wx.NOT_FOUND or self.selector_2.GetSelection() == wx.NOT_FOUND:
    #         self.AddText('Two assemblies not selected')
    #         return

    #     s1 = self.selector_1.GetSelection()
    #     s2 = self.selector_2.GetSelection()

    #     if s1 == s2:
    #         self.AddText('Two different assemblies must be selected')
    #         return None

    #     name1 = self.selector_1.GetString(s1)
    #     name2 = self.selector_1.GetString(s2)
    #     self.AddText('Assemblies selected:')
    #     print(name1)
    #     print(name2)

    #     # a1 = self._assembly_manager._mgr[id1]
    #     # a2 = self._assembly_manager._mgr[id2]
    #     p1 = [el for el in self._notebook_manager if el.name == name1][0]
    #     id1 = self._notebook_manager[p1]
    #     p2 = [el for el in self._notebook_manager if el.name == name2][0]
    #     id2 = self._notebook_manager[p2]

    #     # return a1, a2
    #     return id1, id2



    # def OnMapAssemblies(self, event):

    #     ''' HR FEB 2021
    #         Disabled for now '''
    #     # print('Mapping assembly elements...')
    #     # _assemblies = self.get_selected_assemblies()

    #     # if not _assemblies:
    #     #     self.AddText('Could not get assemblies')
    #     #     return None

    #     # a1 = _assemblies[0]
    #     # a2 = _assemblies[1]

    #     # _mapped, _unmapped = StepParse.map_nodes(a1, a2)
    #     # self.AddText('Done mapping nodes')
    #     # print('Mapped nodes: ', _mapped)
    #     # print('Unmapped nodes: ', _unmapped)

    #     ''' HR June 21 xlsx_write removed here -> fileutils as want to consolidate in future '''
    #     # self.xlsx_write()



    # def OnCalcSim(self, event):

    #     ''' HR FEB 2021
    #         Disabled for now '''
    #     # self.AddText('Calculate similarity button pressed')

    #     # _assemblies = self.get_selected_assemblies()

    #     # if not _assemblies:
    #     #     self.AddText('Could not get assemblies')
    #     #     return None

    #     # a1 = _assemblies[0]
    #     # a2 = _assemblies[1]
    #     # _map = {}

    #     # l1 = a1.leaves
    #     # l2 = a2.leaves

    #     # for n1 in l1:
    #     #     for n2 in l2:
    #     #         _map[(n1, n2)] = StepParse.similarity(a1.nodes[n1]['label'], a2.nodes[n2]['label'])

    #     # _g = nx.compose(a1,a2)
    #     # print('Nodes:', _g.nodes)
    #     # print('Edges:', _g.edges)

    #     # return _map
    #     pass



    # def OnRecon(self, event = None):

    #     self.AddText('Tree reconciliation running...')

    #     assemblies = self.get_selected_assemblies()

    #     if not assemblies:
    #         self.AddText('Could not get assemblies')
    #         return None

    #     a1 = assemblies[0]
    #     a2 = assemblies[1]

    #     ''' HR June 21 "Reconcile" moved from StepParse class method to AssemblyManager '''
    #     # paths, cost, cost_from_edits, node_edits, edge_edits = StepParse.Reconcile(a1, a2)
    #     paths, cost, cost_from_edits, node_edits, edge_edits = self._assembly_manager.Reconcile(a1, a2)

    #     textout = 'Node edits: {}\nEdge edits: {}\nTotal cost (Networkx): {}\nTotal cost (no. of edits): {}'.format(
    #         node_edits, edge_edits, cost, cost_from_edits)

    #     self.AddText('Tree reconciliation finished')
    #     self.DoNothingDialog(event, textout)



    ''' HR 24/06/22 To create BoM reconciliation dialog and retrieve:
                    (1) Blocking spec (by name, by BB or none)
                    (2) Metrics to consider (name, local structure, BB, topology) '''
    def OnRecon(self, event = None, *args, **kwargs):
        ''' Check that active assembly not already in lattice '''
        id2 = self.assembly.assembly_id
        # if id2 in self._assembly_manager._assemblies_in_lattice:
        #     print('Assembly already in lattice; not proceeding with reconciliation')
        #     return

        ''' Set up choices '''
        ids = [el for el in self._assembly_manager._assemblies_in_lattice]
        blocking_dict = {'Block by name':'bn', 'Block by BB':'bb', 'No blocking':None}
        blocking_modes = blocking_dict.keys()
        matching_properties = ['By name', 'By local structure', 'By BB', 'By topology']

        ''' Create recon spec dialog in context manager '''
        with ReconciliationSpecDialog(parent = self,
                                      ids = ids,
                                      blocking_modes = blocking_modes,
                                      matching_properties = matching_properties) as recon_dialog:
            if recon_dialog.ShowModal() == wx.ID_OK:
                recon_spec = recon_dialog.get_spec()
                # recon_spec = True
            else:
                # recon_spec = None
                recon_spec = None
                print('Could not get recon spec; returning...')
                return

        print('recon_spec:', recon_spec)

        if recon_spec:
            print('\nProceeding with recon...\n')
            # return
        else:
            print('\nAborting reconciliation...\n')
            return

        ''' Separate all recon specs '''
        id1 = recon_spec[0]
        blocking_mode = blocking_dict[recon_spec[1]]
        weights = recon_spec[2]
        ''' Set all weights to zero if all one: WORKAROUND FOR NOW '''
        if set(weights) == {0}:
            ''' Set all to 1 if all zero '''
            print('Resetting property weights to 1, as all zero...')
            weights = [1 for el in weights]

        print('recon_args:', id1, blocking_mode, weights)

        ''' Add BoM to lattice using retrieved matches '''
        results = self._assembly_manager.matching_strategy(id1 = id1, id2 = id2, stages = [((blocking_mode, {}), ('mb', {'weights': weights}))])
        # if not results:
        #     return

        print('Matching results:\n', results)
        print('\nFinished "OnRecon"\n')

        matches = results[1][0]
        print('Matches:', matches)
        matches_text = []
        ass1 = self._assembly_manager._mgr[id1]
        ass2 = self._assembly_manager._mgr[id2]
        for match in matches:
            text1 = str(id1) + ': node ' + str(match[0]) + '; name: ' + str(ass1.nodes[match[0]]['screen_name'])
            text2 = str(id2) + ': node ' + str(match[1]) + '; name: ' + str(ass2.nodes[match[1]]['screen_name'])
            matches_text.append(text1 + '; ' + text2 + '\n')
        matches_text = ''.join(matches_text)

        print('Formatted matching text:\n', matches_text, '\n')

        ''' Create report dialog for user to decide whether to add to lattice '''
        report_dialog = ReconciliationResultsDialog(parent = self,
                                                    id1 = id1,
                                                    id2 = id2,
                                                    matches_text = matches_text)
        if not report_dialog.ShowModal() == wx.ID_OK:
            print('Not adding to lattice')
            return

        print('Trying to add assembly', id2, 'to lattice...')
        self._assembly_manager.AddToLattice(id1, id2, matches)
        print('Added assembly', id2, 'to lattice')



    def OnSuggestionsButton(self, event):
        self.AddText('Generating suggestions for new assembly based on selected theme (priorities)...')



    def OnSuggestionsDropdown(self, event):
        menu = wx.Menu()
        for item in self.themes:
            menu.Append(wx.ID_ANY, item)

        event.PopupMenu(menu)



    @property
    def assembly_list(self):
        try:
            _list = [el.name for el in self._notebook_manager]
        except:
            print('Exception while trying to populate assembly list; returning empty list')
            _list = []

        return _list



    def OnRibbonTabChanging(self, event = None):
        print('Ribbon tab changing')

        ''' To repopulate assembly selectors (ComboBox)whenever that tab is selected '''
        if event.GetPage().GetId() == self.ID_ASSISTANT_PAGE:
            print('Assistant page selected')
            try:
                _list = self.assembly_list
                print('List of assemblies:', _list)
                self.selector_1.Set(_list)
                self.selector_2.Set(_list)
            except:
                print('Could not reset assembly selector tools')

        if event:
            event.Skip()



    def OnNotebookRightDown(self, event):
        menu = wx.Menu()
        ID_NEW_ASSEMBLY = self.NewControlId()
        ID_DELETE_ASSEMBLY = self.NewControlId()
        ID_RENAME_ASSEMBLY = self.NewControlId()
        ID_ADD_TO_LATTICE = self.NewControlId()
        ID_REMOVE_FROM_LATTICE = self.NewControlId()
        ID_DUPLICATE_ASSEMBLY = self.NewControlId()
        ID_IMPORT_ASSEMBLY = self.NewControlId()

        menu.Append(ID_DELETE_ASSEMBLY, 'Delete assembly')
        menu.Append(ID_RENAME_ASSEMBLY, 'Rename assembly')
        menu.Append(ID_ADD_TO_LATTICE, 'Add assembly to lattice')
        menu.Append(ID_REMOVE_FROM_LATTICE, 'Remove assembly from lattice')
        menu.Append(ID_DUPLICATE_ASSEMBLY, 'Duplicate active assembly')
        menu.Append(ID_IMPORT_ASSEMBLY, 'Import StrEmbed assembly from file')

        menu.Bind(wx.EVT_MENU, self.OnNewAssembly, id = ID_NEW_ASSEMBLY)
        menu.Bind(wx.EVT_MENU, self.OnRenameAssembly, id = ID_RENAME_ASSEMBLY)
        menu.Bind(wx.EVT_MENU, self.OnDeleteAssembly, id = ID_DELETE_ASSEMBLY)
        menu.Bind(wx.EVT_MENU, self.OnAddToLattice, id = ID_ADD_TO_LATTICE)
        menu.Bind(wx.EVT_MENU, self.OnRemoveFromLattice, id = ID_REMOVE_FROM_LATTICE)
        menu.Bind(wx.EVT_MENU, self.OnDuplicateAssembly, id = ID_DUPLICATE_ASSEMBLY)
        menu.Bind(wx.EVT_MENU, self.OnImportAssembly, id = ID_IMPORT_ASSEMBLY)

        self.PopupMenu(menu)



    def UserInput(self, message = 'Text input', caption = 'Enter text', value = None):
        dlg = wx.TextEntryDialog(self, message, caption, value = value)
        dlg.ShowModal()
        result = dlg.GetValue()
        dlg.Destroy()
        return result



    ''' Should be integrated into AssemblyManager '''
    def OnRenameAssembly(self, event):
        # page = self._notebook.GetPage(self._notebook.GetSelection())
        old_name = self.assembly.assembly_name

        new_name_okay = False
        while not new_name_okay:
            new_name = self.UserInput(caption = 'Enter new assembly name', value = old_name)
            if old_name == new_name:
                return
            ''' Remove special characters '''
            new_name_corr = re.sub('[!@~#$_]', '', new_name)
            if new_name_corr != new_name:
                new_name = new_name_corr
                print('Special characters removed')
            ''' Check new name not in existing names (excluding current) '''
            # names = [el.name for el in self._notebook_manager]
            names = [a.assembly_name for a in self._assembly_manager._mgr.values()]
            names.remove(old_name)
            if new_name not in names:
                print('New name not in existing names')
                new_name_okay = True
            else:
                print('New name in existing names! No can do, buddy!')
                continue
            ''' Check new name is string of non-zero length '''
            if isinstance(new_name, str) and new_name:
                print('New name applied')
                new_name_okay = True

        ''' Set screen text for notebook page '''
        # page.name = new_name
        self._notebook.SetPageText(self._notebook.GetSelection(), new_name)
        ''' Also change assembly name '''
        self.assembly.assembly_name = new_name



    def OnDeleteAssembly(self, event):
        ''' Veto if page being deleted is the only one... '''
        if self._notebook.GetPageCount() <= 1:
            print('Cannot delete only assembly')
            return

        selection = self._notebook.GetSelection()
        page = self._notebook.GetPage(selection)

        ''' Delete notebook page, correponding assembly object and dictionary entry '''
        self._notebook.DeletePage(selection)
        _id = self._notebook_manager[page]

        # self._assembly_manager.RemoveFromLattice(_id)
        self._assembly_manager.DeleteAssembly(_id)
        self._notebook_manager.pop(page)
        self.AddText('Assembly deleted')

        ''' WX will default to another notebook page, so get active page and assembly '''
        selection = self._notebook.GetSelection()
        page = self._notebook.GetPage(selection)
        _id = self._notebook_manager[page]
        self.assembly = self._assembly_manager._mgr[_id]

        ''' Finally, refresh lattice view '''
        self.DisplayLattice(called_by = 'OnDeleteAssembly')



    ''' HR 03/03/22 To add assembly to lattice, with dialog for user spec '''
    def OnAddToLattice(self, event = None, *args, **kwargs):
        print('Running "OnAddToLattice"')
        # ''' Not tested '''
        # _id = self.assembly.assembly_id

        # ''' HR 05/07/22 MUST ADD DECISION HERE -> SIMPLE OR NORMAL ADD TO LATTICE '''
        
        # ''' Must get user input here '''
        
        # ''' Then add to lattice if user confirms '''
        # results = self.matching_strategy(id1, id2, *args, **kwargs)[1]
        # matches = dict(results[0])
        # self._assembly_manager.AddToLattice(id1, id2, matches)

        ''' HR 05/07/22 Allow user to decide whether to add assembly to lattice '''

        ''' If manager is empty, do simple add '''
        if len(self._assembly_manager._assemblies_in_lattice) == 0:
            with DecisionDialog(parent = self,
                                message = 'Assembly load dialog',
                                caption = 'OK to add loaded assembly to lattice?') as dialog:
                if dialog.ShowModal() == wx.ID_OK:
                    print('Adding assembly to lattice...')
                    self._assembly_manager.AddToLatticeSimple(_id)
                else:
                    print('Not adding loaded assembly to lattice; returning...')

        else:
            self.OnRecon()
            print('Finished "OnAddToLattice"')



    ''' HR 03/03/22 To remove assembly from lattice '''
    def OnRemoveFromLattice(self, event = None):
        print('Running "OnRemoveFromLattice"')
        ''' Not tested '''
        _id = self.assembly.assembly_id
        self._assembly_manager.RemoveFromLattice(_id)

        self.DisplayLattice(set_pos = True, called_by = 'OnRemoveFromLattice')

        self.Update3DView()



    ''' General file-open method; takes list of file extensions as argument
        and can be used for specific file names ("starter", string)
        or types ("ender", string or list) '''
    def GetFilename(self, dialog_text = "Open file", starter = None, ender = None):

        ''' Convert "ender" to list if only one element '''
        if isinstance(ender, str):
            ender = [ender]

        ''' Check that only one argument is present '''
        ''' Create text for file dialog '''
        if starter and ender:
            file_open_text = starter.upper() + " files (" + starter.lower() + "*)|" + starter.lower() + "*"
        elif starter is None and ender is not None:
            file_open_text = [el.upper() + " files (*." + el.lower() + ")|*." + el.lower() for el in ender]
            file_open_text = "|".join(file_open_text)
        else:
            raise ValueError("Requires starter or ender only")

        ''' Create file dialog '''
        fileDialog = wx.FileDialog(self, dialog_text, "", "",
                                   file_open_text,
                                   wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fileDialog.ShowModal()
        filename = fileDialog.GetPath()
        print('Full path from file dialog: \n', filename)
        fileDialog.Destroy()

        ''' Return file name, ignoring rest of path '''
        return filename



    def OnFileOpen(self, event = None, add_to_lattice = None):

        ''' Get STEP filename '''
        # open_filename = self.GetFilename(ender = ["step", "stp"]).split("\\")[-1]
        open_filename = self.GetFilename(ender = ["step", "stp"])

        ''' Return if filename is empty, i.e. if user selects "cancel" in file-open dialog '''
        if not open_filename:
            print('File not found')
            return
        else:
            print('Trying to load file...')

        ''' Get active page and assembly ID '''
        _page = self._notebook.GetPage(self._notebook.GetSelection())
        _id = self._notebook_manager[_page]

        # _page.filename_fullpath = open_filename

        ''' Wipe existing assembly if one already loaded; replace with empty one '''
        if self._page.file_open:
            ''' Remove old assembly from manager '''
            self._assembly_manager.RemoveFromLattice(_id)

            ''' Create new assembly + ID and replace link to page '''
            _id, _assembly = self._assembly_manager.new_assembly()
            self._notebook_manager[_page] = _id

            ''' Set new assembly to be active one '''
            self.assembly = _assembly

            ''' Rename displayed assembly name '''
            new_name = _assembly.assembly_name
            self._notebook.SetPageText(self._notebook.GetSelection(), new_name)

        ''' Load data, create nodes and edges, etc. '''
        try:
            self.assembly.load_step(open_filename)
            print('File loaded')
        except Exception as e:
            print('Could not load file; returning...', e)
            return

        ''' Show parts list and lattice '''
        self.DisplayPartsList()

        ''' Do some tidying up '''
        if self._page.file_open:
            ''' Clear selector window if necessary '''
            try:
                self._page.slct_sizer.Clear(True)
            except:
                print("Couldn't clear selector sizer")

            ''' Clear lattice plot if necessary '''
            try:
                self.latt_axes.clear()
            except:
                print("Couldn't clear lattice axes")

        else:
            ''' Set "file is open" tag '''
            self._page.file_open = True
            self._page.Enable()

        ''' ------------------- '''

        ''' Older code redundant '''
        # ''' Add to lattice '''
        # if not add_to_lattice:
        #     add_to_lattice = self.ADD_TO_LATTICE_DEFAULT

        # if add_to_lattice:
        #     print('Adding assembly to lattice')
        #     self._assembly_manager.AddToLattice(_id)

        ''' HR 05/07/22 Allow user to decide whether to add loaded assembly to lattice '''

        ''' If manager is empty, do simple add '''
        if len(self._assembly_manager._assemblies_in_lattice) == 0:
            with DecisionDialog(parent = self,
                                message = 'Assembly load dialog',
                                caption = 'OK to add loaded assembly to lattice?') as dialog:
                if dialog.ShowModal() == wx.ID_OK:
                    print('Adding assembly to lattice...')
                    self._assembly_manager.AddToLatticeSimple(_id)
                else:
                    print('Not adding loaded assembly to lattice; returning...')

        else:
            self.OnRecon()

        print('Added assembly to lattice; refreshing lattice and 3D views')

        ''' Display lattice and update 3D viewer '''
        self.DisplayLattice(set_pos = True, called_by = 'OnFileOpen')
        # self.Update3DView(selected_items = self.selected_items)
        self.Update3DView()



    ''' HR 11/03/22 To export project to Excel '''
    def OnFileSave(self, event = None, filename = None, path = None):
        print('Running "OnFileSave"...')

        ''' Grab default path and filename if not specified '''
        if not path:
            path = self._assembly_manager.SAVE_PATH_DEFAULT
        if not filename:
            filename = self._assembly_manager.SAVE_FILENAME_DEFAULT

        ''' Open file dialog and populate with path and filename for starters;
            do even if path and file specified, to confirm with user '''
        dialog_text = 'Export project to Excel'
        ''' Create file dialog '''
        fileDialog = wx.FileDialog(parent = self,
                                   message = dialog_text,
                                   defaultDir = path,
                                   defaultFile = filename,
                                   style = wx.FD_SAVE)
        fileDialog.ShowModal()
        file_fullpath = fileDialog.GetPath()
        print('Full path from file dialog: \n', file_fullpath)
        fileDialog.Destroy()

        ''' Construct full file path and save project to Excel '''
        print('Filename (full path): ', file_fullpath)

        ''' Dump project to Excel file and return full file path '''
        self._assembly_manager.xlsx_write(save_file = file_fullpath, name_field = 'screen_name')
        return file_fullpath



    def DisplayPartsList(self, display_field = 'screen_name'):

        print('Running DisplayPartsList')
        ''' Check if file loaded previously '''
        try:
            self._page.partTree_ctc.DeleteAllItems()
        except:
            pass

        ''' Create root node... '''
        root_id = self.assembly.get_root()
        print('Found root:', root_id)
        text = self.assembly.nodes[root_id][display_field]
        label = self.assembly.nodes[root_id][display_field]

        ctc_root_item = self._page.partTree_ctc.AddRoot(text = text, ct_type = 1, data = {'id_': root_id, 'sort_id': root_id, 'label': label})

        self._page.ctc_dict     = {}
        self._page.ctc_dict_inv = {}

        self._page.ctc_dict[root_id] = ctc_root_item
        self._page.ctc_dict_inv[ctc_root_item] = root_id

        '''' ...then all others '''
        # tree_depth = nx.dag_longest_path_length(self.assembly, root_id)
        tree_depth = nx.dag_longest_path_length(self.assembly)

        for i in range(tree_depth + 1)[1:]:
            for node in self.assembly.nodes:
                depth = nx.shortest_path_length(self.assembly, root_id, node)

                if depth == i:
                    parent_id = [el for el in self.assembly.predecessors(node)][-1]
                    ctc_parent = self._page.ctc_dict[parent_id]

                    ''' Text and label will differ if changed previously by user in parts view '''
                    try:
                        label = self.assembly.nodes[node][display_field]
                    except:
                        label = self.assembly.default_label_part

                    '''HR 10/06/22 To allow user-renamed items to retain names after assembly operations '''
                    if 'text' in self.assembly.nodes[node]:
                        text = self.assembly.nodes[node]['text']
                    else:
                        try:
                            text = self.assembly.nodes[node][display_field]
                        except:
                            text = self.assembly.default_label_part

                    ctc_item = self._page.partTree_ctc.AppendItem(ctc_parent, text = text, ct_type = 1, data = {'id_': node, 'sort_id': node, 'label': label})

                    self._page.ctc_dict[node]         = ctc_item
                    self._page.ctc_dict_inv[ctc_item] = node

        self._page.partTree_ctc.ExpandAll()

        ''' Sort all tree items '''
        self._page.partTree_ctc.SortAllChildren(self._page.partTree_ctc.GetRootItem())

        print('Finished DisplayPartsList')



    '''Propagate user selections in 3D view to all views'''
    def OnLeftUp_3D(self, event):
        ''' Pass event to Viewer3D class (goes via Select or SelectArea) '''
        self._page.occ_panel.OnLeftUp(event)

        ''' Grab selected parts in 3D view '''
        print('Getting selected part(s) from 3D view...')
        shapes = self._page.occ_panel._display.selected_shapes

        if not shapes:
            return

        ''' ------------------------------------
        HR 25/11/21 New GUI update functionality
        '''
        ''' Check if CTRL key pressed; if so, append selected items to existing
            GetModifiers avoids problems with different keyboard layouts...
            ...but is equivalent to ControlDown, see here:
            https://wxpython.org/Phoenix/docs/html/wx.KeyboardState.html#wx.KeyboardState.ControlDown '''
        if event.GetModifiers() == wx.MOD_CONTROL:
            print('CTRL held during 3D selection; retaining old selection(s)...')
            retain = True
        else:
            print('CTRL not held during 3D selection; not retaining old selection(s)...')
            retain = False

        ''' Get IDs of 3D shapes '''
        IDS = []
        print('IDs of item(s) selected:')
        for shape in shapes:
            ''' Inverse dict look-up '''
            # item = [k for k,v in self.assembly.OCC_dict.items() if v == shape][-1]
            ''' HR 19/05/12 New version to look in node dicts for shape '''
            # item = [node for node in self.assembly.nodes if self.assembly.nodes[node]['shape_loc'][0] == shape][-1]
            ''' HR 05/11/21 Updated to account for empty shape field (e.g. for user-created sub-assemblies) '''
            item = [node for node in self.assembly.nodes if 'shape_loc' in self.assembly.nodes[node] and self.assembly.nodes[node]['shape_loc'][0] == shape][-1]
            IDS.append(item)
        print('Items selected in 3D view: ', IDS)

        ''' Get selected items in old state, OS '''
        OS = set(self.selected_items)

        ''' Get selections in new state, NS '''
        NS = self.get_NS(OS, IDS, retain = retain, select_all_children = self.SELECT_ALL_CHILDREN)

        ''' Get changing items '''
        TS, TU = self.get_changes(OS, NS)[0:2]

        ''' Update GUI globally '''
        self.update_GUI(OS, NS, TS, TU)
        ''' ------------------------------------ '''



    # @property
    # def hidden_nodes(self):
    #     _hidden_nodes = [node for node in self.nodes if self.nodes[node]['hide']]
    #     return _hidden_nodes



    ''' HR 19/05/21 Refreshed to work with new STEP parsing method
        HR 01/03/22 Major rejig to improve logic '''
    def Update3DView(self, selected_items = None, leaves = None, hidden_nodes = None, parts_only = True):

        ''' Avoid calling some node lists if already known when called;
            purpose of kwargs only to reduce size of sets and/or speed up look-up and set operations '''
        if selected_items == None:
            selected_items = self.selected_items
        if leaves == None:
            leaves = self.assembly.leaves
        # if hidden_nodes == None:
        #     hidden_nodes = self.hidden_nodes
        if parts_only:
            ''' Only consider shapes of leaf nodes, i.e. parts... '''
            all_nodes = leaves
        else:
            ''' ...else consider sub-assemblies as well '''
            all_nodes = [el for el in self.assembly.nodes]
            if hasattr(self.assembly, 'head'):
                head = self.assembly.head
                if head in all_nodes:
                    all_nodes.remove(head)

        print('Selected items: ', selected_items)
        print('All nodes: ', all_nodes)

        ''' All selected parts, ASP '''
        ASP = set(all_nodes) & set(selected_items)
        print('ASP: ', ASP)
        ''' All unselected parts, AUP '''
        # AUP = set(all_nodes) & (set(all_nodes) - set(selected_items))
        AUP = set(all_nodes) - set(selected_items)
        print('AUP: ', AUP)
        ''' All selected parts to show '''
        ASS = []
        for node in ASP:
            node_dict = self.assembly.nodes[node]
            if not node_dict['shape_loc'][0]:
                continue
            if 'hide' in node_dict:
                if not node_dict['hide']:
                    continue
            ASS.append(node)
        print('ASS: ', ASS)
        ''' All unselected parts to show '''
        AUS = []
        for node in AUP:
            node_dict = self.assembly.nodes[node]
            if 'shape_loc' in node_dict:
                if not node_dict['shape_loc'][0]:
                    continue
            if 'hide' in node_dict:
                if not node_dict['hide']:
                    continue
            AUS.append(node)
        print('AUS: ', AUS)


        ''' Clear 3D view completely '''
        self._page.occ_panel._display.EraseAll()

        ''' Tidy up ASS and AUP '''
        for node in ASS:
            shape, c = self.assembly.nodes[node]['shape_loc']
            self.display_shape(node, shape, c)
        for node in AUS:
            shape, c = self.assembly.nodes[node]['shape_loc']
            self.display_shape(node, shape, c, transparency = 1)

        self._page.occ_panel._display.View.FitAll()
        self._page.occ_panel._display.View.ZFitAll()
        print('Done "Update3DView"')



    def ScaleImage(self, img, target_w = None, scaling = 0.95):

        ''' Default: target width is that of selector view holding image '''
        if target_w == None:
            target_w  = self.tight * self._page.slct_panel.GetSize()[0]/self._page.image_cols

        w, h = img.GetSize()

        if h/w > 1:
            h_new = target_w
            w_new = h_new*w/h
        else:
            w_new = target_w
            h_new = w_new*h/w

        ''' Rescale '''
        img = img.Scale(int(w_new), int(h_new), wx.IMAGE_QUALITY_HIGH)

        return img



    ''' HR JAN/FEB 2021
        Much improved version, delegates to assembly manager '''
    def DisplayLattice(self, set_pos = True, called_by = None):

        print('Running DisplayLattice')

        if called_by:
            print('Called by: ', called_by)

        _id = self.assembly.assembly_id

        try:
            print('Trying to clear lattice axes...')
            self.latt_axes.clear()
            print('Done')
        except Exception as e:
            print('Failed: exception follows')
            print(e)

        ''' Create all guide lines, nodes and edges '''
        self._assembly_manager.create_plot_elements()
        ''' ...then update active assembly... '''
        self._assembly_manager.update_colours_active(to_activate = [_id])

        active = self.assembly.assembly_id
        selected_items = []
        to_select = []
        # self._assembly_manager.update_colours_selected(active, selected = selected_items, to_select = to_select, to_unselect = to_unselect)
        self._assembly_manager.update_colours_selected(active, selected = selected_items, to_select = to_select, called_by = "DisplayLattice")

        print('Finished "DisplayLattice"')
        self.DoDraw('DisplayLattice')



    def DoDraw(self, called_by = None):

        ''' All GUI-specific stuff here
            The rest should be elsewhere (i.e. step_parse)
            for testing outside GUI '''

        if called_by:
            print('DoDraw called by ', called_by)

        ''' Show lattice figure '''
        self.latt_canvas.draw()
        print('Done "draw"')

        self.latt_canvas.Show()
        print('Done canvas "Show"')

        self.latt_tb.Show()
        print('Done toolbar "Show"')

        # ''' Update lattice panel layout '''
        # self.latt_panel.Layout()
        # print('Done layout')



    ''' HR 26/11/21 To compute all selected nodes, NS, in new state during global GUI update '''
    def get_NS(self, OS, IDS, retain = False, select_all_children = False):
        print('Running "get_NS"')

        # ''' Prepare OS and ID '''
        # if not type(OS) == set():
        #     OS = set(OS)

        ''' If ID is single node, i.e. originates from view that can only toggle
            + only one at a time (lattice, selector) '''
        if len(IDS) == 1 and OS :
            ID = IDS[0]
            if retain:
                NS = OS.copy()
                if ID in OS:
                    NS.remove(ID)
                else:
                    NS.add(ID)
                    if select_all_children:
                        children = nx.descendants(self.assembly, ID)
                        NS.update(children)
            else:
                if ID in OS:
                    NS = set()
                else:
                    NS = {ID}
                    if select_all_children:
                        children = nx.descendants(self.assembly, ID)
                        NS.update(children)

        else:
            ''' ...else if multiple IDs passed (len(IDS) > 1), i.e. multiple selections (parts or 3D views) '''
            if retain:
                NS = OS.copy()
            else:
                NS = set()
            for ID in IDS:
                NS.add(ID)
                if select_all_children:
                    children = nx.descendants(self.assembly, ID)
                    NS.update(children)

        print('NS: ', NS)
        return NS



    ''' HR 30/11/21 To get all items to be changed and excluded '''
    def get_changes(self, OS, NS, IS = None):

        ''' If IS not specified, assume same as OS '''
        if not IS:
            IS = OS.copy()

        ''' Get unselected sets '''
        HEAD = self.assembly.head
        ALL = set(self.assembly.nodes) - {HEAD}
        OU = ALL - OS
        IU = ALL - IS
        NU = ALL - NS

        ''' Get selecting, unselecting and changing nodes '''
        TS = NS & OU
        TU = NU & OS
        # CH = TS | TU

        ''' Get already-selected/unselected nodes, and both, to be excluded as already done '''
        AS = TS & IS
        AU = TU & IU
        # EX = AS | AU

        # ''' Get still-to-select/unselect nodes '''
        # SS = TS & IU
        # SU = TU & IS

        ''' Wrongly (un)selected items in IS, to be redone '''
        ADS = (OS & NS) & IU
        ADU = (OU & NU) & IS

        return TS, TU, AS, AU, ADS, ADU



    ''' HR 01/12/21 New method to include shape dictionary
                    for displaying shapes individually; with "erase_shape"
                    can avoid full erase and redraw; adapted from PythonOCC example here:
                    https://github.com/tpaviot/pythonocc-demos/blob/master/examples/core_display_erase_shape.py '''
    def display_shape(self, ID, shape, c, transparency = None):

        # print('   Node ID: ', ID)
        # print('   Shape colours (RGB):', c.Red(), c.Green(), c.Blue())
        # shape_obj = self._page.occ_panel._display.DisplayShape(shape,
        #                                                        color = Quantity_Color(c.Red(),
        #                                                                               c.Green(),
        #                                                                               c.Blue(),
        #                                                                               Quantity_TOC_RGB),
        #                                                        transparency = transparency)[0]
        shape_obj = self._page.occ_panel._display.DisplayShape(shape,
                                                               color = c,
                                                               transparency = transparency)[0]

        if hasattr(self._page, 'shape_dict'):
            self._page.shape_dict[ID] = shape_obj
        else:
            self._page.shape_dict = {ID:shape_obj}



    ''' HR 01/12/21 New method to erase shape individually to avoid full erase and redraw
                    Adapted from PythonOCC example here:
                    https://github.com/tpaviot/pythonocc-demos/blob/master/examples/core_display_erase_shape.py '''
    def erase_shape(self, ID):
        try:
            shape_obj = self._page.shape_dict[ID]
            self._page.shape_dict.pop(ID)
            self._page.occ_panel._display.Context.Erase(shape_obj, True)
            # print('Erased shape from 3D view')
        except:
            print("Couldn't erase shape from 3D view: shape not present")



    ''' HR 25/11/21
        Method to update (de)selections in all views based on new analysis of GUI processes
        OS, NS are nodes selected in new and old states
        TS, TU are node to be selected/unselected
        EX_<VIEW> (in kwargs) is view-specific exclusions, i.e. (de)selections to be vetoed
            as already changed within event-emitting view
            i.e.    EX_PARTS = node(s) already changed in parts view
                    EX_SELECTOR = node already changed in selector view (can only be one) '''
    def update_GUI(self, OS, NS, TS, TU, called_by = None, parts_only = True, **kwargs):

        print('\nRunning "update_GUI"')
        if called_by:
            print(' Called by: ', called_by)

        ''' Freeze (and later thaw) to stop flickering while updating all views '''
        self.Freeze()



        # self._page.occ_panel._display.EraseAll()

        if 'leaves' in kwargs:
            leaves = kwargs['leaves']
        else:
            leaves = self.assembly.leaves

        to_update = TS | TU
        print(' Nodes before...', to_update)
        if parts_only:
            to_update = set(leaves) & to_update
            print(' Nodes after...', to_update)

        for ID in to_update:
            node_dict = self.assembly.nodes[ID]
            ''' HR 29/10/21 Do not display if "hide" is true '''
            if 'hide' in node_dict:
                if node_dict['hide']:
                    continue
            try:
                shape, c = node_dict['shape_loc']
            except:
                shape, c = None, None
                # continue
            ''' Don't display assemblies, i.e. nodes without shapes '''
            if not shape:
                continue
            self.erase_shape(ID)
            if ID in TS:
                self.display_shape(ID, shape, c)
                # print('Displaying S shape')
            else:
                self.display_shape(ID, shape, c, transparency = 1)
                # print('Displaying U shape')
                # self.erase_shape(ID)

        self._page.occ_panel._display.View.FitAll()



        ''' ---------------------
        UPDATE LATTICE VIEW
        '''
        active = self.assembly.assembly_id
        latt = self._assembly_manager._lattice
        NS_MASTER = set([self._assembly_manager.get_master_node(active, ID) for ID in NS])
        TS_MASTER = set([self._assembly_manager.get_master_node(active, ID) for ID in TS])
        TU_MASTER = set([self._assembly_manager.get_master_node(active, ID) for ID in TU])

        print('NS: ', NS_MASTER)
        print('TS: ', TS_MASTER)
        print('TU: ', TU_MASTER)

        active_edges = [edge for edge in latt.edges if active in latt.edges[edge]]

        latt = self._assembly_manager._lattice
        sc = self._assembly_manager.sc
        dc = self._assembly_manager.dc

        ''' Colour nodes '''
        for ID in TS_MASTER:
            latt.node_dict[ID].set_facecolor(sc)
        for ID in TU_MASTER:
            latt.node_dict[ID].set_facecolor(dc)

        ''' Colour main edges '''
        for ID in TS_MASTER:
            for u,v in latt.in_edges(ID):
                if (u in NS_MASTER) and (u,v) in active_edges:
                    print('Colouring edge (selected): ', (u,v))
                    latt.edge_dict[(u,v)].set_color(sc)
            for u,v in latt.out_edges(ID):
                if (v in NS_MASTER) and (u,v) in active_edges:
                    print('Colouring edge (selected): ', (u,v))
                    latt.edge_dict[(u,v)].set_color(sc)
        for ID in TU_MASTER:
            for u,v in latt.in_edges(ID):
                if (u,v) in active_edges:
                    latt.edge_dict[(u,v)].set_color(dc)
                    print('Colouring edge (deselected): ', (u,v))
            for u,v in latt.out_edges(ID):
                if (u,v) in active_edges:
                    latt.edge_dict[(u,v)].set_color(dc)
                    print('Colouring edge (deselected): ', (u,v))

        ''' Colour infumum edges '''
        leaves = set(latt.leaves)
        TS_leaves = TS_MASTER & leaves
        TU_leaves = TU_MASTER & leaves
        for leaf in TS_leaves:
            latt.edge_dict[(leaf,None)].set_color(sc)
        for leaf in TU_leaves:
            latt.edge_dict[(leaf,None)].set_color(dc)
        ''' Redraw lattice '''
        self.DoDraw()



        ''' ---------------------
        UPDATE SELECTOR VIEW
        '''
        self.VETO_SELECTOR = True

        ''' Exclude already-toggled image '''
        if 'EX_SELECTOR' in kwargs:
            EX_SELECTOR = kwargs['EX_SELECTOR']
            TS_ = TS - EX_SELECTOR
            TU_ = TU - EX_SELECTOR
        else:
            TS_ = TS
            TU_ = TU
        ''' Do all selections '''
        for node in TS_:
            b_dict = self._page.button_dict
            if node in b_dict:
                button = b_dict[node]
                try:
                    button.SetValue(True)
                except:
                    print('Could not set button toggle value')
        ''' Do all deselections '''
        for node in TU_:
            b_dict = self._page.button_dict
            if node in b_dict:
                button = b_dict[node]
                try:
                    button.SetValue(False)
                except:
                    print('Could not set button toggle value')

        self.VETO_SELECTOR = False



        ''' ---------------------
        UPDATE PART VIEWS
        '''
        self.VETO_PARTS = True
        print(' Veto parts ON')

        ''' Get all IDs to change, as parts list items can be toggled '''
        TC = TS | TU
        print(' IDs to change in parts list: ', TC)
        ''' Exclude already-toggled ctc items '''
        if 'EX_PARTS' in kwargs:
            EX_ = kwargs['EX_PARTS']
            TC = TC - EX_
            print(' Excluding: ', EX_)
        ''' Add extra parts that are wrongly (un)selected in IS/IU '''
        if 'AD_PARTS' in kwargs:
            AD_ = kwargs['AD_PARTS']
            TC = TC | AD_
        ''' Select/deselect parts list item
            With "select = True", SelectItem toggles state if multiple selections enabled
            https://wxpython.org/Phoenix/docs/html/wx.lib.agw.customtreectrl.CustomTreeCtrl.html '''
        for ID in TC:
            print('   Toggling parts list item ', ID)
            self._page.partTree_ctc.SelectItem(self._page.ctc_dict[ID], select = True)

        self.VETO_PARTS = False
        print(' Veto parts OFF')



        self.Thaw()
        print('Done "update_GUI"\n')



    # def UpdateToggledImages(self):

    #     for id_, button in self._page.button_dict.items():
    #         button.SetValue(False)

    #     selected_items = self.selected_items

    #     for id_ in selected_items:
    #         if id_ in self._page.button_dict:
    #             button = self._page.button_dict[id_]
    #             button.SetValue(True)
    #         else:
    #             pass



    def OnRightClick(self, event):

        '''
        HR 5/3/20 SOME DUPLICATION HERE WITH OPERATION-SPECIFIC METHOD, E.G. "ONFLATTEN"
        IN TERMS OF FILTERING/SELECTION OF OPTIONS BASED ON SELECTED ITEM TYPE/QUANTITY

        HR 5/3/20 SHOULD ADD CHECK HERE THAT MOUSE CLICK IS OVER A SELECTED ITEM
        '''
        # pos = event.GetPosition()

        selected_items = self.selected_items

        ''' Check selected items are present and suitable '''
        if not selected_items:
            print('No items selected')
            return

        '''
        POPUP MENU (WITH BINDINGS) UPON RIGHT-CLICK IN PARTS VIEW
        '''
        menu = wx.Menu()
        # menu_item = menu.Append(wx.ID_ANY, 'Change item and get all affected', 'Change item property and find affected parts in all assemblies')
        # self.Bind(wx.EVT_MENU, self.OnChangeItemProperty, menu_item)


        '''
        FILTERING OF ITEM TYPES -> PARTICULAR POP-UP MENU OPTIONS
        '''
        ''' Single-item options '''
        if len(selected_items) == 1:
            # node = self._page.ctc_dict_inv[selected_items[-1]]
            node = selected_items[-1]
            if node in self.assembly.leaves:
                ''' Part options '''
                menu_item = menu.Append(wx.ID_ANY,
                                        'Disaggregate',
                                        'Disaggregate part into parts')
                self.Bind(wx.EVT_MENU,self.OnDisaggregate, menu_item)
                menu_item = menu.Append(wx.ID_ANY,
                                        'Remove part',
                                        'Remove part')
                self.Bind(wx.EVT_MENU, self.OnRemoveNode, menu_item)
                ''' HR 29/10/21 To allow parts to be hidden in 3D viewer '''
                menu_item = menu.Append(wx.ID_ANY,
                                        'Hide/show',
                                        'Hide/show part in 3D view')
                self.Bind(wx.EVT_MENU, self.OnHideMode, menu_item)
            else:
                ''' Assembly options '''
                menu_item = menu.Append(wx.ID_ANY,
                                        'Flatten',
                                        'Flatten assembly')
                self.Bind(wx.EVT_MENU, self.OnFlatten, menu_item)
                menu_item = menu.Append(wx.ID_ANY,
                                        'Aggregate',
                                        'Aggregate assembly')
                self.Bind(wx.EVT_MENU, self.OnAggregate, menu_item)
                menu_item = menu.Append(wx.ID_ANY,
                                        'Add node',
                                        'Add node to assembly')
                self.Bind(wx.EVT_MENU, self.OnAddNode, menu_item)
                menu_item = menu.Append(wx.ID_ANY,
                                        'Remove sub-assembly',
                                        'Remove sub-assembly')
                self.Bind(wx.EVT_MENU, self.OnRemoveNode, menu_item)
                ''' Sorting options '''
                menu_text = 'Sort children alphabetically'
                menu_item = menu.Append(wx.ID_ANY,
                                        menu_text,
                                        menu_text)
                self.Bind(wx.EVT_MENU, self.OnSortAlpha, menu_item)
                menu_text = 'Sort children by unique ID'
                menu_item = menu.Append(wx.ID_ANY,
                                        menu_text,
                                        menu_text)
                self.Bind(wx.EVT_MENU, self.OnSortByID, menu_item)


            ''' HR 12/10/21 To add/view node data '''
            menu_text = 'Add node data'
            menu_item = menu.Append(wx.ID_ANY,
                                    menu_text,
                                    menu_text)
            self.Bind(wx.EVT_MENU, self.OnAddNodeData, menu_item)
            # menu_text = 'View node data'
            # menu_item = menu.Append(wx.ID_ANY,
            #                         menu_text,
            #                         menu_text)
            # self.Bind(wx.EVT_MENU, self.OnViewNodeData, menu_item)

        elif len(selected_items) > 1:
            ''' Multiple-item options '''
            menu_item = menu.Append(wx.ID_ANY,
                                    'Assemble',
                                    'Form assembly from selected items')
            self.Bind(wx.EVT_MENU, self.OnAssemble, menu_item)
            menu_item = menu.Append(wx.ID_ANY,
                                    'Remove parts',
                                    'Remove parts')
            self.Bind(wx.EVT_MENU, self.OnRemoveNode, menu_item)

            ''' HR 10/12/21 To add on-the-spot similarity score '''
            if len(selected_items) == 2:
                menu_item = menu.Append(wx.ID_ANY,
                                        'Get similarity scores',
                                        'Get similarity scores between two items')
                self.Bind(wx.EVT_MENU, self.OnGetSims, menu_item)

        ''' Create popup menu at current mouse position (default if no positional argument passed) '''
        self.PopupMenu(menu)
        menu.Destroy()



    # def OnChangeItemProperty(self, event):
    #     _selected = self.selected_items
    #     for item in _selected:
    #         tree_item = self._page.ctc_dict[item]
    #         self._page.partTree_ctc.SetItemTextColour(tree_item, self._highlight_colour)
    #     print('Changing item property and finding affected items...')



    def OnGetSims(self, event = None):
        print('Getting all similarity scores between two selected items...')
        items = self.selected_items
        print(' Selected items: ', items)

        ''' Get all scores via assembly manager '''
        _page = self._notebook.GetPage(self._notebook.GetSelection())
        assembly_id = self._notebook_manager[_page]
        s1, s2, s3, s4 = self._assembly_manager.get_sims(assembly_id, assembly_id, items[0], items[1])[1]
        sim_text = 'Name: {:10.3f}\nLocal structure: {:10.3f}\nBounding box: {:10.3f}\nShape: {:10.3f}'.format(s1, s2, s3, s4)

        dialog = wx.MessageDialog(self, sim_text, 'Similarity scores for selected items', wx.OK)
        dialog.ShowModal()
        dialog.Destroy()



    @property
    def selected_items(self):

        '''
        Get items selected in parts view using GetSelections() rather than maintaining list
        b/c e.g. releasing ctrl key during multiple selection
        means not all selections are tracked easily '''

        try:
            _selected_items = [self._page.ctc_dict_inv[item] for item in self._page.partTree_ctc.GetSelections()]
            return _selected_items
        except AttributeError('No items selected'):
            return None

    @selected_items.setter
    def selected_items(self, items):
        if type(items) is list:
            self.selected_items = items
        elif type(items) is int:
            self.selected_items = [items]
        else:
            print('Selected items not reset: items must be list or int')



    # def get_image_name(self, node, suffix = '.jpg'):
    #     ''' Image file type and "suffix" here (jpg) is dictated by python-occ "Dump" method
    #         which can't be changed without delving into C++ '''
    #     full_name = os.path.join(self.im_path, str(self.assembly.assembly_id), str(node)) + suffix
    #     print('Full path of image to fetch:\n', full_name)

    #     return full_name



    ''' HR 02/11/21 To uncheck all ctc items to allow common selector view '''
    def uncheck_all(self):
        ''' Uncheck via "checked = False " '''
        print('Trying to uncheck all ctc items in new page')
        for item in self._page.ctc_dict_inv.keys():
            self._page.partTree_ctc.CheckItem(item, checked = False)



    ''' HR 02/11/21 To differentiate between manual checking (already done via TreeItemChecked)
        and automated checking upon notebook page change to allow common selector view '''
    def check_items(self, nodes):
        print('Trying to check ctc items in new page')
        for node in nodes:
            item = self._page.ctc_dict[node]
            self._page.partTree_ctc.CheckItem(item)



    ''' HR 24/05/21
        To overhaul to account for now-improved OCC-based shape parsing
        and for sub-shapes; also images are held in memory, not saved,
        to avoid temporary folder(s) being created '''
    def TreeItemChecked(self, event):

        ''' Get checked item and search for corresponding image '''
        item = event.GetItem()
        node  = self._page.ctc_dict_inv[item]

        # print('Getting image...')
        # print('Node ID = ', node)

        selected_items = self.selected_items

        if item.IsChecked():
            ''' Get image data '''
            img_data = self.assembly.get_image_data(node)
            if img_data:
                W,H,data = img_data
                img = wx.Image(W,H,data)
                ''' Workaround here until image data can be rotated,
                    as images rendered upside down '''
                img = img.Rotate180()
            else:
                img = self.no_image.ConvertToImage()

            ''' Create/add button in slct_panel
                ---
                1/ Start with null image... '''
            button = wx.BitmapToggleButton(self._page.slct_panel)
            button.SetBackgroundColour('white')
            self._page.slct_sizer.Add(button, 1, wx.EXPAND)
            ''' 2/ Add image after computing size and rescaling '''
            button.SetBitmap(wx.Bitmap(self.ScaleImage(img)))

            ''' Update global list and dict
                ---
                Data is list, i.e. same format as "selected_items"
                but ctc lacks "get selections" method for checked items '''
            self._page.button_dict[node]       = button
            self._page.button_dict_inv[button] = node
            self._page.button_img_dict[node]   = img

            ''' Toggle if already selected elsewhere '''
            if node in selected_items:
                button.SetValue(True)
            else:
                pass

        else:
            if node in self._page.button_dict:
                ''' Remove button from slct_panel '''
                button = self._page.button_dict[node]
                button.Destroy()

                ''' Update global list and dict '''
                self._page.button_dict.pop(node)
                self._page.button_dict_inv.pop(button)
                self._page.button_img_dict.pop(node)

        self._page.slct_panel.SetupScrolling(scrollToTop = False)



    def TreeItemSelectionChanging(self, event):

        if self.VETO_PARTS:
            # OS = None
            print('Tree selections changed, but vetoing GUI update: parts view veto')
        else:
            self.OS = set(self.selected_items)
            print('Items selected before change in tree selections:', self.OS)

            ''' HR 01/12/21 "CallAfter" NOT compatible with VETO_<VIEW> GUI update design!
                            b/c event processing sequence is NESTED, not linear
                            so results in out-of-veto selections being executed
                            that should be vetoed
                            Resolved by directly using separate "changing" and "changed" methods '''
            # wx.CallAfter(self.TreeItemSelectionChanged, OS, event)



    def TreeItemSelectionChanged(self, event):

        ''' HR 30/11/21 To integrate global GUI update method '''
        ''' Abort if vetoed '''
        if self.VETO_PARTS:
            print('Part veto; returning')
            return



        ''' Get intermediate (current) state '''
        IS = set(self.selected_items)
        print('Items selected in intermediate state:', IS)

        ''' Get new state '''
        NS = IS.copy()
        if self.SELECT_ALL_CHILDREN:
            print('Children added to NS: ')
            for ID in IS:
                children = nx.descendants(self.assembly, ID)
                NS.update(children)
                print(' ', children)

        print('Items to be selected in new state:', NS)

        ''' Get changing items '''
        results = self.get_changes(self.OS, NS, IS = IS)
        TS, TU = results[0:2]
        EX = set(results[2]) | set(results[3])
        AD = set(results[4]) | set(results[5])

        ''' Update GUI globally '''
        self.update_GUI(self.OS, NS, TS, TU, called_by = 'TISC', EX_PARTS = EX, AD_PARTS = AD)



    def ImageToggled(self, event):

        # print('Image toggled')
        # node = self._page.button_dict_inv[event.GetEventObject()]
        # self.UpdateListSelections(node)

        ''' HR 30/11/21 To integrate new GUI-wide update method '''
        ''' Abort if vetoed '''
        if self.VETO_SELECTOR:
            print('Image toggled, but vetoing GUI update: selector view veto')
            return

        print('Image toggled')
        ''' Get ID of toggled item '''
        ID = self._page.button_dict_inv[event.GetEventObject()]

        ''' Get old state '''
        OS = set(self.selected_items)

        ''' Get intermediate (current) state '''
        IS = OS.copy()
        if ID in OS:
            IS.remove(ID)
        else:
            IS.add(ID)

        ''' Get new state '''
        NS = self.get_NS(OS, [ID], retain = True, select_all_children = self.SELECT_ALL_CHILDREN)

        ''' Get changing items '''
        results = self.get_changes(OS, NS, IS = IS)
        TS, TU = results[0:2]
        EX = set(results[2]) | set(results[3])

        ''' Update GUI globally '''
        self.update_GUI(OS, NS, TS, TU, EX_SELECTOR = EX)



    def GetLattPos(self, event):

        print('Running "GetLattPos"')

        # print('%s: button = %d, x = %d, y = %d, xdata = %f, ydata = %f' %
        #       ('Double click' if event.dblclick else 'Single click', event.button,
        #        event.x, event.y, event.xdata, event.ydata))

        ''' Get position and type of click event '''
        self.click_pos = (event.xdata, event.ydata)
        # print('Click_position = ', self.click_pos)



    def OnLatticeMouseRelease(self, event):

        print('OnLatticeMouseRelease')

        ''' Get plot object '''
        plot_obj = self._assembly_manager._lattice

        ''' Tolerance for node/line picker; tweak if necessary '''
        picker_tol = len(plot_obj.leaves)/100

        ''' Retain zoom settings for later '''
        self.latt_plotlims = (self.latt_axes.get_xlim(), self.latt_axes.get_ylim())

        ''' If right-click event, then use pop-up menu... '''
        if event.button == 3:
            self.OnRightClick(event)
            return

        ''' ...otherwise select item
            ---
            Functor to find nearest value in sorted list
            ---
            HR 4/3/20 THIS SHOULD BE REWRITTEN COMPLETELY TO USE MPL PICKER/ARTIST FUNCTIONALITY
            HR 01/21 NO, PICKER/ARTIST NOT SUITABLE '''
        def get_nearest(value, list_in):

            ''' First check if value beyond upper bound '''
            if value > list_in[-1]:
                print('case 1: beyond upper bound')
                answer = list_in[-1]

            else:
                for i,el in enumerate(list_in):
                    if value < el:

                        if i == 0:
                            ''' Then check if below lower bound '''
                            print('case 2: below lower bound')
                            answer = list_in[0]
                            break

                        else:
                            ''' All other cases: somewhere in between '''
                            print('case 3: intermediate')
                            if abs(value - el) < abs(value - list_in[i-1]):
                                answer = el
                            else:
                                answer = list_in[i-1]
                            break

            return answer

        ''' Check that click and release are in same position
            as FigureCanvas also allows dragging to move plot position '''
        if (self.click_pos) and event.xdata == self.click_pos[0] and event.ydata == self.click_pos[1]:

            ''' Get nearest y value (same as lattice level) '''
            # y_list = self.assembly.levels_p_sorted[:]
            y_list = sorted(list(plot_obj.S_p))
            if not y_list:
                print('No nodes found; aborting...')
                return
            # # Must prepend lattice level of single part to list
            # y_list.insert(0, self.assembly.part_level)
            # y_list.insert(0, plot_obj.part_level)
            y_  = get_nearest(event.ydata, y_list)
            print('y_list = ', y_list)
            print('y_     = ', y_)

            ''' Get nearest x value within known y level '''
            # x_dict = {self.assembly.nodes[el]['x']:el for el in self.assembly.nodes if self.assembly.nodes[el]['n_p'] == y_}
            # x_all  = self.assembly.levels_dict[y_]
            # x_dict = {self.assembly.nodes[el]['x']:el for el in x_all}
            x_all  = [node for node in plot_obj.levels_map[y_]]
            x_dict = {plot_obj.pos[node][0]:node for node in x_all}
            x_list = sorted([k for k in x_dict])
            if not x_list:
                print('No nodes found; aborting...')
                return
            x_  = get_nearest(event.xdata, x_list)
            print('x_list = ', x_list, '\n')
            print('x_dict = ', x_dict, '\n')
            print('x_     = ', x_, '\n')

            ''' Get nearest node '''
            node = x_dict[x_]

            print('Nearest node: x = %f, y = %f; node ID: %i\n' %
                  (x_, y_, node))



            ''' ---------------------------------------------------------- '''
            ''' HR 1/6/20 Added calculation of distance nearest node + tolerance
                If outside tolerance, ignore nodes
                and generate point on nearest line instead
                then unrank and generate alternative assembly '''

            x_dist = event.xdata - x_
            y_dist = event.ydata - y_
            dist = np.sqrt(x_dist**2 + y_dist**2)

            print('x_dist = %f, y_dist = %f, dist = %f' % (x_dist, y_dist, dist))

            ''' If too far from any node, get alternative assembly by unranking position '''
            if dist > picker_tol:
                print('Outside tolerance, getting position on nearest line')

                # list_ = [el for el in range(len(plot_obj.leaves)+1)]
                # y__ = get_nearest(event.ydata, list_)
                return

            print('Inside tolerance, (de)selecting nearest node')

            ''' ---------------------------------------------------------- '''



            ''' ------------------------------------
            HR 25/11/21 New GUI update functionality
            '''
            ''' Get already-selected items in active assembly '''
            active = self.assembly.assembly_id
            latt = self._assembly_manager._lattice

            ''' Check if node is in active assembly; if not, veto and return '''
            if active in latt.nodes[node]:
                print('Node in active assembly: de/selecting...')
                ID = latt.nodes[node][active]
            else:
                print('Node not in active assembly; returning')
                return

            ''' Get selected items in old state, OS '''
            OS = set(self.selected_items)

            ''' Get selections in new state, NS '''
            NS = self.get_NS(OS, [ID], retain = True, select_all_children = self.SELECT_ALL_CHILDREN)

            ''' Get changing items '''
            results = self.get_changes(OS, NS)
            TS = results[0]
            TU = results[1]

            ''' Update GUI globally '''
            self.update_GUI(OS, NS, TS, TU)
            ''' ------------------------------------ '''



    def UpdateSelectedNodes(self, called_by = None):

        # if called_by:
        #     print('UpdateSelectedNodes called by', called_by)

        print('UpdateSelectedNodes called by', called_by)

        _id = self.assembly.assembly_id
        to_select = self.selected_items
        # to_unselect = [el for el in self.assembly.nodes if el not in to_select]

        # self._assembly_manager.update_colours_selected(_id, selected = [], to_select = to_select, to_unselect = to_unselect)
        self._assembly_manager.update_colours_selected(_id, selected = [], to_select = to_select, called_by = "UpdateSelectedNodes")

        self.DoDraw('UpdateSelectedNodes')



    # def UpdateListSelections(self, node, select = True):

    #     ''' Select/deselect parts list item
    #         With "select = True", SelectItem toggles state if multiple selections (ctc.TR_MULTIPLE) enabled
    #             https://wxpython.org/Phoenix/docs/html/wx.lib.agw.customtreectrl.CustomTreeCtrl.html '''
    #     self._page.partTree_ctc.SelectItem(self._page.ctc_dict[node], select = select)



    # def UpdateToggledImages(self):

    #     for id_, button in self._page.button_dict.items():
    #         button.SetValue(False)

    #     selected_items = self.selected_items

    #     for id_ in selected_items:
    #         if id_ in self._page.button_dict:
    #             button = self._page.button_dict[id_]
    #             button.SetValue(True)
    #         else:
    #             pass



    def OnTreeCtrlChanged(self):

        print('Running OnTreeCtrlChanged')
        # Remake parts list and lattice
        # HR 17/02/2020 CAN BE IMPROVED SO ONLY AFFECTED CTC AND LATTICE ITEMS MODIFIED
        self.DisplayPartsList()
        self.DisplayLattice(called_by = 'OnTreeCtrlChanged')



    def OnAssemble(self, event = None):

        selected_items = self.selected_items

        ''' Check selected items are present and suitable '''
        if (len(selected_items) <= 1):
            print('No or one item(s) selected')
            return

        page = self._notebook.GetPage(self._notebook.GetSelection())
        assembly_id = self._notebook_manager[page]
        parent = self._assembly_manager.assemble_in_lattice(assembly_id, selected_items)
        if not parent:
            print('Could not assemble')
            return

        ''' Propagate changes '''
        self.ClearGUIItems()
        self.OnTreeCtrlChanged()
        self.Update3DView()



    def OnFlatten(self, event = None):

        selected_items = self.selected_items

        ''' Check selected items are present and suitable '''
        if not selected_items:
            print('No items selected')
            return

        if len(selected_items) == 1:
            node = selected_items[-1]
        else:
            print('Cannot flatten: no/more than one item(s) selected')
            return

        page = self._notebook.GetPage(self._notebook.GetSelection())
        assembly_id = self._notebook_manager[page]
        done = self._assembly_manager.flatten_in_lattice(assembly_id, node)
        if not done:
            print('Could not flatten')
            return

        ''' Propagate changes '''
        self.ClearGUIItems()
        self.OnTreeCtrlChanged()



    def OnDisaggregate(self, event = None):

        selected_items = self.selected_items

        ''' Check selected items are present and suitable '''
        if not selected_items:
            print('No items selected')
            return

        if len(selected_items) == 1:
            node = selected_items[-1]
        else:
            print('Cannot disaggregate: no/more than one item(s) selected')
            return

        page = self._notebook.GetPage(self._notebook.GetSelection())
        assembly_id = self._notebook_manager[page]
        new_nodes = self._assembly_manager.disaggregate_in_lattice(assembly_id, node)
        if not new_nodes:
            print('Could not disaggregate')
            return

        ''' Propagate changes '''
        self.ClearGUIItems()
        self.OnTreeCtrlChanged()
        self.Update3DView()



    def OnAggregate(self, event = None):

        selected_items = self.selected_items

        ''' Check selected items are present and suitable '''
        if not selected_items:
            print('No items selected')
            return

        if len(selected_items) == 1:
            node = selected_items[-1]
        else:
            print('Cannot aggregate: no/more than one item(s) selected')
            return

        page = self._notebook.GetPage(self._notebook.GetSelection())
        assembly_id = self._notebook_manager[page]
        removed_nodes = self._assembly_manager.aggregate_in_lattice(assembly_id, node)
        if not removed_nodes:
            print('Could not aggregate')
            return

        ''' Propagate changes '''
        self.ClearGUIItems()
        self.OnTreeCtrlChanged()
        self.Update3DView()



    def OnAddNode(self, event = None):

        selected_items = self.selected_items

        ''' Check selected items are present and suitable '''
        if not selected_items:
            print('No items selected')
            return

        if len(selected_items) == 1:
            node = selected_items[-1]
        else:
            print('Cannot add node: no/more than one item(s) selected')
            return

        page = self._notebook.GetPage(self._notebook.GetSelection())
        assembly_id = self._notebook_manager[page]
        new_node = self._assembly_manager.add_node_in_lattice(assembly_id, node)
        if not new_node:
            print('Could not add node')
            return

        ''' Propagate changes '''
        self.ClearGUIItems()
        self.OnTreeCtrlChanged()
        self.Update3DView()



    def OnRemoveNode(self, event = None):

        selected_items = self.selected_items

        ''' Check selected items are present and suitable '''
        if not selected_items:
            print('No items selected')
            return

        ''' Further checks '''
        if len(selected_items) >= 1:
            print('Selected item(s) to remove:\n')
            for node in selected_items:
                print('ID = ', node)
        else:
            print('Cannot remove: no items selected\n')
            return

        ''' Check root is not present in selected items '''
        root = self.assembly.get_root()
        if root in selected_items:
            if len(selected_items) == 1:
                print('Cannot remove root')
                return
            else:
                print('Cannot remove root; removing other selected nodes')
                selected_items.remove(root)

        page = self._notebook.GetPage(self._notebook.GetSelection())
        assembly_id = self._notebook_manager[page]
        for node in selected_items:
            try:
                self._assembly_manager.remove_node_in_lattice(assembly_id, node)
            except:
                print('Could not remove node ', node, ' as not present; may have been removed already')


        ''' Propagate changes '''
        self.ClearGUIItems()
        self.OnTreeCtrlChanged()
        self.Update3DView()



    def OnHideMode(self, event = None):

        selected_items = self.selected_items

        ''' Check selected items are present and suitable '''
        if not selected_items:
            print('No items selected')
            return
        elif len(selected_items) > 1:
            print('Cannot hide/uhide: more than one node selected\n')
            return

        node = selected_items[0]
        print('ID of selected item to hide/unhide: \n', node)

        ''' Create/toggle hide mode of node '''
        node_dict = self.assembly.nodes[selected_items[0]]
        if 'hide' not in node_dict:
            print('Creating hide tag and setting true')
            node_dict['hide'] = True
        else:
            if node_dict['hide']:
                print('Hide tag present, setting to false')
                node_dict['hide'] = False
            else:
                print('Hide tag present, setting to true')
                node_dict['hide'] = True

        ''' Grey out/ungrey in parts view '''
        ctc_item = self._page.ctc_dict[node]
        if node_dict['hide']:
            colour = wx.Colour('GREY')
        else:
            colour = wx.Colour('BLACK')
        ctc_attr = ctc.TreeItemAttr(colText = colour)
        ctc_item.SetAttributes(ctc_attr)

        self.Update3DView()



    def sort_check(self):

        ''' Check only one non-part item selected '''
        if not self.assembly.nodes:
            print('No assembly present')
            return

        if len(self._page.partTree_ctc.GetSelections()) != 1:
            print('No or more than one item(s) selected')
            return

        item = self._page.partTree_ctc.GetSelection()
        if not item.HasChildren():
            print('Item is leaf node, cannot sort')
            return

        children_count = item.GetChildrenCount(recursively = False)
        if not children_count > 1:
            print('Cannot sort: item has single child')
            return

        '''' If all checks above passed... '''
        return True



    def OnSortMode(self, event):

        if not self.sort_check():
            return

        item = self._page.partTree_ctc.GetSelection()

        ''' Toggle sort mode, then sort '''
        if self._page.partTree_ctc.alphabetical:
            self._page.partTree_ctc.alphabetical = False
        else:
            self._page.partTree_ctc.alphabetical = True
        self._page.partTree_ctc.SortChildren(item)



    def OnSortReverse(self, event):

        if not self.sort_check():
            return

        item = self._page.partTree_ctc.GetSelection()

        ''' Toggle sort mode, then sort '''
        if self._page.partTree_ctc.reverse_sort:
            self._page.partTree_ctc.reverse_sort = False
        else:
            self._page.partTree_ctc.reverse_sort = True
        self._page.partTree_ctc.SortChildren(item)



    def OnSortAlpha(self, event = None):

        ''' Sort children of selected items alphabetically '''
        item = self._page.partTree_ctc.GetSelection()
        self._page.partTree_ctc.alphabetical = True
        self._page.partTree_ctc.SortChildren(item)



    def OnSortByID(self, event = None):

        ''' Sort children of selected item by ID '''
        item = self._page.partTree_ctc.GetSelection()

        ''' First reset "sort_id" as can be changed by drap and drop elsewhere
            ---
            MUST create shallow copy here (".copy()") to avoid strange behaviour
            According to ctc docs, "It is advised not to change this list
            [i.e. returned list] and to make a copy before calling
            other tree methods as they could change the contents of the list." '''
        children = item.GetChildren().copy()
        for child in children:
            data = self._page.partTree_ctc.GetPyData(child)
            data['sort_id'] = data['id_']

        self._page.partTree_ctc.alphabetical = False
        self._page.partTree_ctc.SortChildren(item)



    def OnAddNodeData(self, event = None):

        ''' HR 12/10/21 To add user-defined data to node via dialog '''
        print('Adding node data...')
        dlg = DataEntryDialog(parent = self)
        dlg.ShowModal()
        if dlg.result_field and dlg.result_value:
            print("Field:value = " + dlg.result_field + ':' + dlg.result_value + "\n")
        else:
            print("No data entered\n")
            return
        # dlg.Destroy()

        ''' Add data to node '''
        ass = self.assembly
        node = self.selected_items[0]
        if 'data' in ass.nodes[node]:
            print('Data dict already present; adding')
            ass.nodes[node]['data'][dlg.result_field] = dlg.result_value
        else:
            print('Data dict not present; creating and adding')
            ass.nodes[node]['data'] = {dlg.result_field: dlg.result_value}



    # def OnViewNodeData(self, event = None):

    #     ''' HR 12/10/21 To view all node data '''
    #     print('Viewing node data...')



    def OnTreeDrag(self, event):

        ''' Drag and drop events are vetoed by default '''
        event.Allow()
        self.tree_drag_item = event.GetItem()
        id_ = self._page.ctc_dict_inv[event.GetItem()]
        print('ID of drag item = ', id_)
        self.tree_drag_id = id_



    def OnTreeDrop(self, event):

        ''' Allow event: drag and drop events vetoed by WX by default '''
        event.Allow()

        drop_item = event.GetItem()
        id_ = self._page.ctc_dict_inv[drop_item]
        print('ID of item at drop point = ', id_)

        drag_parent = self.tree_drag_item.GetParent()
        drop_parent = drop_item.GetParent()

        ''' Check if root node involved; return if so '''
        if (not drag_parent) or (not drop_parent):
            print('Drag or drop item is root: cannot proceed')
            return


        '''
        CASE 1: DRAG AND DROP ITEMS HAVE THE SAME PARENT: MODIFY SORT ORDER

        If so, prepare sibling items by changing "sort_id" in part tree data

        HR 17/03/20: WHOLE SECTION NEEDS REWRITING TO BE SHORTER AND MORE EFFICIENT
        PROBABLY VIA A FEW LIST OPERATIONS
        '''
        if drop_parent == drag_parent:

            sort_id = 1
            (child, cookie) = self._page.partTree_ctc.GetFirstChild(drop_parent)

            ''' If drop item found, slip drag item into its place '''
            if child == drop_item:
                self._page.partTree_ctc.GetPyData(self.tree_drag_item)['sort_id'] = sort_id
                sort_id += 1
            elif child == self.tree_drag_item:
                pass
            else:
                self._page.partTree_ctc.GetPyData(child)['sort_id'] = sort_id
                sort_id += 1

            child = self._page.partTree_ctc.GetNextSibling(child)
            while child:

                ''' If drop item found, slip drag item into its place '''
                if child == drop_item:
                    self._page.partTree_ctc.GetPyData(self.tree_drag_item)['sort_id'] = sort_id
                    sort_id += 1
                elif child == self.tree_drag_item:
                    pass
                else:
                    self._page.partTree_ctc.GetPyData(child)['sort_id'] = sort_id
                    sort_id += 1
                child = self._page.partTree_ctc.GetNextSibling(child)

            ''' Re-sort, then return to avoid redrawing part tree otherwise '''
            self._page.partTree_ctc.alphabetical = False
            self._page.partTree_ctc.SortChildren(drop_parent)
            return

        '''
        CASE 2: DRAG AND DROP ITEMS DO NOT HAVE THE SAME PARENT: SIMPLE MOVE

        Drop item becomes sibling; unless it's root, then it becomes parent
        '''
        if self.assembly.get_parent(id_):
            parent = self.assembly.get_parent(id_)
        else:
            parent = id_

        ''' HR 15/01/21
            Move node via assembly manager (was assembly-specific)
            No need to check if present in lattice, as manager checks during
            all node and edge removal operations '''
        page = self._notebook.GetPage(self._notebook.GetSelection())
        assembly_id = self._notebook_manager[page]
        self._assembly_manager.move_node_in_lattice(assembly_id, self.tree_drag_id, parent)

        ''' Propagate changes '''
        self.ClearGUIItems()
        self.OnTreeCtrlChanged()



    def OnTreeLabelEditEnd(self, event):
        text_before = event.GetItem().GetText()
        wx.CallAfter(self.AfterTreeLabelEdit, event, text_before)
        event.Skip()



    def AfterTreeLabelEdit(self, event, text_before):
        item = event.GetItem()
        text = item.GetText()
        if text_before != text:
            id_ = self._page.ctc_dict_inv[item]
            self.assembly.nodes[id_]['screen_name'] = text
            print('Text changed to:',text)



    def ClearGUIItems(self):
        ''' Destroy all button objects '''
        for button_ in self._page.button_dict:
            obj = self._page.button_dict[button_]
            obj.Destroy()

        ''' Clear all relevant lists/dictionaries '''
        self._page.ctc_dict.clear()
        self._page.ctc_dict_inv.clear()

        self._page.button_dict.clear()
        self._page.button_dict_inv.clear()
        self._page.button_img_dict.clear()



    def OnSettings(self, event):
        self.AddText('Settings button pressed')



    def OnAbout(self, event):
        ''' Show program info '''
        abt_text = """StrEmbed-6-1: A user interface for manipulation of design configurations\n
            Copyright (C) 2019-2022 Hugh Patrick Rice\n
            This research is supported by the UK Engineering and Physical Sciences
            Research Council (EPSRC) under grant number EP/S016406/1.\n
            All code can be found here: https://github.com/paddy-r/StrEmbed-6-1,
            and bugs should be reported there or directly to the author at h.p.rice@leeds.ac.uk\n
            This program is free software: you can redistribute it and/or modify
            it under the terms of the GNU General Public License as published by
            the Free Software Foundation, either version 3 of the License, or
            (at your option) any later version.\n
            This program is distributed in the hope that it will be useful,
            but WITHOUT ANY WARRANTY; without even the implied warranty of
            MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
            GNU General Public License for more details.\n
            You should have received a copy of the GNU General Public License
            along with this program. If not, see <https://www.gnu.org/licenses/>."""

        abt = wx.MessageDialog(self, abt_text, 'About StrEmbed-6-1', wx.OK)
        ''' Show dialogue that stops process (modal) '''
        abt.ShowModal()
        abt.Destroy()



    def OnLineViewMode(self, event):
        ''' HR 28/10/21 To toggle lattice line view mode
            Default is to show all; toggle removes any unpopulated lines '''
        print('Line view toggled')
        latt = self._assembly_manager
        if latt.DO_ALL_LATTICE_LINES:
            latt.DO_ALL_LATTICE_LINES = False
        else:
            latt.DO_ALL_LATTICE_LINES = True
        ''' Redraw lattice'''
        self.DisplayLattice()



    def OnCommonSelectorMode(self, event = None):
        print('Common selector view mode toggled')
        if self.COMMON_SELECTOR_VIEW:
            self.COMMON_SELECTOR_VIEW = False
        else:
            self.COMMON_SELECTOR_VIEW = True



    def OnResize(self, event):
        ''' Display window size in status bar '''
        self.AddText("Window size = " + format(self.GetSize()))
        wx.CallAfter(self.AfterResize, event)
        event.Skip()



    def AfterResize(self, event = None):
        ''' HR 06/10/20 ISSUE: Button widths don't resize (although images do)
            when window is resized '''
        try:
            ''' Resize all images in selector view '''
            if self._page.file_open:
                ''' Get size of selector grid element '''
                for k, v in self._page.button_dict.items():
                    img = self._page.button_img_dict[k]
                    v.SetBitmap(wx.Bitmap(self.ScaleImage(img)))

                self._page.slct_panel.SetupScrolling(scrollToTop = False)
        except:
            pass



    def DoNothingDialog(self, event = None, text = 'Dialog', message = 'Dialog'):
        nowt = wx.MessageDialog(self, text, message, wx.OK)
        ''' Create modal dialogue that stops process '''
        nowt.ShowModal()
        nowt.Destroy()



    def OnNewAssembly(self, event = None):
        self.AddText("New assembly button pressed")
        self.MakeNewAssemblyPage()



    def MakeNewAssemblyPage(self, event = None):

        self.Freeze()
        print('Trying to make new assembly with new page...')

        ''' Create assembly object and add to NB manager '''
        new_id, new_assembly = self._assembly_manager.new_assembly()
        name = new_assembly.assembly_name
        page = NotebookPanel(self._notebook, new_id, border = self._border)
        self._notebook_manager[page] = new_id

        ''' Add tab with select = True, so EVT_NOTEBOOK_PAGE_CHANGED fires
            and relevant assembly is activated via OnNotebookPageChanged;
            "text = name" equivalent to SetPageText if done later
            e.g. in RenameAssembly '''
        self._notebook.AddPage(page, text = name, select = True)
        self._page = page

        self.setup_new_page(disable = True)
        self.Thaw()



    def OnDuplicateAssembly(self, event = None):
        self.AddText("Duplicate assembly button pressed")
        self.MakeDuplicateAssemblyPage()



    ''' HR 08/04/22 To account for successful deepcopy functionality;
                    see notes above "PickleSWIG" mixin at top '''
    def MakeDuplicateAssemblyPage(self, event = None, add_to_lattice = None):

        self.Freeze()
        print('Trying to create new assembly page...')

        ''' Duplicate assembly object and add to NB manager '''
        old_id = self.assembly.assembly_id
        new_id, new_assembly = self._assembly_manager.duplicate_assembly(old_id)
        name = new_assembly.assembly_name
        page = NotebookPanel(self._notebook, new_id, border = self._border)
        self._notebook_manager[page] = new_id

        ''' Add tab with select = True, so EVT_NOTEBOOK_PAGE_CHANGED fires
            and relevant assembly is activated via OnNotebookPageChanged;
            "text = name" equivalent to SetPageText if done later
            e.g. in RenameAssembly '''
        self._notebook.AddPage(page, text = name, select = True)
        self._page = page
        self.assembly = new_assembly

        self.setup_new_page(disable = False)
        self.Thaw()

        ''' Show parts list and lattice '''
        self.DisplayPartsList()

        ''' Do some tidying up '''

        ''' Clear selector window if necessary '''
        try:
            self._page.slct_sizer.Clear(True)
        except:
            print("Couldn't clear selector sizer")

        ''' Clear lattice plot if necessary '''
        try:
            self.latt_axes.clear()
        except:
            print("Couldn't clear lattice axes")

        ''' Old code redundant '''
        # if not add_to_lattice:
        #     add_to_lattice = self.ADD_TO_LATTICE_DEFAULT

        # ''' Duplicate to lattice '''
        # if add_to_lattice:
        #     self._assembly_manager.DuplicateInLattice(old_id, new_id)

        ''' HR 05/07/22 Allow user to decide whether to add duplicated assembly to lattice '''
        ''' Create recon spec dialog '''
        with DecisionDialog(parent = self,
                            message = 'Assembly duplication dialog',
                            caption = 'OK to add duplicated assembly to lattice?') as dialog:
            if not dialog.ShowModal() == wx.ID_OK:
                print('Not adding duplicated assembly to lattice; returning...')
                return

        ''' Add assembly to lattice '''
        print('Duplicating assembly in lattice...')
        self._assembly_manager.DuplicateInLattice(old_id, new_id)
        print('Duplicated assembly in lattice; refreshing lattice and 3D views')

        ''' Display lattice and update 3D viewer '''
        self.DisplayLattice(set_pos = True, called_by = 'MakeDuplicateAssemblyPage')
        # self.Update3DView(selected_items = self.selected_items)
        self.Update3DView()



    ''' HR 11/04/22 To import pickled StepParse assembly '''
    def OnImportAssembly(self, event = None):
        self.AddText("Import assembly button pressed")
        self.MakeImportedAssemblyPage()



    def MakeImportedAssemblyPage(self, add_to_lattice = None):
        print('Running "OnImportAssembly')

        ''' Get file to import '''
        ext = self._assembly_manager.ASSEMBLY_EXTENSION_DEFAULT
        filename = self.GetFilename(dialog_text = "Import assembly", ender = [ext])
        if not filename:
            print('No filename given; returning')
            return

        ''' Load assembly '''
        try:
            id_imported, ass_imported = self._assembly_manager.import_assembly(filename)
            print('Done')
        except Exception as e:
            print('Could not import assembly, exception follows')
            print(e)
            return

        ''' Create new notebook tab, etc. '''
        self.Freeze()
        print('Trying to create new page for imported assembly...')

        name = ass_imported.assembly_name
        page = NotebookPanel(self._notebook, id_imported, border = self._border)
        self._notebook_manager[page] = id_imported

        ''' Add tab with select = True, so EVT_NOTEBOOK_PAGE_CHANGED fires
            and relevant assembly is activated via OnNotebookPageChanged;
            "text = name" equivalent to SetPageText if done later
            e.g. in RenameAssembly '''
        self._notebook.AddPage(page, text = name, select = True)
        self._page = page
        self.assembly = ass_imported

        self.setup_new_page(disable = False)
        self.Thaw()

        ''' Show parts list and lattice '''
        self.DisplayPartsList()

        ''' Do some tidying up '''

        ''' Clear selector window if necessary '''
        try:
            self._page.slct_sizer.Clear(True)
        except:
            print("Couldn't clear selector sizer")

        ''' Clear lattice plot if necessary '''
        try:
            self.latt_axes.clear()
        except:
            print("Couldn't clear lattice axes")

        ''' Older code redundant '''
        # ''' Add to lattice '''
        # if not add_to_lattice:
        #     add_to_lattice = self.ADD_TO_LATTICE_DEFAULT

        # if add_to_lattice:
        #     self._assembly_manager.AddToLattice(id_imported)

        ''' HR 05/07/22 Allow user to decide whether to add imported assembly to lattice '''

        ''' If manager is empty, do simple add '''
        if len(self._assembly_manager._assemblies_in_lattice) == 0:
            with DecisionDialog(parent = self,
                                message = 'Assembly import dialog',
                                caption = 'OK to add imported assembly to lattice?') as dialog:
                if dialog.ShowModal() == wx.ID_OK:
                    print('Adding assembly to lattice...')
                    self._assembly_manager.AddToLatticeSimple(id_imported)
                else:
                    print('Not adding imported assembly to lattice; returning...')

        else:
            self.OnRecon()

        print('Added assembly lattice; refreshing lattice and 3D views')



        ''' Display lattice and update 3D viewer '''
        self.DisplayLattice(set_pos = True, called_by = 'MakeImportedAssemblyPage')
        # self.Update3DView(selected_items = self.selected_items)
        self.Update3DView()



    ''' HR 08/04/22 Separated from MakeNewAssemblyPage as now common with DuplicateAssemblyPage '''
    def setup_new_page(self, disable = True):
        ''' No need to do this, as caught by "OnNotebookPageChanged" '''
        # self.assembly = self._assembly_manager._mgr[new_id]

        ''' All tab-specific bindings '''
        self._page.partTree_ctc.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        self._page.partTree_ctc.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnTreeDrag)
        self._page.partTree_ctc.Bind(wx.EVT_TREE_END_DRAG, self.OnTreeDrop)
        self._page.partTree_ctc.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnTreeLabelEditEnd)

        self._page.Bind(ctc.EVT_TREE_ITEM_CHECKED, self.TreeItemChecked)
        self._page.Bind(ctc.EVT_TREE_SEL_CHANGING, self.TreeItemSelectionChanging)
        self._page.Bind(ctc.EVT_TREE_SEL_CHANGED, self.TreeItemSelectionChanged)

        self._page.Bind(wx.EVT_TOGGLEBUTTON, self.ImageToggled)

        self._page.occ_panel.Bind(wx.EVT_LEFT_UP, self.OnLeftUp_3D)

        if disable:
            ''' Disable until file loaded '''
            self._page.Disable()



    ''' HR 12/04/22 Pass to "save_assembly" method '''
    def OnExportAssembly(self, event = None):
        print('Running "OnSaveAssembly"')
        self.export_assembly()



    ''' HR To save active assembly via pickle '''
    def export_assembly(self):
        assembly_id = self.assembly.assembly_id
        if not self.assembly.file_loaded:
            print('No file loaded into active assembly; not exporting')
            return None

        ''' Construct default path and filename for file dialog;
            filename is a timestamp '''
        defaultDir = os.getcwd()
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        defaultFile = "assembly_" + timestamp + '.' + self._assembly_manager.ASSEMBLY_EXTENSION_DEFAULT

        ''' Open file dialog and populate with default path and filename '''
        dialog_text = 'Export assembly to file'
        fileDialog = wx.FileDialog(parent = self,
                                   message = dialog_text,
                                   defaultDir = defaultDir,
                                   defaultFile = defaultFile,
                                   style = wx.FD_SAVE)
        fileDialog.ShowModal()
        filename = fileDialog.GetPath()
        fileDialog.Destroy()

        ''' Pass to manager to actually save '''
        self._assembly_manager.save_assembly(filename, assembly_id)
        return filename



    ''' HR 02/11/21 To grab IDs of nodes of all checked items in parts view '''
    @property
    def checked_nodes(self):
        page = self._page
        # _id = self._notebook_manager[page]
        # assembly = self._assembly_manager._mgr[_id]

        checked_items = []

        for node,item in page.ctc_dict.items():
            if item.IsChecked():
                checked_items.append(node)

        return checked_items



    def OnNotebookPageChanging(self, event = None):
        print('Notebook page changing')

        ''' Get active assembly before notebook page is changed
            and pass to CallAfter '''
        selection = self._notebook.GetSelection()
        ''' If selection not found (b/c doesn't exist) then pass None '''
        if selection == wx.NOT_FOUND:
            print('No previous page found')
            id_old = None
            checked_old = []
        else:
            page = self._notebook.GetPage(selection)
            id_old = self._notebook_manager[page]
            if self.COMMON_SELECTOR_VIEW:
                checked_old = self.checked_nodes
            else:
                checked_old = []

        print('Checked nodes in old page: ', checked_old)

        wx.CallAfter(self.OnNotebookPageChanged, id_old, event, checked_old = checked_old)
        event.Skip()



    def OnNotebookPageChanged(self, id_old, event, checked_old = []):
        print('Notebook page changed')

        selection = self._notebook.GetSelection()
        print('Notebook tab index: ', selection)
        page = self._notebook.GetPage(selection)
        print('Notebook tab name: ', page.name)

        text = 'Active notebook tab: ' + self._notebook.GetPageText(selection)
        self.AddText(text)

        ''' Activate window (here NotebookPanel) and assembly '''
        _id = self._notebook_manager[page]
        self.assembly = self._assembly_manager._mgr[_id]
        self._page = page
        print('Assembly ID: ', _id)

        ''' Switch to activated assembly in lattive view '''
        if not self._page.file_open:
            self.DisplayLattice(called_by = 'OnNotebookPageChanged')
        else:
            if not id_old:
                to_deactivate = []
            else:
                to_deactivate = [id_old]
            to_select = self.selected_items

            self._assembly_manager.update_colours_active(to_activate = [_id], to_deactivate = to_deactivate)
            # self._assembly_manager.update_colours_selected(_id, to_select = to_select, to_unselect = to_unselect)
            self._assembly_manager.update_colours_selected(_id, to_select = to_select, called_by = "OnNBPageChanged")
            self.DoDraw(called_by = 'OnNotebookPageChanged')



        ''' HR 02/11/12 To check in parts view + show in selector view
            all items checked/shown in previous page, if present in lattice '''
        ''' 1. Get all lattice nodes corresponding to checked items in old page '''
        if self.COMMON_SELECTOR_VIEW:
            latt_nodes = []
            for node_old in checked_old:
                latt_node = self._assembly_manager.get_master_node(id_old, node_old)
                if latt_node:
                    latt_nodes.append(latt_node)
            print('Lattice IDs of checked nodes: ', latt_nodes)
            ''' 2. Get all nodes and ctc items in current page, if present '''
            checked_new = []
            for latt_node in latt_nodes:
                latt_dict = self._assembly_manager._lattice.nodes[latt_node]
                print('Assembly ID, latt dict: ', _id, latt_dict)
                if _id in latt_dict:
                    checked_new.append(latt_dict[_id])
            print('Nodes in new page: ', checked_new)
            ''' 3. Uncheck all ctc items '''
            self.uncheck_all()
            ''' 4. Check ctc items '''
            self.check_items(checked_new)
            ''' 5. Show all images in selector view '''
            ''' Happens automatically, as checking caught by "TreeItemChecked" '''

        event.Skip()



    def AddText(self, msg):
        self.statbar.SetStatusText(msg)
        print(msg)



    # def remove_saved_images(self):
    #     ''' Remove all saved images '''
    #     print('Trying to remove saved images...')
    #     try:
    #         shutil.rmtree(self.im_path)
    #         print('Done')
    #     except:
    #         print('Could not delete saved images: none may be present')



    def OnExit(self, event):
        # self.remove_saved_images()
        event.Skip()



if __name__ == '__main__':
    # app = wit.InspectableApp()
    app = wx.App()
    frame = MainWindow()

    frame.Show()
    # frame.SetTransparent(220)
    frame.Maximize()

    app.MainLoop()