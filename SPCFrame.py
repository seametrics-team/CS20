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
  1.13  17/01/05    SPN     -Updated GetTestResults method: Implemented curve fit correction to ref volume
  1.12  16/10/14    SPN     -Updated OnOPCDataChange method: added message display for C20 (safety check, test aborted)
  1.11  15/05/01    SPN     -Updated OnClamped method: added ResetCycleNumber call
  1.10  15/01/19    SPN     -Updated VerifyFlowMeterIsCheckStandard method: display error msg if FSADC can't be retrieved
  1.09  14/05/12    JAH     -Added some diagnostics to the GetTestResults method for viewing the number of pulses captured by both meters
                            -Reverted changes from rev 1.08 to deactivate kfactor correction
  1.08  14/05/09    SPN     -Updated GetTestResults method where ref_kfactor, ref_volume references corrected k-factor
                            based on current flow rate
  1.07  14/05/08    SPN     -Updated GetTestResults method to include flow rate and date in test results file
  1.06  14/02/07    SPN     -Disabled temperature indicator for RTD_4_ID event (HF-3/4 downstream) associated with unused thermistor
  1.05  13/10/03    SPN     Updated GetTestResults method to generate secondary copy of SPC test results files for WinSPC experiment
  1.04  13/09/25    SPN     Updated VerifyFlowMeterIsCheckStandard method by replacing fsadc constants with myHeader variables
  1.03  13/08/23    SPN     Apply thermal bias correction to temperature display in the OnOPCDataChange method
  1.02  13/06/27    SPN     -Added calibrated ADC values in VerifyFlowMeterIsCheckStandard method for LF reference meter
  1.01  13/03/13    SPN     -Added calibrated ADC values in VerifyFlowMeterIsCheckStandard method for HF reference meter
                            -Updated OnStartButton method for StartPulseCapture delay from 5 minutes to
                            2 minutes
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
import Modules.myDateTime as myDateTime
import Modules.myUtil as myUtil
import Modules.myThermal as myThermal
import Modules.myString as myString
import Modules.myFile as myFile
from Modules.myHeader import *
from os.path import exists
import datetime

