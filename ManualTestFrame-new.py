#-------------------------------------------------------------------------
# PE Calibration System HMI Program
''' author: Jeff Peery '''
# date: 11/29/2007
# email: JeffPeery@yahoo.com
#-------------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''
1.07    16/12/12    SPN     -Updated GetTestResults method: Implemented curve fit correction to ref volume
1.06    16/10/14    SPN     -Updated OnOPCDataChange method: added message display for C20 (safety check, test aborted)
                            to indicate possible causes, such as resevoir level low, e-stop button pressed
1.05    15/04/17    SPN     -Hide clamp button
1.04    14/08/27    SPN     -Disabled SetXLimits, SetYLimits method calls from InitializePlot method
                            to allow auto zoom
1.03    14/02/26    SPN     Added CopyTestDataFile method to OnPrintButton event
1.02    14/02/07    SPN     -Disabled temperature indicator for RTD_4_ID event (HF-3/4 downstream) associated with unused thermistor
1.01    13/08/23    SPN     Apply thermal bias correction to temperature display in the OnOPCDataChange method
'''

#-------------------------------------------------------------------------
# Modules
#-------------------------------------------------------------------------
import wx
import Images.throbImages as throbImages
import wx.lib.throbber as throb
import numpy
from time import ctime as ctime
from time import clock as clock
from time import sleep as sleep
import Modules.myHex2Float as myHex2Float
import Modules.myFile as myFile
import Modules.myFlowMeters as myFlowMeters
import Modules.myDatabase as myDatabase
import Modules.myUncertainty as myUncertainty
import Modules.myThermal as myThermal
import Modules.myPlot as myPlot
import Modules.myHTMLReport as myReport
import Modules.myPrinter as myPrinter
import Modules.myUtil as myUtil
import Modules.myString as myString
from Modules.myHeader import *
from os.path import exists

#-------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------
class Frame(wx.Frame):
    def __init__(self, parent, fs_ref, ls_ref):
        #----------------------------------
        # GUI Ctrl Id's
        #----------------------------------
        FRAME_ID                = wx.NewId()
        PANEL_ID                = wx.NewId()
        PANEL2_ID               = wx.NewId()
        PANEL3_ID               = wx.NewId()
        EXIT_BUTTON_ID          = wx.NewId()
        TEST_BUTTON_ID          = wx.NewId()
        START_BUTTON_ID         = wx.NewId()
        STOP_BUTTON_ID          = wx.NewId()
        CLAMP_BUTTON_ID         = wx.NewId()
        FILL_BUTTON_ID          = wx.NewId()
        PRINT_BUTTON_ID         = wx.NewId()
        ADC_BUTTON_ID           = wx.NewId()
        CLEAR_PLOT_BUTTON_ID    = wx.NewId()
        FLOW_BUTTON_ID          = wx.NewId()
        TEST_TIME_BUTTON_ID     = wx.NewId()
        THROB_ID                = wx.NewId()
        TEXT_ID                 = wx.NewId()
        Q1_TEXT_ID              = wx.NewId()
        Q2_TEXT_ID              = wx.NewId()
        Q3_TEXT_ID              = wx.NewId()
        Q4_TEXT_ID              = wx.NewId()
        MUT_AO_TEXT_ID          = wx.NewId()
        TIME_TEXT_ID            = wx.NewId()
        RTD1_TEXT_ID            = wx.NewId()
        RTD2_TEXT_ID            = wx.NewId()
        RTD3_TEXT_ID            = wx.NewId()
        RTD4_TEXT_ID            = wx.NewId()
        TIME_TEXT_ID            = wx.NewId()        
        K_TEXT_ID               = wx.NewId()        
        TIME_TEXT_ID            = wx.NewId()
        FLOW_RATE_TEXT_ID       = wx.NewId()
        STATUS_BAR_ID           = wx.NewId()
        STATIC_BOX1_ID          = wx.NewId()
        STATIC_BOX2_ID          = wx.NewId()           
        CHOICE_ID               = wx.NewId()
        #----------------------------------
        # GUI Ctrl Definitions
        #----------------------------------
        if TEST_MODE: 
            wx.Frame.__init__(self, id=FRAME_ID, name='', parent=parent,
                              pos=wx.Point(184, 300), size=wx.Size(989, 550),
                              style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT, title='Calibration')
        else:
            wx.Frame.__init__(self, id=FRAME_ID, name='', parent=parent,
                              pos=wx.Point(184, 300), size=wx.Size(989, 550),
                              style=wx.FRAME_FLOAT_ON_PARENT, title='Calibration')
            self.SetClientSize(wx.Size(981, 516))
            self.SetToolTipString('')
            self.Maximize() # keep maximize here to reduce flickering on screen
        
        self.panel = wx.Panel(id=PANEL_ID, name='panel', parent=self, style=wx.TAB_TRAVERSAL)
        self.panel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.panel2 = wx.Panel(id=PANEL2_ID, name='panel2', parent=self.panel, style=wx.BORDER_SUNKEN)
        self.panel2.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.panel3 = wx.Panel(id=PANEL3_ID, name='panel3', parent=self.panel2)
        self.panel3.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.figure1 = myPlot.Figure(self.panel3)
        self.figure2 = myPlot.Figure(self.panel3)
        
        self.StartButton = wx.Button(id=START_BUTTON_ID, label='Start',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.StartButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.TestButton = wx.Button(id=TEST_BUTTON_ID, label='Test',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.TestButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))
        
        self.StopButton = wx.Button(id=STOP_BUTTON_ID, label='Stop',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.StopButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))
        
        self.ClampButton = wx.ToggleButton(id=CLAMP_BUTTON_ID, label='Close',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.ClampButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.PrintButton = wx.Button(id=PRINT_BUTTON_ID, label='Print',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.PrintButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.ExitButton = wx.Button(id=EXIT_BUTTON_ID, label='Exit', name='exit',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.ExitButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.ClearPlotButton = wx.Button(id=CLEAR_PLOT_BUTTON_ID, label='Clear', name='clear plot',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.ClearPlotButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.FillButton = wx.Button(id=FILL_BUTTON_ID, label='Fill', name='fill',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.FillButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.FlowButton = wx.Button(id=FLOW_BUTTON_ID, label='Target: 0.0 gpm',
                                     parent=self.panel2, pos=wx.Point(400, 300),
                                     size=wx.Size(200, 50))
        self.FlowButton.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.TestTimeButton = wx.Button(id=TEST_TIME_BUTTON_ID, label='Test Time: 60 secs',
                                     parent=self.panel2, pos=wx.Point(400, 300),
                                     size=wx.Size(200, 50))
        self.TestTimeButton.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        images = [throbImages.catalog[i].getBitmap()
                  for i in throbImages.index
                  if i not in ['eclouds', 'logo']]
        self.throbber = throb.Throbber(self.panel2, -1, images, size=(36, 36),frameDelay = 0.1, reverse=True)
        self.label = wx.StaticText(id=TEXT_ID,label='', name='label', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(400, 40), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.label.SetFont(wx.Font(25, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.MUTAOLabel = wx.StaticText(id=MUT_AO_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.MUTAOLabel.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.kLabel = wx.StaticText(id=K_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48), size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.kLabel.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.timeLabel = wx.StaticText(id=TIME_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48), size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.timeLabel.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.ref1Label = wx.StaticText(id=Q1_TEXT_ID,label='', name='ref1', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.ref1Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.ref2Label = wx.StaticText(id=Q2_TEXT_ID,label='', name='ref2', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.ref2Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.ref3Label = wx.StaticText(id=Q3_TEXT_ID,label='', name='ref3', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.ref3Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.ref4Label = wx.StaticText(id=Q4_TEXT_ID,label='', name='ref4', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.ref4Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.RTD1Label = wx.StaticText(id=RTD1_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.RTD1Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.RTD2Label = wx.StaticText(id=RTD2_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.RTD2Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.RTD3Label = wx.StaticText(id=RTD3_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.RTD3Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.RTD4Label = wx.StaticText(id=RTD4_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.RTD4Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.staticBox1 = wx.StaticBox(id=STATIC_BOX1_ID, label='Test Outputs', parent=self.panel2, pos=wx.Point(200,48),
                                       size=wx.Size(400, 200), style=0 )

        self.staticBox2 = wx.StaticBox(id=STATIC_BOX2_ID, label='Test Setup', parent=self.panel2, pos=wx.Point(400,48),
                                       size=wx.Size(400, 200), style=0 )

        self.choice = wx.Choice(id=CHOICE_ID, parent=self.panel2, size=wx.Size(100,25), choices=[HF_SYS_LABEL, LF_SYS_LABEL])
        self.choice.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))
        
        self.statusBar = wx.StatusBar(id=STATUS_BAR_ID, name='statusbar', parent=self, style=wx.ALWAYS_SHOW_SB)
        self.SetStatusBar(self.statusBar)

        self.timer = wx.Timer(self)
        
        #----------------------------------
        # GUI Sizers
        #----------------------------------
        '''Sizer layout'''
        # frame
        # Panel
        # ---------------------------------------------------------
        # |   |---------|  |-----------------------------------| 1|
        # |   |        2|  | |-----------------------------|3  |  |  
        # |   |         |  | |                            4|   |  |
        # |   |start    |  | |throbber                     |   |  |
        # |   |stop     |  | |label                        |   |  |
        # |   |clamp    |  | |-----------------------------|   |  |
        # |   |print    |  |                                   |  |
        # |   |exit     |  | |-------------------------------| |  |  
        # |   |test     |  | | |----------------| |------|  5| |  |
        # |   |fill     |  | | |               6| |     7|   | |  |
        # |   |         |  | | |                | |4-20  |   | |  |
        # |   |         |  | | |chc             | |kLabel|   | |  |
        # |   |         |  | | |flow_button     | |q1    |   | |  |
        # |   |         |  | | |                | |q1    |   | |  |
        # |   |         |  | | |                | |q2    |   | |  |
        # |   |         |  | | |                | |q3    |   | |  |
        # |   |         |  | | |                | |q4    |   | |  |
        # |   |         |  | | |                | |rtd1  |   | |  |
        # |   |         |  | | |                | |rtd2  |   | |  |
        # |   |         |  | | |                | |rtd3  |   | |  |
        # |   |         |  | | |                | |rtd4  |   | |  |
        # |   |         |  | | |----------------| |------|   | |  |
        # |   |         |  | |-------------------------------| |  |  
        # |   |         |  |                                   |  |
        # |   |         |  |   Panel3 (holds figure)           |  |
        # |   |         |  |                                   |  |
        # |   |---------|  |-----------------------------------|  |
        # ---------------------------------------------------------
        # status bar
        #
        self.boxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.boxSizer2 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer3 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer4 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.boxSizer5 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.boxSizer6 = wx.StaticBoxSizer(box = self.staticBox2, orient=wx.VERTICAL)
        self.boxSizer7 = wx.StaticBoxSizer(box = self.staticBox1, orient=wx.HORIZONTAL)
        self.boxSizer8 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer9 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer10 = wx.BoxSizer(orient=wx.VERTICAL)
               
        self.boxSizer1.Add(self.boxSizer2, 0, border=20, flag=wx.ALL | wx.ALIGN_TOP )
        self.boxSizer1.Add(self.panel2, 1, border=20, flag=wx.ALL | wx.ALIGN_CENTER | wx.EXPAND)

        self.boxSizer2.Add(self.StartButton, 0, border=0, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.StopButton, 0, border=10, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.ClampButton, 0, border=10, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.FillButton, 0, border=10, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.TestButton, 0, border=10, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.ClearPlotButton, 0, border=10, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.PrintButton, 0, border=10, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.ExitButton, 0, border=10, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        
        self.boxSizer3.Add(self.boxSizer4, 0, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        self.boxSizer3.Add(self.boxSizer5, 2, border=5, flag=wx.ALL | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer3.Add(self.panel3, 3, border=5, flag=wx.ALL | wx.ALIGN_LEFT | wx.EXPAND)

        self.boxSizer4.Add(self.throbber, 0, border=10, flag=wx.ALL | wx.ALIGN_TOP)
        self.boxSizer4.Add(self.label, 1, border=10, flag=wx.ALL | wx.EXPAND | wx.ALIGN_TOP)

        self.boxSizer5.Add(self.boxSizer6, 1, border=5, flag=wx.ALL | wx.ALIGN_TOP | wx.EXPAND)
        self.boxSizer5.Add(self.boxSizer7, 2, border=5, flag=wx.ALL | wx.ALIGN_TOP | wx.EXPAND)

        self.boxSizer6.Add(self.FlowButton, 0, border=0, flag=wx.ALL |wx.EXPAND)
        self.boxSizer6.Add(self.TestTimeButton, 0, border=0, flag=wx.ALL |wx.EXPAND)
        self.boxSizer6.Add(self.choice, 0, border=5, flag=wx.TOP | wx.EXPAND)                

        self.boxSizer7.Add(self.boxSizer9, 1, border=0, flag=wx.ALL | wx.EXPAND)
        self.boxSizer7.Add(self.boxSizer10, 1, border=0, flag=wx.ALL | wx.EXPAND)

        self.boxSizer9.Add(self.ref1Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer9.Add(self.ref2Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer9.Add(self.ref3Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer9.Add(self.ref4Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer9.Add(self.RTD1Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer9.Add(self.RTD2Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer9.Add(self.RTD3Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer9.Add(self.RTD4Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)

        self.boxSizer10.Add(self.MUTAOLabel, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer10.Add(self.kLabel, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer10.Add(self.timeLabel, 0, border=10, flag=wx.ALL| wx.ALIGN_LEFT | wx.EXPAND)
                 
        self.boxSizer8.Add(self.figure1, 1, border=0, flag=wx.ALL | wx.EXPAND)
        self.boxSizer8.Add(self.figure2, 1, border=0, flag=wx.ALL | wx.EXPAND)

        self.panel3.SetSizer(self.boxSizer8)
        self.panel2.SetSizer(self.boxSizer3)
        self.panel.SetSizer(self.boxSizer1)
        self.panel.Layout()        
        #----------------------------------
        # Event Definitions
        #----------------------------------
        self.ClampButton.Bind(wx.EVT_TOGGLEBUTTON, self.OnClampButton)
        self.StartButton.Bind(wx.EVT_BUTTON, self.OnStartButton)
        self.StopButton.Bind(wx.EVT_BUTTON, self.OnStopButton)
        self.TestButton.Bind(wx.EVT_BUTTON, self.OnTestButton)
        self.ExitButton.Bind(wx.EVT_BUTTON, self.OnExitButton)
        self.ClearPlotButton.Bind(wx.EVT_BUTTON, self.OnClearPlotButton)
        self.PrintButton.Bind(wx.EVT_BUTTON, self.OnPrintButton)
        self.FlowButton.Bind(wx.EVT_BUTTON, self.OnFlowButton)
        self.TestTimeButton.Bind(wx.EVT_BUTTON, self.TestTimeButton)
        self.FillButton.Bind(wx.EVT_BUTTON, self.OnFillButton)
        self.choice.Bind(wx.EVT_CHOICE, self.OnSystemChoice)
        self.Bind(wx.EVT_CLOSE, self.OnExitButton)     
        self.Bind(wx.EVT_TIMER, self.OnTimer)                 
        #----------------------------------
        # Attributes
        #----------------------------------
        # parent
        self.parent = parent.parent
        # a print object for printing reports
        self.print_obj = myPrinter.Printer()
        # full scale reference meter object
        self.fs_ref = fs_ref
        # low scale reference meter object
        self.ls_ref = ls_ref
        # default to HF_SYSTEM
        self.system_type = HF_SYSTEM
        # flow rate set point
        self.flow_rate_set_point = 0.0
        # target test time
        self.
        # file for saving measurment data
        self.file = myFile.myFile(TEST_RESULTS_FILE_PATH)
        self.file.CreateFile()
        # use call later here to allow time for
        # OPC server to process data change
        # must be called here or AFTER __init__() method
        # of page since page must exist before invoking 
        # SetSystemType()
        wx.CallLater(500, self.parent.SetSystemType)
        #----------------------------------
        # GUI Ctrl Initializations
        #----------------------------------
        self.StartButton.SetForegroundColour(wx.Colour(0, 250, 0))
        self.StopButton.SetForegroundColour(wx.Colour(250, 0, 0))
        self.TestButton.SetForegroundColour(wx.Colour(0, 0, 250))
        self.StopButton.Enable(True)
        self.ClampButton.Show(False)
        self.ClampButton.Enable(True)
        self.ExitButton.Enable(True)
        self.PrintButton.Enable(True)
        self.StartButton.Enable(False)
        self.TestButton.Enable(False)
        self.FillButton.Enable(False)
        self.ClearPlotButton.Enable(True)
        self.FlowButton.Enable(True)
        self.TestTimeButton.Enable(True)
        self.choice.Enable(True)
        self.SetupLabels()
        self.HideOutputLabels()
        #----------------------------------
        # GUI SetupboxSizer6
        #----------------------------------
        self.InitializePlot()
        self.choice.SetSelection(0)
        
    #----------------------------------
    # Event Handler Methods
    #----------------------------------
    def OnTimer(self, event):
        """
        Event handler for timer events, updates approx time label
        """
        self.timeLabel.SetLabel('Time: %d (s)'%(clock() - self.time))

    def OnFillButton(self, event):
        """Event handler for Fill button"""
        self.parent.FillReservoir()
        
    def OnFlowButton(self, event):
        """Event handler for Flow button"""
        x = self.GetFlowRateNumber()
        assert self.IsGoodFlowRate(x)
##        # stop flow if transitioning thru trans flow rate. required for the PLC PID
##        # to change
##        if self.flow_rate_set_point >= myUtil.GetTransitionFlowRate(self.system_type):
##            if x <= myUtil.GetTransitionFlowRate(self.system_type):
##                self.parent.StopTest()                
##        elif self.flow_rate_set_point <= myUtil.GetTransitionFlowRate(self.system_type):
##            if x >= myUtil.GetTransitionFlowRate(self.system_type):
##                self.parent.StopTest()
        self.flow_rate_set_point = x
        self.FlowButton.SetLabel('Target: %0.3f gpm'%self.flow_rate_set_point)
        self.parent.SetTargetFlowRate(self.flow_rate_set_point)
        
    def OnClearPlotButton(self, event):
        """Event handler for Clear Plot button"""
        self.InitializePlot()
        self.file.CreateFile()
        
    def OnExitButton(self, event):
        """Event handler for Exit button"""
        self.Destroy()

    def OnTestButton(self, event):
        """Event handler for Test button"""
        self.parent.StartPulseCapture()
        
    def OnClampButton(self, event):
        """Event handler for Clamp button"""
        if self.ClampButton.GetValue() == CLAMP_BUTTON_DOWN:
            self.SetStatusLabels('Closing Clamp...')                       
            self.throbber.Start()
            self.parent.CloseClamp()
        elif self.ClampButton.GetValue() == CLAMP_BUTTON_UP:
            self.SetStatusLabels('Opening Clamp...')
            self.throbber.Start()
            self.parent.OpenClamp()
        else: raise TypeError, 'Unknown Clamp Button value.'

    def OnStartButton(self, event):
        """Event handler for Start button event"""        
        # Start Test
        self.parent.SetTargetTestTime(60)
        self.parent.SetTargetFlowRate(self.flow_rate_set_point)
        self.parent.StartFlow()
       
    def OnPrintButton(self, event):
        """Event handler for Print button event"""
        self.throbber.Start()
        self.SetStatusLabels('Saving Figure...')
        # Save test results
        self.parent.CopyTestDataFile()
        # create and print report
        self.figure1.SaveFigure('C:\\Documents and Settings\\pecal\\Desktop\\image1')
        self.figure2.SaveFigure('C:\\Documents and Settings\\pecal\\Desktop\\image2')
        self.SetStatusLabels('Figure Saved.')
        
    def OnStopButton(self, event):
        """Event handler for Stop button event"""
        self.throbber.Start()
        self.SetStatusLabels('Stopping Test...')
        self.parent.StopTest()
        
    def OnSystemChoice(self, evt):
        """Event handler for System Type choice event"""
        system_label = self.choice.GetStringSelection()

        if system_label == HF_SYS_LABEL:            
            self.system_type = HF_SYSTEM
            self.fs_ref = self.parent.directory.ref1
            self.ls_ref = self.parent.directory.ref2
            self.FillButton.Enable(False)
        elif system_label == LF_SYS_LABEL:            
            self.system_type = LF_SYSTEM
            self.fs_ref = self.parent.directory.ref3
            self.ls_ref = self.parent.directory.ref4 
            self.FillButton.Enable(True)      
        else:
            raise TypeError, 'received unknown meter label'
            return

        self.parent.SetSystemType()
        self.HideOutputLabels()
        self.SetupLabels()
        
    def OnOPCDataChange(self, evt):
        """
        Event handler for OPC Data Change events
        """
        # only accept True valued events. False valued
        # events are caused by the HMI or PLC reseting
        # the True valued event.
        if evt.value == False: return

        #----------------------------------
        # PLC Events
        #----------------------------------
        if evt.msg == PLC_RELAY_C0_ID:
            print 'System ID Relay Event,', ctime()
            
        elif evt.msg == PLC_RELAY_C1_ID:
            print 'Process Flow Relay Event,', ctime()
            
        elif evt.msg == PLC_RELAY_C2_ID:
            print 'Initialize Event,', ctime()
            
        elif evt.msg == PLC_RELAY_C3_ID:
            print 'Pass Test Event,', ctime()
            
        elif evt.msg == PLC_RELAY_C4_ID:
            print 'Fail Test Event,', ctime()
            
        elif evt.msg == PLC_RELAY_C5_ID:
            print 'Gravity Start Test Event,', ctime()
            
        elif evt.msg == PLC_RELAY_C7_ID:
            print 'Motor Test Start Event,', ctime()
            
        elif evt.msg == PLC_RELAY_C11_ID:
            print 'Stop Test Event,', ctime()
            
        elif evt.msg == PLC_RELAY_C12_ID:            
            print 'Close Clamp Event,', ctime()
            
        elif evt.msg == PLC_RELAY_C13_ID:
            print 'Open Clamp Event,', ctime()


        elif evt.msg == PLC_RELAY_C15_ID:
            print 'Fill Reservoir Event,', ctime()
            self.SetStatusLabels('Preparing Reservoir Valves...')
            self.throbber.Start()

        elif evt.msg == PLC_RELAY_C32_ID:
            print 'Flow Started Event,', ctime()
            
        #----------------------------------
        # HMI Events
        #----------------------------------          
        elif evt.msg == PLC_RELAY_C14_ID:
            print 'Filling Reservoir Event,', ctime()
            self.SetStatusLabels('Filling Reservoir...')
            self.throbber.Start()
            self.parent.ResetFillingReservoir()

        elif evt.msg == MUT_AO_ID:
##            print '4-20 counts:: ', evt.value
            self.MUTAOLabel.SetLabel('4-20: %0.3f (mA)'%myUtil.DigitalToMilliAmps(evt.value))

        elif evt.msg == REF_1_ID:
            self.ref1Label.SetLabel('Ref 1: %0.3f (gpm)'%myUtil.DigitalToFlowRate(evt.value, REF1_MAX_Q))
            
        elif evt.msg == REF_2_ID:
            self.ref2Label.SetLabel('Ref 2: %0.3f (gpm)'%myUtil.DigitalToFlowRate(evt.value, REF2_MAX_Q))
            
        elif evt.msg == REF_3_ID:
            self.ref3Label.SetLabel('Ref 3: %0.3f (gpm)'%myUtil.DigitalToFlowRate(evt.value, REF3_MAX_Q))
            
        elif evt.msg == REF_4_ID:
            self.ref4Label.SetLabel('Ref 4: %0.4f (gpm)'%myUtil.DigitalToFlowRate(evt.value, REF4_MAX_Q))
            
        elif evt.msg == RTD_1_ID:
            return
##            self.RTD1Label.SetLabel('Temp 1: %0.2f (C)'%(myThermal.DigitalToTemp(evt.value,
##                                                                                THERMAL_1_B0,
##                                                                                THERMAL_1_B1,
##                                                                                THERMAL_1_B2,
##                                                                                THERMAL_1_B3) + THERMAL_1_BIAS_CORRECTION))
        elif evt.msg == RTD_2_ID:
            self.RTD2Label.SetLabel('Temp 2: %0.2f (C)'%(myThermal.DigitalToTemp(evt.value,
                                                                                THERMAL_2_B0,
                                                                                THERMAL_2_B1,
                                                                                THERMAL_2_B2,
                                                                                THERMAL_2_B3) + THERMAL_2_BIAS_CORRECTION))
        elif evt.msg == RTD_3_ID:
            self.RTD3Label.SetLabel('Temp 3: %0.2f (C)'%(myThermal.DigitalToTemp(evt.value,
                                                                                THERMAL_3_B0,
                                                                                THERMAL_3_B1,
                                                                                THERMAL_3_B2,
                                                                                THERMAL_3_B3) + THERMAL_3_BIAS_CORRECTION))
        elif evt.msg == RTD_4_ID:
            return
##            self.RTD4Label.SetLabel('Temp 4: %0.2f (C)'%(myThermal.DigitalToTemp(evt.value,
##                                                                                THERMAL_4_B0,
##                                                                                THERMAL_4_B1,
##                                                                                THERMAL_4_B2,
##                                                                                THERMAL_4_B3) + THERMAL_4_BIAS_CORRECTION))
        elif evt.msg == PLC_RELAY_C20_ID:
            print 'Test Aborted Event', ctime()
            self.EnableCtrls(True)
            if self.ClampButton.GetValue():
                self.StartButton.Enable(True)
                self.EnableFillButton(True)
                self.choice.Enable(False)
            else:
                self.StartButton.Enable(False)
                self.EnableFillButton(False)
                self.ExitButton.Enable(False)
                self.choice.Enable(True)
            self.SetStatusLabels('Safety Check Aborted Test')                        
            self.parent.ResetAbortedTest()
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.EnableLabels(False)
            self.SetupLabels()
            self.StopTimer()

            myUtil.MessageFrame(self, MSG_TEST_STOPPED)
            
        elif evt.msg == PLC_RELAY_C21_ID:
            print 'Test Stopped Event', ctime()
            self.EnableCtrls(True)
            self.TestButton.Enable(False)
            if self.ClampButton.GetValue():
                self.StartButton.Enable(True)
                self.EnableFillButton(True)
                self.ExitButton.Enable(False)
                self.choice.Enable(False)
            else:
                self.StartButton.Enable(False)
                self.EnableFillButton(False)
                self.choice.Enable(True)
            self.SetStatusLabels('Stopped Test')
            self.parent.ResetStoppedTest()             
            self.throbber.Stop()
            self.throbber.Rest()
            self.EnableLabels(False)
            self.SetupLabels()
            self.StopTimer()
            
        elif evt.msg == PLC_RELAY_C22_ID:
            print 'Test Finished Event', ctime()   
            self.parent.ResetTestFinished()
            self.StopTimer()
            self.SetStatusLabels('Retreiving Test Results...')
            # get test results, plot error, update labels
            self.GetTestResults()
            self.SetStatusLabels('Test Complete.')
            self.TestButton.Enable(True)
                    
        elif evt.msg == PLC_RELAY_C24_ID:
            print 'Closed Clamp Event', ctime()
            self.ClampButton.SetLabel('Open')
            self.ClampButton.SetValue(CLAMP_BUTTON_DOWN)
            self.ExitButton.Enable(False)
            self.StartButton.Enable(True)
            self.EnableFillButton(True)
            self.choice.Enable(False)                
            self.SetStatusLabels('Clamp Closed')
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.parent.ResetClosedClamp()
            
        elif evt.msg == PLC_RELAY_C25_ID:
            print 'Opened Clamp Event', ctime()
            self.ClampButton.SetLabel('Close')
            self.ClampButton.SetValue(CLAMP_BUTTON_UP)
            self.EnableCtrls(True)
            self.StartButton.Enable(False)
            self.EnableFillButton(False)
            self.TestButton.Enable(False)
            self.SetStatusLabels('Clamp Opened')  
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.parent.ResetOpenedClamp() 
            self.SetupLabels()
            
        elif evt.msg == PLC_RELAY_C30_ID:
            print 'Filled Reservoir Event', ctime()
            self.SetStatusLabels('Reservoir Full')
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.parent.ResetReservoirFilled()
            
        elif evt.msg == PLC_RELAY_C31_ID:
            print 'Test Started Event,', ctime()
            self.SetStatusLabels('Operating...')
            self.EnableCtrls(False)
            self.TestButton.Enable(True)
            self.EnableLabels(True)
            self.throbber.Start()
            self.parent.ResetTestStarted()
       
        elif evt.msg == PLC_RELAY_C33_ID:
            print 'Pulse Capture Started Event,', ctime()
            self.SetStatusLabels('Capturing Pulses...')
            self.ClampButton.Enable(False)
            self.StartButton.Enable(False)
            self.TestButton.Enable(False)
            self.EnableFillButton(False)                
            self.EnableLabels(True) 
            self.throbber.Start()
            self.StartTimer()
            
        else:
            raise TypeError, 'Unknown event message (event.msg) received in OnResult() method.'
        
    #----------------------------------
    # GUI Methods
    #----------------------------------
    def GetFlowRateNumber(self):
        """
        Prompt operator for serial number
        """
        q = myUtil.NumEntryDialog(self)
        if q != None:
            while not self.IsGoodFlowRate(q):
                self.Error('Invalid Flow rate. Values must be numeric \nand may not exceed system limits.', stop_test=True)
                q = myUtil.NumEntryDialog(self)
                if q == None:
                    return 1.0
            q = float(q)
        return q

    def IsGoodFlowRate(self, q):
        """
        Check that input number has valid format
        """
        if not myString.IsNumber(q):
            return False
        else:
            q = float(q)

        if self.GetSysType() == HF_SYSTEM and (q < HF_MIN_FLOW_RATE or q > HF_MAX_FLOW_RATE):
            return False
        elif self.GetSysType() == LF_SYSTEM and (q < LF_MIN_FLOW_RATE or q > LF_MAX_FLOW_RATE):
            return False
        else:
            return True
        
    def GetSysType(self):
        assert self.system_type in [HF_SYSTEM, LF_SYSTEM]
        return self.system_type
    
    def Error(self, msg, stop_test=True):
        """
        Stop test and show error message
        """
        myUtil.ErrorDialog(self, msg)
        if stop_test:
            self.OnStopButton(None)
                                                                     
    def SetStatusLabels(self, msg):
        self.label.SetLabel(msg)
        self.statusBar.SetStatusText(msg)

    def SetupLabels(self):
        """Setup labels"""
        self.MUTAOLabel.SetLabel('4-20: (mA)')
        self.kLabel.SetLabel('K:')
        self.ref1Label.SetLabel('Ref 1: (gpm)')     
        self.ref2Label.SetLabel('Ref 2: (gpm)')          
        self.ref3Label.SetLabel('Ref 3: (gpm)')          
        self.ref4Label.SetLabel('Ref 4: (gpm)')
        self.RTD1Label.SetLabel('Temp 1: (C)')
        self.RTD2Label.SetLabel('Temp 2: (C)')
        self.RTD3Label.SetLabel('Temp 3: (C)')
        self.RTD4Label.SetLabel('Temp 4: (C)')
        self.timeLabel.SetLabel('')

    def HideOutputLabels(self):
        """Hide output labels"""
        if self.system_type == LF_SYSTEM:
            self.boxSizer9.Hide(0)
            self.boxSizer9.Hide(1)
            self.boxSizer9.Hide(6)
            self.boxSizer9.Hide(7)
            self.boxSizer9.Show(2)
            self.boxSizer9.Show(3)
            self.boxSizer9.Show(4)
            self.boxSizer9.Show(5)
        elif self.system_type == HF_SYSTEM:
            self.boxSizer9.Hide(2)
            self.boxSizer9.Hide(3)
            self.boxSizer9.Hide(4)
            self.boxSizer9.Hide(5)
            self.boxSizer9.Show(0)
            self.boxSizer9.Show(1)
            self.boxSizer9.Show(6)
            self.boxSizer9.Show(7)
        else:
            raise TypeError, 'receive unknown meter type'
        self.boxSizer7.Layout()

    def EnableLabels(self, value):
        """Enable labels"""
        self.timeLabel.Enable(value)
        self.MUTAOLabel.Enable(value)
        self.ref1Label.Enable(value)
        self.ref2Label.Enable(value)
        self.ref3Label.Enable(value)
        self.ref4Label.Enable(value)
        self.RTD1Label.Enable(value)
        self.RTD2Label.Enable(value)
        self.RTD3Label.Enable(value)
        self.RTD4Label.Enable(value)
        self.kLabel.Enable(value)
    
    def EnableCtrls(self, value):
        self.ClampButton.Enable(value)
        self.StartButton.Enable(value)
        self.FillButton.Enable(value)
        self.PrintButton.Enable(value)
        self.ExitButton.Enable(value)
        self.TestButton.Enable(value)
##        self.FlowButton.Enable(value)
        self.choice.Enable(value)

    def EnableFillButton(self, value):
        if value == True and self.system_type == LF_SYSTEM:     
            self.FillButton.Enable(True)   
        else:
            self.FillButton.Enable(False) 

    def InitializePlot(self):
        self.figure1.Initialize()
        self.figure1.SetXLabel('Flow Rate (gpm)')
        self.figure1.SetYLabel('K-Factor (ppg)')
##        self.figure1.SetXLimits(UPPER_X_LIMIT, LOWER_X_LIMIT)
##        self.figure1.SetYLimits(UPPER_Y_LIMIT, LOWER_Y_LIMIT)
        self.figure1.Draw()
        
        self.figure2.Initialize()
        self.figure2.SetXLabel('Sample Number')
        self.figure2.SetYLabel('K-Factor (ppg)')
##        self.figure2.SetXLimits(UPPER_X_LIMIT, LOWER_X_LIMIT)
##        self.figure2.SetYLimits(UPPER_Y_LIMIT, LOWER_Y_LIMIT)
        self.figure2.Draw()
        
    def PlotKFactor(self, rate, k_factor):
        """
        Plot test results
        """
        a=self.figure2.figure.get_axes()[0]
        a=a.get_lines()
##        if a.__len__() > 0:
##            y=a[0].get_ydata()
##            y=y.tolist()
##            y.append(k_factor)
##        else:
        y=[k_factor]
        
        self.figure2.Scatter([a.__len__()+1], y, MARKER_SHAPE, MARKER_SIZE, MARKER_FACE_COLOR, MARKER_EDGE_COLOR, MARKER_EDGE_WIDTH, ALPHA_SCATTER)
        self.figure1.Scatter([rate,], [k_factor,], MARKER_SHAPE, MARKER_SIZE, MARKER_FACE_COLOR, MARKER_EDGE_COLOR, MARKER_EDGE_WIDTH, ALPHA_SCATTER)
        self.figure1.Draw()
        self.figure2.Draw()

    def StartTimer(self):
        """
        Start timer, controls approx time label
        """
        self.time = clock()      
        self.timer.Start(TIMER_PERIOD_MS)

    def StopTimer(self):
        """
        Stop timer, controls approx time label
        """
        self.time = clock()
        self.timer.Stop()
        self.timeLabel.SetLabel('Time: 0 (s)')
        
    #----------------------------------
    # Calibration Methods
    #----------------------------------
    def GetTestResults(self):
        """
        Get test results

        Correct reference meter volume for theremal changes in storage volume
        (see 'A Measurement Assurance Program for Flow Calibration by the
        Transfer Method') located in the PE Cal Sys Binder.
        """
        # create a new test instance
        test = myDatabase.Test()
        # query opc server for results
        temp_change, avg_temp, test_time, ref_count, mut_count = self.parent.GetTestResults()
        print ref_count, 'ref count'
        print mut_count, 'mut count'
        print test_time, 'test time'
        print temp_change, 'temp change'
        print self.flow_rate_set_point, 'flow rate set point'
        storage_volume      = myUtil.GetStorageVolume(self.system_type, self.flow_rate_set_point)
        u_storage_volume    = myUtil.GetStorageVolumeUncert(self.system_type, self.flow_rate_set_point)

        if myUtil.CalValuesAreOk(ref_count, mut_count, test_time, temp_change):
            if self.flow_rate_set_point > myUtil.GetTransitionFlowRate(self.system_type):
                ref_volume      = ref_count/(self.fs_ref.GetKFactor()*GAL_PER_CUBIC_METER)  # convert to m^3
                ref_kfactor     = self.fs_ref.GetKFactor()
                u_ref           = self.fs_ref.GetUncertainty()
                thermal_volume  = myThermal.GetVolume2(temp_change, ref_volume, storage_volume) - ref_volume
                poly_coef       = self.fs_ref.GetCurvefitPoly()
            else:                
                ref_volume      = ref_count/(self.ls_ref.GetKFactor()*GAL_PER_CUBIC_METER)  # convert to m^3
                ref_kfactor     = self.ls_ref.GetKFactor()
                u_ref           = self.ls_ref.GetUncertainty()
                thermal_volume  = myThermal.GetVolume1(temp_change, ref_volume, storage_volume) - ref_volume
                poly_coef       = self.ls_ref.GetCurvefitPoly()

            # Apply corrections to ref volume
            ref_volume = myUtil.GetCorrectedVolume(ref_volume, thermal_volume, test_time, poly_coef)

            # set reference pulse count from corrected reference volume
            ref_count = ref_kfactor*(ref_volume*GAL_PER_CUBIC_METER)
            print ref_kfactor, 'ref k-factor'
            print ref_volume*GAL_PER_CUBIC_METER, 'corrected ref_volume (gal)'
            print ref_count, 'adjusted ref count'
            # calculate and save measurement uncertainties                                               
##            myUncertainty.GetUncertainty(temp_change,
##                                        test_time,
##                                        storage_volume,
##                                        ref_volume,
##                                        mut_count,
##                                        u_ref*ref_volume,
##                                        u_storage_volume)
            
            kfactor = float(mut_count)/float(ref_volume*GAL_PER_CUBIC_METER)
            flow_rate = ref_volume/test_time * GAL_PER_CUBIC_METER * SEC_PER_MIN
            self.kLabel.SetLabel('K: %0.2f'%(kfactor))
            self.PlotKFactor(flow_rate, kfactor)
            self.file.Append('%0.3f, %0.3f\n'%(flow_rate, kfactor))
            return True    
        else:
            self.Error('Test results are invalid:\nref count: %d\nmut count: %d\ntest time: %0.2f\ntemp change: %0.3f'%(ref_count, mut_count, test_time, temp_change))
            return False
        
