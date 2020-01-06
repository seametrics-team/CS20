#-------------------------------------------------------------------------
# PE Custom Multipoint System HMI Program
''' author: Steve Nguyen '''
# date: 10/14/2014
# email: SteveN@seametrics.com
#-------------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''
1.06    17/01/05    SPN     -Updated GetTestResults method: Implemented curve fit correction to ref volume
1.05    16/12/29    SPN     -Updated OnImportButton, OnExportButton: implement default folder
                            -Update init method to load default profile as DEFAULT_PROFILE_PATH
1.04    16/10/14    SPN     -Updated OnOPCDataChange method: added message display for C20 (safety check, test aborted)
1.03    15/04/17    SPN     -Hide clamp button
1.02    14/10/20    SPN     -Created CancelPulseCapture method and implemented into test stopped
                            and test aborted events
                            -Updated Test Finished, Filled Reservoir, Test Stopped events and
                            OnStartbutton method to support continuous pulse capture tests on LF system
1.01    14/10/16    SPN     -Update GetTestResults method: Optimize and echo flow rate and
                            mut kfactor calculations
                            -Set timer to operate over entire length of test rather than
                            over each pulse capture
1.00    14/10/14    SPN     Initial release
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
import Modules.myFlowMeters as myFlowMeters
import Modules.myDatabase as myDatabase
import Modules.myUncertainty as myUncertainty
import Modules.myThermal as myThermal
import Modules.myPlot as myPlot
import Modules.myHTMLReport as myReport
import Modules.myPrinter as myPrinter
import Modules.myUtil as myUtil
import Modules.myFile as myFile
from Modules.myHeader import *
from os.path import exists

