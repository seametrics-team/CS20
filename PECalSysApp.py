#----------------------------------------------------------------------
# PE Calibration System HMI Program
''' author: Jeff Peery '''
# date: 11/29/2007
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------

'''
    NOTES:

    For variable references, program diagrams, mechanical and electrical
    diagrams of the PE calibration system, consult 'PE Cal System Schematics.vsd'.
    'PE Cal System Schematics.vsd' is a Microsoft Viso program.

    For OPC reference, consult the OPCDataAccessAutomationStandard. This is the
    standard protocol for OPC servers and clients. The OPC module was developed
    according to this standard. The OPC settings are managed in the __init__
    method of PeCalSysApp module.
     
    This information may also be located within the PE calibration system
    design binder in hard copy form.

    The Program was designed to be completely event driven. There are no
    timed events, processes, or methods. Hence the system is never locked up
    and will respond in the most efficient manner.

    There are two kinds of events:
    (1) PLC (Programmable Logic Controller) events, and (2) HMI (Human Machine
    Interface) events. PLC events are handled in the OnEventHandler stage
    within the PLC. This stage is ALWAYS on, do not RST this stage as it
    will disable the program. HMI events are handled in the OnOPCDataChange
    method within this script. These events are triggered when an OPCDataChange
    event occurs. The events are setup/initialized in the PeCalSysApp.py
    __init__ method. When an OPC item (that is setup to have a data change event)
    changes value an event is sent to OnOPCDataChange. OnOPCDataChange then
    resets the event coil so that it may be used again. THERE MUST BE
    TWO COILS ESTABLISHED FOR ANY EVENT!! One coil is used to send the event to
    the HMI and one is used to send the event to the PLC. You cannot use
    a single coil for two events (a PLC event and a HMI event, using coil high\
    for the PLC event, and coil low for the HMI event) because the changes
    occur too quickly and the OPC server does not register the change as
    significant enough to send an OnDataChange event. If the system is not responding
    this is likely because a coil did not get reset after an event occured.
    i.e., if an event occured and a coil was set high then it must be reset
    to low if the same event is to be used again. Else the coil is set from
    high to high which the OPC server does not see as a DataChange and hence
    it will not send an event.

    The program is object oriented. Please use classes setup in the Modules
    folder to instantiate and operate class objects. DO NOT code methods outside
    an objects class. This destroys the strucutre of the code and the flexibility
    of object oriented code.

    The progam is also 'modular' and to some extent 'captured'. When editing
    this program please keep methods reduce to one single purpose. i.e., each
    method does one and only one thing. This reduces complexity and produces
    easily readable, manageable, and reproducable code. It is to some extent
    captured, i.e., the API is separate from the GUI, they are not bound together.
    this is important to enable changing GUI and API independantly. It is also
    important so that the code can be used on other systems, not just the PE
    Cal Sys.
'''
#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''

    1   12/02/08    JTP     (1) Initial Release
    2   12/14/08    JTP     (1) Added sleep time between reading and
                                writing to OPC server. Otherwise the
                                quality of returned values is zero.
    3   12/20/08    JTP     (1) Separated HMI and PLC event coils. If
                                they are the same they may change too
                                fast (ie, faster than group.UpdateRate)
                                and the OPC Server Instance may not
                                post OnDataChange events if going from
                                low-high-low. Of course low-high or high-low
                                events would be posted. however switching from
                                low-high-low may be faster than the update rate
                                and the server would not see any datachange.
    4   14/01/17    SPN     -Added GetMUTAO method to capture 4-20 value from MUT
                            -Added GetRef1AO, GetRef2AO, GetRef3AO, GetRef4AO methods to capture 4-20 values from reference meters
    5   14/02/25    SPN     Updated GetTemp method to disable dst, det (unused thermisters) calculations to prevent "divide by zero" error
    6   14/02/26    SPN     Added file handling methods (CopyFile, CopyTestDataFile)
    7   14/09/16    SPN     Disable database load in OnInit method
    8   14/10/14    SPN     Updated GetTestResults method by echoing temps, test time, and pulse counts
    9   15/05/01    SPN     -Added LockClamp and ResetLockClamp methods so PLC can lock clamp during test
                            -Updated OnInit method: Added ResetLockClamp, open clamp if closed
                            -Updated OnOPCDataChange method: Ignore C34 Lock Clamp PLC event
    10  15/05/04    SPN     -Reassign OPC C34 to C16
                            -Revert latest changes to OnOPCDataChange method
                            -Added UnlockClamp and ResetUnlockClamp methods so PLC can unlock clamp
