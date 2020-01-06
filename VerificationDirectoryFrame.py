#----------------------------------------------------------------------
# VerificationDirectoryFrame
''' author: Steve Nguyen '''
# date: 10/02/2013
# email: Steven@seametrics.com
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
# frame handles the directory for VERIFICATION frames ONLY. DO NOT include
# engineering frames here.
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''

    1   2013/10/02  JTP     (1) Initial Release

'''
#----------------------------------------------------------------------
# Modules
#----------------------------------------------------------------------
import wx
import CalibrationFrame
import MultiCalFrame
import HistoryFrame
import DirectoryFrame
import QuickMeterTestFrame
import SPCFrame
import Images.throbImages as throbImages
import wx.lib.throbber as throb
from time import sleep as sleep
from Modules.myHeader import *
import Modules.myFlowMeters as myFlowMeters
import Modules.myUtil as myUtil
import Modules.myDateTime as myDateTime
import Modules.myFile as myFile
import datetime
from time import clock as clock

#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------
class Frame(DirectoryFrame.Frame):
    def __init__(self, parent, main):
        #----------------------------------
        # Ctrl Id's
        #----------------------------------
        DIRECTORY_TEXT_ID       = wx.NewId()
        
        #----------------------------------
        # Ctrl Initialization
        #----------------------------------
        DirectoryFrame.Frame.__init__(self, parent, main)
        self.Maximize() # keep maximize here to reduce screen flicker
                       
        self.PE075Button = wx.Button(label='PE075', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.PE075Button.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'MS Shell Dlg 2'))
        self.PE038Button = wx.Button(label='PE038', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.PE038Button.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'MS Shell Dlg 2'))
        
        self.DirectoryLabel = wx.StaticText(id=DIRECTORY_TEXT_ID,label='VERIFICATION', parent=self.panel, size=wx.Size(150, 25), style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.DirectoryLabel.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))
        
        self.timer = wx.Timer(owner = self)
        #----------------------------------
        #  Event Definitions
        #----------------------------------
        self.PE075Button.Bind(wx.EVT_BUTTON, self.OnPE075Button) 
        self.PE038Button.Bind(wx.EVT_BUTTON, self.OnPE038Button) 
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        #----------------------------------
        # Sizers
        #----------------------------------
        '''Sizer layout'''
        # frame
        # Panel
        # -------------------------------------------
        # |   |-------------|  |-------------|     1|
        # |   |            2|  |            3|      |  
        # |   |             |  |             |      |
        # |   |             |  |             |      |
        # |   |             |  |             |      |
        # |   |             |  |             |      |
        # |   |PE075Button  |  |             |      |
        # |   |PE038Button  |  |             |      |
        # |   |ExitButton   |  |             |      |
        # |   |             |  |             |      |
        # |   |-------------|  |-------------|      |
        # ------------------------------------------|
        # status bar
        #
        self.sizer2.Add(self.PE075Button, 0, border=BUTTON_SPACING, flag=wx.ALL | wx.ALIGN_LEFT)
        self.sizer2.Add(self.PE038Button, 0, border=BUTTON_SPACING, flag=wx.ALL | wx.ALIGN_LEFT)
        self.sizer2.Add(self.DirectoryLabel, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.panel.Layout()
        #----------------------------------
        # Variable Initialization
        #----------------------------------
        self.wait_time = clock()+60*30      
        #----------------------------------
        # GUI Initialization
        #----------------------------------
        self.PE075Button.Enable(True)
        self.PE038Button.Enable(True)
        self.Layout()

    #----------------------------------
    # GUI Event Handler Methods
    #----------------------------------
    def OnTimer(self, evy):
        self.wait_time -= clock()
        t = int(self.wait_time/60.0)
        self.dlg.SetLabel('System warm-up: %d min'%t)
        self.dlg.Layout()
        if t<=0:
            self.timer.Stop()
            if self.dlg:
                self.dlg.Destroy()
            self.panel.Enable(True)
                
    def OnLFSysTestButton(self):
        # grab the correct meter class from the flow meter class dictionary
        mut = myFlowMeters.PE102_REV_D()
        mut.SetIdentity038()
        
        self.page = self.DestroyOpenPage()
        self.page = SPCFrame.Frame(self,
                                   mut,
                                   self.ref3,
                                   self.ref3,
                                   LF_SYSTEM)
        self.page.Show()
        # use call later here to allow time for
        # OPC server to process data change
        # must be called here or AFTER __init__() method
        # of page since page must exist before invoking 
        # SetSystemType()
        wx.CallLater(500, self.parent.SetSystemType)
        
    def OnHFSysTestButton(self):
        # grab the correct meter class from the flow meter class dictionary
        mut = myFlowMeters.PE102_REV_D()
        mut.SetIdentity075()
        
        self.page = self.DestroyOpenPage()
        self.page = SPCFrame.Frame(self,
                                   mut,
                                   self.ref1,
                                   self.ref2,
                                   HF_SYSTEM)
        self.page.Show()
        # use call later here to allow time for
        # OPC server to process data change
        # must be called here or AFTER __init__() method
        # of page since page must exist before invoking 
        # SetSystemType()
        wx.CallLater(500, self.parent.SetSystemType)
        
    def OnPE075Button(self, event):        
        #----------------------------------
        # Run System Test on demand
        #----------------------------------        
        self.OnHFSysTestButton()
        return

    def OnPE038Button(self, event):
        #----------------------------------
        # Run System Test on demand
        #----------------------------------        
        self.OnLFSysTestButton()
        return
            

