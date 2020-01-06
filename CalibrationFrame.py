#----------------------------------------------------------------------
# PE Calibration System HMI Program
''' author: Jeff Peery '''
# date: 11/29/2007
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''
 1.17   17/01/05    SPN     -Updated GetTestResults method: Implemented curve fit correction to ref volume
 1.16   16/12/29    SPN     -Updated OnStartButton method: Display error msg if verification check fails
 1.15   16/12/19    SPN     -Updated OnStartButton method: check if MUT is verification meter right after com port
                             is open, move verify error msg to calling method
 1.14   16/12/13    SPN     -Updated OnStartButton method: check if MUT is verification meter before starting calibration
 1.13   16/10/14    SPN     -Updated OnOPCDataChange method: added message display for C20 (safety check, test aborted)
                            to indicate possible causes, such as resevoir level low, e-stop button pressed
 1.12   15/05/01    SPN     -Updated OnClamped method: lock clamp when entering serial #,
                             unlock clamp on no serial #
                            -Updated IsSerialNum method: Don't stop test on error so Lock Clamp stays set
 1.11   15/04/17    SPN     -Hide clamp button
 1.10   15/01/19    SPN     -Updated _init_ method: select PE102 option by default for older rev
 1.09   15/01/13    SPN     -Implemented ZRADC filter by adding IsGoodZRADC and FailProcess methods
                            -Optimized TestMUTAO method by incorporating FailProcess method
                            -Updated _init_ method: select PE202 option by default
 1.08   14/08/27    SPN     -Updated GetTestResults method to echo fs & test frequency
                            -Moved TestMUTAO method call from "test started" event to "pulse capture started" event
                            -Disabled TestMUTAO method call in "test stopped" and "test aborted" events
                            -Updated SetupLabels method to move ':' from end of serial # value to beginning of serial # value
 1.07   14/02/07    SPN     -Disabled temperature indicator for RTD_4_ID event (HF-3/4 downstream) associated with unused thermistor
 1.06   14/01/28    SPN     -Created BuildTestDataDict method invoked in "Test Finished" event used to save results to Syteline database
                            -Added reference to myDbClientApp module used to save results to Syteline database
 1.05   14/01/24    SPN     -Created TestMUTAO method invoked in "Test Started" event to test MUT analog output (4-20 mA)
                            -Created CancelMUTAO method invoked in "Test Stopped" and "Test Aborted" events to cancel MUT analog output test
 1.04   14/01/22    SPN     Updated MUT_AO_ID event to display analog output in gpm and mA
 1.03   13/08/23    SPN     Apply thermal bias correction to temperature display in the OnOPCDataChange method
 1.02   13/08/09    SPN     Added pass/fail sound feature:
                            -added mySound module
                            -updated Pass & Fail methods to invoke sound files
 1.01   13/02/19    SPN     Updated IsSerialNum method to accomodate for extended serial #'s
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
import Modules.myDatabase as myDatabase
import Modules.myUncertainty as myUncertainty
import Modules.myThermal as myThermal
import Modules.myPlot as myPlot
import Modules.myHTMLReport as myReport
import Modules.myPrinter as myPrinter
import Modules.myUtil as myUtil
import Modules.myString as myString
import Modules.myFlowMeters as myFlowMeters
from Modules.myHeader import *
from os.path import exists
import Modules.mySound as mySound
import Modules.myDbClientApp as myDbClientApp
import types
        
