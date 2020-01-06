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
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''
  1.03  2016/12/12  SPN     -Updated init method: incorporated SetCurvefitPoly method
  1.02  2014/09/16  SPN     Disable database save in OnExitButton method
  1.01  2014/05/09  SPN     Added SetRefID method to variable initializations
'''
#----------------------------------------------------------------------
# Modules
#----------------------------------------------------------------------
import wx
import CalibrationFrame
import MultiCalFrame
import HistoryFrame
import Images.throbImages as throbImages
import wx.lib.throbber as throb
from time import sleep as sleep
from Modules.myHeader import *
import Modules.myFlowMeters as myFlowMeters
import Modules.myUtil as myUtil

#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------
class Frame(wx.Frame):
    def __init__(self, parent, main):        
        #----------------------------------
        # Ctrl Id's
        #----------------------------------
        FRAME_ID        = wx.NewId()
        PANEL_ID        = wx.NewId()
        THROB_ID        = wx.NewId()
        TEXT_ID         = wx.NewId() 
        EXIT_BUTTON_ID  = wx.NewId()
        STATUS_BAR      = wx.NewId()
        #----------------------------------------------------
        #----------------------------------
        # Ctrl Initialization
        #----------------------------------

        if not TEST_MODE:
            wx.Frame.__init__(self, id=FRAME_ID, parent=parent, size=wx.Size(600, 400), style=0, title='Directory')
            self.Maximize() # keep maximize here to reduce screen flicker
        else:
            wx.Frame.__init__(self, id=FRAME_ID, parent=parent, size=wx.Size(600, 400), style=wx.DEFAULT_FRAME_STYLE, title='Directory')

        self.panel = wx.Panel(id=PANEL_ID, name='panel', parent=self, size=wx.Size(900, 600), style=wx.TAB_TRAVERSAL)
        self.panel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'MS Shell Dlg 2'))
                              
        self.ExitButton = wx.Button(id=EXIT_BUTTON_ID, label='Exit', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.ExitButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'MS Shell Dlg 2'))
        #----------------------------------
        #  Event Definitions
        #----------------------------------
        self.ExitButton.Bind(wx.EVT_BUTTON, self.OnExitButton)
        self.Bind(wx.EVT_CLOSE, self.OnExitButton)                
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
        # |   |ExitButton   |                       |
        # |   |             |                       |
        # |   |-------------|                       |
        # ------------------------------------------|
        # status bar
        #
        self.sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.sizer2 = wx.BoxSizer(orient=wx.VERTICAL)
        self.sizer3 = wx.BoxSizer(orient=wx.VERTICAL) 
        
        self.sizer.AddStretchSpacer(1)
        self.sizer.Add(self.sizer2, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add(self.sizer3, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.sizer.AddStretchSpacer(1)
        
        self.sizer2.Add(self.ExitButton, 0, border=BUTTON_SPACING, flag=wx.ALL | wx.ALIGN_RIGHT)
        
        self.statusBar = wx.StatusBar(id=STATUS_BAR, name='statusbar', parent=self, style=wx.ALWAYS_SHOW_SB)
        self.SetStatusBar(self.statusBar)
        
        self.panel.SetSizer(self.sizer)        
        #----------------------------------
        # Variable Initialization
        #-------------------------------OnPE013Button---
        # A page in from the main directory
        self.page = None
        # busy dialog
        self.busyDlg = None
        # parent module
        self.parent = main
        # database instance
        self.db = main.db
        # reference meter objects
        #
        # HF system FS flow reference
        self.ref1 = myFlowMeters.Reference()
        # HF system LS flow reference
        self.ref2 = myFlowMeters.Reference()
        # LF system FS flow reference
        self.ref3 = myFlowMeters.Reference()
        # LF system LS flow reference
        self.ref4 = myFlowMeters.Reference()
        # HF system check standard
##        self.check_standard = myFlowMeters.Reference()
        # initialize reference attributes
        self.ref1.SetRefID(REF_1_ID)
        self.ref1.SetKFactor(REF1_K)
        self.ref1.SetMaxFlowRate(REF1_MAX_Q)
        self.ref1.SetMinFlowRate(REF1_MIN_Q)
        self.ref1.SetUncertainty(REF1_U)
        self.ref1.SetCurvefitPoly(REF1_POLY_COEF)

        self.ref2.SetRefID(REF_2_ID)
        self.ref2.SetKFactor(REF2_K)    
        self.ref2.SetMaxFlowRate(REF2_MAX_Q)
        self.ref2.SetMinFlowRate(REF2_MIN_Q)
        self.ref2.SetUncertainty(REF2_U)
        self.ref2.SetCurvefitPoly(REF2_POLY_COEF)

        self.ref3.SetRefID(REF_3_ID)
        self.ref3.SetKFactor(REF3_K)
        self.ref3.SetMaxFlowRate(REF3_MAX_Q)
        self.ref3.SetMinFlowRate(REF3_MIN_Q)
        self.ref3.SetUncertainty(REF3_U)
        self.ref3.SetCurvefitPoly(REF3_POLY_COEF)

        self.ref4.SetRefID(REF_4_ID)
        self.ref4.SetKFactor(REF4_K)
        self.ref4.SetMaxFlowRate(REF4_MAX_Q)
        self.ref4.SetMinFlowRate(REF4_MIN_Q)
        self.ref4.SetUncertainty(REF4_U)
        self.ref4.SetCurvefitPoly(REF4_POLY_COEF) 

##        self.check_standard.SetKFactor(CHECK_STANDARD_K)
##        self.check_standard.SetMaxFlowRate(CHECK_STANDARD_MAX_Q)
##        self.check_standard.SetMinFlowRate(CHECK_STANDARD_MIN_Q)
##        self.check_standard.SetUncertainty(CHECK_STANDARD_U)
        #----------------------------------
        # GUI Initialization
        #----------------------------------
        self.ExitButton.Enable(True)
        self.Layout()
        
    #----------------------------------
    # GUI Event Handler Methods
    #----------------------------------        
    def OnExitButton(self, event):
        self.ExitButton.Enable(False)
        dlg = myUtil.BusyInfo(self, 'One moment please, closing OPC client...')
        
        if not TEST_MODE:
            self.parent.disconnectOPC()
        
##        self.db.Save()
        dlg.Destroy()
        self.Destroy()

    #----------------------------------
    # GUI Methods
    #----------------------------------        
    def DestroyOpenPage(self):
        if self.page != None:
            try:
                self.page.Destroy()
            except:
                print 'No page available to destroy'
        return None
