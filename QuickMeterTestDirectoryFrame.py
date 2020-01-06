#----------------------------------------------------------------------
# ProductionDirectoryFrame
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
# frame handles the directoy for PRODUCTION frames ONLY. DO NOT include
# engineering frames here.
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''
  1.03  2016/12/13  SPN     Updated OnPE075Button, OnPE038Button methods: removed verification meter check
                            since it has been added to the calibration GUI
  1.02  2013/10/03  SPN     Added static text label to indicate directory type
  1.01  2013/9/25   SPN     Updated OnPE075Button, OnPE038Button methods to call 
                            IsVerificationMeter method to prevent verification meter 
                            from being accidentally calibrated
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
        
        self.DirectoryLabel = wx.StaticText(id=DIRECTORY_TEXT_ID,label='PRE-TEST', parent=self.panel, size=wx.Size(150, 25), style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
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

    def OnPE075Button(self, event):
        # a serial command is used to query the software version
        # of the flow meter.
        #
        # In all the pe102 code revisions, there has been
        # two different commands to query the software version.
        # hence to instantiate the correct meter object we need
        # to try two different serial commands. try rev c as default.
        dlg = myUtil.BusyInfo(None, '')
        dlg.SetLabel('Communicating. Please wait...')
        dlg.Layout()

        mut = myFlowMeters.PE102_REV_C()
        mut.SetIdentity075()

        isok = mut.SerialConnect(MUT_SERIAL_PORT)

        if isok == None:
            myUtil.ErrorDialog(self, 'Unable to open serial port %d'%MUT_SERIAL_PORT)
            mut.SerialDisconnect()
            dlg.Destroy()
            return
        elif isok == False:
            myUtil.ErrorDialog(self, 'MUT serial connection is not open.')
            mut.SerialDisconnect()
            dlg.Destroy()
            return

        x = mut.ReadSoftwareVersion().strip('f')

        if x not in myFlowMeters.FLOW_METER_OBJECT_DICT.keys():
            # if no response then try rev d as default
            mut = myFlowMeters.PE102_REV_D()
            mut.SerialConnect(MUT_SERIAL_PORT)
            mut.SetIdentity075()
            x = mut.ReadSoftwareVersion().strip('f')
        mut.SerialDisconnect()

        if x not in myFlowMeters.FLOW_METER_OBJECT_DICT.keys():
            myUtil.ErrorDialog(self, 'Unable to determine flowmeter software version')
            dlg.Destroy()
            return
        
        # grab the correct meter class from the flow meter class dictionary
        mut = myFlowMeters.FLOW_METER_OBJECT_DICT[x]
        mut.SetIdentity075()

##        # Check if trying to calibrate verification meter
##        if myUtil.IsVerificationMeter(mut):
##            myUtil.ErrorDialog(self, 'MUT recognized as verification meter and cannot be calibrated')
##            dlg.Destroy()
##            return

        dlg.Destroy()
        dlg = None
        
        self.page = self.DestroyOpenPage()
        self.page = QuickMeterTestFrame.Frame(self,
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
        
    def OnPE038Button(self, event):
        # a serial command is used to query the software version
        # of the flow meter.
        #
        # In all the pe102 code revisions, there has been
        # two different commands to query the software version.
        # hence to instantiate the correct meter object we need
        # to try two different serial commands. try rev c as default.
        dlg = myUtil.BusyInfo(None, '')
        dlg.SetLabel('Communicating. Please wait...')
        dlg.Layout()

        mut = myFlowMeters.PE102_REV_C()
        mut.SetIdentity038()

        isok = mut.SerialConnect(MUT_SERIAL_PORT)

        if isok == None:
            myUtil.ErrorDialog(self, 'Unable to open serial port %d'%MUT_SERIAL_PORT)
            mut.SerialDisconnect()
            dlg.Destroy()
            return
        elif isok == False:
            myUtil.ErrorDialog(self, 'MUT serial connection is not open.')
            mut.SerialDisconnect()
            dlg.Destroy()
            return

        if not mut.SetSerialReadyState():
            myUtil.ErrorDialog(self, 'Unable to Set Serial in Ready State.')
            dlg.Destroy()
            return
            
        x = mut.ReadSoftwareVersion().strip('f')        
        if x not in myFlowMeters.FLOW_METER_OBJECT_DICT.keys():
            # if no response then try rev d as default
            mut = myFlowMeters.PE102_REV_D()
            mut.SerialConnect(MUT_SERIAL_PORT)
            mut.SetIdentity038()
            x = mut.ReadSoftwareVersion().strip('f')
        mut.SerialDisconnect()

        if x not in myFlowMeters.FLOW_METER_OBJECT_DICT.keys():
            myUtil.ErrorDialog(self, 'Unable to determine flowmeter software version')
            dlg.Destroy()
            return

        # grab the correct meter class from the flow meter class dictionary
        mut = myFlowMeters.FLOW_METER_OBJECT_DICT[x]
        mut.SetIdentity038()

##        # Check if trying to calibrate verification meter
##        if myUtil.IsVerificationMeter(mut):
##            myUtil.ErrorDialog(self, 'MUT recognized as verification meter and cannot be calibrated')
##            dlg.Destroy()
##            return

        dlg.Destroy()
        dlg = None
        
        self.page = self.DestroyOpenPage()
        self.page = QuickMeterTestFrame.Frame(self,
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

        