#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------
class Frame(wx.Frame):
    def __init__(self, parent, meter_object, fs_ref, ls_ref, system_type):
        #----------------------------------
        # GUI Ctrl Id's
        #----------------------------------
        FRAME_ID            = wx.NewId()
        PANEL_ID            = wx.NewId()
        PANEL2_ID           = wx.NewId()
        PANEL3_ID           = wx.NewId()
        EXIT_BUTTON_ID      = wx.NewId()
        START_BUTTON_ID     = wx.NewId()
        STOP_BUTTON_ID      = wx.NewId()
        CLAMP_BUTTON_ID     = wx.NewId()
        PRINT_BUTTON_ID     = wx.NewId()
        THROB_ID            = wx.NewId()
        TEXT_ID             = wx.NewId()
        K_TEXT_ID           = wx.NewId()
        Q1_TEXT_ID          = wx.NewId()
        Q2_TEXT_ID          = wx.NewId()
        Q3_TEXT_ID          = wx.NewId()
        Q4_TEXT_ID          = wx.NewId()
        MUT_AO_TEXT_ID      = wx.NewId()
        RTD1_TEXT_ID        = wx.NewId()
        RTD2_TEXT_ID        = wx.NewId()
        RTD3_TEXT_ID        = wx.NewId()
        RTD4_TEXT_ID        = wx.NewId()
        NOM_K_TEXT_ID       = wx.NewId()
        IDENTITY_TEXT_ID    = wx.NewId()
        TIME_TEXT_ID        = wx.NewId()
        FLOW_RATE_TEXT_ID   = wx.NewId()
        SERIAL_TEXT_ID      = wx.NewId()
        STATUS_BAR          = wx.NewId()
        STATIC_BOX1         = wx.NewId()
        STATIC_BOX2         = wx.NewId()
        OPT_CHOICE_ID       = wx.NewId()
                     
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
        
        self.figure = myPlot.Figure(self.panel3)

        self.StartButton = wx.Button(id=START_BUTTON_ID, label='Start', name='start', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.StartButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.StopButton = wx.Button(id=STOP_BUTTON_ID, label='Stop', name='stop', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.StopButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))
        
        self.ClampButton = wx.ToggleButton(id=CLAMP_BUTTON_ID, label='Close', name='clamp', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.ClampButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.PrintButton = wx.Button(id=PRINT_BUTTON_ID, label='Print', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.PrintButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.ExitButton = wx.Button(id=EXIT_BUTTON_ID, label='Exit', name='exit', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.ExitButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.OptChoice = wx.Choice(id=OPT_CHOICE_ID, parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), choices=meter_object.GetOptions())
        self.OptChoice.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))
        
        images = [throbImages.catalog[i].getBitmap()
                  for i in throbImages.index
                  if i not in ['eclouds', 'logo']]
        self.throbber = throb.Throbber(self.panel2, -1, images, size=(36, 36),frameDelay = 0.1, reverse=True)
        self.label = wx.StaticText(id=TEXT_ID,label='', name='label', parent=self.panel2, size=wx.Size(400, 40), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.label.SetFont(wx.Font(25, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.MUTAOLabel = wx.StaticText(id=MUT_AO_TEXT_ID,label='', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.MUTAOLabel.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.kLabel = wx.StaticText(id=K_TEXT_ID,label='K:', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.kLabel.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.timeLabel = wx.StaticText(id=TIME_TEXT_ID,label='Time: 0 (s)', name='label', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.timeLabel.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.kNomLabel = wx.StaticText(id=NOM_K_TEXT_ID,label='', name='klabel', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.kNomLabel.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.serialLabel = wx.StaticText(id=SERIAL_TEXT_ID,label='', name='serial label', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.serialLabel.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.identityLabel = wx.StaticText(id=IDENTITY_TEXT_ID,label='', name='id label', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.identityLabel.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.ref1Label = wx.StaticText(id=Q1_TEXT_ID,label='', name='ref1', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.ref1Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.ref2Label = wx.StaticText(id=Q2_TEXT_ID,label='', name='ref2', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.ref2Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.ref3Label = wx.StaticText(id=Q3_TEXT_ID,label='', name='ref3', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.ref3Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.ref4Label = wx.StaticText(id=Q4_TEXT_ID,label='', name='ref4', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.ref4Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.RTD1Label = wx.StaticText(id=RTD1_TEXT_ID,label='', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.RTD1Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.RTD2Label = wx.StaticText(id=RTD2_TEXT_ID,label='', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.RTD2Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.RTD3Label = wx.StaticText(id=RTD3_TEXT_ID,label='', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.RTD3Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.RTD4Label = wx.StaticText(id=RTD4_TEXT_ID,label='', parent=self.panel2, size=wx.Size(200, 25), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.RTD4Label.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Tahoma'))

        self.staticBox1 = wx.StaticBox(id=STATIC_BOX1, label='Test Conditions', parent=self.panel2, size=wx.Size(400, 200), style=0 )
        self.staticBox2 = wx.StaticBox(id=STATIC_BOX2, label='Test Results', parent=self.panel2, size=wx.Size(400, 200), style=0 )
        
        self.timer = wx.Timer(self)
        
        self.statusBar = wx.StatusBar(id=STATUS_BAR, name='statusbar', parent=self, style=wx.ALWAYS_SHOW_SB)
        self.SetStatusBar(self.statusBar)
    
        #----------------------------------
        # GUI Sizers
        #----------------------------------
        '''Sizer layout'''
        # frame
        # Panel
        # -----------------------------------------------
        # |   |---------|  |-------------------------| 1|
        # |   |        2|  | |---------------------|3|  |  
        # |   |         |  | |                    4| |  |
        # |   |start    |  | |throbber             | |  |
        # |   |stop     |  | |label                | |  |
        # |   |clamp    |  | |---------------------| |  |
        # |   |print    |  |                         |  |
        # |   |exit     |  | |---------------------| |  |  
        # |   |         |  | | |--------||-------|5| |  |
        # |   |         |  | | |       6||      7| | |  |
        # |   |         |  | | |        ||       | | |  |
        # |   |         |  | | |time    ||meter  | | |  |
        # |   |         |  | | |q1      ||serial | | |  |
        # |   |         |  | | |q2      ||knom   | | |  |
        # |   |         |  | | |q3      ||Err    | | |  |
        # |   |         |  | | |q4      ||MUT AO | | |  |
        # |   |         |  | | |rtd1    ||       | | |  |
        # |   |         |  | | |rtd2    ||       | | |  |
        # |   |         |  | | |rtd3    ||       | | |  |
        # |   |         |  | | |rtd4    ||       | | |  |
        # |   |         |  | | |--------||-------| | |  |
        # |   |         |  | |---------------------| |  |  
        # |   |         |  |                         |  |
        # |   |         |  |   Panel3 (holds figure) |  |
        # |   |         |  |                         |  |
        # |   |---------|  |-------------------------|  |
        # -----------------------------------------------
        # status bar
        #
        self.boxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.boxSizer2 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer3 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer4 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.boxSizer5 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.boxSizer6 = wx.StaticBoxSizer(box = self.staticBox2, orient=wx.VERTICAL)
        self.boxSizer7 = wx.StaticBoxSizer(box = self.staticBox1, orient=wx.VERTICAL)
        self.boxSizer8 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizer1.Add(self.boxSizer2, 0, border=20, flag=wx.ALL | wx.ALIGN_TOP )
        self.boxSizer1.Add(self.panel2, 1, border=20, flag=wx.ALL | wx.ALIGN_CENTER | wx.EXPAND)

        self.boxSizer2.Add(self.StartButton, 0, border=0, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.StopButton, 0, border=20, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.ClampButton, 0, border=20, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.PrintButton, 0, border=20, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.ExitButton, 0, border=20, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.OptChoice, 0, border=20, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )

        self.boxSizer3.Add(self.boxSizer4, 0, border=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        self.boxSizer3.Add(self.boxSizer5, 1, border=0, flag=wx.ALL | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer3.Add(self.panel3, 1, border=0, flag=wx.ALL | wx.ALIGN_LEFT | wx.EXPAND)

        self.boxSizer4.Add(self.throbber, 0, border=20, flag=wx.ALL | wx.ALIGN_TOP)
        self.boxSizer4.Add(self.label, 1, border=20, flag=wx.ALL | wx.EXPAND | wx.ALIGN_TOP)

        self.boxSizer5.Add(self.boxSizer7, 1, border=10, flag=wx.ALL | wx.ALIGN_TOP | wx.EXPAND)
        self.boxSizer5.Add(self.boxSizer6, 1, border=10, flag=wx.ALL | wx.ALIGN_TOP | wx.EXPAND)
        
        self.boxSizer6.Add(self.identityLabel, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer6.Add(self.serialLabel, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer6.Add(self.MUTAOLabel, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer6.Add(self.kNomLabel, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND) 
        self.boxSizer6.Add(self.kLabel, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)            

        self.boxSizer7.Add(self.timeLabel, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.ref1Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.ref2Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.ref3Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.ref4Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.RTD1Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.RTD2Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.RTD3Label, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
        self.boxSizer7.Add(self.RTD4Label, 0, border=10, flag=wx.ALL | wx.ALIGN_LEFT | wx.EXPAND)
        
        self.boxSizer8.Add(self.figure, 1, border=10, flag=wx.ALL | wx.ALIGN_CENTER | wx.EXPAND)

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
        self.PrintButton.Bind(wx.EVT_BUTTON, self.OnPrintButton)
        self.ExitButton.Bind(wx.EVT_BUTTON, self.OnExitButton)
        self.OptChoice.Bind(wx.EVT_CHOICE, self.OnOptionChoice)
        self.Bind(wx.EVT_CLOSE, self.OnExitButton)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        #----------------------------------
        # Attributes
        #----------------------------------
        # type of calibration system
        self.system_type = system_type
        # MUT meter instance
        self.mut = meter_object
        # full scale reference meter object
        self.fs_ref = fs_ref
        # low scale reference meter object
        self.ls_ref = ls_ref
        # parent
        self.parent = parent.parent
        # holds status of Calibration. options are
        # IDLE, FS, LS.
        self.SetTestStatusIdle()
        # holds number of attempts to calibate
        self.cycle_num = 0
        # database production items instance
        # this object is instantiated on a clamp event
        self.db_item = None
        # a print object for printing reports
        self.print_obj = myPrinter.Printer()
        # Invoke analog output test
        self.call_ao_test = None
        #----------------------------------
        # GUI Ctrl Initializations
        #----------------------------------
        if self.mut.revision == myFlowMeters.PE102_REV_J().revision:
            # default to PE202 standard for current rev
            self.OptChoice.SetStringSelection(myFlowMeters.PE202_STANDARD)
        else:
            # default to PE102 standard for older rev
            self.OptChoice.SetStringSelection(myFlowMeters.OPTION_STANDARD)
        
        self.EnableLabels(False)     
        self.StartButton.Enable(False)
        self.OptChoice.Enable(False)
        self.StopButton.Enable(True)
        self.ClampButton.Show(False)
        self.StartButton.SetForegroundColour(wx.Colour(0, 250, 0))
        self.StopButton.SetForegroundColour(wx.Colour(250, 0, 0))
        self.InitializePlot()
        self.HideTestResultsLabels()
        self.SetupLabels()
        self.HideOutputLabels()
        
    #----------------------------------
    # Event Handler Methods
    #----------------------------------
    def OnOptionChoice(self, evt):
        """
        Event handler for option choice events.
        """
        # enable mut's analog output test by default
        self.mut.test_analog_output = True

        if not self.mut.SetOption(self.OptChoice.GetStringSelection()):
            self.Error('Unable to set option number!')
        self.SetupLabels()
        self.db_item.SetLabel(self.mut.GetLabel())

    def OnTimer(self, event):
        """
        Event handler for timer events, updates approx time label
        """
        self.timeLabel.SetLabel('Time: %d (s)'%(clock() - self.time))

    def OnExitButton(self, event):
        """
        Event handler for exit button events
        """
        self.Destroy()

    def OnPrintButton(self, event):
        """
        Event handler for print button events
        """
        self.PrintReport()
        
    def OnClampButton(self, event):
        """
        Event handler for clamp button events
        """
        if self.ClampButton.GetValue() == CLAMP_BUTTON_DOWN:
            self.ResetCycleNumber()
            self.SetStatusLabels('Closing Clamp...')                       
            self.throbber.Start()
            self.parent.CloseClamp()
        elif self.ClampButton.GetValue() == CLAMP_BUTTON_UP:
            self.SetStatusLabels('Opening Clamp...')
            self.throbber.Start()
            self.parent.OpenClamp()
        else: raise TypeError, 'Unknown Clamp Button value.'

    def OnUnclamped(self):
        """
        Event handler for clamp open.
        This is different that the OnClampButton method. Here
        the system is actually unclamped.
        """
        self.mut.SerialDisconnect()
        
    def OnClamped(self):
        """
        Event handler for Clamp Closed.
        This is different that OnClampButton. Here
        the system is actually clamped.
        """
        # Lock clamp while entering serial #
        self.parent.LockClamp()
        self.ResetCycleNumber()
        serial_num = self.GetSerialNumber()
        self.mut.SetCalibrationDate()
        if serial_num == None:
            # open clamp (set value as up to assure
            # we are opening the clamp)
            self.parent.UnlockClamp()
            self.ClampButton.SetValue(CLAMP_BUTTON_UP) 
            self.OnClampButton(None)
        elif not self.DoesSerialNumExist(serial_num):
            self.db_item = myDatabase.Item(self.mut.GetLabel(), serial_num)
            self.serialLabel.SetLabel('Serial #: %s'%serial_num)
            self.mut.SetSerialNumber(serial_num)
        elif self.DoesSerialNumExist(serial_num):
            dlg = myUtil.YesNoDialog(self, 'This serial number has already been used.\nWould you like to overwrite the old item?')
            if dlg.ShowModal() == wx.ID_YES:
                dlg.Destroy()
                self.db_item = myDatabase.Item(self.mut.GetLabel(), serial_num)
                self.serialLabel.SetLabel('Serial #: %s'%serial_num)
                self.mut.SetSerialNumber(serial_num)
            else:
                self.serialLabel.SetLabel('Serial #:')
                dlg.Destroy()
                self.OnClamped()
        else:
            raise TypeError, 'received invalid type for serial number'

        # Unlock clamp in case operator needs to remove meter
        self.parent.UnlockClamp()

    def OnStartButton(self, event):
        # Lock clamp when starting calibration process
        self.parent.LockClamp()
        self.SetStatusLabels('Connecting to Meter...')
        
        isok = self.mut.SerialConnect(MUT_SERIAL_PORT)
        if isok == None:
            self.Error('Unable to open serial port %d'%MUT_SERIAL_PORT)
            return
        elif isok == False:
            self.Error('MUT serial connection is not open.')
            return

        # Check if trying to calibrate verification meter
        if myUtil.IsVerificationMeter(self.mut):
            self.Error('Verification meter error')
            return

        self.OnUpdateThrobber()
        self.SetStatusLabels('Setting Test Freq..')
        if not self.mut.WriteTestFreq():
            self.Error('Unable to set MUT test frequency.')
            return

        self.OnUpdateThrobber()
        self.SetStatusLabels('Setting FSADC..')
        if not self.mut.WriteFSADC(self.mut.GetTypicalFSADC()):
            self.Error('Unable to set FSADC.')
            return

        self.OnUpdateThrobber()
        self.SetStatusLabels('Setting ZRADC..')
        if not self.mut.WriteZRADC(self.mut.GetTypicalZRADC()):
            self.Error('Unable to set ZRADC.')
            return

        if hasattr(self.mut, 'low_flow_cuttoff'):
            self.OnUpdateThrobber()
            self.SetStatusLabels('Setting Low Flow Cuttoff..')
            self.OnUpdateThrobber()
            if not self.mut.WriteLowFlowCuttoff(value=myFlowMeters.PE102_DEFAULT_LOW_FLOW_CUTTOFF):
                self.Error('Unable to set low flow cutoff.')
                return
                        
        if hasattr(self.mut, 'filter_constant'):
            self.OnUpdateThrobber()
            self.SetStatusLabels('Disabling Filter..')
            self.OnUpdateThrobber()
            if not self.mut.WriteFLTR(self.mut.GetCalibrationFilterConstant()):
                self.Error('Unable to set filter constant.')
                return
        elif not self.mut.WriteDisableFilter():
            self.Error('Unable to disable filter.')
            return

        self.OnUpdateThrobber()   
        self.parent.SetTargetTestTime(self.mut.GetTargetFSTestTime())
        self.parent.StartTest(self.mut.GetFSFlowRate())
        self.StartTimer()

    def OnStopButton(self, event):
        """
        Event handler for stop button events
        """
        self.throbber.Start()
        self.SetStatusLabels('Stopping Test...')
        self.parent.StopTest()

    def OnUpdateThrobber(self):
        i=0
        while i < 5:
            self.throbber.Update(self)
            sleep(0.25)
            i+=1
        
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

        elif evt.msg == PLC_RELAY_C14_ID:
            print 'Filling Reservoir Event,', ctime()
            self.SetStatusLabels('Filling Reservoir...')
            self.throbber.Start()

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
            mA_4_20 = myUtil.DigitalToMilliAmps(evt.value)
            flow_4_20 = myUtil.DigitalToFlowRate(evt.value, self.mut.GetMaxFlowRate())
            self.MUTAOLabel.SetLabel('4-20: %0.3f (gpm) / %0.3f (mA)'%(flow_4_20, mA_4_20))
##            self.MUTAOLabel.SetLabel('4-20: %0.3f (gpm)'%myUtil.DigitalToFlowRate(evt.value, self.mut.GetMaxFlowRate()))
##            self.MUTAOLabel.SetLabel('4-20: %0.3f (mA)'%myUtil.DigitalToMilliAmps(evt.value))
            
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
            self.ClampButton.Enable(True)
            if self.ClampButton.GetValue():
                self.StartButton.Enable(True)
                self.OptChoice.Enable(True)
            self.SetStatusLabels('Safety Check Aborted Test') 
            self.ResetCycleNumber()
            self.parent.ResetAbortedTest() 
            self.SetTestStatusIdle() 
            self.StopTimer()                     
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.HideTestResultsLabels()
            self.InitializePlot()

            # Stop call later execution of analog output test
##            self.CancelMUTAO()

            myUtil.MessageFrame(self, MSG_TEST_STOPPED)
            
        elif evt.msg == PLC_RELAY_C21_ID:
            print 'Test Stopped Event', ctime()
            self.ClampButton.Enable(True)
            if self.ClampButton.GetValue():
                self.StartButton.Enable(True)
                self.OptChoice.Enable(True)
            self.SetStatusLabels('Stopped Test')
            self.ResetCycleNumber()
            self.parent.ResetStoppedTest()
            self.SetTestStatusIdle()
            self.StopTimer()
            self.throbber.Stop()
            self.throbber.Rest()
            self.HideTestResultsLabels()
            self.EnableLabels(False)
            self.InitializePlot()

            # Stop call later execution of analog output test
##            self.CancelMUTAO()
            
        elif evt.msg == PLC_RELAY_C22_ID:
            print 'Test Finished Event', ctime()            
            if self.GetTestStatus() == STATUS_FS_TEST:
                self.SetStatusLabels('FS Test Finished...')
            elif self.GetTestStatus() == STATUS_LS_TEST:
                self.SetStatusLabels('LS Test Finished...')
            else: raise TypeError, 'Received invalid test status type.'

            self.parent.ResetTestFinished()
            
            self.SetStatusLabels('Retreiving Test Results...')
            # get test results, plot error, update labels
            if self.GetTestResults():
                # check test results, calibrate
                # or start LS test
                self.PlotError(self.GetDbItem().GetFSTestData())
                if self.GetTestStatus() == STATUS_LS_TEST:
                    self.PlotError(self.GetDbItem().GetLSTestData())
                    self.SetTestStatusIdle()
                    if self.DidMeterPass():
                        self.SetStatusLabels('Passed Test...')
                        self.parent.PassTest()
                        # Save results to Syteline database before meter is unclamped and gui is destroyed in Pass method below
                        client = myDbClientApp.PostCalibrationDataClient(self.BuildTestDataDict(self.mut, self.GetDbItem(), True))
                        client.start()
                        self.Pass()
                    else:
                        self.parent.FailTest()
                        self.SetStatusLabels('Failed Test...')
                        # Save results to Syteline database before meter is unclamped and gui is destroyed in Fail method below
                        client = myDbClientApp.PostCalibrationDataClient(self.BuildTestDataDict(self.mut, self.GetDbItem(), False))
                        client.start()
                        self.Fail()
                elif self.GetTestStatus() == STATUS_FS_TEST:
                    # set start test prior to drawing. drawing causes
                    # errors in opc writing to plc. also use a sleep here
                    # because opc may not handle multiple
                    # syncronous writes consecutively without time between.
                    # at least one white paper recommends 5 sec wait time. here
                    # 1 second appears to work.
                    self.parent.SetTargetTestTime(self.mut.GetTargetLSTestTime())
                    self.parent.StartTest(self.mut.GetLSFlowRate())
                else: raise TypeError, 'Received invalid test status type.' 
            
            self.throbber.Stop()
            self.throbber.Rest()
                
        elif evt.msg == PLC_RELAY_C24_ID:
            print 'Closed Clamp Event', ctime()
            self.ClampButton.SetLabel('Open')
            self.ClampButton.SetValue(CLAMP_BUTTON_DOWN)
            self.ExitButton.Enable(False)
            self.StartButton.Enable(True)
            self.OptChoice.Enable(True)
            self.SetStatusLabels('Clamp Closed')
            self.StopTimer()                       
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.parent.ResetClosedClamp()
            # create new data base production item instance
            self.OnClamped()
            self.SetTestStatusIdle()
            
        elif evt.msg == PLC_RELAY_C25_ID:
            print 'Opened Clamp Event', ctime()
            self.ClampButton.SetLabel('Close')
            self.ClampButton.SetValue(CLAMP_BUTTON_UP)
            self.ExitButton.Enable(True)
            self.StartButton.Enable(False)
            self.OptChoice.Enable(False)
            self.SetStatusLabels('Clamp Opened')
            self.StopTimer()
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.parent.ResetOpenedClamp() 
            self.SetTestStatusIdle() 
            self.SetupLabels()
            self.OnUnclamped()
            
        elif evt.msg == PLC_RELAY_C30_ID:
            print 'Filled Reservoir Event', ctime()
            self.SetStatusLabels('Reservoir Full')
            self.throbber.Stop()                    
            self.throbber.Rest()
            
        elif evt.msg == PLC_RELAY_C31_ID:
            print 'Test Started Event,', ctime()
            self.SetStatusLabels('Test in Progress...')
            self.ClampButton.Enable(False)
            self.StartButton.Enable(False)
            self.OptChoice.Enable(False)
            self.EnableLabels(True) 
            self.IncrementTestStatus()
            self.throbber.Start()
            self.parent.ResetTestStarted()

        elif evt.msg == PLC_RELAY_C32_ID:
            print 'Flow Started Event,', ctime()
            self.SetStatusLabels('Test in Progress...')

        elif evt.msg == PLC_RELAY_C33_ID:
            print 'Pulse Capture Started Event,', ctime()
            self.SetStatusLabels('Capturing Pulses...')

            # Test analog output at FS flow
            print 'test analog output?: ', self.mut.test_analog_output
            if self.mut.test_analog_output:
                self.TestMUTAO()

        else:
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
        
    def SetStatusLabels(self, msg):
        """
        Set status bar label value
        """
        self.label.SetLabel(msg)
        self.statusBar.SetStatusText(msg)

    def SetKLabel(self, k):
        """
        Set K-factor label value
        """
        assert k != None
        self.kLabel.SetLabel('K: %0.2f'%k)
        
    def HideTestResultsLabels(self):
        """
        Hide test results labels
        """
        self.kLabel.SetLabel('')

    def SetupLabels(self):
        """
        Setup labels
        """
        self.identityLabel.SetLabel(self.mut.GetLabel())
        self.kNomLabel.SetLabel('Ideal K: %d'%self.mut.GetKFactor())
        if self.mut.GetSerialNumber() != None:
            self.serialLabel.SetLabel('Serial #: %s'%self.mut.GetSerialNumber())
        else:
            self.serialLabel.SetLabel('Serial #:')            
        self.ref1Label.SetLabel('Ref 1: (gpm)')     
        self.ref2Label.SetLabel('Ref 2: (gpm)')          
        self.ref3Label.SetLabel('Ref 3: (gpm)')          
        self.ref4Label.SetLabel('Ref 4: (gpm)')
        self.RTD1Label.SetLabel('Temp 1: (C)')
        self.RTD2Label.SetLabel('Temp 2: (C)')
        self.RTD3Label.SetLabel('Temp 3: (C)')
        self.RTD4Label.SetLabel('Temp 4: (C)')
        self.MUTAOLabel.SetLabel('4-20: (mA)')
        self.timeLabel.SetLabel('')

    def HideOutputLabels(self):
        """
        Hide output labels
        """
        self.kLabel.SetLabel('')
        if self.system_type == LF_SYSTEM:
            self.boxSizer7.Hide(1)
            self.boxSizer7.Hide(2)
            self.boxSizer7.Hide(7)
            self.boxSizer7.Hide(8)
            self.boxSizer7.Show(3)
            self.boxSizer7.Show(4)
            self.boxSizer7.Show(5)
            self.boxSizer7.Show(6)
        elif self.system_type == HF_SYSTEM:
            self.boxSizer7.Hide(3)
            self.boxSizer7.Hide(4)
            self.boxSizer7.Hide(5)
            self.boxSizer7.Hide(6)
            self.boxSizer7.Show(1)
            self.boxSizer7.Show(2)
            self.boxSizer7.Show(7)
            self.boxSizer7.Show(8)
        else:
            raise TypeError, 'receive unknown meter type'
        self.boxSizer7.Layout()

    def EnableLabels(self, value):
        """
        Enable labels
        """
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
        self.kNomLabel.Enable(value)
        self.identityLabel.Enable(value)
        self.serialLabel.Enable(value)

    def InitializePlot(self):
        """
        Initialize figure
        """
        self.figure.Initialize()
        self.figure.PlotSpecLimits(PERCENT_ACCURACY,
                                   self.mut.GetAllowance(),
                                   self.mut.GetMaxFlowRate())
        self.figure.SetXLabel(X_LABEL)
        self.figure.SetYLabel(Y_LABEL)
        self.figure.SetXLimits(UPPER_X_LIMIT, LOWER_X_LIMIT)
        self.figure.SetYLimits(UPPER_Y_LIMIT, LOWER_Y_LIMIT)
        self.figure.Draw()
        
    def PlotError(self, test):
        """
        Plot test results
        """
        err = myUtil.GetError(test.GetKFactor(), self.mut.GetKFactor())        
        rate = 100.0*test.GetRefFlowRate()/self.mut.GetMaxFlowRate()
        self.figure.Scatter([rate,], [err,], MARKER_SHAPE, MARKER_SIZE, MARKER_FACE_COLOR, MARKER_EDGE_COLOR, MARKER_EDGE_WIDTH, ALPHA_SCATTER)
        self.figure.SetXLimits(UPPER_X_LIMIT, LOWER_X_LIMIT)
        self.figure.SetYLimits(UPPER_Y_LIMIT, LOWER_Y_LIMIT)
        self.figure.Draw()

    #----------------------------------
    # Database Methods
    #----------------------------------
    def GetSerialNumber(self):
        """
        Prompt operator for serial number
        """
        serial_num = myUtil.SerialNumEntryDialog(self)
        if serial_num != None:
            while not self.IsSerialNum(serial_num):
                serial_num = myUtil.SerialNumEntryDialog(self)
                if serial_num == None: break
        return serial_num

    def IsSerialNum(self, serial_num):
        """
        Check that serial number has valid format
        """
        correct_length = len(serial_num) == SERIAL_NUMBER_LENGTH or len(serial_num) == SERIAL_NUMBER_LENGTH2
        if myString.IsNumber(serial_num) and correct_length:
            return True
        else:
            self.Error('Invalid serial number. Please re-enter the serial number.', stop_test=False)
            return False

    def DoesSerialNumExist(self, serial_num):
        """
        Check if serial number exists in database
        """
        if self.parent.db.HasItem(serial_num):
            return True
        else:
            return False    

    def GetDbItem(self):
        """
        Get database item
        """
        return self.db_item
    
    def AppendDbItemToDb(self):
        """
        Append database item to data base
        """
        # save db item if not None (None occurs if user hits cancel when
        # queried for a serial number
        assert self.GetDbItem() != None
        self.parent.db.AppendItem(self.GetDbItem(), self.GetDbItem().GetSerialNum())       
        
    #----------------------------------
    # Calibration Methods
    #----------------------------------
    def Pass(self):
        """
        Pass Calibration
        """
        # enable filter
        self.SetStatusLabels('Enabling Filter...')
        if not self.mut.WriteEnableFilter():
            self.Error('Unable to enable filter.')
            return

        # set filter value
        if hasattr(self.mut, 'filter_constant'):
            self.SetStatusLabels('Setting Filter Value...')
            if not self.mut.WriteFLTR(self.mut.GetFilterConstant()):
                self.Error('Unable to set filter constant.')
                return

            self.SetStatusLabels('Reading Filter Value...')
            if round(self.mut.ReadFLTR(), 2) != round(self.mut.GetFilterConstant(), 2):
                self.Error('Filter constant not set.')    
                return            
                    
        # set frequency
        self.SetStatusLabels('Setting Output Frequency...')
        if not self.mut.WriteFreq():
            self.Error('Unable to set MUT frequency.')
            return

        # set low flow cuttoff
        if hasattr(self.mut, 'low_flow_cuttoff'):
            self.OnUpdateThrobber()
            self.SetStatusLabels('Setting Low Flow Cuttoff..')
            self.OnUpdateThrobber()
            if not self.mut.WriteLowFlowCuttoff(value=self.mut.GetLowFlowCuttoff()):
                self.Error('Unable to set low flow cutoff.')
                return

        # play pass sound
        mySound.Sound().PlaySound(SOUNDS_PASS)

        # display pass dialog
        dlg = myUtil.PassDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
            
        self.parent.ContinueProgram()
        self.ResetCycleNumber()

        # append the database production item
        # object to the database object
        self.AppendDbItemToDb()

        # stop test
        self.StopTimer()
        self.OnStopButton(None)

        # create and print report
        self.figure.SaveFigure(str(REPORT_IMAGE_FOLDER+'\\'+self.mut.GetSerialNumber()))
        report = myReport.Report(self.GetDbItem().GetTestData(), self.mut, self.mut.GetLabel())
        report.CreateReport()       
        self.PrintReport()

        self.InitializePlot()    
        # kick user out of calibration frame
        self.mut.SerialDisconnect()
        self.parent.OpenClamp()
        self.Destroy()                    
                
    def Fail(self):
        """
        Fail Calibration
        """
        if self.GetCycleNumber() < MAX_CALIBRATION_CYCLES:
            # Calibrate
            self.SetStatusLabels('Calibrating...')
            self.CalibrateMUT()
            #Ensure programmed zradc value is within allowable limit
            if self.IsGoodZRADC():
                self.IncrementCycleNumber()
                # Start Test
                self.InitializePlot()
                self.parent.ContinueProgram()
                self.parent.SetTargetTestTime(self.mut.GetTargetFSTestTime())
                self.parent.StartTest(self.mut.GetFSFlowRate())
        else:
            # enable filter
##            self.mut.SetSerialReadyState()
            if not self.mut.WriteEnableFilter():
                self.Error('Unable to enable filter.')

            # set frequency
##            self.mut.SetSerialReadyState()
            if not self.mut.WriteFreq():
                self.Error('Unable to set MUT frequency.')
            
            # play fail sound
            mySound.Sound().PlaySound(SOUNDS_FAIL)

            self.StopTimer()
            dlg = myUtil.FailDialog(self)
            dlg.ShowModal()
            dlg.Destroy()

            self.parent.ContinueProgram()
            self.parent.StopTest()
            self.ResetCycleNumber()
            self.InitializePlot()
            # kick user out of calibration frame
            self.mut.SerialDisconnect()
            self.parent.OpenClamp()
            self.Destroy()
        
    def GetTestResults(self):
        """
        Get test results

        Correct reference meter volume for theremal changes in storage volume
        (see 'A Measurement Assurance Program for Flow Calibration by the
        Transfer Method') located in the PE Cal Sys Binder.
        """
        # create a new test instance
        test = myDatabase.Test()
        self.OnUpdateThrobber()
        
        # query opc server for results
        temp_change, avg_temp, test_time, ref_count, mut_count = self.parent.GetTestResults()        
        print 'temp change:',temp_change
        print 'avg temp:', avg_temp
        print 'test time:',test_time
        print 'ref count:', ref_count
        print 'mut count:', mut_count
        # convert mut_count to normal counts (i.e., when calibrating
        # the system increases the FS frequency to 1000 Hz; however this is
        # only for testing and the FS frequency is set to the proper value
        # at the end of the test). Here we need to convert the counts so that
        # we can compare the test result to what we would get if the
        # frequency were set to give the production k-factor (i.e., not the
        # test k-factor).
        fs_freq = self.mut.GetFSFreq()
        test_freq = self.mut.GetTestFreq()
        mut_count = mut_count*fs_freq/test_freq
        print 'fs freq:', fs_freq
        print 'test freq:', test_freq
        print 'adjusted count:',mut_count

        self.OnUpdateThrobber()

        if myUtil.CalValuesAreOk(ref_count, mut_count, test_time, temp_change):
            if self.GetTestStatus() == STATUS_FS_TEST:
                storage_volume      = myUtil.GetStorageVolume(self.system_type, self.mut.GetFSFlowRate())
                u_storage_volume    = myUtil.GetStorageVolumeUncert(self.system_type, self.mut.GetFSFlowRate())
                ref_volume          = ref_count/(self.fs_ref.GetKFactor()*GAL_PER_CUBIC_METER)
                ref_kfactor         = self.fs_ref.GetKFactor()
                u_ref               = self.fs_ref.GetUncertainty()
                thermal_volume  = myThermal.GetVolume2(temp_change, ref_volume, storage_volume) - ref_volume
                poly_coef       = self.fs_ref.GetCurvefitPoly()
            elif self.GetTestStatus() == STATUS_LS_TEST:
                storage_volume      = myUtil.GetStorageVolume(self.system_type, self.mut.GetLSFlowRate())
                u_storage_volume    = myUtil.GetStorageVolumeUncert(self.system_type, self.mut.GetLSFlowRate())
                ref_volume          = ref_count/(self.ls_ref.GetKFactor()*GAL_PER_CUBIC_METER)
                ref_kfactor         = self.ls_ref.GetKFactor()
                u_ref               = self.ls_ref.GetUncertainty()
                thermal_volume  = myThermal.GetVolume1(temp_change, ref_volume, storage_volume) - ref_volume
                poly_coef       = self.ls_ref.GetCurvefitPoly()
            else:
                raise TypeError, 'Received invalid test status type.'

            # Apply corrections to ref volume
            ref_volume = myUtil.GetCorrectedVolume(ref_volume, thermal_volume, test_time, poly_coef)

            # set reference pulse count from corrected reference volume
            ref_count = ref_kfactor*(ref_volume*GAL_PER_CUBIC_METER)
            print ref_kfactor, 'ref k-factor'
            print ref_volume*GAL_PER_CUBIC_METER, 'corrected ref_volume (gal)'
            print ref_count, 'adjusted ref count'

            # calculate and save measurement uncertainties                                               
            test.SetUncertainties(myUncertainty.GetUncertainty(temp_change,
                                                               test_time,
                                                               storage_volume,
                                                               ref_volume,
                                                               mut_count,
                                                               u_ref*ref_volume,
                                                               u_storage_volume))

            # save calibration data to database item test object
            test.SetRefPulseCount(float(ref_count))
            test.SetMUTPulseCount(float(mut_count))
            test.SetTime(float(test_time))
            test.SetTemp(float(avg_temp))
            test.SetRefVolume(float(ref_volume*GAL_PER_CUBIC_METER))

            kfactor = float(mut_count)/float(ref_volume*GAL_PER_CUBIC_METER)
            self.SetKLabel(kfactor)

            # append calibration test to database item
            if self.GetTestStatus() == STATUS_FS_TEST:
                self.GetDbItem().AppendCalTest(DB_FS_INDEX, test)
            elif self.GetTestStatus() == STATUS_LS_TEST:
                self.GetDbItem().AppendCalTest(DB_LS_INDEX, test)
            else: raise TypeError, 'Received invalid test status type.'
            
            return True    
        else:
            self.Error('Test results are invalid:\nref count: %d\nmut count: %d\ntest time: %0.2f\ntemp change: %0.3f'%(ref_count, mut_count, test_time, temp_change))
            return False
        
    def CalibrateMUT(self):
        fsadc, zradc = self.GetCalibrationValues()

        # save calibration values to database
        if fsadc == None:
            self.Error('FSADC value is NoneType')
            return
        if zradc == None:
            self.Error('ZRADC value is NoneType')
            return
            
        self.SetStatusLabels('Setting Calibration Values...')
        self.OnUpdateThrobber()
##        self.mut.SetSerialReadyState()
        self.OnUpdateThrobber()
        if not self.mut.WriteZRADC(zradc):
            self.Error('Error writing ZRADC to meter')
        self.OnUpdateThrobber()
##        self.mut.SetSerialReadyState()
        self.OnUpdateThrobber()
        if not self.mut.WriteFSADC(fsadc):
            self.Error('Error writing FSADC to meter')
        self.OnUpdateThrobber()
        self.GetDbItem().SetFSADC(fsadc)
        self.GetDbItem().SetZRADC(zradc)
        return True

    def GetCalibrationValues(self):
        self.SetStatusLabels('Getting Calibration Values...')
        
        self.OnUpdateThrobber()
##        self.mut.SetSerialReadyState() 
        self.OnUpdateThrobber()
        fsadc = self.mut.ReadFSADC()
        self.OnUpdateThrobber()
##        self.mut.SetSerialReadyState()  
        self.OnUpdateThrobber()
        zradc = self.mut.ReadZRADC()
        self.OnUpdateThrobber()
        
        fs_item = self.GetDbItem().GetFSTestData()
        ls_item = self.GetDbItem().GetLSTestData()
        if fsadc == None: self.Error('FSADC value is NoneType')
        if zradc == None: self.Error('ZRADC value is NoneType')
        # coefficients for Actual measurements
        A1 = fs_item.GetMUTPulseCount()/(fs_item.GetTime()*self.mut.GetFSFreq())
        A2 = ls_item.GetMUTPulseCount()/(ls_item.GetTime()*self.mut.GetFSFreq())
        # coefficients for Ideal measurements
        B1 = (fs_item.GetRefPulseCount()*self.mut.GetKFactor()/self.fs_ref.GetKFactor())/(fs_item.GetTime()*self.mut.GetFSFreq())
        B2 = (ls_item.GetRefPulseCount()*self.mut.GetKFactor()/self.ls_ref.GetKFactor())/(ls_item.GetTime()*self.mut.GetFSFreq())
        # calculate FSADC and ZRADC such that K == K_nom
        A = numpy.matrix([[1,1.0/B1-1],[1,1.0/B2-1]])
        b = numpy.matrix([[A1*(fsadc-zradc)/B1 + zradc/B1],[A2*(fsadc-zradc)/B2 + zradc/B2]])
        x = numpy.linalg.linalg.solve(A,b)
        x = numpy.array(x)
        print x[0], x[1], 'fsadc, zradc'
        return float(x[0]), float(x[1])

    def DidMeterPass(self):
        assert len(self.GetDbItem().GetTestData()) > FS_TEST_INDEX
        assert len(self.GetDbItem().GetTestData()) > LS_TEST_INDEX
        fs_err = myUtil.GetError(self.GetDbItem().GetFSTestData().GetKFactor(), self.mut.GetKFactor())
        ls_err = myUtil.GetError(self.GetDbItem().GetLSTestData().GetKFactor(), self.mut.GetKFactor())
        assert fs_err != None
        assert ls_err != None

        print '======== Pulse Ouput Results ========'
        print 'fs error: ', fs_err
        print 'ls error: ', ls_err

        # use tighter restrictions if passing on first test
        if self.cycle_num == 0:
            # compare results of fs and ls accuracy against spec
            fs_limit = 0.25
            ls_limit = 0.25
            print 'fs limit: ',fs_limit
            print 'ls limit: ',ls_limit
            if abs(fs_err) <= fs_limit:
                if abs(ls_err) <= ls_limit:
                    return True
                else: return False
            else: return False
        else:
            # compare results of fs and ls accuracy against spec
            fs_limit = PERCENT_ACCURACY + 100.0*self.mut.GetAllowance()/self.GetDbItem().GetFSTestData().GetRefFlowRate() - 0.5
            ls_limit = PERCENT_ACCURACY + 100.0*self.mut.GetAllowance()/self.GetDbItem().GetLSTestData().GetRefFlowRate() - 0.5
            print 'fs limit: ',fs_limit
            print 'ls limit: ',ls_limit
            if abs(fs_err) <= fs_limit:
                if abs(ls_err) <= ls_limit:
                    return True
                else: return False
            else: return False

    def ResetCycleNumber(self):
        self.cycle_num = 0

    def IncrementCycleNumber(self):
        self.cycle_num += 1

    def GetCycleNumber(self):
        return self.cycle_num

    def GetTestStatus(self):
        return self.status

    def SetTestStatusIdle(self):
        self.status = STATUS_IDLE

    def IncrementTestStatus(self):
        if self.status == STATUS_IDLE:
            self.status = STATUS_FS_TEST
        elif self.status == STATUS_FS_TEST:
            self.status = STATUS_LS_TEST
        elif self.status == STATUS_LS_TEST:
            self.status = STATUS_IDLE
        else:
            raise TypeError, 'Received invalid status type.'
        
    def PrintReport(self):
        if exists(REPORT_FOLDER+'\\'+self.mut.GetSerialNumber()+'.htm'):
            if not self.print_obj.Print(str(REPORT_FOLDER+'\\'+self.mut.GetSerialNumber()+'.htm')):
                self.Error('Problem with Internet Explorer. Unable to print', stop_test=False)
        else:
            self.Error('Unable to find calibration report for serial number: %s'%self.mut.GetSerialNumber(), stop_test=False)

    def TestMUTAO(self):
        # Test analog output at FS flow
        if self.GetTestStatus() == STATUS_FS_TEST:
            mut_ao = int(self.parent.GetMUTAO())
            if self.system_type == HF_SYSTEM:
                ref_ao = int(self.parent.GetRef1AO())
                ref_max_q = REF1_MAX_Q
            else:
                ref_ao = int(self.parent.GetRef3AO())
                ref_max_q = REF3_MAX_Q

            mut_max_q = self.mut.GetMaxFlowRate()
            mut_flowrate = myUtil.DigitalToFlowRate(mut_ao, mut_max_q)
            ref_flowrate = myUtil.DigitalToFlowRate(ref_ao, ref_max_q)
            accuracy_limit = self.mut.GetReasonableAccuracyLimit()
            accuracy_error = myUtil.GetError(mut_flowrate, ref_flowrate)
            test_passed = abs(accuracy_error) <= accuracy_limit

            print '======== Analog Ouput Results ========'
            print 'mut ao: ', mut_ao
            print 'ref ao: ', ref_ao
            print 'mut flowrate: ', mut_flowrate
            print 'ref flowrate: ', ref_flowrate
            print '4-20 error: ', accuracy_error
            print '4-20 limit: ', accuracy_limit
            
            if not test_passed:
                msg = 'ERROR: Failed 4-20mA Test: %0.2f%% \n'%accuracy_error
                msg += '4-20mA Accuracy Limit: %0.2f%%'%accuracy_limit
                myUtil.MessageFrame(self, msg)
                self.FailProcess()
            return
        else:
            return

    def CancelMUTAO(self):
        # Stop analog output test
        try:
            self.call_ao_test.Stop()
        except:
            self.call_ao_test = None

    def IsGoodZRADC(self):
        zradc = self.GetDbItem().GetZRADC()
        if not self.mut.zradc_limit_lower <= zradc <= self.mut.zradc_limit_upper:
            msg = 'ERROR: Failed ZRADC Test: %0.2f \n'%zradc
            msg += 'ZRADC Limit (lower/upper): %0.2f/%0.2f'%(self.mut.zradc_limit_lower, self.mut.zradc_limit_upper)
            myUtil.MessageFrame(self, msg)
            self.FailProcess()
            return False

        return True

    def FailProcess(self):
        """
        Force fail test condition, save test results, and abort process
        """
##                self.Error(msg)
        self.OnStopButton(None)
##                self.IncrementCycleNumber()
        self.parent.FailTest()
        self.SetStatusLabels('Failed Test...')
        # Save results to Syteline database before meter is unclamped and gui is destroyed in Fail method below
        client = myDbClientApp.PostCalibrationDataClient(self.BuildTestDataDict(self.mut, self.GetDbItem(), False))
        client.start()
        # Set cycle number to max to force test completed
        self.cycle_num = MAX_CALIBRATION_CYCLES
        self.Fail()
        self.throbber.Stop()
        self.throbber.Rest()
       
    def BuildTestDataDict(self, meter_object, db_item, success):
        """
        Build dictionary of test data for inserting test results into server database
        """
        # build insert string
        # must be in order: [SERIAL_NUMBER], [V_Q3_1], [V_Q3_2], [V_Q3_3], [V_Q1_1], [V_Q1_2], [V_Q1_3], [T_Q3_1], [T_Q3_2], [T_Q3_3], [T_Q1_1], [T_Q1_2], [T_Q1_3], K_Q3_1, K_Q3_2, K_Q3_3, K_Q1_1, K_Q1_2, K_Q1_3, U_K, REF_K_Q3, REF_K_Q1, FSADC, ZRADC, DATE_TIME, PASS    
        data = {}
        data[myDbClientApp.TEST_RESULT_SERIAL_NUMBER_KEY] = meter_object.GetSerialNumber()

        # Q3 K factors- only one replicate per pulse capture
        try: data[myDbClientApp.TEST_RESULT_K_Q3_1_KEY] = db_item.GetTestData()[myDatabase.DB_FS_INDEX].GetKFactor()
        except: data[myDbClientApp.TEST_RESULT_K_Q3_1_KEY] = 0

        data[myDbClientApp.TEST_RESULT_K_Q3_2_KEY] = 0
        data[myDbClientApp.TEST_RESULT_K_Q3_3_KEY] = 0        
            
        # Q1 factors
        try: data[myDbClientApp.TEST_RESULT_K_Q1_1_KEY] = db_item.GetTestData()[myDatabase.DB_LS_INDEX].GetKFactor()
        except: data[myDbClientApp.TEST_RESULT_K_Q1_1_KEY] = 0

        data[myDbClientApp.TEST_RESULT_K_Q1_2_KEY] = 0
        data[myDbClientApp.TEST_RESULT_K_Q1_3_KEY] = 0

        # Q3 times
        try: data[myDbClientApp.TEST_RESULT_T_Q3_1_KEY] = db_item.GetTestData()[myDatabase.DB_FS_INDEX].GetTime()
        except: data[myDbClientApp.TEST_RESULT_T_Q3_1_KEY] = 0

        data[myDbClientApp.TEST_RESULT_T_Q3_2_KEY] = 0
        data[myDbClientApp.TEST_RESULT_T_Q3_3_KEY] = 0

        # Q1 times
        try: data[myDbClientApp.TEST_RESULT_T_Q1_1_KEY] = db_item.GetTestData()[myDatabase.DB_LS_INDEX].GetTime()
        except: data[myDbClientApp.TEST_RESULT_T_Q1_1_KEY] = 0

        data[myDbClientApp.TEST_RESULT_T_Q1_2_KEY] = 0
        data[myDbClientApp.TEST_RESULT_T_Q1_3_KEY] = 0

        # Q3 volumes
        try: data[myDbClientApp.TEST_RESULT_V_Q3_1_KEY] = db_item.GetTestData()[myDatabase.DB_FS_INDEX].GetRefVolume()
        except: data[myDbClientApp.TEST_RESULT_V_Q3_1_KEY] = 0

        data[myDbClientApp.TEST_RESULT_V_Q3_2_KEY] = 0
        data[myDbClientApp.TEST_RESULT_V_Q3_3_KEY] = 0

        # Q1 volumes
        try: data[myDbClientApp.TEST_RESULT_V_Q1_1_KEY] = db_item.GetTestData()[myDatabase.DB_LS_INDEX].GetRefVolume()
        except: data[myDbClientApp.TEST_RESULT_V_Q1_1_KEY] = 0

        data[myDbClientApp.TEST_RESULT_V_Q1_2_KEY] = 0
        data[myDbClientApp.TEST_RESULT_V_Q1_3_KEY] = 0

        data[myDbClientApp.TEST_RESULT_UNCERTAINTY_KEY] = SYSTEM_K_UNCERTAINTY
        
        # Q3 Ref K Factor
        try: data[myDbClientApp.TEST_RESULT_REF_K_Q3_KEY] = db_item.GetTestData()[myDatabase.DB_FS_INDEX].GetTestRefKFactor()
        except: data[myDbClientApp.TEST_RESULT_REF_K_Q3_KEY] = 0
            
        # Q1 Ref K Factor
        try: data[myDbClientApp.TEST_RESULT_REF_K_Q1_KEY] = db_item.GetTestData()[myDatabase.DB_LS_INDEX].GetTestRefKFactor()
        except: data[myDbClientApp.TEST_RESULT_REF_K_Q1_KEY] = 0
            
        data[myDbClientApp.TEST_RESULT_FSADC_KEY] = db_item.GetFSADC()
        data[myDbClientApp.TEST_RESULT_ZRADC_KEY] = db_item.GetZRADC()

        # Use calibration date/time instead of today's date/time to match actual cal report
        # Shave off miliseconds from calibration date/time
        data[myDbClientApp.TEST_RESULT_DATE_TIME_KEY] = meter_object.GetCalibrationDate().split('.')[0]
##        data[myDbClientApp.TEST_RESULT_DATE_TIME_KEY] = myDateTime.GetISOFormat(myDateTime.GetToday(), isUseTime=True)

        data[myDbClientApp.TEST_RESULT_PASS_KEY] = success
        data[myDbClientApp.TEST_RESULT_BENCH_ID_KEY] = BENCH_ID

        # set all NoneType values to zero
        # The SQL server handles none type; however when searching through tables containing
        # nonetype values the search may not execute properly.
        for key in data.keys():
            if type(data[key]) == types.NoneType:
                    data[key] == 0

        print '---test data dictionary---'
        print data
        return data