TEST_TIME = 120
 
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
        EXIT_BUTTON_ID      = wx.NewId()
        START_BUTTON_ID     = wx.NewId()
        STOP_BUTTON_ID      = wx.NewId()
        CLAMP_BUTTON_ID     = wx.NewId()
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
        STATUS_BAR          = wx.NewId()
        STATIC_BOX1         = wx.NewId()
        STATIC_BOX2         = wx.NewId()
                     
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

        self.panel = wx.Panel(id=PANEL_ID, name='panel', parent=self, style=wx.BORDER_SUNKEN)
        self.panel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.panel2 = wx.Panel(id=PANEL2_ID, name='panel2', parent=self.panel, style=wx.BORDER_SUNKEN)
        self.panel2.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.StartButton = wx.Button(id=START_BUTTON_ID, label='Start', name='start', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.StartButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.StopButton = wx.Button(id=STOP_BUTTON_ID, label='Stop', name='stop', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.StopButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))
        
        self.ClampButton = wx.ToggleButton(id=CLAMP_BUTTON_ID, label='Close', name='clamp', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.ClampButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.ExitButton = wx.Button(id=EXIT_BUTTON_ID, label='Exit', name='exit', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.ExitButton.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

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
        # |   |         |  |                         |  |
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

        self.boxSizer1.Add(self.boxSizer2, 0, border=20, flag=wx.ALL | wx.ALIGN_TOP )
        self.boxSizer1.Add(self.panel2, 1, border=20, flag=wx.ALL | wx.ALIGN_CENTER | wx.EXPAND)

        self.boxSizer2.Add(self.StartButton, 0, border=0, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.StopButton, 0, border=20, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.ClampButton, 0, border=20, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )
        self.boxSizer2.Add(self.ExitButton, 0, border=20, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL )

        self.boxSizer3.Add(self.boxSizer4, 0, border=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        self.boxSizer3.Add(self.boxSizer5, 1, border=0, flag=wx.ALL | wx.ALIGN_LEFT | wx.EXPAND)
      
        self.boxSizer4.Add(self.throbber, 0, border=20, flag=wx.ALL | wx.ALIGN_TOP)
        self.boxSizer4.Add(self.label, 1, border=20, flag=wx.ALL | wx.EXPAND | wx.ALIGN_TOP)

        self.boxSizer5.Add(self.boxSizer7, 1, border=10, flag=wx.ALL | wx.ALIGN_TOP | wx.EXPAND)
        self.boxSizer5.Add(self.boxSizer6, 1, border=10, flag=wx.ALL | wx.ALIGN_TOP | wx.EXPAND)
        
        self.boxSizer6.Add(self.identityLabel, 0, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.EXPAND)
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
        # holds number of calibration replicates per calibration point
        self.cycle_num = 0
        #----------------------------------
        # GUI Ctrl Initializations
        #----------------------------------
        self.EnableLabels(False)     
        self.StartButton.Enable(False)
        self.ExitButton.Enable(False)
        self.StopButton.Enable(True)  
        self.StopButton.Enable(False)
        self.ClampButton.Show(False)
        self.StartButton.SetForegroundColour(wx.Colour(0, 250, 0))
        self.StopButton.SetForegroundColour(wx.Colour(250, 0, 0))

        self.HideTestResultsLabels()
        self.SetupLabels()
        self.HideOutputLabels()
        self.Layout()

    #----------------------------------
    # Event Handler Methods
    #----------------------------------
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
        self.ResetCycleNumber()

    def VerifyFlowMeterIsCheckStandard(self):
        """
        Used to confirm that the meter under test is the check standard
        check FSADC is a match
        """
        fsadc = str(self.mut.ReadFSADC())[0:7]

        if fsadc == None:
            self.Error('Unable to read FSADC, please try again.', stop_test=False)
            self.parent.StopTest()
            return False

        # Calibrated reference meter on 03/13/2013
        # fsadc: 426.009, zradc: 0.60372
        if self.system_type == HF_SYSTEM and fsadc[0:7] == HF_VERIFICATION_FSADC:
            return True
        # Calibrated LF reference meter on 06/27/2013
        # fsadc:  286.215, zradc: 0.54904
        elif self.system_type == LF_SYSTEM and fsadc[0:7] == LF_VERIFICATION_FSADC:
            return True
        else:
            self.Error('HEY! This is not the correct flow meter!', stop_test=False)
            self.parent.StopTest()
            return False
        
    def OnStartButton(self, event):
        """
        Event handler for start button events
        """
        self.status = STATUS_FS_TEST
        # Open Serial Connection to MUT
        self.SetStatusLabels('Connecting to Meter...')
        isok = self.mut.SerialConnect(MUT_SERIAL_PORT)
        if isok == None:
            self.Error('Unable to open serial port %d'%MUT_SERIAL_PORT)
        elif isok == False:
            self.Error('MUT serial connection is not open.')
        else:
            if not self.VerifyFlowMeterIsCheckStandard():
                return
            self.parent.SetTargetTestTime(TEST_TIME)
            self.parent.SetTargetFlowRate(self.mut.GetFSFlowRate())
            # flush system here. there may be some issue collecting the first
            # k-factor. this delay should allow system to stabilize.
            wx.CallLater(2*60000, self.parent.StartPulseCapture)
            self.parent.StartFlow()
        
    def OnStopButton(self, event):
        """
        Event handler for stop button events
        """
        self.status = STATUS_IDLE
        self.throbber.Start()
        self.SetStatusLabels('Stopping Test...')
        self.parent.StopTest()
    
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
            self.RTD1Label.SetLabel('Temp 1: %0.2f (C)'%(myThermal.DigitalToTemp(evt.value,
                                                                                THERMAL_1_B0,
                                                                                THERMAL_1_B1,
                                                                                THERMAL_1_B2,
                                                                                THERMAL_1_B3) + THERMAL_1_BIAS_CORRECTION))
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
            self.SetStatusLabels('Safety Check Aborted Test') 
            self.ResetCycleNumber()
            self.parent.ResetAbortedTest() 
            self.SetTestStatusIdle() 
            self.StopTimer()                     
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.HideTestResultsLabels()

            myUtil.MessageFrame(self, MSG_TEST_STOPPED)
            
        elif evt.msg == PLC_RELAY_C21_ID:
            print 'Test Stopped Event', ctime()
            self.ClampButton.Enable(True)
            if self.ClampButton.GetValue():
                self.StartButton.Enable(True)
            self.SetStatusLabels('Stopped Test')
            self.ResetCycleNumber()
            self.parent.ResetStoppedTest()
            self.SetTestStatusIdle()
            self.StopTimer()
            self.throbber.Stop()
            self.throbber.Rest()
            self.HideTestResultsLabels()
            self.EnableLabels(False)
            
        elif evt.msg == PLC_RELAY_C22_ID:
            print 'Test Finished Event', ctime()            
            if self.GetTestStatus() == STATUS_FS_TEST:
                self.SetStatusLabels('FS Test Finished...')
            elif self.GetTestStatus() == STATUS_LS_TEST:
                self.SetStatusLabels('LS Test Finished...')
            else: raise TypeError, 'Received invalid test status type.'

            self.StopTimer()
            self.parent.ResetTestFinished()
            sleep(1)
            
            self.SetStatusLabels('Retreiving Test Results...')
            # get test results, update labels
            if self.GetTestResults():

                self.IncrementCycleNumber()
                if self.GetTestStatus() == STATUS_FS_TEST:
                    if self.GetCycleNumber() < NUM_REPLICATES:
                        self.parent.ContinueProgram()
                        # use a sleep here
                        # because opc may not handle multiple
                        # syncronous writes consecutively without time between.
                        # at least one white paper recommends 5 sec wait time. here
                        # 1 second appears to work.
                        self.parent.SetTargetFlowRate(self.mut.GetFSFlowRate())
                        sleep(1)
                        self.parent.StartFlow()  
                        sleep(1)
                        self.parent.StartPulseCapture()
                        sleep(1)
                        self.StartTimer()  
                        self.parent.ResetTestStarted()
                    else:
                        # set flow rate above transition so pump may slow down
                        # before closing valve.
                        self.parent.SetTargetFlowRate(2.0)
                        sleep(1)
                        self.IncrementTestStatus()
                        sleep(1)
                        self.ResetCycleNumber()
                        sleep(1)
                        self.parent.SetTargetFlowRate(self.mut.GetLSFlowRate())
                        sleep(1)
                        self.parent.StartFlow()  
                        sleep(1)
                        wx.CallLater(60000, self.parent.StartPulseCapture)
                        sleep(1)
                        self.StartTimer()  
                        self.parent.ResetTestStarted()

                elif self.GetTestStatus() == STATUS_LS_TEST:
                    if self.GetCycleNumber() < NUM_REPLICATES:
                        self.parent.ContinueProgram()
                        # use a sleep here
                        # because opc may not handle multiple
                        # syncronous writes consecutively without time between.
                        # at least one white paper recommends 5 sec wait time. here
                        # 1 second appears to work.
                        sleep(1)
                        self.parent.SetTargetFlowRate(self.mut.GetLSFlowRate())
                        sleep(1)
                        self.parent.StartFlow()  
                        sleep(1)
                        self.parent.StartPulseCapture()
                        sleep(1)
                        self.StartTimer()  
                        self.parent.ResetTestStarted()
                    else:                        
                        self.parent.ContinueProgram()
                        self.ResetCycleNumber()
                        self.SetTestStatusIdle()
                        wx.CallLater(5000, self.SetStatusLabels, 'Test is complete.')
                        self.parent.StopTest()
                        self.StopButton.Enable(True)
                        if self.system_type == HF_SYSTEM:
                            myFile.myFile(LAST_HF_TEST_DATE_FILE).WriteToFile(datetime.datetime.today().isoformat(' '))
                        else:
                            myFile.myFile(LAST_LF_TEST_DATE_FILE).WriteToFile(datetime.datetime.today().isoformat(' '))
                            
                else: raise TypeError, 'Received invalid test status type.'
                
        elif evt.msg == PLC_RELAY_C24_ID:
            print 'Closed Clamp Event', ctime()
            self.ClampButton.SetLabel('Open')
            self.ClampButton.SetValue(CLAMP_BUTTON_DOWN)
            self.ExitButton.Enable(False)
            self.StartButton.Enable(True)
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
            self.SetStatusLabels('Clamp Opened')
            self.StopTimer()
            self.throbber.Stop()                    
            self.throbber.Rest()
            self.parent.ResetOpenedClamp() 
            self.SetTestStatusIdle() 
            self.SetupLabels()
            self.OnUnclamped()
##            try:
##                d = myFile.myFile(LAST_HF_TEST_DATE_FILE).GetTextByLines()
##                if len(d) == 0:
##                    is_test = True
##                elif myDateTime.IsStringDate(d[0]):            
##                    dt = datetime.datetime.today() - myDateTime.GetDateFromString(d[0])
##                    if dt > datetime.timedelta(days=1):
##                        is_test = True
##                    else:
##                        is_test = False
##                else:
##                    is_test = False
##            except:
##                    is_test = True
##
##            self.ClampButton.SetLabel('Close')
##            self.ClampButton.SetValue(CLAMP_BUTTON_UP)
##            self.ExitButton.Enable(not is_test)
##            self.StartButton.Enable(False)
##            self.SetStatusLabels('Clamp Opened')
##            self.StopTimer()
##            self.throbber.Stop()                    
##            self.throbber.Rest()
##            self.parent.ResetOpenedClamp() 
##            self.SetTestStatusIdle() 
##            self.SetupLabels()
##            self.OnUnclamped()
            
        elif evt.msg == PLC_RELAY_C30_ID:
            print 'Filled Reservoir Event', ctime()
            self.SetStatusLabels('Reservoir Full')
            self.StopTimer()
            self.throbber.Stop()                    
            self.throbber.Rest()
            
        elif evt.msg == PLC_RELAY_C31_ID:
            print 'Test Started Event,', ctime()
            self.SetStatusLabels('Test in Progress...')
            self.ClampButton.Enable(False)
            self.StartButton.Enable(False)
            self.EnableLabels(True) 
            self.StartTimer()
            self.throbber.Start()
            self.parent.ResetTestStarted()

        elif evt.msg == PLC_RELAY_C32_ID:
            print 'Flow Started Event,', ctime()
            self.SetStatusLabels('Test in Progress...')

        elif evt.msg == PLC_RELAY_C33_ID:
            print 'Pulse Capture Started Event,', ctime()
            self.SetStatusLabels('Capturing Pulses...')

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
        
    #----------------------------------
    # Database Methods
    #----------------------------------
    def GetDbItem(self):
        """
        Get database item
        """
        return self.db_item
    
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
        # query opc server for results
        temp_change, avg_temp, test_time, ref_count, mut_count = self.parent.GetTestResults()

        # SANITY CHECK --JAH
        #####################
        print 'REF COUNTS:\t' + str(ref_count)
        print 'MUT COUNTS:\t' + str(mut_count)
        #####################

        if myUtil.CalValuesAreOk(ref_count, mut_count, test_time, temp_change):
            if self.GetTestStatus() == STATUS_FS_TEST:
                storage_volume      = myUtil.GetStorageVolume(self.system_type, self.mut.GetFSFlowRate())
                u_storage_volume    = myUtil.GetStorageVolumeUncert(self.system_type, self.mut.GetFSFlowRate())
                ref_kfactor         = self.fs_ref.GetKFactor(self.mut.GetFSFlowRate())
                ref_volume          = ref_count/(ref_kfactor*GAL_PER_CUBIC_METER)
                u_ref               = self.fs_ref.GetUncertainty()
                thermal_volume  = myThermal.GetVolume2(temp_change, ref_volume, storage_volume) - ref_volume
                poly_coef       = self.fs_ref.GetCurvefitPoly()
            elif self.GetTestStatus() == STATUS_LS_TEST:
                storage_volume      = myUtil.GetStorageVolume(self.system_type, self.mut.GetLSFlowRate())
                u_storage_volume    = myUtil.GetStorageVolumeUncert(self.system_type, self.mut.GetLSFlowRate())
                ref_kfactor         = self.ls_ref.GetKFactor(self.mut.GetLSFlowRate())
                ref_volume          = ref_count/(ref_kfactor*GAL_PER_CUBIC_METER)
                u_ref               = self.ls_ref.GetUncertainty()
                thermal_volume  = myThermal.GetVolume1(temp_change, ref_volume, storage_volume) - ref_volume
                poly_coef       = self.ls_ref.GetCurvefitPoly()
            else:
                raise TypeError, 'Received invalid test status type.'

            # Apply corrections to ref volume
            ref_volume = myUtil.GetCorrectedVolume(ref_volume, thermal_volume, test_time, poly_coef)

            #  I'm not sure why the pulses needs to be corrected if the
            #  k-factor is being adjusted already. -JAH
            
            # set reference pulse count from corrected reference volume
            #ref_count = ref_kfactor*(ref_volume*GAL_PER_CUBIC_METER)
            
            # k-factor
            k = float(mut_count)/float(ref_volume*GAL_PER_CUBIC_METER)
            self.SetKLabel(k)

            # reference flow rate
            ref_flowrate = (ref_volume*GAL_PER_CUBIC_METER) / float(test_time) * SEC_PER_MIN
            
            # save data to file
            if self.parent.GetSystemType() == HF_SYSTEM:
                if self.GetTestStatus() == STATUS_LS_TEST:
                    fh = myFile.myFile(HF_VERIFICATION_LS_DATA_PATH)
                    fh2 = myFile.myFile(HF_VERIFICATION_LS_DATA_PATH2)
                else:
                    fh = myFile.myFile(HF_VERIFICATION_FS_DATA_PATH)
                    fh2 = myFile.myFile(HF_VERIFICATION_FS_DATA_PATH2)
            else:
                if self.GetTestStatus() == STATUS_LS_TEST:
                    fh = myFile.myFile(LF_VERIFICATION_LS_DATA_PATH)
                    fh2 = myFile.myFile(LF_VERIFICATION_LS_DATA_PATH2)
                else:
                    fh = myFile.myFile(LF_VERIFICATION_FS_DATA_PATH)
                    fh2 = myFile.myFile(LF_VERIFICATION_FS_DATA_PATH2)

            d = myDateTime.GetISOFormatSec(myDateTime.GetToday())
            results = ['%0.9f, %0.9f, %s\n'%(ref_flowrate, k, d)]
            
            if not fh.Lock():
                self.Error('Unable to lock data file')
            fh.WriteToFile(results)
            if not fh.UnLock():
                self.Error('Unable to unlock data file')

            # Create secondary file for WinSPC experiment
            if not fh2.Lock():
                self.Error('Unable to lock data file')
            fh2.WriteToFile(results)
            if not fh2.UnLock():
                self.Error('Unable to unlock data file')
                
            return True    
        else:
            self.Error('Test results are invalid:\nref count: %d\nmut count: %d\ntest time: %0.2f\ntemp change: %0.3f'%(ref_count, mut_count, test_time, temp_change))
            return False

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
        