#-------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------
WAIT_TIME_HF = 60000
WAIT_TIME_LF = 75000
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
        PANEL4_ID               = wx.NewId()
        EXIT_BUTTON_ID          = wx.NewId()
        START_BUTTON_ID         = wx.NewId()
        STOP_BUTTON_ID          = wx.NewId()
        CLAMP_BUTTON_ID         = wx.NewId()
        CLEAR_PLOT_BUTTON_ID    = wx.NewId()
        PRINT_BUTTON_ID         = wx.NewId()
        IMPORT_BUTTON_ID         = wx.NewId()
        EXPORT_BUTTON_ID         = wx.NewId()
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
        K_TEXT_ID               = wx.NewId()
        TIME_TEXT_ID            = wx.NewId()
        FLOW_RATE_TEXT_ID       = wx.NewId()
        STATUS_BAR_ID           = wx.NewId()
        STATIC_BOX1_ID          = wx.NewId()
        STATIC_BOX3_ID          = wx.NewId()
        STATIC_BOX4_ID          = wx.NewId()
        STATIC_BOX5_ID          = wx.NewId()
        STATIC_BOX6_ID          = wx.NewId()
        STATIC_BOX7_ID          = wx.NewId()
        STATIC_BOX8_ID          = wx.NewId()
        TEXT_CTRL_ID            = wx.NewId()
        CHOICE2_ID              = wx.NewId()
        #----------------------------------
        # GUI Ctrl Definitions
        #----------------------------------
        wx.Frame.__init__(self, id=FRAME_ID, parent=parent,
                          pos=wx.Point(184, 300), size=wx.Size(989, 550),
                          style=wx.FRAME_FLOAT_ON_PARENT)
        self.SetClientSize(wx.Size(981, 516))
        self.SetToolTipString('')
        self.Maximize() # keep maximize here to reduce flickering on screen
    
        self.panel = wx.Panel(id=PANEL_ID, name='panel', parent=self, style=wx.TAB_TRAVERSAL)
        self.panel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.panel2 = wx.Panel(id=PANEL2_ID, name='panel2', parent=self.panel, style=wx.BORDER_SUNKEN)
        self.panel2.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.panel3 = wx.Panel(id=PANEL3_ID, name='panel3', parent=self.panel2)
        self.panel3.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.panel4 = wx.Panel(id=PANEL4_ID, parent=self.panel2)
        self.panel4.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.figure1 = myPlot.Figure(self.panel3)
        self.figure2 = myPlot.Figure(self.panel3)
        
        self.StartButton = wx.Button(id=START_BUTTON_ID, label='Start',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.StartButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

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

        self.ClearPlotButton = wx.Button(id=CLEAR_PLOT_BUTTON_ID, label='Clear', name='clear plot',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.ClearPlotButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.ImportButton = wx.Button(id=IMPORT_BUTTON_ID, label='Import',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.ImportButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.ExportButton = wx.Button(id=EXPORT_BUTTON_ID, label='Export',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.ExportButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.SaveButton = wx.Button(id=EXPORT_BUTTON_ID, label='Save As\nDefault',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.SaveButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))
        
        self.ExitButton = wx.Button(id=EXIT_BUTTON_ID, label='Exit', name='exit',
                                     parent=self.panel, pos=wx.Point(400, 300),
                                     size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.ExitButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        images = [throbImages.catalog[i].getBitmap()
                  for i in throbImages.index
                  if i not in ['eclouds', 'logo']]
        self.throbber = throb.Throbber(self.panel2, -1, images, size=(36, 36),frameDelay = 0.1, reverse=True)
        self.label = wx.StaticText(id=TEXT_ID,label='', name='label', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(400, 30), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.label.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.MUTAOLabel = wx.StaticText(id=MUT_AO_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.MUTAOLabel.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.kLabel = wx.StaticText(id=K_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48), size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.kLabel.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.timeLabel = wx.StaticText(id=TIME_TEXT_ID,label='Time: 0 (s)', name='label', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.timeLabel.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.ref1Label = wx.StaticText(id=Q1_TEXT_ID,label='', name='ref1', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.ref1Label.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.ref2Label = wx.StaticText(id=Q2_TEXT_ID,label='', name='ref2', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.ref2Label.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.ref3Label = wx.StaticText(id=Q3_TEXT_ID,label='', name='ref3', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.ref3Label.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.ref4Label = wx.StaticText(id=Q4_TEXT_ID,label='', name='ref4', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.ref4Label.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.RTD1Label = wx.StaticText(id=RTD1_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.RTD1Label.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.RTD2Label = wx.StaticText(id=RTD2_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.RTD2Label.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.RTD3Label = wx.StaticText(id=RTD3_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.RTD3Label.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.RTD4Label = wx.StaticText(id=RTD4_TEXT_ID,label='', parent=self.panel2, pos=wx.Point(200, 48),
                                   size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.RTD4Label.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.staticBox1 = wx.StaticBox(id=STATIC_BOX1_ID, label='Test Conditions', parent=self.panel2, pos=wx.Point(200,48),
                                       size=wx.Size(400, 200), style=0 )

        self.staticBox7 = wx.StaticBox(id=STATIC_BOX7_ID, label='Setup', parent=self.panel4, pos=wx.Point(400,48),
                                       size=wx.Size(800, 200), style=0 )

        self.staticBox8 = wx.StaticBox(id=STATIC_BOX8_ID, label='Profile (row = [flow rate], [test time], [replicates])', parent=self.panel4, pos=wx.Point(200,48),
                                       size=wx.Size(400, 200), style=0 )
            
        self.profile_text_ctrl = wx.TextCtrl(id=TEXT_CTRL_ID, parent=self.panel4, size=wx.Size(400, 200), style=wx.TE_MULTILINE)

        self.choice2 = wx.Choice(id=CHOICE2_ID, parent=self.panel4, size=wx.Size(200,25), choices=[HF_SYS_LABEL, LF_SYS_LABEL])
        self.choice2.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))
        
        self.statusBar = wx.StatusBar(id=STATUS_BAR_ID, name='statusbar', parent=self, style=wx.ALWAYS_SHOW_SB)
        self.SetStatusBar(self.statusBar)
    
        self.timer = wx.Timer(self)

        #----------------------------------
        # GUI Sizers
        #----------------------------------
        '''Sizer layout'''
        # frame
        # Panel
        # -------------------------------------------------------
        # |   |---------|  |---------------------------------| 1|
        # |   |        2|  | |-----------------------------|3|  |  
        # |   |         |  | |                            4| |  |
        # |   |start    |  | |throbber                     | |  |
        # |   |stop     |  | |label                        | |  |
        # |   |clamp    |  | |-----------------------------| |  |
        # |   |print    |  |                                 |  |
        # |   |exit     |  | |-----------------------------| |  |  
        # |   |         |  | | |----||----||-------------|5| |  |
        # |   |         |  | | |  14||  15||            7| | |  |
        # |   |         |  | | |    ||    ||             | | |  |
        # |   |         |  | | |chc2||sldr||             | | |  |
        # |   |         |  | | |chc ||sldr||q1           | | |  |
        # |   |         |  | | |chc ||sldr||q1           | | |  |
        # |   |         |  | | |    ||sldr||q2           | | |  |
        # |   |         |  | | |    ||sldr||q3           | | |  |
        # |   |         |  | | |    ||    ||q4           | | |  |
        # |   |         |  | | |    ||    ||rtd1         | | |  |
        # |   |         |  | | |    ||    ||rtd2         | | |  |
        # |   |         |  | | |    ||    ||rtd3         | | |  |
        # |   |         |  | | |    ||    ||rtd4         | | |  |
        # |   |         |  | | |    ||    ||kLabel       | | |  |
        # |   |         |  | | |    ||    ||4-20         | | |  |
        # |   |         |  | | |----||----||----||-------| | |  | 
        # |   |         |  | |-----------------------------| |  |  
        # |   |         |  |                                 |  |
        # |   |         |  |   Panel3 (holds figure)         |  |
        # |   |         |  |                                 |  |
        # |   |---------|  |---------------------------------|  |
        # -------------------------------------------------------
        # status bar
        #
        self.boxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.boxSizer2 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer3 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer4 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.boxSizer5 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.boxSizer7 = wx.StaticBoxSizer(box = self.staticBox1, orient=wx.VERTICAL)
        self.boxSizer8 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer13 = wx.StaticBoxSizer(box = self.staticBox7, orient=wx.HORIZONTAL)
        self.boxSizer14 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer16 = wx.StaticBoxSizer(box = self.staticBox8, orient=wx.HORIZONTAL)
        
        self.boxSizer1.Add(self.boxSizer2, 0, border=20, flag=wx.ALL | wx.ALIGN_TOP )
        self.boxSizer1.Add(self.panel2, 1, border=20, flag=wx.ALL | wx.ALIGN_CENTER | wx.EXPAND)

        self.boxSizer2.Add(self.StartButton, 0, border=0, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.StopButton, 0, border=5, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.ClampButton, 0, border=5, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.ClearPlotButton, 0, border=5, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.PrintButton, 0, border=5, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.ImportButton, 0, border=5, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.ExportButton, 0, border=5, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.SaveButton, 0, border=5, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.ExitButton, 0, border=5, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        
        self.boxSizer3.Add(self.boxSizer4, 0, border=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        self.boxSizer3.Add(self.boxSizer5, 3, border=0, flag=wx.ALL | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer3.Add(self.panel3, 4, border=10, flag=wx.ALL | wx.ALIGN_LEFT | wx.EXPAND)

        self.boxSizer4.Add(self.throbber, 0, border=10, flag=wx.ALL | wx.ALIGN_TOP)
        self.boxSizer4.Add(self.label, 1, border=10, flag=wx.ALL | wx.EXPAND | wx.ALIGN_TOP)

        self.boxSizer5.Add(self.panel4, 1, border=10, flag=wx.ALL | wx.EXPAND)
        self.boxSizer5.Add(self.boxSizer7, 1, border=10, flag=wx.ALL | wx.ALIGN_TOP | wx.EXPAND)      

        self.boxSizer7.Add(self.ref1Label, 0, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.ref2Label, 0, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.ref3Label, 0, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.ref4Label, 0, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.RTD1Label, 0, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.RTD2Label, 0, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.RTD3Label, 0, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.RTD4Label, 0, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.timeLabel, 0, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.MUTAOLabel, 0, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND) 
        self.boxSizer7.Add(self.kLabel, 0, border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND) 
      
        self.boxSizer8.Add(self.figure1, 1, border=0, flag=wx.ALL | wx.EXPAND)
        self.boxSizer8.Add(self.figure2, 1, border=0, flag=wx.ALL | wx.EXPAND)

        self.boxSizer16.Add(self.profile_text_ctrl, 1, border=0, flag=wx.ALL |wx.EXPAND)
        
        self.boxSizer13.Add(self.boxSizer14, 1, border=10, flag=wx.ALL | wx.EXPAND)
        
        self.boxSizer14.Add(self.choice2, 0, border=5, flag=wx.TOP)
        self.boxSizer14.Add(self.boxSizer16, 1, border=5, flag=wx.TOP | wx.EXPAND)
        
        self.panel4.SetSizer(self.boxSizer13)
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
        self.ExitButton.Bind(wx.EVT_BUTTON, self.OnExitButton)
        self.PrintButton.Bind(wx.EVT_BUTTON, self.OnPrintButton)
        self.ImportButton.Bind(wx.EVT_BUTTON, self.OnImportButton)
        self.ExportButton.Bind(wx.EVT_BUTTON, self.OnExportButton)
        self.SaveButton.Bind(wx.EVT_BUTTON, self.OnSaveButton)
        self.ClearPlotButton.Bind(wx.EVT_BUTTON, self.OnClearPlotButton)
        self.choice2.Bind(wx.EVT_CHOICE, self.OnSystemChoice)
        self.Bind(wx.EVT_CLOSE, self.OnExitButton)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        #----------------------------------
        # Attributes
        #----------------------------------
        # list of calibration test instances
        self.test = myDatabase.Test()
        # parent
        self.parent = parent.parent
        # a print object for printing reports
        self.print_obj = myPrinter.Printer()
        # list of flow rates to be tested
        self.q = []
        # list of test times
        self.test_times = []
        # list test replicates
        self.replicates = []
        # test results
        self.test_results = []
        # index of flow rate, test time, and replicate held in list of flow rates to be tested (above)
        self.flow_rate_index = 0
        # full scale reference meter object
        self.fs_ref = fs_ref
        # low scale reference meter object
        self.ls_ref = ls_ref
        # default to HF_SYSTEM
        self.system_type = HF_SYSTEM
        # file for saving measurment data
        self.file = myFile.myFile(TEST_RESULTS_FILE_PATH)
        self.file.CreateFile()
        # use call later here to allow time for
        # OPC server to process data change
        # must be called here or AFTER __init__() method
        # of page since page must exist before invoking 
        # SetSystemType()
        wx.CallLater(500, self.parent.SetSystemType)
        # Don't fill on test stopped by default
        self.FillOnTestStopped = False
        # Invoke pulse capture test
        self.call_pulse_capture = None
        #----------------------------------
        # GUI Setup
        #----------------------------------
        self.ClampButton.Show(False)
        self.StartButton.SetForegroundColour(wx.Colour(0, 250, 0))
        self.StopButton.SetForegroundColour(wx.Colour(250, 0, 0))
        self.choice2.SetStringSelection(HF_SYS_LABEL)
        self.SetupLabels()
        self.HideOutputLabels()
        self.InitializePlot()
        # disable controls until user selects system type
        self.EnableCtrls(False)
        self.StopButton.Enable(True)
        self.ClearPlotButton.Enable(True)
        wx.CallLater(500, self.OnSystemChoice, None)
        # Load default profile on startup
        self.ImportProfile(DEFAULT_PROFILE_PATH)
        
    #----------------------------------
    # Event Handler Methods
    #----------------------------------
    def OnTimer(self, event):
        """Event handler for timer events, updates approx time label"""
        self.timeLabel.SetLabel('Time: %d (s)'%(clock() - self.time))

    def OnExitButton(self, event):
        """Event handler for Exit button"""
        self.Destroy()
        
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
        if not self.ValidateProfile():
            return

        # Initialize flow rate profile
        self.flow_rate_index = 0
        self.SetTargetTestTime()
        self.ResetNumberReplicates()

        # Purge test results file
        self.file.CreateFile()
        self.InitializePlot()
        self.StartTimer()

        system_label = self.choice2.GetStringSelection()
        self.parent.SetTargetFlowRate(self.q[self.flow_rate_index])
        if system_label == HF_SYS_LABEL:
            self.parent.StartFlow()
            self.call_pulse_capture = wx.CallLater(WAIT_TIME_HF, self.parent.StartPulseCapture)
            self.DrawFlowRates()
        elif system_label == LF_SYS_LABEL:
            if self.q[self.flow_rate_index] < GRAVITY_PUMP_TRANSITION_FLOW_RATE:
                # Prepare gravity test
                self.parent.FillReservoir()
            else:
                # Start pump test
                self.parent.StartFlow()
                self.call_pulse_capture = wx.CallLater(WAIT_TIME_LF, self.parent.StartPulseCapture)
            
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

    def OnImportButton(self,event):
        path = myUtil.FileDialog(self, 'Import profile', folder=DEFAULT_PROFILE_FOLDER)
        self.ImportProfile(path)

    def OnExportButton(self,event):
        path = myUtil.FileDialog(self, 'Export profile', folder=DEFAULT_PROFILE_FOLDER)
        self.ExportProfile(path)

    def OnSaveButton(self,event):
        self.ExportProfile(DEFAULT_PROFILE)
        
    def OnStopButton(self, event):
        """Event handler for Stop button event"""
        self.throbber.Start()
        self.SetStatusLabels('Stopping Test...')
        self.parent.StopTest()

    def OnRangeChoice(self, evy):
        """Event handler for Flow Range distribution choice event"""
        self.InitializePlot()
        self.DrawFlowRates()
        
    def OnClearPlotButton(self, event):
        """Event handler for Clear Plot button"""
        self.InitializePlot()
        self.file.CreateFile()
        
    def OnSystemChoice(self, evt):
        """Event handler for Flow Meter Type choice event"""
        # type of meterOnPrintButton
        system_label = self.choice2.GetStringSelection()
        assert system_label in [LF_SYS_LABEL, HF_SYS_LABEL]

        if system_label == HF_SYS_LABEL:
            self.system_type = HF_SYSTEM
            self.fs_ref = self.parent.directory.ref1
            self.ls_ref = self.parent.directory.ref2
        elif system_label == LF_SYS_LABEL:
            self.system_type = LF_SYSTEM
            self.fs_ref = self.parent.directory.ref3
            self.ls_ref = self.parent.directory.ref4
        else:
            raise TypeError, 'received unknown system type'
            return
        self.HideOutputLabels()
        self.EnableCtrls(True)
        self.parent.SetSystemType()
        self.SetupLabels()
        self.DrawFlowRates()
        
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
            
        #----------------------------------
        # HMI Events
        #----------------------------------
        elif evt.msg == PLC_RELAY_C14_ID:
            print 'Fill Reservoir Event,', ctime()
            self.SetStatusLabels('Filling Reservoir...')
            self.throbber.Start()
            self.parent.ResetFillingReservoir()
            
        elif evt.msg == MUT_AO_ID:
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
            self.RTD4Label.SetLabel('Temp 4: %0.2f (C)'%(myThermal.DigitalToTemp(evt.value,
                                                                                THERMAL_4_B0,
                                                                                THERMAL_4_B1,
                                                                                THERMAL_4_B2,
                                                                                THERMAL_4_B3) + THERMAL_4_BIAS_CORRECTION))
        elif evt.msg == PLC_RELAY_C20_ID:
            print 'Test Aborted Event', ctime()
            self.ClampButton.Enable(True)
            if self.ClampButton.GetValue():
                self.StartButton.Enable(True)
            self.SetStatusLabels('Safety Check Aborted Test') 
            self.StopTimer()                       
            self.parent.ResetAbortedTest()
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.InitializePlot()
            self.DrawFlowRates()

            # Stop call later execution of pulse capture test
            self.CancelPulseCapture()

            myUtil.MessageFrame(self, MSG_TEST_STOPPED)
            
        elif evt.msg == PLC_RELAY_C21_ID:
            print 'Test Stopped Event', ctime()
            self.parent.ResetStoppedTest()
            
            if self.FillOnTestStopped:
                # Prepare gravity test
                self.parent.FillReservoir()
                self.FillOnTestStopped = False
            else:
                self.ClampButton.Enable(True)
                if self.ClampButton.GetValue():
                    self.StartButton.Enable(True)
                self.SetStatusLabels('Stopped Test')
                self.StopTimer()                       
                self.throbber.Stop()
                self.throbber.Rest()
                self.EnableLabels(False)

                # Stop call later execution of pulse capture test
                self.CancelPulseCapture()
            
        elif evt.msg == PLC_RELAY_C22_ID:
            print 'Test Finished Event', ctime()                      
            self.SetStatusLabels('Test Finished...')
            self.parent.ResetTestFinished()
            self.throbber.Start()                       
            self.SetStatusLabels('Retreiving Test Results...')
            system_label = self.choice2.GetStringSelection()
##            system_type = self.GetSysType()
##            transition_flow_rate = myUtil.GetTransitionFlowRate(system_type)
            self.FillOnTestStopped = False

##            print 'q:', self.q
            print 'flow rate index:', self.flow_rate_index

            # get test results, plot error, update labels
            if self.GetTestResults():

                # If finishing last pulse capture then stop test
                if self.flow_rate_index >= len(self.q)-1 and self.replicate_index <= 1:
                    # Save test results
                    self.parent.CopyTestDataFile()
                    
                    self.throbber.Start()
                    self.SetStatusLabels('Stopping Test...')
                    self.parent.StopTest()
                    myUtil.MsgDialog(self, 'Test Complete')
                    self.throbber.Stop()
                    self.flow_rate_index = 0
                else:
                    # start next pulse capture
                    self.replicate_index += -1
                    if self.replicate_index <= 0:
                        self.flow_rate_index +=1
                        self.parent.SetTargetFlowRate(self.q[self.flow_rate_index])
                        self.SetTargetTestTime()
                        self.ResetNumberReplicates()
                        if system_label == HF_SYS_LABEL:
                            self.parent.StartFlow()
                            # start pulse capture after 60 seconds
                            self.call_pulse_capture = wx.CallLater(WAIT_TIME_HF, self.parent.StartPulseCapture)
                        elif system_label == LF_SYS_LABEL:
                            if self.q[self.flow_rate_index] < GRAVITY_PUMP_TRANSITION_FLOW_RATE:
                                # In gravity mode, stop then fill on flow rate change before starting flow
                                self.FillOnTestStopped = True
                                self.parent.StopTest()
                            else:
                                # Start pump test
                                self.parent.StartFlow()
                                self.call_pulse_capture = wx.CallLater(WAIT_TIME_LF, self.parent.StartPulseCapture)
                    else:
##                        if system_label == HF_SYS_LABEL:
##                            self.parent.StartPulseCapture()
##                        elif system_label == LF_SYS_LABEL:
##                            self.parent.StartTest(self.q[self.flow_rate_index])

                        # Start next pulse capture if flow rate doesn't change
                        self.parent.StartPulseCapture()
                        
                    self.SetStatusLabels('Test in Progress...')
                    self.EnableLabels(True) 
                    self.throbber.Start()  
                    self.parent.ResetTestStarted()
                
        elif evt.msg == PLC_RELAY_C24_ID:
            print 'Closed Clamp Event', ctime()
            self.ClampButton.SetLabel('Open')
            self.ClampButton.SetValue(CLAMP_BUTTON_DOWN)
            self.StopTimer()                       
            self.ExitButton.Enable(False)
            self.StartButton.Enable(True)
            self.SetStatusLabels('Clamp Closed')  
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.parent.ResetClosedClamp()
            
        elif evt.msg == PLC_RELAY_C25_ID:
            print 'Opened Clamp Event', ctime()
            self.ClampButton.SetLabel('Close')
            self.ClampButton.SetValue(CLAMP_BUTTON_UP)
            self.ExitButton.Enable(True)
            self.StartButton.Enable(False)
            self.SetStatusLabels('Clamp Opened')
            self.StopTimer()                       
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.parent.ResetOpenedClamp() 
            self.SetupLabels()
            self.flow_rate_index = 0
            
        elif evt.msg == PLC_RELAY_C30_ID:
            print 'Filled Reservoir Event', ctime()
            self.SetStatusLabels('Reservoir Full')
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.parent.ResetReservoirFilled()

            # Start gravity test
            self.parent.StartFlow()
            self.call_pulse_capture = wx.CallLater(WAIT_TIME_LF, self.parent.StartPulseCapture)
            
        elif evt.msg == PLC_RELAY_C31_ID:
            print 'Test Started Event,', ctime()
            self.SetStatusLabels('Test in Progress...')
            self.ClampButton.Enable(False)
            self.StartButton.Enable(False)
            self.EnableLabels(True) 
            self.throbber.Start()
            self.parent.ResetTestStarted()

        elif evt.msg == PLC_RELAY_C32_ID:
            print 'Flow Started Event,', ctime()
            self.SetStatusLabels('Test in Progress...')

        elif evt.msg == PLC_RELAY_C33_ID:
            print 'Pulse Capture Started Event,', ctime()
            self.SetStatusLabels('Capturing Pulses...')
            
        else:
            print evt.msg, 'here it is'
            raise TypeError, 'Unknown event message (event.msg) received in OnResult() method.'     
        
    #----------------------------------
    # GUI Methods
    #----------------------------------
    def Error(self, msg, stop_test=True):
        """
        Stop test and show error message
        """
        myUtil.ErrorDialog(self, msg)
        if stop_test:
            self.OnStopButton(None)
            
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
        self.SetupLabels()
        
    def DrawFlowRates(self):
        """Draw markers at test flow rates. Disabled for Custom Multipoint"""
        return
    
        xmax, xmin, ymax, ymin = self.figure1.GetAxesLimits()
        h = ymax-ymin
        self.figure1.Scatter(self.q,numpy.zeros(len(self.q))+h*0.05+ymin, 'v', 3, 'r', 'r', 1.0, 1.0)
        self.figure1.SetYLimits(ymax, ymin)
        self.figure1.Draw()
                
        return
    
        assert type(num_tests) == int
        assert type(start) in [float, int]
        assert type(end) in [float, int]
        assert type(is_linear) == int
        assert is_linear in [0,1]
        if start == end:
            self.Error('Starting flow rate must not be same as ending flow rate')
        elif num_tests < 2:
            self.Error('Number of tests must be greater than two')
        else:
            q = myUtil.GetFlowRange(num_tests, start, end, linear = is_linear)
            if len(q) > 1:
                xmax, xmin, ymax, ymin = self.figure1.GetAxesLimits()
                h = ymax-ymin
                self.figure1.Scatter(q,numpy.zeros(len(q))+h*0.05+ymin, 'v', 3, 'r', 'r', 1.0, 1.0)
                self.figure1.SetYLimits(ymax, ymin)
                self.figure1.Draw()
            
            self.q = q

    def SetTargetTestTime(self):
        """
        Set target test time based on current flow rate index
        """
        self.parent.SetTargetTestTime(self.test_times[self.flow_rate_index])
    
    def ResetNumberReplicates(self):
        """
        Returns number of replicates
        """
        print 'resetting replicate index'
        self.replicate_index = self.replicates[self.flow_rate_index]
                                                         
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

    def HideOutputLabels(self):
        """Hide output labels"""
        if self.system_type == LF_SYSTEM:
            self.boxSizer7.Hide(0)
            self.boxSizer7.Hide(1)
            self.boxSizer7.Hide(6)
            self.boxSizer7.Hide(7)
            self.boxSizer7.Show(2)
            self.boxSizer7.Show(3)
            self.boxSizer7.Show(4)
            self.boxSizer7.Show(5)
        elif self.system_type == HF_SYSTEM:
            self.boxSizer7.Hide(2)
            self.boxSizer7.Hide(3)
            self.boxSizer7.Hide(4)
            self.boxSizer7.Hide(5)
            self.boxSizer7.Show(0)
            self.boxSizer7.Show(1)
            self.boxSizer7.Show(6)
            self.boxSizer7.Show(7)
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

    def GetSysType(self):
        assert self.system_type in [HF_SYSTEM, LF_SYSTEM]
        return self.system_type
        
    def EnableCtrls(self, value):
        if self.ClampButton.GetValue():
            self.StartButton.Enable(value)
        else:
            self.StartButton.Enable(False)

        self.ClampButton.Enable(value)
        self.PrintButton.Enable(value)
        self.ImportButton.Enable(value)
        self.ExportButton.Enable(value)
        self.SaveButton.Enable(value)
        
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

    def SaveResults(self, test):
        """
        Save results to file
        """
        self.file.Append('%0.3f, %0.3f\n'%(test.GetRefFlowRate(), test.GetKFactor()))

                
    #----------------------------------
    # Calibration Methods
    #----------------------------------
    def StopOnTransition(self):
        """
        this is required for the PLC to stop the current PID loop and switch to the low flow rate
        PID loop.
        """
        if len(self.q)< self.flow_rate_index+1:
            if self.q[self.flow_rate_index] > myUtil.GetTransitionFlowRate(self.system_type):
                if self.q[self.flow_rate_index+1] < myUtil.GetTransitionFlowRate(self.system_type):
                    self.parent.StopTest()
    
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
        
        # convert mut_count to normal counts (i.e., when calibrating
        # the system increases the FS frequency to 1000 Hz; however this is
        # only for testing and the FS frequency is set to the proper value
        # at the end of the test). Here we need to convert the counts so that
        # we can compare the test result to what we would get if the
        # frequency were set to give the production k-factor (i.e., not the
        # test k-factor).

        storage_volume      = myUtil.GetStorageVolume(self.system_type, self.q[self.flow_rate_index])
        u_storage_volume    = myUtil.GetStorageVolumeUncert(self.system_type, self.q[self.flow_rate_index])

        if myUtil.CalValuesAreOk(ref_count, mut_count, test_time, temp_change):
            if self.q[self.flow_rate_index] > myUtil.GetTransitionFlowRate(self.system_type):
                ref_volume      = ref_count/(self.fs_ref.GetKFactor()*GAL_PER_CUBIC_METER)
                ref_kfactor     = self.fs_ref.GetKFactor()
                print 'fs ref kfactor:', ref_kfactor
                u_ref           = self.fs_ref.GetUncertainty()
                thermal_volume  = myThermal.GetVolume2(temp_change, ref_volume, storage_volume) - ref_volume
                poly_coef       = self.fs_ref.GetCurvefitPoly()
            else:
                ref_volume      = ref_count/(self.ls_ref.GetKFactor()*GAL_PER_CUBIC_METER)
                ref_kfactor     = self.ls_ref.GetKFactor()
                print 'ls ref kfactor:', ref_kfactor
                u_ref           = self.ls_ref.GetUncertainty()
                thermal_volume  = myThermal.GetVolume1(temp_change, ref_volume, storage_volume) - ref_volume
                poly_coef       = self.ls_ref.GetCurvefitPoly()

            print 'ref volume (m^3)', ref_volume
            print 'thermal volume (m^3)', thermal_volume
            # Apply curve fit correction
            uncorrected_flow_rate       = ref_volume/test_time * GAL_PER_CUBIC_METER * SEC_PER_MIN     # convert to gpm
            print 'uncorrected flow rate', uncorrected_flow_rate
            corr_factor     = myUtil.GetCorrectionFactor(poly_coef, uncorrected_flow_rate)
            ref_volume      = ref_volume * corr_factor - thermal_volume     # corrected ref volume (m^3)

            # set reference pulse count from corrected reference volume
            ref_count = ref_kfactor*(ref_volume*GAL_PER_CUBIC_METER)
            kfactor = float(mut_count)/float(ref_volume*GAL_PER_CUBIC_METER)
            flow_rate = ref_volume/test_time * GAL_PER_CUBIC_METER * SEC_PER_MIN

            print ref_kfactor, 'ref k-factor'
            print ref_volume*GAL_PER_CUBIC_METER, 'corrected ref_volume (gal)'
            print ref_count, 'adjusted ref count'
            print 'corrected flow rate:', flow_rate
            print 'mut kfactor:', kfactor

            self.kLabel.SetLabel('K: %0.2f'%(kfactor))
            self.PlotKFactor(flow_rate, kfactor)
            self.file.Append('%0.3f, %0.3f\n'%(flow_rate, kfactor))
            return True    
        else:
            self.Error('Test results are invalid:\nref count: %d\nmut count: %d\ntest time: %0.2f\ntemp change: %0.3f'%(ref_count, mut_count, test_time, temp_change))
            return False

    def CancelPulseCapture(self):
        # Stop pulse capture
        try:
            self.call_pulse_capture.Stop()
        except:
            self.call_pulse_capture = None
        
    #----------------------------------
    # Import/Export Methods
    #----------------------------------
    def ImportProfile(self, path):
        fh = myFile.myFile(path)
        lines = fh.GetTextByLines()
        self.DisplayProfile(lines)

    def ExportProfile(self, path):
        fh = myFile.myFile(path)
        fh.WriteToFile(self.profile_text_ctrl.GetValue())

    def DisplayProfile(self, lines):
        """
        Display profile in text ctrl
        """
        profile = ''.join(lines)
        self.profile_text_ctrl.SetValue(profile)
            
    def ValidateProfile(self):
        """
        Validate profile then parse flow rates, test times, and replilcates
        """
        lines = str(self.profile_text_ctrl.GetValue())
        lines = lines.split('\n')

        self.q = []
        self.test_times = []
        self.replicates = []        

        for line in lines:
            # remove surrounding whitespace
            line.strip()

            # Ensure line is not blank or begins with comment character '#'
            if len(line) and line[0] != '#':
                try:            
                    flow_rate = float(line.split(',')[0].strip())
                    test_time = float(line.split(',')[1].strip())
                    replicate = int(line.split(',')[2].strip())

                    if not self.ValidateFlowRate(flow_rate):
                        return False
                    elif not self.ValidateTestTime(test_time):
                        return False
                    elif not self.ValidateReplicate(replicate):
                        return False
                except:
                    self.Error('Invalid profile', stop_test=False)
                    return False

                self.q.append(flow_rate)
                self.test_times.append(test_time)
                self.replicates.append(replicate)

        print 'flow rates:', self.q
        print 'test times:', self.test_times
        print 'replicates:', self.replicates

        return True

    def ValidateFlowRate(self, value):
        valid = True
        if self.GetSysType() == HF_SYSTEM:
            if not HF_MIN_FLOW_RATE <= value <= HF_MAX_FLOW_RATE:
                valid = False
        elif self.GetSysType() == LF_SYSTEM:
            if not LF_MIN_FLOW_RATE <= value <= LF_MAX_FLOW_RATE:
                valid = False
        else:
            raise TypeError, 'received unknown system type'

        if not valid:
            self.Error('Invalid flow rate in profile', stop_test=False)
            
        return valid

    def ValidateTestTime(self, value):
        valid = True
        if value < 1:
            valid = False

        if not valid:
            self.Error('Invalid test time in profile', stop_test=False)

        return valid

    def ValidateReplicate(self, value):
        valid = True
        if value < 1:
            valid = False

        if not valid:
            self.Error('Invalid replicate in profile', stop_test=False)

        return valid
        