'''
#----------------------------------------------------------------------
# Modules
#----------------------------------------------------------------------
import wx
import Modules.myOPC as myOPC
import time
import DirectoryFrame
import CalibrationFrame
import Modules.myDatabase as myDatabase
import Modules.myUtil as myUtil
import Modules.myDateTime as myDateTime
import Modules.myThermal as myThermal
from Modules.myHeader import *
import os
import sys
import Modules.myFile as myFile

#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------
class PECalSysApp(wx.App):
    def OnInit(self):
        #----------------------------------
        # GUI
        #----------------------------------        
        # test check standard on mondays
##        if myDateTime.MONDAY == myDateTime.Weekday():
##            myUtil.MsgDialog(None, 'IMPORTANT!\n Please calibrate the check standard.')

        dlg = myUtil.BusyInfo(None, '')
        dlg.SetLabel('Loading PE Calibration System HMI...')
        dlg.Layout()            
        #----------------------------------
        # Instantiate OPC Client Object
        #----------------------------------        
        dlg.SetLabel('Creating OPC Client...')
        print "Creating OPC Server COM Object..."
        self.opcServer, self.group, self.groups = myOPC.connectServer(OPC_SERVER_NAME)
        print "Setting Group One Update Rate to %d (ms)..."%GENERAL_UPDATE_RATE
        myOPC.SetGroupUpdateRate(self.group, GENERAL_UPDATE_RATE)
        print "Setting Group One DeadBand to %d %%FS..."%GENERAL_DEAD_BAND
        myOPC.SetGroupDeadBand(self.group, GENERAL_DEAD_BAND)
        print "Adding OPC Group Two (Non-DataChange Items)..."
        self.group2 = self.groups.Add() 
        self.group2.IsActive = 1   
        self.group2.IsSubscribed = 0
        print "Setting Group Two DeadBand to %d %%FS..."%GENERAL_DEAD_BAND
        myOPC.SetGroupDeadBand(self.group2, GENERAL_DEAD_BAND)
        print "Setting Group Two Update Rate to %d (ms)..."%GENERAL_UPDATE_RATE
        myOPC.SetGroupUpdateRate(self.group2, GENERAL_UPDATE_RATE)
        print "Adding OPC Group Three (Analog Input Items)..."
        self.group3 = self.groups.Add() 
        self.group3.IsActive = 1   
        self.group3.IsSubscribed = 1
        print "Setting Group Three DeadBand to %d %%FS..."%AI_DEAD_BAND
        myOPC.SetGroupDeadBand(self.group3, AI_DEAD_BAND)
        print "Setting Group Three Update Rate to %d (ms)..."%AI_UPDATE_RATE
        myOPC.SetGroupUpdateRate(self.group3, AI_UPDATE_RATE)
        print "Adding OPC Items to Group..."
        self.InitOPCItems()
        # The following must be called after adding items to groups
        print "Creating OnDataChange Event for Group One..."
        self.groupEvents = myOPC.SetGroupEvents(self.group)
        print "Creating OnDataChange Event for Group Three..."
        self.groupEvents2 = myOPC.SetGroupEvents(self.group3)
        print "Setting Group One OnDataChange Class Attribute 'parent'..."
        self.groupEvents.SetParent(self)
        print "Setting Group Three OnDataChange Class Attribute 'parent'..."
        self.groupEvents2.SetParent(self)
        print "Initializing PLC"
        self.InitializePLC()

        # Start with clamp open if it's already unlocked
        if self.ReadOPC(self.closed_clamp) == True:
            self.OpenClamp()

        #----------------------------------
        # Instantiate Database Object
        #----------------------------------
        print "Loading database..."
        dlg.SetLabel('Loading Database...')
        self.db = myDatabase.Database()
        # Don't load db so always return True
        isok = True
##        isok = self.db.Load()
        dlg.Destroy()

        if not isok:
            myUtil.ErrorDialog(None, 'unable to locate production database. closing program.')
            sys.exit(0)

        #----------------------------------
        # Event Definitions
        #----------------------------------
        print "Binding OnDataChange Events to OnOPCDataChange method..."
        dlg.SetLabel('Binding OPC Data Change Events...')
        try:
            self.Bind(myOPC.EVT_OPC_DATA_CHANGE, self.OnOPCDataChange)
        except:
            print 'Error Occured When Trying to Bind OnDataChange Events'

        return True

    #---------------------------------------
    # PLC Event Methods
    #---------------------------------------
    def StartFlow(self):
        print 'HMI Posting PLC Start Flow Event'
        self.WriteOPC(self.start_flow, True)

    def StartPulseCapture(self):
        print 'HMI Posting PLC Start Pulse Capture Event'
        self.WriteOPC(self.start_pulse_capture, True)
        
    def ContinueProgram(self):
        print 'HMI Posting PLC Continue Program Event'
        self.WriteOPC(self.go, True)

    def CloseClamp(self):
        print 'HMI Posting PLC Close Clamp Event'
        self.WriteOPC(self.close_clamp, True)

    def OpenClamp(self):
        print 'HMI Posting PLC Open Clamp Event'
        self.WriteOPC(self.open_clamp, True)

    def LockClamp(self):
        print 'HMI Posting PLC Lock Clamp Event'
        self.WriteOPC(self.lock_clamp, True)

    def UnlockClamp(self):
        print 'HMI Posting PLC Unlock Clamp Event'
        self.WriteOPC(self.unlock_clamp, True)   

    def StopTest(self):
        print 'HMI Posting PLC Stop Test Event'
        self.WriteOPC(self.stop_test, True)
        
    def SetTargetFlowRate(self, flow_rate):
        print 'HMI Setting PLC Target Flow Rate: %0.2f'%flow_rate
        assert self.directory.page, 'directory or page does not exist'
        assert 'system_type' in dir(self.directory.page)
        assert self.directory.page.system_type in [HF_SYSTEM, LF_SYSTEM]
        if self.directory.page.system_type == HF_SYSTEM:
            assert flow_rate <= HF_MAX_FLOW_RATE, 'flow rate > maximum limit'
            assert flow_rate >= HF_MIN_FLOW_RATE, 'flow rate < minimum limit'
        elif self.directory.page.system_type == LF_SYSTEM:
            assert flow_rate <= LF_MAX_FLOW_RATE, 'flow rate > maximum limit'
            assert flow_rate >= LF_MIN_FLOW_RATE, 'flow rate < minimum limit'
        self.WriteOPC(self.target_flow_rate, flow_rate)
        
    def SetTargetTestTime(self, test_time):
        print 'HMI Setting PLC Target Test Time: %0.2f'%(test_time*100)
        assert self.directory.page, 'directory or page does not exist'
        assert 'system_type' in dir(self.directory.page)
        assert self.directory.page.system_type in [HF_SYSTEM, LF_SYSTEM]
        self.WriteOPC(self.target_test_time, test_time*100)

    def StartTest(self, flow_rate):
        assert self.directory.page
        assert 'system_type' in dir(self.directory.page)
        assert self.directory.page.system_type in [HF_SYSTEM, LF_SYSTEM]        
        if self.directory.page.system_type == HF_SYSTEM:
            self.StartMotorTest(flow_rate)
        elif self.directory.page.system_type == LF_SYSTEM:
            self.StartGravityTest(flow_rate)
        else:
            assert TypeError, 'Received unknown system type'

    def StartMotorTest(self, flow_rate):
        print 'HMI Posting PLC Start Motor Test Event'
        self.SetTargetFlowRate(flow_rate)
        self.WriteOPC(self.start_motor_test, True)

    def StartGravityTest(self, flow_rate):
        print 'HMI Posting PLC Start Gravity Test Event'
        self.SetTargetFlowRate(flow_rate)
        self.WriteOPC(self.start_gravity_test, True)
        
    def FillReservoir(self):
        print 'HMI Posting PLC Fill Reservoir Event'
        self.WriteOPC(self.fill_reserv, True)
        
    def FailTest(self):
        print 'HMI Posting PLC Fail Test Event'
        self.WriteOPC(self.fail_test, True)
        
    def PassTest(self):
        print 'HMI Posting PLC Pass Test Event'
        self.WriteOPC(self.pass_test, True)

    def InitializePLC(self):
        print 'HMI Posting PLC Initialize PLC Event'
        self.WriteOPC(self.init_plc, True)

    #---------------------------------------
    # Reset HMI Event Coils
    #---------------------------------------        
    def ResetAbortedTest(self):
        print "HMI Reseting 'Aborted Test' Coil"
        self.WriteOPC(self.aborted_test, False)
        
    def ResetStoppedTest(self):
        print "HMI Reseting 'Stopped Test' Coil"
        self.WriteOPC(self.stopped_test, False)
        
    def ResetClosedClamp(self):
        print "HMI Reseting 'Closed Clamp' Coil"
        self.WriteOPC(self.closed_clamp, False)
        
    def ResetOpenedClamp(self):
        print "HMI Reseting 'Opened Clamped' Coil"
        self.WriteOPC(self.opened_clamp, False)

    def ResetLockClamp(self):
        print "HMI Reseting 'Lock Clamp' Coil"
        self.WriteOPC(self.lock_clamp, False)

    def ResetUnlockClamp(self):
        print "HMI Reseting 'Unlock Clamp' Coil"
        self.WriteOPC(self.unlock_clamp, False)

    def ResetTestFinished(self):
        print "HMI Reseting 'Test Finished' Coil"
        self.WriteOPC(self.test_finished, False)

    def ResetTestStarted(self):
        print "HMI Resetting 'Test Started' Coil"
        self.WriteOPC(self.test_started, False)

    def ResetReservoirFilled(self):
        print "HMI Reseting WriteOPC 'Reservoir Filled' Coil"
        self.WriteOPC(self.reserv_filled, False)

    def ResetFillingReservoir(self):
        print "HMI Reseting WriteOPC 'Filling Reservoir' Coil"
        self.WriteOPC(self.filling_reserv, False)
        
    
    #----------------------------------
    # OPC Methods
    #----------------------------------
    def OnOPCDataChange(self, evt):
        if self.directory.page:
            self.directory.page.OnOPCDataChange(evt)
                
    def GetTestResults(self):
        assert self.directory.page
        assert 'system_type' in dir(self.directory.page)
        assert self.directory.page.system_type in [HF_SYSTEM, LF_SYSTEM]
        test_time = self.GetTestTime()
        ref_count = self.GetRefPulseCount()
        mut_count = self.GetMUTPulseCount()
        temp_change, avg_temp = self.GetTemp(self.directory.page.system_type)
        print 'temp change:',temp_change
        print 'avg temp:', avg_temp
        print 'test time:',test_time
        print 'ref count:', ref_count
        print 'mut count:', mut_count
        return temp_change, avg_temp, test_time, ref_count, mut_count
                
    def AddItem(self, item, group, num):
        item = myOPC.addItem(item, group, num)
        assert item != None, 'Received NoneType item while adding the OPC item'
        return item
    
    def disconnectOPC(self):
        myOPC.disconnectServer(self.opcServer)
        
    def WriteOPC(self, item, value):
        assert value != None
        myOPC.writeItemValue(item, value)

    def ReadOPC(self, item):
        (value, quality, time_stamp) = myOPC.readItemValue(item)
        assert type(value) == int or type(value) == bool or type(value) == float
        assert type(quality) == int
        assert int(quality) == HIGH_QUALITY, 'Received low quality item value from OPC server'
        return value
                     
    def SetSystemType(self):
        assert self.directory.page
        assert 'system_type' in dir(self.directory.page)
        assert self.directory.page.system_type in [HF_SYSTEM, LF_SYSTEM]
        self.WriteOPC(self.system_id, self.directory.page.system_type)

    def GetSystemType(self):
        return self.ReadOPC(self.system_id)
        
    def GetRefPulseCount(self):
        return self.ReadOPC(self.ref_count)

    def GetMUTPulseCount(self):
        return self.ReadOPC(self.mut_count)

    def GetRef1AO(self):
        return self.ReadOPC(self.ref1AO)

    def GetRef2AO(self):
        return self.ReadOPC(self.ref2AO)

    def GetRef3AO(self):
        return self.ReadOPC(self.ref3AO)

    def GetRef4AO(self):
        return self.ReadOPC(self.ref4AO)

    def GetMUTAO(self):
        return self.ReadOPC(self.MUTAO)

    def GetTemp(self, system_type):
        # upstream test start temp (digital value)
        ust = self.ReadOPC(self.upstream_start_temp)
        # downstream test start temp (digital value)
        dst = self.ReadOPC(self.downstream_start_temp)
        # upstream test end temp (digital value)
        uet = self.ReadOPC(self.upstream_end_temp)
        # downstream test end temp (digital value)
        det = self.ReadOPC(self.downstream_end_temp)

        if system_type == HF_SYSTEM:
            ust = myThermal.DigitalToTemp(ust,
                                        THERMAL_3_B0,
                                        THERMAL_3_B1,
                                        THERMAL_3_B2,
                                        THERMAL_3_B3)

            uet = myThermal.DigitalToTemp(uet,
                                        THERMAL_3_B0,
                                        THERMAL_3_B1,
                                        THERMAL_3_B2,
                                        THERMAL_3_B3)

##            dst = myThermal.DigitalToTemp(dst,
##                                        THERMAL_4_B0,
##                                        THERMAL_4_B1,
##                                        THERMAL_4_B2,
##                                        THERMAL_4_B3)
##
##            det = myThermal.DigitalToTemp(det,
##                                        THERMAL_4_B0,
##                                        THERMAL_4_B1,
##                                        THERMAL_4_B2,
##                                        THERMAL_4_B3)

            # correct bias
            ust = ust + THERMAL_3_BIAS_CORRECTION
            uet = ust + THERMAL_3_BIAS_CORRECTION
            dst = ust + THERMAL_4_BIAS_CORRECTION
            det = ust + THERMAL_4_BIAS_CORRECTION
            # set these to zero because the downstream
            # thermistor is not installed.
            dst = 0.0
            det = 0.0
            
        elif system_type == LF_SYSTEM:
##            dst = myThermal.DigitalToTemp(dst,
##                                        THERMAL_1_B0,
##                                        THERMAL_1_B1,
##                                        THERMAL_1_B2,
##                                        THERMAL_1_B3)
##
##            det = myThermal.DigitalToTemp(det,
##                                        THERMAL_1_B0,
##                                        THERMAL_1_B1,
##                                        THERMAL_1_B2,
##                                        THERMAL_1_B3)

            ust = myThermal.DigitalToTemp(ust,
                                        THERMAL_2_B0,
                                        THERMAL_2_B1,
                                        THERMAL_2_B2,
                                        THERMAL_2_B3)

            uet = myThermal.DigitalToTemp(uet,
                                        THERMAL_2_B0,
                                        THERMAL_2_B1,
                                        THERMAL_2_B2,
                                        THERMAL_2_B3)
            # correct bias
            dst = ust + THERMAL_1_BIAS_CORRECTION
            det = ust + THERMAL_1_BIAS_CORRECTION
            ust = ust + THERMAL_2_BIAS_CORRECTION
            uet = ust + THERMAL_2_BIAS_CORRECTION
            # set these to zero because the downstream
            # thermistor is not installed.
            dst = 0.0
            det = 0.0
        else:
            raise TypeError, 'Received unknown system type'
        
##        # return the average change in temperature.
##        # prevent zero division.
##        if uet + ust == 0:
##            return 0
##        else:
##            return (uet + det - ust - dst)/2.0
        return (uet - ust), (uet + ust)/2.0

    def GetTestTime(self):
        t = self.ReadOPC(self.test_time)
        return t/100.0        

    def InitOPCItems(self):
        #----------------------------------
        # These items do not produce an
        # OnDataChange event (ie part of group2)
        #----------------------------------
        # Ref pulse count
        self.ref_count = self.AddItem(REF_PULSE_COUNT_NAME, self.group2, REF_PULSE_COUNT_ID)
        # MUT pulse count
        self.mut_count = self.AddItem(MUT_PULSE_COUNT_NAME, self.group2, MUT_PULSE_COUNT_ID)
        # target flow rate
        self.target_flow_rate = self.AddItem(TARGET_FLOW_RATE_NAME, self.group2, TARGET_FLOW_RATE_ID)
        # target test time
        self.target_test_time = self.AddItem(TARGET_TEST_TIME_NAME, self.group2, TARGET_TEST_TIME_ID)
        # Test time
        self.test_time = self.AddItem(TEST_TIME_NAME, self.group2, TEST_TIME_ID)
        # Test upstream start temp
        self.upstream_start_temp = self.AddItem(UPSTREAM_START_TEMP_NAME, self.group2, UPSTREAM_START_TEMP_ID)
        # Test upstream end temp
        self.upstream_end_temp = self.AddItem(UPSTREAM_END_TEMP_NAME, self.group2, UPSTREAM_START_TEMP_ID)
        # Test downstream start temp
        self.downstream_start_temp = self.AddItem(DOWNSTREAM_START_TEMP_NAME, self.group2, DOWNSTREAM_START_TEMP_ID)
        # Test downstream end temp
        self.downstream_end_temp = self.AddItem(DOWNSTREAM_END_TEMP_NAME, self.group2, DOWNSTREAM_END_TEMP_ID)
        #----------------------------------
        # These items produce an
        # OnDataChange event (ie part of group3)
        #----------------------------------
        # temperature
        self.RTD1 = self.AddItem(RTD_1_NAME, self.group3, RTD_1_ID)
        self.RTD2 = self.AddItem(RTD_2_NAME, self.group3, RTD_2_ID)
        self.RTD3 = self.AddItem(RTD_3_NAME, self.group3, RTD_3_ID)
        self.RTD4 = self.AddItem(RTD_4_NAME, self.group3, RTD_4_ID)
        # flow rate
        self.ref1AO = self.AddItem(REF_1_NAME, self.group3, REF_1_ID)
        self.ref2AO = self.AddItem(REF_2_NAME, self.group3, REF_2_ID)
        self.ref3AO = self.AddItem(REF_3_NAME, self.group3, REF_3_ID)
        self.ref4AO = self.AddItem(REF_4_NAME, self.group3, REF_4_ID)
        self.MUTAO = self.AddItem(MUT_AO_NAME, self.group3, MUT_AO_ID)
        #----------------------------------
        # These items produce an
        # OnDataChange event (ie part of group)
        #----------------------------------        
        '''Misc PLC Handles'''
        # System Identifier, Set if High Flow Sys, Reset if Low Flow Sys
        self.system_id = self.AddItem(PLC_RELAY_C0, self.group, PLC_RELAY_C0_ID)
        # Controls Program Flow
        self.go = self.AddItem(PLC_RELAY_C1, self.group, PLC_RELAY_C1_ID)
        '''PLC Event Handles'''
        # Used for HMI to Post Initialize Event to PLC
        self.init_plc = self.AddItem(PLC_RELAY_C2, self.group, PLC_RELAY_C2_ID)
        # Used for HMI to Post Pass Test Event to PLC
        self.pass_test = self.AddItem(PLC_RELAY_C3, self.group, PLC_RELAY_C3_ID)
        # Used for HMI to Post Fail Test Event to PLC
        self.fail_test = self.AddItem(PLC_RELAY_C4, self.group, PLC_RELAY_C4_ID)
        # Used for HMI to Post Gravity Test Start Event to PLC
        self.start_gravity_test = self.AddItem(PLC_RELAY_C5, self.group, PLC_RELAY_C5_ID)
        # Used for HMI to Post Motor Test Start Event to PLC
        self.start_motor_test = self.AddItem(PLC_RELAY_C7, self.group, PLC_RELAY_C7_ID)
        # Used for HMI to Post Stop Test Event to PLC
        self.stop_test = self.AddItem(PLC_RELAY_C11, self.group, PLC_RELAY_C11_ID)
        # Used for HMI to Post Close Clamp Event to PLC
        self.close_clamp = self.AddItem(PLC_RELAY_C12, self.group, PLC_RELAY_C12_ID)
        # Used for HMI to Post Open Clamp Event to PLC
        self.open_clamp = self.AddItem(PLC_RELAY_C13, self.group, PLC_RELAY_C13_ID) 
        # Used for HMI to Post Fill Reservoir Event to PLC
        self.fill_reserv = self.AddItem(PLC_RELAY_C15, self.group, PLC_RELAY_C15_ID)    
        # Used for HMI to Post Start Flow Event to PLC
        self.start_flow = self.AddItem(PLC_RELAY_C32, self.group, PLC_RELAY_C32_ID) 
        # Used for HMI to Post Start Pulse Capture Event to PLC
        self.start_pulse_capture = self.AddItem(PLC_RELAY_C33, self.group, PLC_RELAY_C33_ID)
        # Used for HMI to Post Lock Clamp Event to PLC
        self.lock_clamp = self.AddItem(PLC_RELAY_C16, self.group, PLC_RELAY_C16_ID)
        # Used for HMI to Post Unlock Clamp Event to PLC
        self.unlock_clamp = self.AddItem(PLC_RELAY_C17, self.group, PLC_RELAY_C17_ID)  
        '''HMI Event Handles'''
        # Used for PLC to Post Aborted Test Event to HMI
        self.aborted_test = self.AddItem(PLC_RELAY_C20, self.group, PLC_RELAY_C20_ID)    
        # Used for PLC to Post Test Stopped Event to HMI
        self.stopped_test = self.AddItem(PLC_RELAY_C21, self.group, PLC_RELAY_C21_ID)
        # Used for PLC to Post Test Finished Event to HMI
        self.test_finished = self.AddItem(PLC_RELAY_C22, self.group, PLC_RELAY_C22_ID)
        # Used for PLC to Post Clamp Closed Event to HMI
        self.closed_clamp = self.AddItem(PLC_RELAY_C24, self.group, PLC_RELAY_C24_ID)
        # Used for PLC to Post Clamp Opened Event to HMI
        self.opened_clamp = self.AddItem(PLC_RELAY_C25, self.group, PLC_RELAY_C25_ID)        
        # Used for PLC to Post Reservoir Filled Event to HMI
        self.reserv_filled = self.AddItem(PLC_RELAY_C30, self.group, PLC_RELAY_C30_ID)         
        # Used for PLC to Post Test Started Event to HMI
        self.test_started = self.AddItem(PLC_RELAY_C31, self.group, PLC_RELAY_C31_ID)        
        # Used for PLC to Post Filling Reservoir Event to HMI
        self.filling_reserv = self.AddItem(PLC_RELAY_C14, self.group, PLC_RELAY_C14_ID) 

    #-------------------------------------------------------------------------
    # file handling
    #-------------------------------------------------------------------------
    def CopyFile(self, from_path, to_path, header=None):
        fh = myFile.myFile(from_path)
        lines = fh.GetTextByLines()

        fh = myFile.myFile(to_path)
        if header != None:
            fh.WriteToFile(header)
            fh.AppendLines(lines)
        else:
            fh.WriteToFile(lines)    
        
    def CopyTestDataFile(self, header=None, path=None):
        """
        header is list of lines to add to header of saved file
        """
        self.CopyFile(TEST_RESULTS_FILE_PATH,
                      myFile.GetUniquePath(TEST_RESULTS_FILE_PATH))
        return True
        
   
def main():
    application = PECalSysApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()

