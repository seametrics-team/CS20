#----------------------------------------------------------------------
# PE102 Meter Module
# Rev: 3
''' author: Jeff Peery '''
# date: 08/18/2008
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''
   19   2017/01/04  SPN     -Added option -138 to PE202
   18   2016/12/12  SPN     -Added GetCurvefitPoly, SetCurvefitPoly methods
   17   2015/01/13  SPN     -   Added option -270 for PE202 by updating SetOption, SetOptions methods
                                and adding SetIdentity075_PE202_270 and SetIdentity038_PE202_270 methods
                            -   Updated PE202 identity methods:
                                Updated init adc values based on latest statistics
                                Optimized and moved to rev J class
                            -   Added zradc limit constants to _init_ method
   16   2014/10/28  SPN     -   Renamed previous changes associated with "new body" to "PE202"
                            -   Added option -277 for PE202
                                New/updated methods: SetOption, SetIdentity075_PE202_277, SetIdentity038_PE202_277
   15   2014/09/05  SPN     -   Add new constants: new PE meter body labels, New body option
                            -   Updated Rev H class SetOption method by adding option to support new meter body
                            -   Add SetIdentity038_NewBody method to provide new meter body option for calibration with characterized
                                initial FSADC & ZRADC values
                            -   Updated SetOptions method in Rev J class to support new options related to new meter body
   14   2014/08/27  SPN     -   Initialize test frequency to 1,000 Hz for any meter type.
                            -   Disable test frequency assignment within each meter type.
   13   2014/05/12  JAH     -   Changed a / to * in the Reference.GetKFactor method.
                            -   Reverted changes from rev 12
   12   2014/05/09  SPN     -   Updated Reference.GetKFactor method to incorporate corrected k-factor based on current flow rate
   11   2014/02/07  SNP     -   Disabled analog output test for -277 and -270 option
   10   2014/01/24  SNP         Added self.test_analog_output variable to enable/disable analog output according to option type
    9   01/07/2011  JTP     -   added 270 option for PE102-038.
    8   04/08/2010  JTP     -   Included ReadFLTR and WriteFLTR for PE102_REV_G flow
                                meter class.
                            -   Added PE102_REV_G flow meter class.
    7   xx/xx/xxxx  JTP     -   Added PE102_REV_E flow meter class.
                            -   Added PE102_REV_F flow meter class.
                            -   Added PE102_REV_G flow meter class.
    6   12/16/2008  JTP     -   Included ReadFSADC and ReadZRADC for PE102_REV_D flow
                                meter class. uses GetFSADC and GetZRADC routines in
                                CP-13848-D.asm.
    5   12/15/2008  JTP     -   Editted GetSoftwareVersion() method in myFlowMeters
                                such that it strips the combinations 'cp' an not the 'c'
                                or 'p' individually. (otherwise rev 'c' or rev 'p' may not
                                work properly).
    4   10/27/2008  JTP     -   Added ReadADC                            
    3   08/18/2008  JTP     -   Added class for AG2000
    2   08/18/2008  JTP     -   Added base class for all flow meters
    1   2/1/08      JTP     -   Initial release
