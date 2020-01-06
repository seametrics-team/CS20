#----------------------------------------------------------------------
# PE Calibration System HMI Program
''' author: Jeff Peery '''
# date: 11/29/2007
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# for variable references, program diagrams, mechanical and electrical
# diagrams of the PE calibration system, consult 'PE Cal System Schematics.vsd'.
# 'PE Cal System Schematics.vsd' is a Microsoft Viso program. 
# 
# This information may also be located within the PE calibration system \
# design binder in hard copy form.
#
# This frame is a subclass of the DirectoryFrame (i.e., its methods and
# attributes and properties are inherited from the DirectoryFrame). This
# frame handles the directoy for ENGINEERING frames ONLY. DO NOT include
# production frames here.
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
"""
 1.00   14/10/15    SPN     Added Custom Multipoint (multical2) button
"""
#----------------------------------------------------------------------
# Modules
#----------------------------------------------------------------------
import wx
import CalibrationFrame
import MultiCalFrame
import MultiCalFrame2
import HistoryFrame
import DirectoryFrame
import ManualTestFrame
import Images.throbImages as throbImages
import wx.lib.throbber as throb
from time import sleep as sleep
from Modules.myHeader import *
import Modules.myFlowMeters as myFlowMeters
import Modules.myUtil as myUtil

#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------
class Frame(DirectoryFrame.Frame):
    def __init__(self, parent, main):        
        #----------------------------------
        # Ctrl Id's
        #----------------------------------
        FRAME_ID            = wx.NewId()
        PANEL_ID            = wx.NewId()
        THROB_ID            = wx.NewId()
        TEXT_ID             = wx.NewId() 
        HIST_BUTTON_ID      = wx.NewId()  
        MANUAL_BUTTON_ID    = wx.NewId()
        MULTI_BUTTON_ID     = wx.NewId()
        MULTI2_BUTTON_ID     = wx.NewId()
        #----------------------------------------------------
        #----------------------------------
        # Ctrl Initialization
        #----------------------------------
        DirectoryFrame.Frame.__init__(self, parent, main)
        self.Maximize() # keep maximize here to reduce screen flicker
                           
        self.HistButton = wx.Button(id=HIST_BUTTON_ID, label='History', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.HistButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'MS Shell Dlg 2'))

        self.ManualButton = wx.Button(id=MANUAL_BUTTON_ID, label='Manual', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.ManualButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'MS Shell Dlg 2'))

        self.MultiButton = wx.Button(id=MULTI_BUTTON_ID, label='Auto', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.MultiButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'MS Shell Dlg 2'))

        self.Multi2Button = wx.Button(id=MULTI2_BUTTON_ID, label='Custom', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.Multi2Button.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'MS Shell Dlg 2'))
        #----------------------------------
        #  Event Definitions
        #----------------------------------
        self.HistButton.Bind(wx.EVT_BUTTON, self.OnHistButton)
        self.ManualButton.Bind(wx.EVT_BUTTON, self.OnManualButton)
        self.MultiButton.Bind(wx.EVT_BUTTON, self.OnMultiButton)
        self.Multi2Button.Bind(wx.EVT_BUTTON, self.OnMulti2Button)   
        #----------------------------------
        # Sizers
        #----------------------------------
        '''Sizer layout'''
        # frame
        # Panel
        # -------------------------------------------
        # |   |-------------|                      1|
        # |   |            2|                       |  
        # |   |             |                       |
        # |   |MultiButton  |                       |
        # |   |Multi2Button  |                       |
        # |   |HistButton   |                       |
        # |   |ManualButton |                       |
        # |   |ExitButton   |                       |
        # |   |             |                       |
        # |   |-------------|                       |
        # ------------------------------------------|
        # status bar
        #
        self.sizer2.Add(self.ManualButton, 0, border=BUTTON_SPACING, flag=wx.ALL | wx.ALIGN_RIGHT)
        self.sizer2.Add(self.MultiButton, 0, border=BUTTON_SPACING, flag=wx.ALL | wx.ALIGN_RIGHT)
        self.sizer2.Add(self.Multi2Button, 0, border=BUTTON_SPACING, flag=wx.ALL | wx.ALIGN_RIGHT)
        self.sizer2.Add(self.HistButton, 0, border=BUTTON_SPACING, flag=wx.ALL | wx.ALIGN_RIGHT)
        self.panel.Layout()
        #----------------------------------
        # Variable Initialization
        #----------------------------------
        
        #----------------------------------
        # GUI Initialization
        #----------------------------------
        self.HistButton.Enable(True)
        self.MultiButton.Enable(True)
        self.Multi2Button.Enable(True)
        self.Layout()
        
    #----------------------------------
    # GUI Event Handler Methods
    #----------------------------------        
    def OnHistButton(self, event):
        self.page = self.DestroyOpenPage()
        self.page = HistoryFrame.Frame(self)
        self.page.Show()

    def OnManualButton(self, event):
        self.page = self.DestroyOpenPage()
        self.page = ManualTestFrame.Frame(self,
                                        self.ref1,
                                        self.ref2)
        self.page.Show()
        
    def OnMultiButton(self, event):
        self.page = self.DestroyOpenPage()
        self.page = MultiCalFrame.Frame(self,
                                        self.ref1,
                                        self.ref2)
        self.page.Show()

    def OnMulti2Button(self, event):
        self.page = self.DestroyOpenPage()
        self.page = MultiCalFrame2.Frame(self,
                                        self.ref1,
                                        self.ref2)
        self.page.Show()