'''

#-------------------------------------------------------------------------
# Modules
#-------------------------------------------------------------------------
import mySerial
import myHex2Float
import string
from datetime import datetime
from myHeader import *
import myString
import myUtil
import numpy
import time

#-------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------
# Binary to integer conversion
INT_BINARY_DICT = {'0':'0000','1':'0001','2':'0010','3':'0011','4':'0100','5':'0101','6':'0110','7':'0111','8':'1000','9':'1001','A':'1010','B':'1011','C':'1100','D':'1101','E':'1110','F':'1111'}
# meter labels
METER_LABEL_AG2000          = 'AG2000'
METER_LABEL_WMX             = 'WMX'
METER_LABEL_PE102_075        = 'PE102-075'
METER_LABEL_PE102_075_270    = 'PE102-075-270'
METER_LABEL_PE102_075_271    = 'PE102-075-271'
METER_LABEL_PE102_075_272    = 'PE102-075-272'
METER_LABEL_PE102_075_277    = 'PE102-075-277'
METER_LABEL_PE102_050        = 'PE102-050'
METER_LABEL_PE102_038        = 'PE102-038'
METER_LABEL_PE102_038_277    = 'PE102-038-277'
METER_LABEL_PE102_038_270    = 'PE102-038-270'
METER_LABEL_PE102_025        = 'PE102-025'
METER_LABEL_PE102_013        = 'PE102-013'
METER_LABEL_PE202_075        = 'PE202-075'
METER_LABEL_PE202_075_138    = 'PE202-075-138'
METER_LABEL_PE202_075_270    = 'PE202-075-270'
METER_LABEL_PE202_075_277    = 'PE202-075-277'
METER_LABEL_PE202_075_400    = 'PE202-075-400'
METER_LABEL_PE202_038        = 'PE202-038'
METER_LABEL_PE202_038_138    = 'PE202-038-138'
METER_LABEL_PE202_038_270    = 'PE202-038-270'
METER_LABEL_PE202_038_277    = 'PE202-038-277'
METER_LABEL_PE202_038_400    = 'PE202-038-400'
# if adding a new option be sure to edit SetOptions method
METER_LABELS = [METER_LABEL_PE102_075_270,
                METER_LABEL_PE102_075_271,
                METER_LABEL_PE102_075_272,
                METER_LABEL_PE102_075_277,
                METER_LABEL_PE102_075,
                METER_LABEL_PE102_050,
                METER_LABEL_PE102_038_277,
                METER_LABEL_PE102_038_270,
                METER_LABEL_PE102_038,
                METER_LABEL_PE102_025,
                METER_LABEL_PE102_013,
                METER_LABEL_PE202_075,
                METER_LABEL_PE202_075_270,
                METER_LABEL_PE202_075_277,
                METER_LABEL_PE202_038,
                METER_LABEL_PE202_038_270,
                METER_LABEL_PE202_038_277,
                METER_LABEL_PE202_038_400,
                METER_LABEL_PE202_075_400
                ]
# PE102 OPTION LABELS
OPTION_STANDARD             = 'Std (PE102)'
PE102_OPTION_270            = '-270 (PE102)'
PE102_OPTION_271            = '-271 (PE102)'
PE102_OPTION_272            = '-272 (PE102)'
PE102_OPTION_277            = '-277 (PE102)'
PE202_STANDARD             = 'Std (PE202)'
PE202_OPTION_138           = '-138 (PE202)'
PE202_OPTION_270           = '-270 (PE202)'
PE202_OPTION_277           = '-277 (PE202)'
PE202_OPTION_400           = '-400 (PE202)'
# display types
DISPLAY_TYPE_AG2000         = '1'
DISPLAY_TYPE_WMX            = '0'
DISPLAY_TYPES               = [DISPLAY_TYPE_AG2000,
                               DISPLAY_TYPE_WMX]
# cuttoff (fraction of 1)
PE102_DEFAULT_LOW_FLOW_CUTTOFF = 0.01

# rate unit types
RATE_UNIT_TYPE_GPM  = 'GPM'
RATE_UNIT_TYPE_LPM  = 'LPM'
RATE_UNIT_TYPE_CFM  = 'CFM'
RATE_UNIT_TYPE_CMH  = 'CMH'
RATE_UNIT_TYPE_GPS  = 'GPS'
RATE_UNIT_TYPE_LPS  = 'LPS'
RATE_UNIT_TYPE_CFS  = 'CFS'
RATE_UNIT_TYPE_MI   = 'MI'
RATE_UNIT_TYPE_CMM  = 'CMM'
RATE_UNIT_TYPE_MGD  = 'MGD'
RATE_UNIT_TYPE_MLD  = 'MLD'
# total unit types
TOTAL_UNIT_TYPE_G   = 'G'
TOTAL_UNIT_TYPE_GT  = 'GT'
TOTAL_UNIT_TYPE_L   = 'L'
TOTAL_UNIT_TYPE_LT  = 'LT'
TOTAL_UNIT_TYPE_ML  = 'ML'
TOTAL_UNIT_TYPE_CM  = 'CM'
TOTAL_UNIT_TYPE_CMT = 'CMT'
TOTAL_UNIT_TYPE_AF  = 'AF'
TOTAL_UNIT_TYPE_CF  = 'CF'
TOTAL_UNIT_TYPE_CFT = 'CFT'
TOTAL_UNIT_TYPE_MG  = 'MG'
TOTAL_UNIT_TYPE_MID = 'MID'
TOTAL_UNIT_TYPE_AI  = 'AI'
# meter size options
SIZE_ONE_EIGHTH_INCH        = '0.125'
SIZE_ONE_QUARTER_INCH       = '0.25'
SIZE_THREE_EIGHTS_INCH      = '0.375'
SIZE_ONE_HALF_INCH          = '0.5'
SIZE_THREE_QUARTERS_INCH    = '0.75'
SIZE_ONE_INCH               = '1'
SIZE_TWO_INCH               = '2'
SIZE_THREE_INCH             = '3'
SIZE_FOUR_INCH              = '4'
SIZE_SIX_INCH               = '6'
SIZE_EIGHT_INCH             = '8'
SIZE_TEN_INCH               = '10'
SIZE_TWELVE_INCH            = '12'
NOMINAL_SIZES = [SIZE_ONE_EIGHTH_INCH, SIZE_ONE_QUARTER_INCH, SIZE_THREE_EIGHTS_INCH,
                         SIZE_ONE_HALF_INCH, SIZE_THREE_QUARTERS_INCH, SIZE_ONE_INCH, SIZE_TWO_INCH,
                         SIZE_THREE_INCH, SIZE_FOUR_INCH, SIZE_SIX_INCH, SIZE_EIGHT_INCH, SIZE_TEN_INCH,
                         SIZE_TWELVE_INCH]
# meter size indicies
SIZE_INDEX_FOUR_INCH        = 0
SIZE_INDEX_SIX_INCH         = 1
SIZE_INDEX_EIGHT_INCH       = 2
SIZE_INDEX_TEN_INCH         = 3
SIZE_INDEX_TWELVE_INCH      = 4
# pulse output types
PULSE_TYPE_10G_PER_PULSE    = '10G/P'
PULSE_TYPE_100G_PER_PULSE   = '100G/P'
PULSE_TYPE_1000G_PER_PULSE  = '1000G/P'
PULSE_TYPE_10L_PER_PULSE    = '10L/P'
PULSE_TYPE_100L_PER_PULSE   = '100L/P'
PULSE_TYPE_1000L_PER_PULSE  = '1000L/P'
PULSE_TYPE_100_HZ           = '100Hz'
PULSE_TYPE_400_100_HZ       = '100Hz-400'
PULSE_TYPE_600_100_HZ       = '100Hz-600'
PULSE_TYPE_800_100_HZ       = '100Hz-800'
PULSE_TYPE_1000_100_HZ      = '100Hz-1000'

# turbine flow meter set points
# these are the values of Y0 used as the scale
# to transform into the linearized form. see flow bench notes.
TURBINE_NORM_SET_POINTS = numpy.array([0.0, 0.04, 0.08, 0.16, 0.32, 0.64, 1.28, 2.56])
# intervals are:
# 1.28-2.56+ (projected point) 
# 0.64-1.28 
# 0.32-0.64
# 0.16-0.32
# 0.08-0.16
# 0.04-0.08
# 0.0-0.04
# for each of the intervals above, the turbine is calibrated at the below values
TURBINE_NORM_CAL_FLOW_RATES = numpy.array([1.00, 0.64, 0.32, 0.16, 0.08, 0.04, 0.02])

# NUMBER OF ATTEMPTS TO SEND/RECEIVE SERIAL COMMANDS BEFORE FAILING
NUM_SERIAL_COM_ATTEMPTS = 10
#-------------------------------------------------------------------------
# Flow Meter Base Class
#-------------------------------------------------------------------------
class FlowMeter():
    def __init__(self):
        """
        flow meter attributes
        """
        # nominal size of meter
        self.nominal_size       = None
        # meter label (product identity)
        self.product_label      = None
        # k-factor
        self.k_factor           = None
        # test k-factorsz
        self.test_k_factor      = None
        # date of calibration
        self.calibration_date   = datetime.today().isoformat(' ')
        # calibration flow rates
        self.fs_flow_rate       = None
        self.ls_flow_rate       = None
        # maximum and cutoff flow rates
        self.max_flow_rate      = None
        self.min_flow_rate      = None
        # accurancy allowance (gpm) 
        self.allowance          = None
        # identifies if meter has 4-20 analog output 
        self.has_analog_out     = True
        # test frequency
        self.test_freq          = 1000.0
        # population mean fsadc, zradc
        self.typical_fsadc      = None
        self.typical_zradc      = None
        # location of cal values in EEPROM
        self.EEPROM_FSADC_STARTING_INDEX = 6
        self.EEPROM_ZRADC_STARTING_INDEX = 2
        # flow meter software version
        self.revision           = None
        # holds options numbers
        self.options            = [OPTION_STANDARD,]
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5
        # reasonable k-factor limits
        # used for quick test that meter is acceptable.
        # this is a percentage
        self.reasonable_accuracy_limit = 10.0
##        self.reasonable_accuracy_limit = 30.0
        # enable mut's analog output test by default
        self.test_analog_output = True
        # Implement reasonable limits on resulting ZRADC value
        self.zradc_limit_upper = 6.0
        self.zradc_limit_lower = -4.0

        """
        serial communication attributes
        """
        # serial connection object
        self.serial_con         = None
        # seametrics serial number
        self.serial_num         = None
        # error code (serial string returned from meter
        # meter error occurred)
        self.ERROR_RESPONSE    = '!x'
        # serial communication settings
        self.TIME_OUT          = 1
        self.BAUD_RATE         = 2400
        self.BYTE_SIZE         = serial.EIGHTBITS
        self.PARITY            = serial.PARITY_NONE
        self.STOP_BITS         = serial.STOPBITS_ONE
        # string length of flow meter software version
        self.METER_VERSION_LENGTH = 10

    def GetOptions(self):
        return self.options
    
    def GetAllowance(self):
        """
        Return accuracy allowance
        """
        assert type(self.allowance) == float
        return self.allowance

    def SetCalibrationDate(self):
        """
        Return date of calibration
        """
        self.calibration_date = datetime.today().isoformat(' ')
    
    def GetCalibrationDate(self):
        """
        Return date of calibration
        """
        assert self.calibration_date != None
        return self.calibration_date
    
    def SetLabel(self, product_label):
        """
        Set meter label
        """
        assert type(product_label) in [str, unicode]
        self.product_label = product_label
        
    def SetSerialNumber(self, serial_num):
        """
        Set meter serial number
        """
        assert type(serial_num) in [str, unicode]
        self.serial_num = serial_num

    def GetLabel(self):
        """
        Return product label
        """
        assert type(self.product_label) in [str, unicode]
        return self.product_label

    def GetSerialNumber(self):
        """
        Return meter serial number
        """
        assert type(self.serial_num) in [str, unicode] or self.serial_num == None
        return self.serial_num

    def GetTestKFactor(self):
        """
        Returns the test k-factor
        to use during calibration
        """
        return self.test_freq*SEC_PER_MIN/self.GetMaxFlowRate()
    
    def GetTestFreq(self):
        """
        Returns the full scale frequency
        to use during calibration
        """
        assert type(self.test_freq) == float
        return self.test_freq
        
    def GetFSFreq(self):
        """
        Return FS frequency
        """
        return self.GetKFactor()*self.GetMaxFlowRate()/SEC_PER_MIN

    def GetKFactor(self):
        """Return meter ideal k-factor"""
        assert type(self.k_factor) == float
        return self.k_factor

    def GetFSFlowRate(self):
        """
        Return ideal fs calibration flow rate
        """
        assert type(self.fs_flow_rate) == float
        return self.fs_flow_rate

    def GetLSFlowRate(self):
        """
        Return ideal ls calibration flow rate
        """
        assert type(self.ls_flow_rate) == float
        return self.ls_flow_rate

    def GetMaxFlowRate(self):
        """
        Return specified maximum flow rate
        """
        assert type(self.max_flow_rate) == float
        return self.max_flow_rate

    def GetMinFlowRate(self):
        """Return specified minimum flow rate
        """
        return self.min_flow_rate

    def GetTypicalFSADC(self):
        """
        Return population mean fsadc calibration value
        """
        assert type(self.typical_fsadc) == float
        return self.typical_fsadc

    def GetTypicalZRADC(self):
        """
        Return population mean zradc calibration value
        """
        assert type(self.typical_zradc) == float
        return self.typical_zradc

    def SetOptions(self, s):
        assert s in NOMINAL_SIZES
        if s == SIZE_THREE_QUARTERS_INCH:
            self.options = [OPTION_STANDARD,
                            PE102_OPTION_270,
                            PE102_OPTION_271,
                            PE102_OPTION_272,
                            PE102_OPTION_277,
                            ]
        elif s == SIZE_THREE_EIGHTS_INCH:
            self.options = [OPTION_STANDARD,
                            PE102_OPTION_270,
                            PE102_OPTION_277,
                            ]
        
    def SetNominalSize(self, s):
        """
        Set nominal size of flow meter
        """
        assert s in NOMINAL_SIZES
        self.nominal_size = s
        self.SetOptions(s)
        
    def GetNominalSize(self):
        """
        Return nominal size of flow meter
        """
        assert type(self.nominal_size) == str
        return self.nominal_size

    def GetRevision(self):
        """
        Return software revision of flow meter
        """
        assert type(self.revision) == str
        return self.revision

    def SetRevision(self, value):
        """
        Set software revision of flow meter
        """
        assert type(value) == str
        self.revision = value

    def GetTargetLSTestTime(self):
        return self.target_LS_test_time
    
    def GetTargetFSTestTime(self):
        return self.target_FS_test_time
    
    def GetReasonableAccuracyLimit(self):
        return self.reasonable_accuracy_limit
    
    #-----------------------------------
    # Serial Communication
    #-----------------------------------
    def WakeUp(self, c):
        c.FlushOutput()
        c.FlushInput()
        c.Write('#')
        time.sleep(0.75)
        c.Write('#')
        time.sleep(0.75)
        
    def SerialConnect(self, port):                      
        """Create serial com instance"""
        try:
            self.serial_con = mySerial.mySerial(port,
                                                    self.BAUD_RATE,
                                                    self.BYTE_SIZE,
                                                    self.PARITY,
                                                    self.STOP_BITS,
                                                    self.TIME_OUT)
            self.serial_con.Open()
            if self.serial_con.IsOpen():
                return True
            else:
                return False
        except:
            return False

    def SerialDisconnect(self):
        """disconnect from serial com"""
        if self.serial_con: self.serial_con.Close()
                
    def IsSerialConnectionOpen(self):
        """
        Returns True if a connection to a flow meter is open
        """
        if self.serial_con == None:return False
        if self.serial_con.IsOpen():return True        
        
    def GetSerialConnection(self):
        """Return serial com instance"""
        return self.serial_con
    
    def TestResponse(self):
        """
        Returns True if flow meter is responding on the current port
        otherwise returns False
        """
        return self.SetSerialReadyState()
        
    def WriteEnableFilter(self):
        """
        Enables Meter filter
        """
        c = self.GetSerialConnection()
        for i in range(NUM_SERIAL_COM_ATTEMPTS):
            self.WakeUp(c)
            c.Write('b')
            time.sleep(0.75)
            if 'f' in c.Read(c.InWaiting()):
                c.FlushInput()
                c.FlushOutput()
                return True
        return False

    def WriteDisableFilter(self):
        """
        Disables Meter filter (Enables averaging)
        """
        c = self.GetSerialConnection()
        for i in range(NUM_SERIAL_COM_ATTEMPTS):
            self.WakeUp(c)
            c.Write('a')
            time.sleep(0.75)
            if 'f' in c.Read(c.InWaiting()):
                c.FlushInput()
                c.FlushOutput()
                return True
        return False
    
    def WriteFreq(self):
        """
        Set FS Frequency value in EEPROM
        """
        c = self.GetSerialConnection()
        for i in range(NUM_SERIAL_COM_ATTEMPTS):
            self.WakeUp(c)
            c.Write('S$'+self.ReadString(self.GetFSFreq())+'\r')
            time.sleep(0.75)
            if 'f' in c.Read(c.InWaiting()):
                c.FlushInput()
                c.FlushOutput()
                return True
        return False

    def WriteTestFreq(self):
        """
        Set FS Frequency value in EEPROM
        """
        c = self.GetSerialConnection()
        for i in range(NUM_SERIAL_COM_ATTEMPTS):
            self.WakeUp(c)
            c.Write('S$'+self.ReadString(self.GetTestFreq())+'\r')
            time.sleep(0.75)
            if 'f' in c.Read(c.InWaiting()): return True
            c.FlushInput()
            c.FlushOutput()
        return False
        
    def WriteFSADC(self, fsadc):
        """
        Set FSADC value in EEPROM
        """
        print 'Write FSADC:',fsadc
        c = self.GetSerialConnection()
        for i in range(NUM_SERIAL_COM_ATTEMPTS):
            self.WakeUp(c)
            c.Write('f$'+self.ReadString(fsadc)+'\r')
            time.sleep(0.75)
            if 'f' in c.Read(c.InWaiting()):
                c.FlushInput()
                c.FlushOutput()
                return True
        return False

    def WriteZRADC(self, zradc):
        """
        Set ZRADC value in EEPROM
        """
        print 'Write ZRADC:',zradc
        c = self.GetSerialConnection()
        for i in range(NUM_SERIAL_COM_ATTEMPTS):
            self.WakeUp(c)
            c.Write('z$'+self.ReadString(zradc)+'\r')
            time.sleep(0.75)
            if 'f' in c.Read(c.InWaiting()):
                c.FlushInput()
                c.FlushOutput()
                return True
        return False
        
    def ReadFSADC(self):
        "Read ZRADC from EEPROM"
        value = self.ReadEEProm(self.EEPROM_FSADC_STARTING_INDEX)
        if myUtil.IsNumber(value): return string.atof(value)
        else: return None
    
    def ReadZRADC(self):
        "Read ZRADC from EEPROM"
        value = self.ReadEEProm(self.EEPROM_ZRADC_STARTING_INDEX)
        if myUtil.IsNumber(value): return string.atof(value)
        else: return None
    
    def ReadEEProm(self, loc):
        "Read a single register from the EEPROM"
        val = ''
 
        loc1 = loc+1
        loc2 = loc+2
        loc3 = loc+3
        
        if loc > 9: loc = str(loc)[1] + str(loc)[0]
        if loc1 > 9: loc1 = str(loc1)[1] + str(loc1)[0]
        if loc2 > 9: loc2 = str(loc2)[1] + str(loc2)[0]
        if loc3 > 9: loc3 = str(loc3)[1] + str(loc3)[0]
        
        val = self.ReadRegisterValue(loc)
        self.SetSerialReadyState()
        val1 = self.ReadRegisterValue(loc1)
        self.SetSerialReadyState()
        val2 = self.ReadRegisterValue(loc2)
        self.SetSerialReadyState()
        val3 = self.ReadRegisterValue(loc3)
        
        if val != None and val1 != None and val2 != None and val3 != None:
            return myHex2Float.Hex2Float(string.upper(val+val1+val2+val3))
        else: return None

    def ReadString(self, myFloat):
        "Format input into appropriate form for floating point input"
        # set decimal precision  
        my_string = '%0.6f'%myFloat
        if numpy.absolute(myFloat) > 9.999999: my_string = '%0.5f'%myFloat 
        if numpy.absolute(myFloat) > 99.99999: my_string = '%0.4f'%myFloat      
        if numpy.absolute(myFloat) > 999.9999: my_string = '%0.3f'%myFloat
        if numpy.absolute(myFloat) > 9999.999: my_string = '%0.2f'%myFloat    
        # if value is negative reduce length by 1 to account for sign
        if numpy.sign(myFloat) == -1: my_string = my_string[0:-1]        
        # start from right side
        mx = len(my_string)
        # meter may only receive 7 digits (not including decimal)
        s=''
        for i in range(mx): s+=my_string[mx-i-1]
        return s

    def ReadRegisterValue(self, loc):
        "Get floating point value from EEPROM register"
        c = self.GetSerialConnection()
        c.FlushInput()
        c.FlushOutput()
        self.WakeUp(c)     
        c.Write('R$%s\r'%loc)
        time.sleep(0.75)
        x = c.Read(2)
        c.FlushInput()
        c.FlushOutput()
        try:
            if x[0] in INT_BINARY_DICT.keys() and x[1] in INT_BINARY_DICT.keys():
                return x
        except:
            return None
   
    def SetSerialReadyState(self):
        """
        Sets flow meter in state ready
        to accept serial commands
        """
        c = self.GetSerialConnection()
        x=''
        for i in range(NUM_SERIAL_COM_ATTEMPTS):
            c.Write('#')
            time.sleep(0.75)            
            if c.InWaiting() >= 2:
                x = c.Read(c.InWaiting())
                if '!x' in x or '!t' in x or '!o' in x:
                    c.FlushInput()
                    c.FlushOutput()
                    return True
        return False
            
    def ReadSoftwareVersion(self):
        """
        Returns sotware revision as string
        """
        print 'getting software version'
        c = self.GetSerialConnection()
        self.WakeUp(c)
        c.Write('A\r')
        time.sleep(0.75)
        x = c.Read(c.InWaiting())
        x = x.replace('*','')
        x = x.replace('\t','')
        x = x.replace('\n','')
        x = x.replace(' ', '')  
        x = x.replace('-', '')
        x = x.replace('Cp', '')
        x = x.replace('cP', '')
        x = x.replace('CP', '')
        x = x.replace('cp', '')
        c.FlushInput()
        c.FlushOutput()
        return x
    
        
#-------------------------------------------------------------------------
# PE102 Flow Meter Class
#-------------------------------------------------------------------------       
class PE102_REV_C(FlowMeter):
    def __init__(self):
        FlowMeter.__init__(self)
        # location of cal values in EEPROM
        self.EEPROM_FSADC_STARTING_INDEX = 10
        self.EEPROM_ZRADC_STARTING_INDEX = 2
        # software version
        self.revision = '13848C'        
        
    def SetOption(self, option):
        assert option in self.options                               
        if option == OPTION_STANDARD:
            if self.GetNominalSize() == SIZE_THREE_EIGHTS_INCH:
                self.SetIdentity038()
            elif self.GetNominalSize() == SIZE_THREE_QUARTERS_INCH:
                self.SetIdentity075()
            return True
        elif option == PE102_OPTION_270:
            self.SetIdentity075_270()
            return True
        elif option == PE102_OPTION_271:
            self.SetIdentity075_271()
            return True
        elif option == PE102_OPTION_272:
            self.SetIdentity075_272()
            return True
        else: return False
        
    def SetIdentity038(self):
        """
        set identity of PE102 to 3/8" flow meter
        """
        self.SetLabel(METER_LABEL_PE102_038)
        # 500 ppL
        self.k_factor = self.test_k_factor = 1000.0*3.78541
        # maximum and flow rates
        self.max_flow_rate = 3.0
        self.min_flow_rate = 0.03
        # calibration flow rates
        self.fs_flow_rate = 2.0
        self.ls_flow_rate = 0.15
        # accuracy allowance
        self.allowance = 0.002
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = -267.3
        self.typical_zradc = 0.0
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_EIGHTS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5  
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0
        
    def SetIdentity075(self):
        """
        set identity of PE102 to 3/4" flow meter
        """
        self.SetLabel(METER_LABEL_PE102_075)
        # 500 ppL
        self.k_factor = self.test_k_factor = 500.0*3.78541
        # maximum and flow rates
        self.max_flow_rate = 20.0
        self.min_flow_rate = 0.2
        # calibration flow rates
        self.fs_flow_rate = 18.0
        self.ls_flow_rate = 0.75
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = -417.0
        self.typical_zradc = 0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5 
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0

    def SetIdentity075_270(self):
        """
        set identity of PE102 to PE102-075-270
        """
        self.SetLabel(METER_LABEL_PE102_075_270)
        self.k_factor = 330.0
        # maximum and flow rates
        self.max_flow_rate = 20.0
        self.min_flow_rate = 0.2
        # calibration flow rates
        self.fs_flow_rate = 18.0
        self.ls_flow_rate = 0.75
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = -417.0
        self.typical_zradc = 0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5 
        # Disable analog output test
        self.test_analog_output = False
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0

    def SetIdentity075_271(self):
        """
        set identity of PE102 to PE-075-271
        """
        self.SetLabel(METER_LABEL_PE102_075_271)
        self.k_factor = 3785.411*5.0
        # maximum and flow rates
        self.max_flow_rate = 4.0
        self.min_flow_rate = 0.15
        # calibration flow rates
        self.fs_flow_rate = 4.0
        self.ls_flow_rate = 0.5
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = -417.0
        self.typical_zradc = 0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5 
        
##        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0

    def SetIdentity075_272(self):
        """
        set identity of PE102 to PE102-075-272
        """
        self.SetLabel(METER_LABEL_PE102_075_272)
        self.k_factor = 10000.0
        # maximum and flow rates
        self.max_flow_rate = 8.0
        self.min_flow_rate = 0.2
        # calibration flow rates
        self.fs_flow_rate = 7.0
        self.ls_flow_rate = 0.75
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = -420.0
        self.typical_zradc = -0.5
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*1.0
        self.target_LS_test_time = 60.0*4.0 
        
##        assert self.max_flow_rate >= 100.0*self.min_flow_rate
##        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0      

    def ReadSoftwareVersion(self):
        """
        Returns sotware revision as string
        """
        print 'getting software version'
        c = self.GetSerialConnection()
        self.WakeUp(c)
        c.Write('V\r')
        time.sleep(0.75)
        x = c.Read(c.InWaiting())
        x = x.replace('*','')
        x = x.replace('\t','')
        x = x.replace('\n','')
        x = x.replace(' ', '')  
        x = x.replace('-', '')
        x = x.replace('Cp', '')
        x = x.replace('cP', '')
        x = x.replace('CP', '')
        x = x.replace('cp', '')
        c.FlushInput()
        c.FlushOutput()
        return x
    
class PE102_REV_D(PE102_REV_C):
    def __init__(self):
        PE102_REV_C.__init__(self)
        # software version
        self.revision = '13848D'

    def SetOption(self, option):
        assert option in self.options                               
        if option == OPTION_STANDARD:
            if self.GetNominalSize() == SIZE_THREE_EIGHTS_INCH:
                self.SetIdentity038()
            elif self.GetNominalSize() == SIZE_THREE_QUARTERS_INCH:
                self.SetIdentity075()
            return True
        elif option == PE102_OPTION_270:
            self.SetIdentity075_270()
            return True
        elif option == PE102_OPTION_271:
            self.SetIdentity075_271()
            return True
        elif option == PE102_OPTION_272:
            self.SetIdentity075_272()
            return True
        else: return False        

    def SetIdentity038(self):
        """
        set identity of PE102 to 3/8" flow meter
        """
        self.SetLabel(METER_LABEL_PE102_038)
        # 500 ppL
        self.k_factor = self.test_k_factor = 1000.0*3.78541
        # maximum and flow rates
        self.max_flow_rate = 3.0
        self.min_flow_rate = 0.03
        # calibration flow rates
        self.fs_flow_rate = 2.0
        self.ls_flow_rate = 0.15
        # accuracy allowance
        self.allowance = 0.002
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = 267.3
        self.typical_zradc = 0.0
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_EIGHTS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5  
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0
        
    def SetIdentity075(self):
        """
        set identity of PE102 to 3/4" flow meter
        """
        self.SetLabel(METER_LABEL_PE102_075)
        # 500 ppL
        self.k_factor = self.test_k_factor = 500.0*3.78541
        # maximum and flow rates
        self.max_flow_rate = 20.0
        self.min_flow_rate = 0.2
        # calibration flow rates
        self.fs_flow_rate = 18.0
        self.ls_flow_rate = 0.75
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = 417.0
        self.typical_zradc = -0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5 
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0
        
    def SetIdentity075_270(self):
        """
        set identity of PE102 to PE-075-270
        """
        self.SetLabel(METER_LABEL_PE102_075_270)
        self.k_factor = 330.0
        # maximum and flow rates
        self.max_flow_rate = 20.0
        self.min_flow_rate = 0.2
        # calibration flow rates
        self.fs_flow_rate = 18.0
        self.ls_flow_rate = 0.75
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = 417.0
        self.typical_zradc = -0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5 
        # Disable analog output test
        self.test_analog_output = False
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0

    def SetIdentity075_271(self):
        """
        set identity of PE102 to PE-075-271
        """
        self.SetLabel(METER_LABEL_PE102_075_271)
        self.k_factor = 3785.411*5.0
        # maximum and flow rates
        self.max_flow_rate = 4.0
        self.min_flow_rate = 0.15
        # calibration flow rates
        self.fs_flow_rate = 4.0
        self.ls_flow_rate = 0.5
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = 417.0
        self.typical_zradc = -0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5 
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0
        
    def SetIdentity075_272(self):
        """
        set identity of PE102 to PE-075-272
        """
        self.SetLabel(METER_LABEL_PE102_075_272)
        self.k_factor = 10000.0
        # maximum and flow rates
        self.max_flow_rate = 8.0
        self.min_flow_rate = 0.2
        # calibration flow rates
        self.fs_flow_rate = 7.0
        self.ls_flow_rate = 0.75
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = 420.0
        self.typical_zradc = -0.5
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*1.0
        self.target_LS_test_time = 60.0*4.0 
        
##        assert self.max_flow_rate >= 100.0*self.min_flow_rate
##        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0      

    def ReadFSADC(self):
        """
        Returns FSADC as float
        """
        print 'reading fsadc'
        c = self.GetSerialConnection()
        self.WakeUp(c)
        c.Write('G')
        time.sleep(0.75)
        x = c.Read(c.InWaiting())
        c.FlushInput()
        c.FlushOutput()
        x = myHex2Float.Hex2Float(string.upper(x))
        if myUtil.IsNumber(x): return string.atof(x)
        else: return None

    def ReadZRADC(self):
        """
        Returns ZRADC as float
        """
        print 'reading zradc'
        c = self.GetSerialConnection()
        self.WakeUp(c)
        c.Write('H')
        time.sleep(0.75)
        x = c.Read(c.InWaiting())
        c.FlushInput()
        c.FlushOutput()
        x = myHex2Float.Hex2Float(string.upper(x))
        if myUtil.IsNumber(x): return string.atof(x)
        else: return None
    
    def ReadEmptyPipe(self):
        """
        Returns True if meter detecting empty pipe,
        otherwise False
        """
        print 'reading empty pipe'
        c = self.GetSerialConnection()
        self.WakeUp(c)
        c.Write('e\r')
        time.sleep(0.75)
        x = c.Read(c.InWaiting())
        c.FlushInput()
        c.FlushOutput()
        if x == '1': return True
        elif x == '0': return False
        else: return None
    
    def ReadADC(self):
        """
        Returns averaged ADC measurment
        """
        print 'getting ADC measurement'
        c = self.GetSerialConnection()
        self.WakeUp(c)
        c.Write('Z')
        time.sleep(0.75)
        i=0
        while c.InWaiting() < 8:
            time.sleep(0.5)
            if i >= 120: break
            else: i+=1
            
        x = c.Read(c.InWaiting())
        c.FlushInput()
        c.FlushOutput()
        return x   

    def ReadSoftwareVersion(self):
        """
        Returns sotware revision as string
        """
        print 'getting software version'
        c = self.GetSerialConnection()
        self.WakeUp(c)
        c.Write('A\r')
        time.sleep(0.75)
        x = c.Read(c.InWaiting())
        x = x.replace('*','')
        x = x.replace('\t','')
        x = x.replace('\n','')
        x = x.replace(' ', '')  
        x = x.replace('-', '')
        x = x.replace('Cp', '')
        x = x.replace('cP', '')
        x = x.replace('CP', '')
        x = x.replace('cp', '')
        c.FlushInput()
        c.FlushOutput()
        return x

class PE102_REV_E(PE102_REV_D):
    def __init__(self):
        PE102_REV_D.__init__(self)
        # software version
        self.revision = '13848E'

class PE102_REV_F(PE102_REV_E):
    def __init__(self):
        PE102_REV_E.__init__(self)
        # software version
        self.revision = '13848F'

class PE102_REV_G(PE102_REV_F):
    def __init__(self):
        PE102_REV_F.__init__(self)
        # software version
        self.revision = '13848G'
        # filter constant
        # zero is no filter
        # 1 is max filter (i.e., no change in output)
        self.filter_constant    = 0.7        
        # filter constant used during calibration
        self.calibration_filter_constant = 0.5
     
    def SetOption(self, option):
        assert option in self.options                               
        if option == OPTION_STANDARD:
            if self.GetNominalSize() == SIZE_THREE_EIGHTS_INCH:
                self.SetIdentity038()
            elif self.GetNominalSize() == SIZE_THREE_QUARTERS_INCH:
                self.SetIdentity075()
            return True
        elif option == PE102_OPTION_270:
            self.SetIdentity075_270()
            return True
        elif option == PE102_OPTION_271:
            self.SetIdentity075_271()
            return True
        elif option == PE102_OPTION_272:
            self.SetIdentity075_272()
            return True
        elif option == PE102_OPTION_277:
            if self.GetNominalSize() == SIZE_THREE_EIGHTS_INCH:
                self.SetIdentity038_277()
            elif self.GetNominalSize() == SIZE_THREE_QUARTERS_INCH:
                self.SetIdentity075_277()
            return True
        else: return False
        
    def SetIdentity038_277(self):
        """
        set identity of PE102 to 3/8" flow meter
        """
        self.SetLabel(METER_LABEL_PE102_038_277)
        # 500 ppL
        self.k_factor = 1000.0*3.78541*5.0
        # maximum and flow rates
        self.max_flow_rate = 3.0
        self.min_flow_rate = 0.03
        # filter value
        self.filter_constant = 0.75
        # calibration flow rates
        self.fs_flow_rate = 2.0
        self.ls_flow_rate = 0.2
        # accuracy allowance
        self.allowance = 0.001
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = 283.0
        self.typical_zradc = 0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_EIGHTS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*1.0
        self.target_LS_test_time = 60.0*1.5  
        # filter constant used during calibration
        self.calibration_filter_constant = 0.5
        # filter constant
        # zero is no filter
        # 1 is max filter (i.e., no change in output)
        self.filter_constant = 0.65
        # Disable analog output test
        self.test_analog_output = False
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0

    def SetIdentity038(self):
        """
        set identity of PE102 to 3/8" flow meter
        """
        self.SetLabel(METER_LABEL_PE102_038)
        # 500 ppL
        self.k_factor = self.test_k_factor = 1000.0*3.78541
        # maximum and flow rates
        self.max_flow_rate = 3.0
        self.min_flow_rate = 0.03
        # filter value
        self.filter_constant = 0.6
        # calibration flow rates
        self.fs_flow_rate = 2.5
        self.ls_flow_rate = 0.1 
        # accuracy allowance
        self.allowance = 0.002
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = 289.0
        self.typical_zradc = 1.6
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_EIGHTS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5  
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0
        
    def SetIdentity075(self):
        """
        set identity of PE102 to 3/4" flow meter
        """
        self.SetLabel(METER_LABEL_PE102_075)
        # 500 ppL
        self.k_factor = self.test_k_factor = 500.0*3.78541
        # maximum and flow rates
        self.max_flow_rate = 20.0
        self.min_flow_rate = 0.2
        # filter value
        self.filter_constant = 0.6
        # calibration flow rates
        self.fs_flow_rate = 12.0
        self.ls_flow_rate = 0.75
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = 417.0
        self.typical_zradc = -0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5 
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0
        
    def SetIdentity075_277(self):
        """
        set identity of PE102 to 3/4" flow meter
        """
        self.SetLabel(METER_LABEL_PE102_075_277)
        # 500 ppL
        self.k_factor = 10000.0
        # maximum and flow rates
        self.max_flow_rate = 8.0
        self.min_flow_rate = 0.2
        # filter value
        self.filter_constant = 0.75
        # calibration flow rates
        self.fs_flow_rate = 8.0
        self.ls_flow_rate = 0.75
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc obtained from "pop mean" xlsx file in source code folder
        self.typical_fsadc = 171.5
        self.typical_zradc = 0.97
##        self.typical_fsadc = 200.0
##        self.typical_zradc = -0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*1.0
        self.target_LS_test_time = 60.0*1.5  
        # filter constant used during calibration
        self.calibration_filter_constant = 0.5
        # filter constant
        # zero is no filter
        # 1 is max filter (i.e., no change in output)
        self.filter_constant = 0.65
        # Disable analog output test
        self.test_analog_output = False
        
        
    def SetIdentity075_270(self):
        """
        set identity of PE102 to PE-075-270
        """
        self.SetLabel(METER_LABEL_PE102_075_270)
        self.k_factor = 330.0
        # maximum and flow rates
        self.max_flow_rate = 20.0
        self.min_flow_rate = 0.2
        # filter value
        self.filter_constant = 0.6
        # calibration flow rates
        self.fs_flow_rate = 12.0
        self.ls_flow_rate = 0.75
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS,not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc obtained from "pop mean" xlsx file in source code folder
        self.typical_fsadc = 431.1
        self.typical_zradc = 0.93
##        self.typical_fsadc = 420.0
##        self.typical_zradc = 0.5
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5 
        # Disable analog output test
        self.test_analog_output = False
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0

    def SetIdentity075_271(self):
        """
        set identity of PE102 to PE-075-271
        """
        self.SetLabel(METER_LABEL_PE102_075_271)
        self.k_factor = 3785.411*5.0
        # maximum and flow rates
        self.max_flow_rate = 4.0
        self.min_flow_rate = 0.15
        # filter value
        self.filter_constant = 0.6
        # calibration flow rates
        self.fs_flow_rate = 4.0
        self.ls_flow_rate = 0.5
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = 417.0
        self.typical_zradc = -0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*0.5
        self.target_LS_test_time = 60.0*1.5 
        
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0
        
    def SetIdentity075_272(self):
        """
        set identity of PE102 to PE-075-272
        """
        self.SetLabel(METER_LABEL_PE102_075_272)
        self.k_factor = 10000.0
        # maximum and flow rates
        self.max_flow_rate = 8.0
        self.min_flow_rate = 0.2
        # filter value
        self.filter_constant = 0.6
        # calibration flow rates
        self.fs_flow_rate = 7.0
        self.ls_flow_rate = 0.75
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc
        self.typical_fsadc = 420.0
        self.typical_zradc = -0.5
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*1.0
        self.target_LS_test_time = 60.0*4.0 
        
##        assert self.max_flow_rate >= 100.0*self.min_flow_rate
##        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0

    def WriteFLTR(self, value):
        """
        Set FLTR value in EEPROM
        """
        c = self.GetSerialConnection()
        for i in range(NUM_SERIAL_COM_ATTEMPTS):
            self.WakeUp(c)
            c.Write('o$'+self.ReadString(value)+'\r')
            time.sleep(0.75)
            if 'f' in c.Read(c.InWaiting()):
                c.FlushInput()
                c.FlushOutput()
                return True
        return False
        
    def ReadFLTR(self):
        """
        Returns FLTR as float
        """
        print 'reading fltr'
        c = self.GetSerialConnection()
        self.WakeUp(c)
        c.Write('O\r')
        time.sleep(0.75)
        x = c.Read(c.InWaiting())
        c.FlushInput()
        c.FlushOutput()
        x = myHex2Float.Hex2Float(string.upper(x))
        if myUtil.IsNumber(x): return string.atof(x)
        else: return None
        
    def GetFilterConstant(self):
        """
        get the value of the filter constant
        0 is not filter
        1 is max filter (no change in output)
        """
        assert type(self.filter_constant) == float
        return self.filter_constant
    
    def SetFilterConstant(self, value):
        """
        get the value of the filter constant
        0 is not filter
        1 is max filter (no change in output)
        """
        assert type(self.filter_constant) == float
        self.filter_constant = value
        
    def GetCalibrationFilterConstant(self):
        return self.calibration_filter_constant
    
class PE102_REV_H(PE102_REV_G):
    def __init__(self):
        PE102_REV_G.__init__(self)
        # software version
        self.revision = '13848H'
        # options
     
    def SetOption(self, option):
        assert option in self.options                               
        if option == OPTION_STANDARD:
            if self.GetNominalSize() == SIZE_THREE_EIGHTS_INCH:
                self.SetIdentity038()
            elif self.GetNominalSize() == SIZE_THREE_QUARTERS_INCH:
                self.SetIdentity075()
            return True
        
        elif option == PE102_OPTION_270:
            if self.GetNominalSize() == SIZE_THREE_EIGHTS_INCH:
                self.SetIdentity038_270()
            elif self.GetNominalSize() == SIZE_THREE_QUARTERS_INCH:
                self.SetIdentity075_270()
            return True
        
        elif option == PE102_OPTION_277:
            if self.GetNominalSize() == SIZE_THREE_EIGHTS_INCH:
                self.SetIdentity038_277()
            elif self.GetNominalSize() == SIZE_THREE_QUARTERS_INCH:
                self.SetIdentity075_277()
            return True

        elif option == PE202_STANDARD:
            if self.GetNominalSize() == SIZE_THREE_EIGHTS_INCH:
                self.SetIdentity038_PE202()
            elif self.GetNominalSize() == SIZE_THREE_QUARTERS_INCH:
                self.SetIdentity075_PE202()
            return True

        elif option == PE202_OPTION_138:
            if self.GetNominalSize() == SIZE_THREE_EIGHTS_INCH:
                self.SetIdentity038_PE202_138()
            elif self.GetNominalSize() == SIZE_THREE_QUARTERS_INCH:
                self.SetIdentity075_PE202_138()
            return True

        elif option == PE202_OPTION_270:
            if self.GetNominalSize() == SIZE_THREE_EIGHTS_INCH:
                self.SetIdentity038_PE202_270()
            elif self.GetNominalSize() == SIZE_THREE_QUARTERS_INCH:
                self.SetIdentity075_PE202_270()
            return True

        elif option == PE202_OPTION_277:
            if self.GetNominalSize() == SIZE_THREE_EIGHTS_INCH:
                self.SetIdentity038_PE202_277()
            elif self.GetNominalSize() == SIZE_THREE_QUARTERS_INCH:
                self.SetIdentity075_PE202_277()
            return True

        elif option == PE202_OPTION_400:
            if self.GetNominalSize() == SIZE_THREE_EIGHTS_INCH:
                self.SetIdentity038_PE202_400()
            elif self.GetNominalSize() == SIZE_THREE_QUARTERS_INCH:
                self.SetIdentity075_PE202_400()
            return True

        else: return False

    def SetIdentity038(self):
        """
        set identity of PE102 to 3/8" flow meter
        """
        self.SetLabel(METER_LABEL_PE102_038)
        # 500 ppL
        self.k_factor = self.test_k_factor = 1000.0*3.78541
        # maximum and flow rates
        self.max_flow_rate = 3.0
        self.min_flow_rate = 0.03
        # filter value
        self.filter_constant = 0.75
        # calibration flow rates
        self.fs_flow_rate = 2.0
        self.ls_flow_rate = 0.1
        # accuracy allowance
        self.allowance = 0.001
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc obtained from "pop mean" xlsx file in source code folder
        self.typical_fsadc = 288.9
        self.typical_zradc = 0.71
##        self.typical_fsadc = 283.0
##        self.typical_zradc = 0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_EIGHTS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*1.0
        self.target_LS_test_time = 60.0*1.5  
        # filter constant used during calibration
        self.calibration_filter_constant = 0.5
        # filter constant
        # zero is no filter
        # 1 is max filter (i.e., no change in output)
        self.filter_constant = 0.65        
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0

    def SetIdentity038_270(self):
        """
        set identity of PE102 to PE-038-270
        """
        self.SetLabel(METER_LABEL_PE102_038_270)
        self.k_factor = 330.0
        # maximum and flow rates
        self.max_flow_rate = 3.0
        self.min_flow_rate = 0.03
        # calibration flow rates
        self.fs_flow_rate = 2.0
        self.ls_flow_rate = 0.1
        # accuracy allowance
        self.allowance = 0.001
        # Frequency output at FS,not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.test_k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc obtained from "pop mean" xlsx file in source code folder
        self.typical_fsadc = 290.2
        self.typical_zradc = 0.70
##        self.typical_fsadc = 283.0
##        self.typical_zradc = 0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_EIGHTS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*1.0
        self.target_LS_test_time = 60.0*1.5  
        # filter constant used during calibration
        self.calibration_filter_constant = 0.5
        # filter constant
        # zero is no filter
        # 1 is max filter (i.e., no change in output)
        self.filter_constant = 0.65  
        # Disable analog output test
        self.test_analog_output = False 
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0

    def SetIdentity075(self):
        """
        set identity of PE102 to 3/8" flow meter
        """
        self.SetLabel(METER_LABEL_PE102_075)
        # 500 ppL
        self.k_factor = self.test_k_factor = 500.0*3.785411
        # maximum and flow rates
        self.max_flow_rate = 20.0
        self.min_flow_rate = 0.2
        # filter value
        self.filter_constant = 0.75
        # calibration flow rates
        self.fs_flow_rate = 12.0
        self.ls_flow_rate = 0.75
        # accuracy allowance
        self.allowance = 0.005
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc obtained from "pop mean" xlsx file in source code folder
        self.typical_fsadc = 422.7
        self.typical_zradc = 1.17
##        self.typical_fsadc = 417.0
##        self.typical_zradc = -0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_QUARTERS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*1.0
        self.target_LS_test_time = 60.0*1.5  
        # filter constant used during calibration
        self.calibration_filter_constant = 0.5
        # filter constant
        # zero is no filter
        # 1 is max filter (i.e., no change in output)
        self.filter_constant = 0.65        
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0
 
    def SetIdentity075_277(self):
        self.SetIdentity075()
        self.SetLabel(METER_LABEL_PE102_075_277)
        self.k_factor = 10000.0
        self.max_flow_rate = 8.0
        self.fs_flow_rate = 8.0
        self.ls_flow_rate = 0.75
        # Disable analog output test
        self.test_analog_output = False
        
    def SetIdentity038_277(self):
        """
        set identity of PE102 to 3/8" flow meter
        """
        self.SetLabel(METER_LABEL_PE102_038_277)
        # 500 ppL
        self.k_factor = 1000.0*3.78541*5.0
        # maximum and flow rates
        self.max_flow_rate = 3.0
        self.min_flow_rate = 0.03
        # filter value
        self.filter_constant = 0.75
        # calibration flow rates
        self.fs_flow_rate = 2.0
        self.ls_flow_rate = 0.1
        # accuracy allowance
        self.allowance = 0.001
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc obtained from "pop mean" xlsx file in source code folder
        self.typical_fsadc = 288.0
        self.typical_zradc = 0.53
##        self.typical_fsadc = 283.0
##        self.typical_zradc = 0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_EIGHTS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*1.0
        self.target_LS_test_time = 60.0*1.5  
        # filter constant used during calibration
        self.calibration_filter_constant = 0.5
        # filter constant
        # zero is no filter
        # 1 is max filter (i.e., no change in output)
        self.filter_constant = 0.65
        # Disable analog output test
        self.test_analog_output = False
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0
    
    def SetIdentity038_400(self):
        #CURRENTLY JUST A COPY OF SetIdentity038_277
        """
        set identity of PE102 to 3/8" flow meter
        """
        self.SetLabel(METER_LABEL_PE102_038_277)
        # 500 ppL
        self.k_factor = 1000.0*3.78541*5.0
        # maximum and flow rates
        self.max_flow_rate = 3.0
        self.min_flow_rate = 0.03
        # filter value
        self.filter_constant = 0.75
        # calibration flow rates
        self.fs_flow_rate = 2.0
        self.ls_flow_rate = 0.1
        # accuracy allowance
        self.allowance = 0.001
        # Frequency output at FS, not specific
        # to any meter. Meters are temporarily
        # set to this freq only during
        # calibration. This is used to assure
        # good resolution of pulse counts during
        # test.
##        self.test_freq = self.k_factor*self.max_flow_rate/SEC_PER_MIN
        # population mean fsadc, zradc obtained from "pop mean" xlsx file in source code folder
        self.typical_fsadc = 288.0
        self.typical_zradc = 0.53
##        self.typical_fsadc = 283.0
##        self.typical_zradc = 0.25
        # nominal size of meter
        self.SetNominalSize(SIZE_THREE_EIGHTS_INCH)
        # calibration target test times
        self.target_FS_test_time = 60.0*1.0
        self.target_LS_test_time = 60.0*1.5  
        # filter constant used during calibration
        self.calibration_filter_constant = 0.5
        # filter constant
        # zero is no filter
        # 1 is max filter (i.e., no change in output)
        self.filter_constant = 0.65
        # Disable analog output test
        self.test_analog_output = False
        
        assert self.max_flow_rate >= 100.0*self.min_flow_rate
        assert self.max_flow_rate*self.k_factor/SEC_PER_MIN < 1500.0

class PE102_REV_J(PE102_REV_H):
    def __init__(self):
        PE102_REV_H.__init__(self)
        # software version
        self.revision = '13848J'
        # low flow cutoff (fraction of 1)
        self.low_flow_cuttoff = PE102_DEFAULT_LOW_FLOW_CUTTOFF

    def GetLowFlowCuttoff(self):
        return self.low_flow_cuttoff
    
    def SetIdentity075_270(self):
        PE102_REV_H.SetIdentity075_270(self)
        self.low_flow_cuttoff = 0.025
        # Disable analog output test
        self.test_analog_output = False
        
    def SetIdentity038_270(self):
        PE102_REV_H.SetIdentity038_270(self)
        self.low_flow_cuttoff = 0.025
        # Disable analog output test
        self.test_analog_output = False

    def SetIdentity075_277(self):
        PE102_REV_H.SetIdentity075(self)
        self.SetLabel(METER_LABEL_PE102_075_277)
        self.k_factor = 10000.0
        self.max_flow_rate = 8.0
        self.fs_flow_rate = 8.0
        self.ls_flow_rate = 0.75
        # Disable analog output test
        self.test_analog_output = False

    def SetIdentity038_277(self):
        PE102_REV_H.SetIdentity038_277(self)
        # Disable analog output test
        self.test_analog_output = False
        
    def SetIdentity075_400(self):
        PE102_REV_H.SetIdentity075(self)
        self.SetLabel(METER_LABEL_PE202_075_400)
        self.k_factor = 10000.0
        self.max_flow_rate = 8.0
        self.fs_flow_rate = 8.0
        self.ls_flow_rate = 0.75
        # Disable analog output test
        self.test_analog_output = False


    def SetIdentity038_400(self):
        PE102_REV_H.SetIdentity038_400(self)



    #-----------------------------
    # PE202 identities
    #-----------------------------
    def SetIdentity075_PE202(self):
        """
        set identity of new PE102 to 3/4" flow meter
        """
        self.SetIdentity075()
        self.SetLabel(METER_LABEL_PE202_075)
        # population mean fsadc, zradc
        # (validation testing)
##        self.typical_fsadc = 417.0
##        self.typical_zradc = -0.25
        # based on 12/2015 statistics
        self.typical_fsadc = 409.0
        self.typical_zradc = 1.0

    def SetIdentity075_PE202_138(self):
        """
        Same as standard PE202 but w/o 4-20
        """
        self.SetIdentity075_PE202()
        self.SetLabel(METER_LABEL_PE202_075_138)
        self.test_analog_output = False

    def SetIdentity075_PE202_270(self):
        self.SetIdentity075_270()
        self.SetLabel(METER_LABEL_PE202_075_270)
        # based on 12/2015 statistics
        self.typical_fsadc = 409.0
        self.typical_zradc = 1.0

    def SetIdentity075_PE202_277(self):
        self.SetIdentity075_277()
        self.SetLabel(METER_LABEL_PE202_075_277)
        # based on engr sample 32B
        self.typical_fsadc = 164.0
        self.typical_zradc = 1.0
    
    def SetIdentity075_PE202_400(self):
        self.SetIdentity075_400()
        self.SetLabel(METER_LABEL_PE202_075_400)
        #BASED ON NOTHING RIGHT NOW
        self.typical_fsadc = 164.0
        self.typical_zradc = 1.0

    def SetIdentity038_PE202(self):
        """
        set identity of new PE202 to 3/8" flow meter
        """
        self.SetIdentity038()
        self.SetLabel(METER_LABEL_PE202_038)
        # fsadc, zradc result from first prototype
##        self.typical_fsadc = 324.0
##        self.typical_zradc = 2.67
        # based on 12/2015 statistics
        self.typical_fsadc = 325.0
        self.typical_zradc = 1.0

    def SetIdentity038_PE202_138(self):
        """
        Same as standard PE202 but w/o 4-20
        """
        self.SetIdentity038_PE202()
        self.SetLabel(METER_LABEL_PE202_038_138)
        self.test_analog_output = False

    def SetIdentity038_PE202_270(self):
        self.SetIdentity038_270()
        self.SetLabel(METER_LABEL_PE202_038_270)
        # based on 12/2015 statistics
        self.typical_fsadc = 325.0
        self.typical_zradc = 1.0

    def SetIdentity038_PE202_277(self):
        self.SetIdentity038_277()
        self.SetLabel(METER_LABEL_PE202_038_277)
        # based on engr sample 32B
        self.typical_fsadc = 325.0
        self.typical_zradc = 1.0

    def SetIdentity038_PE202_400(self):
        self.SetIdentity038_400()
        self.SetLabel(METER_LABEL_PE202_038_400)
        #  NOT BASED ON ANYTHING EXCEPT VALUES IN THE OTHER METHODS
        self.typical_fsadc = 325.0
        self.typical_zradc = 1.0

    def SetOptions(self, s):
        assert s in NOMINAL_SIZES
        if s == SIZE_THREE_QUARTERS_INCH:
            self.options = [OPTION_STANDARD,
                            PE102_OPTION_270,
                            PE102_OPTION_277,
                            PE202_STANDARD,
                            PE202_OPTION_138,
                            PE202_OPTION_270,
                            PE202_OPTION_277,
                            PE202_OPTION_400,
                            ]
        elif s == SIZE_THREE_EIGHTS_INCH:
            self.options = [OPTION_STANDARD,
                            PE102_OPTION_270,
                            PE102_OPTION_277,
                            PE202_STANDARD,
                            PE202_OPTION_138,
                            PE202_OPTION_270,
                            PE202_OPTION_277,
                            PE202_OPTION_400,
                            ]
            
    def WriteLowFlowCuttoff(self, value=PE102_DEFAULT_LOW_FLOW_CUTTOFF):
        c = self.GetSerialConnection()
        for i in range(NUM_SERIAL_COM_ATTEMPTS):
            self.WakeUp(c)
            c.Write('C$'+self.ReadString(value)+'\r')
            time.sleep(0.75)
            if 'f' in c.Read(c.InWaiting()):
                c.FlushInput()
                c.FlushOutput()
                return True
        return False
    

class PE102_REV_K(PE102_REV_J):
    def __init__(self):
        PE102_REV_J.__init__(self)
        # software version
        self.revision = '13848K'
    
#-------------------------------------------------------------------------
# Flow Meter Class
#-------------------------------------------------------------------------
class Reference(PE102_REV_J):
    def __init__(self):
        PE102_REV_H.__init__(self)
        # software version
        self.revision = '13848J'
        # low flow cutoff (fraction of 1)
        self.low_flow_cuttoff = PE102_DEFAULT_LOW_FLOW_CUTTOFF
        
    def __init__(self):
        self.k_factor = None
        self.max_flow_rate = None
        self.min_flow_rate = None
        self.uncertainty = None
        self.curvefit_poly = None

    def SetRefID(self, ref_id):
        self.ref_id = ref_id

    def GetRefID(self):
        assert self.ref_id != None
        return self.ref_id

    def GetFSFreq(self):
        """Return fs frequecy"""
        return self.GetKFactor()*self.GetMaxFlowRate()/SEC_PER_MIN

    def SetKFactor(self, k):
        """Return ideal k-factor"""
        self.k_factor = k
    
    def GetKFactor(self, flow_rate = None):
        """Return ideal k-factor"""
        assert self.k_factor != None
        k_factor = self.k_factor

##        if self.GetRefID() == REF_3_ID:
##            assert flow_rate != None
##            percent_error = REF3_CORRECTION[0] + REF3_CORRECTION[1]*flow_rate + REF3_CORRECTION[2]*flow_rate**2
##            # previously k_factor = self.k_factor / (1 - percent_error/100) --JAH 2014/05/12
##            k_factor = self.k_factor * (1 - percent_error/100)
##            print 'REF3 percent error Q: ', percent_error
##            print 'REF3 corrected k-factor: ', k_factor
        
        return k_factor

    def GetMaxFlowRate(self):
        """Return max flow rate"""
        assert self.max_flow_rate != None
        return self.max_flow_rate

    def GetMinFlowRate(self):
        """Return min flow rate"""
        assert self.min_flow_rate != None
        return self.min_flow_rate

    def SetMaxFlowRate(self, rate):
        """Set maximum flow rate"""
        assert type(rate) == float
        self.max_flow_rate = rate

    def SetMinFlowRate(self, rate):
        """Set minimum flow rate"""
        assert type(rate) == float
        self.min_flow_rate = rate

    def GetUncertainty(self):
        """Return measurement uncertainty as percentage"""
        assert self.uncertainty != None
        return self.uncertainty

    def SetUncertainty(self, u):
        """Set measurement uncertainty as percentage"""
        assert type(u) == float
        self.uncertainty = u

    def GetCurvefitPoly(self):
        """Return curvefit polynomial coefficients"""
        assert self.curvefit_poly != None
        return self.curvefit_poly

    def SetCurvefitPoly(self, poly):
        """Set curvefit polynomial coefficients"""
        assert poly != None
        self.curvefit_poly = poly
        
#-------------------------------------------------------------------------
# CHECK STANDARD
#-------------------------------------------------------------------------

##class PE102_CHECK_STANDARD(PE102_REV_J):
##    def __init__(self):
##        PE102_REV_J.__init__(self)
##        self.revision = 'REFERENCE'



# flow meter objects dictionary

# remove 13609B
FLOW_METER_OBJECT_DICT = {'13609B':PE102_REV_C(),
                        '13848C':PE102_REV_C(),
                        '13848D':PE102_REV_D(),
                        '13848E':PE102_REV_E(),
                        '13848F':PE102_REV_F(),
                        '13848G':PE102_REV_G(),
                        '13848H':PE102_REV_H(),
                        '13848J':PE102_REV_J(),
                        '13848K':PE102_REV_K(),
##                        'REFERENCE': PE102_CHECK_STANDARD(),
                        }
# Calibrated HF reference meter on 03/13/2013
# fsadc: 426.009, zradc: 0.60372

# Calibrated LF reference meter on 06/27/2013
# fsadc:  286.215, zradc: 0.54904

# Calibrated LF reference meter on 05/13/2014:
# fsadc:  285.393, zradc: 0.21753

def test():
    print 'running test: write/read adc values'
    meter = PE102_REV_G()
    isok = meter.SerialConnect(MUT_SERIAL_PORT)
# HF adc values
##    print 'write  fsadc::', meter.WriteFSADC(426.0098)
##    print 'write  zradc::', meter.WriteZRADC(0.603728)
# LF adc values
##    print 'write  fsadc::', meter.WriteFSADC(286.2158)
##    time.sleep(0.75)
##    print 'write  zradc::', meter.WriteZRADC(0.549048)
##    time.sleep(0.75)
##    print 'write  fsadc::', meter.WriteFSADC(285.3938)
##    time.sleep(0.75)
##    print 'write  zradc::', meter.WriteZRADC(0.217538)
##    time.sleep(0.75)
##    print 'write  zradc::', meter.WriteZRADC(200.0000)
##    print 'write  fsadc::', meter.WriteFSADC(100.0000)

##    print 'write  fsadc::', meter.WriteFSADC(403.3415)
##    time.sleep(0.75)
##    print 'write  zradc::', meter.WriteZRADC(5.998338)
##    time.sleep(0.75)
    print 'fsadc::', str(meter.ReadFSADC())[0:7]
    time.sleep(0.75)
    print 'zradc::', str(meter.ReadZRADC())[0:7]
##    print 'write filter', meter.WriteFLTR(0.65)
##    time.sleep(0.75)
##    print 'read filter', meter.ReadFLTR()

##test()
