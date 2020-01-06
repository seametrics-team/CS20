# Header File for the PE Calibration HMI Application
''' author: Jeff Peery '''
# date: 02/19/2008
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''
 1.12   14/12/24    SPN     Added ZRADC_LIMIT to prevent abnormal values from passing calibration
 1.11   14/10/21    SPN     Added GRAVITY_PUMP_TRANSITION_FLOW_RATE to optimize custom multipoint
 1.10   14/10/14    SPN     Added DEFAULT_PROFILE for custom multipoint section
 1.09   14/05/14    JF      Updated LF_VERIFICATION ADC constants by recalibration LF reference meter
 1.08   14/05/09    SPN     Added REF3_CORRECTION to provide % error (Q) coefficients
 1.07   14/02/24    SPN     Changed v: paths over to s: drive
 1.06   14/01/31    SPN     Added SYSTEM UNCERTAINTY CONSTANTS for saving test results to Syteline database
 1.05   14/01/28    SPN     Added BENCH_ID constant for saving test results to Syteline database
 1.04   13/10/03    SPN     Added secondary set of SPC file paths for WinSPC experiment
 1.03   13/08/23    SPN     Swapped Thermal1,2 coefficients between upstream and downstream
 1.02   13/08/09    SPN     Added sound constants
 1.01   13/02/19    SPN     Added SERIAL_NUMBER_LENGTH2 constant to accomodate extended serial #'s (i.e. Syteline)
    1   2/19/08    JTP     -   Initial Release
    
'''

#-------------------------------------------------------------------------
# Constants
''' when adding a new meter, you must edit the REF METER constants and
    the MUT constants. The lists are in order of the REF or MUT ID's
    and must remain in proper order for proper functioning. i.e. REF5 must
    have ID == 4 so that that the 5th element of each list corresponds to
    reference meter 5 etc.'''
#-------------------------------------------------------------------------
import serial
from numpy import pi as PI
import sys
#----------------------------------
# Application
#----------------------------------
SYSTEM_PATH = sys.path[0]
#----------------------------------
# PLC
#----------------------------------
MAX_DIGITAL_COUNT           = 4095.0
#----------------------------------
# Unit Conversions
#----------------------------------
# gallons per m^3
GAL_PER_CUBIC_METER = 264.172052358148
SEC_PER_MIN = 60.0
#----------------------------------
# Serial Communication
#----------------------------------
TIME_OUT                    = 1
MUT_SERIAL_PORT             = 2
BAUD_RATE                   = 2400
BYTE_SIZE                   = serial.EIGHTBITS
PARITY                      = serial.PARITY_NONE
STOP_BITS                   = serial.STOPBITS_ONE
#----------------------------------
# GUI
#----------------------------------
BUTTON_HEIGHT               = 75
BUTTON_WIDTH                = 150
CTRL_WIDTH = 100
CTRL_HEIGHT = 30
CHECKBOX_WIDTH              = 50
CHECKBOX_HEIGHT             = 30
DATE_PICKER_WIDTH           = 100
DATE_PICKER_HEIGHT          = 30
TEXT_CTRL_WIDTH             = 100
TEXT_CTRL_HEIGHT            = 30
STATIC_TEXT_WIDTH           = 50
STATIC_TEXT_HEIGHT          = 30
CTRL_SPACING                = 20
BUTTON_SPACING              = 10
CLAMP_BUTTON_DOWN           = 1
CLAMP_BUTTON_UP             = 0
APPROX_TEST_TIME            = 60.0
QUICK_METER_TEST_TIME       = 20.0
TIMER_PERIOD_MS             = 1000
KEYPAD_BUTTON_HEIGHT        = 50
KEYPAD_BUTTON_WIDTH         = 50
#----------------------------------
# Plotting Styles
#----------------------------------
#
# calibration frame
MARKER_SHAPE = 'o'
MARKER_FACE_COLOR = 'w'
MARKER_EDGE_COLOR = 'k'
MARKER_EDGE_WIDTH = 1
ALPHA_LINE = 0.25
ALPHA_SCATTER = 1.00
MARKER_SIZE = 8
LINE_COLOR = 'w'
LINE_STYLE = '-'
LINE_WIDTH = 1
Y_LABEL = '% Error'
X_LABEL = '% FS Flow Rate'
UPPER_X_LIMIT = 105.0
LOWER_X_LIMIT = -2.0
UPPER_Y_LIMIT = 3.0
LOWER_Y_LIMIT = -3.0
FRAME_ON = False
GRID_ON = False
FIGURE_COLOR = 'w'
AXES_TITLE = 'Error vs. Flow Rate'
FIGURE_SIZE = (5,1.5)
FIGURE_DPI = 80
#
# history frame
HISTORY_HISTOGRAM_COLOR_1 = 'r'
HISTORY_HISTOGRAM_COLOR_2 = 'b'
HISTORY_MARKER_SHAPE = 'o'
HISTORY_MARKER_FACE_COLOR = 'w'
HISTORY_MARKER_EDGE_COLOR = 'r'
HISTORY_MARKER_EDGE_WIDTH = 2
HISTORY_MARKER_SIZE = 2
HISTORY_ALPHA_LINE = 0.25
HISTORY_ALPHA_SCATTER = 0.75
HISTORY_MARKER_SIZE = 10
HISTORY_LINE_COLOR = 'w'
HISTORY_LINE_STYLE = '-'
HISTORY_LINE_WIDTH = 1
HISTORY_Y_LABEL = '% Error'
HISTORY_X_LABEL = '% FS Flow Rate'
HISTORY_FRAME_ON = False
HISTORY_GRID_ON = False
HISTORY_FIGURE_COLOR = 'w'
HISTORY_AXES_TITLE = 'Error vs. Flow Rate'
HISTORY_FIGURE_SIZE = (4,2)
HISTORY_FIGURE_DPI = 80
#----------------------------------
# Utility Module
#----------------------------------
WEIGHTING_FACTOR = 2.0
#----------------------------------
# SPC
#----------------------------------
NUM_REPLICATES = 1
# file holds date of last system test
LAST_LF_TEST_DATE_FILE = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\LAST_LF_SYSTEM_TEST_DATE.txt'     
LAST_HF_TEST_DATE_FILE = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\LAST_HF_SYSTEM_TEST_DATE.txt'
# location of spc data
HF_VERIFICATION_LS_DATA_PATH = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\PE CAL SYS HF LS VERIFICATION K-FACTOR.txt'
HF_VERIFICATION_FS_DATA_PATH = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\PE CAL SYS HF FS VERIFICATION K-FACTOR.txt'
LF_VERIFICATION_LS_DATA_PATH = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\PE CAL SYS LF LS VERIFICATION K-FACTOR.txt'
LF_VERIFICATION_FS_DATA_PATH = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\PE CAL SYS LF FS VERIFICATION K-FACTOR.txt'
# Secondary file set for WinSPC experiment
HF_VERIFICATION_LS_DATA_PATH2 = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\PE CAL SYS HF LS VERIFICATION K-FACTOR2.txt'
HF_VERIFICATION_FS_DATA_PATH2 = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\PE CAL SYS HF FS VERIFICATION K-FACTOR2.txt'
LF_VERIFICATION_LS_DATA_PATH2 = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\PE CAL SYS LF LS VERIFICATION K-FACTOR2.txt'
LF_VERIFICATION_FS_DATA_PATH2 = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\PE CAL SYS LF FS VERIFICATION K-FACTOR2.txt'
#----------------------------------
# Calibration Report
#----------------------------------
REPORT_TEMPLATE_FILE = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\Calibration Reports\\template.htm'
REPORT_FOLDER = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\Calibration Reports'
REPORT_IMAGE_FOLDER = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\Calibration Reports'
REPORT_TITLE = 'SEAMETRICS CALIBRATION REPORT'
REPORT_FIGURE_DPI = 75
REPORT_FIGURE_PAPER_TYPE = 'letter'
REPORT_FIGURE_FORMAT = 'png'
#----------------------------------
# Calibration
#----------------------------------
# Bench ID used for test results saved in Syteline database
BENCH_ID = 2
# Max +/- ZRADC limit allowed during calibration
ZRADC_LIMIT = 5
#----------------------------------
# SYSTEM UNCERTAINTY CONSTANTS
# 99% CI (COVERAGE FACTOR = 3)
# AS REFERENCED FROM NIST DOC
#----------------------------------
SYSTEM_V_UNCERTAINTY = 0.38
SYSTEM_Q_UNCERTAINTY = 0.48
SYSTEM_K_UNCERTAINTY = 0.38
# reference meter k factors (ppg)
REF1_K                      = 2000.0
REF2_K                      = 50000.0
REF3_K                      = 10000.0
REF4_K                      = 250000.0
CHECK_STANDARD_K            = 20000.0
# reference meter corrections:
# % error(Q) = A + BQ + CQ^2
# REFi_CORRECTION = [A, B, C]
REF3_CORRECTION     = [0.414585, 0.170638, 0.00101516]
# percentage uncertainties of reference meters at 65% CI
REF1_U                      = 0.0025/2.0
REF2_U                      = 0.0025/2.0
REF3_U                      = 0.0025/2.0
REF4_U                      = 0.0015/2.0
CHECK_STANDARD_U            = 0.0025/2.0
# max flow rate of reference meters (gpm)
REF1_MAX_Q                  = 25.0
REF2_MAX_Q                  = 0.95
REF3_MAX_Q                  = 3.00
REF4_MAX_Q                  = 0.25
CHECK_STANDARD_MAX_Q        = 1.00
# min flow rate of reference meters (gpm)
REF1_MIN_Q                  = 0.5
REF2_MIN_Q                  = 0.05
REF3_MIN_Q                  = 0.03
REF4_MIN_Q                  = 0.0028
CHECK_STANDARD_MIN_Q        = 0.1
TEST_SERIAL_NUMBER          = '00000000'
# calibration status flags
STATUS_IDLE                 = 0
STATUS_FS_TEST              = 1
STATUS_LS_TEST              = 2
# toggles test mode
TEST_MODE                   = False
# accuracy limit
PERCENT_ACCURACY            = 1.0
# system flag
HF_SYSTEM                   = 1
LF_SYSTEM                   = 0
HF_SYS_LABEL = 'High Flow System'
LF_SYS_LABEL = 'Low Flow System'
# maximum number of attempts at
# calibrating before ending procedure
MAX_CALIBRATION_CYCLES      = 1
# index of FS test in database items'
# list of tests, ie, to access the
# FS test object you must index the
# the FS_TEST_INDEX in the database items'
# list of tests.
FS_TEST_INDEX               = 0
LS_TEST_INDEX               = 1
# Maximum temp change allowed during test
MAX_TEMP_CHANGE             = 2.0
# Maximum flow rate of HF calibration system
HF_MAX_FLOW_RATE            = 25.0
# Maximum flow rate of LF calibration system
LF_MAX_FLOW_RATE            = 5.0
# Minimum flow rate of HF calibration system
HF_MIN_FLOW_RATE            = 0.05
# Minimum flow rate of LF calibration system
LF_MIN_FLOW_RATE            = 0.005
# Maximum replicats available in MultiCalFrame
MULTI_TEST_MAX_REPS         = 100
# Minimum replicats available in MultiCalFrame
MULTI_TEST_MIN_REPS         = 1
# Maximum tests available in MultiCalFrame
MULTI_TEST_MAX_TESTS        = 50
# Minimum tests available in MultiCalFrame
MULTI_TEST_MIN_TESTS        = 2
# high flow system transition flow rate (gpm) (change reference meters)
HF_TRANSITION_FLOW_RATE     = 0.9
# low flow system transition flow rate (gpm) (change reference meters)
LF_TRANSITION_FLOW_RATE     = 0.02
# pump to gravity transition flow rate (gpm): flow rate < 1.0 gpm is gravity mode
GRAVITY_PUMP_TRANSITION_FLOW_RATE = 1.0
#----------------------------------------------------------------------
# Thermal Module
#----------------------------------------------------------------------
# resistance (ohms) of resistor 1
THERMAL_R1 = 1.0*10**5
# resistance (ohms) of resistor 2
THERMAL_R2 = 1.0*10**6
# resistance (ohms) of resistor 3
THERMAL_R3 = 4.99*10**4
# power supplied to thermistor circuit
THERMAL_V_S = 5.0
# nominal resistance of thermistor at 25 c
THERMAL_R25 = 2.5*10**3
# bias corrections (unit are C)
# these values where obtained 08/09/2010
# by Davis Calibration, onsite at seametrics.
# the Davis Calibration reference was 30.0 C.
THERMAL_1_BIAS_CORRECTION = 0
THERMAL_2_BIAS_CORRECTION = -0.28
THERMAL_3_BIAS_CORRECTION = -0.19
THERMAL_4_BIAS_CORRECTION = -0.40
# these coefficients are provided by
# the manufacturer
# MODEL NUMBER: A207A-CSP60BA252M
# SERIAL NUMBER: 
# LF system probe downstream of MUT
THERMAL_1_B0 = 0
THERMAL_1_B1 = 0
THERMAL_1_B2 = 0
THERMAL_1_B3 = 0
# these coefficients are provided by
# the manufacturer
# MODEL NUMBER: A207A-CSP60BA252M
# SERIAL NUMBER: 072524893
# LF system probe upstream of MUT
THERMAL_2_B0 = 1.31075942E-3
THERMAL_2_B1 = 2.43542486E-4
THERMAL_2_B2 = 2.52474104E-6
THERMAL_2_B3 = -6.41289055E-9
# these coefficients are provided by
# the manufacturer
# MODEL NUMBER: A207A-CSP60BA252M
# SERIAL NUMBER: 072524894
# HF system probe upstream of MUT
THERMAL_3_B0 = 1.30663762E-3
THERMAL_3_B1 = 2.50594176E-4
THERMAL_3_B2 = 1.76706128E-6
THERMAL_3_B3 = 2.59632123E-8
# MODEL NUMBER: A207A-CSP60BA252M
# SERIAL NUMBER: 070195
# HF system probe downstream of MUT
THERMAL_4_B0 = 1.25931003E-3
THERMAL_4_B1 = 2.69034579E-4
THERMAL_4_B2 = -1.35873838E-6
THERMAL_4_B3 = 1.93472331E-7

#----------------------------------------------------------------------
# Database
#----------------------------------------------------------------------
# location of database containing the checkstandard calibrations
##CHECK_STANDARD_DATABASE_PATH = SYSTEM_PATH+'S:\\Calibration Bench\\CS20\\Bench Data\\PE CAL SYS CHECK STANDARD DATABASE.txt'
# location of database containing production calibrations
PRODUCTION_ITEMS_DATABASE_PATH = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\PE CAL SYS PRODUCTION DATABASE.txt'
# length of standard serial numbers
SERIAL_NUMBER_LENGTH = 8
# length of extended length serial numbers
SERIAL_NUMBER_LENGTH2 = 12
# Attributes of a DB item
DATE = 'DATE'
FLOW_RATE = 'FLOW RATE'
K_FACTOR = 'K-FACTOR'
TEMP = 'TEMP'
TIME = 'TIME'
FSADC = 'FSADC'
ZRADC = 'ZRADC'
DB_FS_INDEX = 0
DB_LS_INDEX = 1
ALL_VARIABLES = [FLOW_RATE,
                 K_FACTOR,
                 TEMP,
                 TIME,
                 FSADC,
                 ZRADC]
#----------------------------------------------------------------------
# Measurements text file (used to save multipoint and manual measurement data)
#----------------------------------------------------------------------
TEST_RESULTS_FILE_PATH = SYSTEM_PATH+'\\Data\\TEST RESULTS.txt'

#----------------------------------------------------------------------
# OPC
#----------------------------------------------------------------------
SLEEP_TIME                  = 0.5
HIGH_QUALITY                = 192
LOW_QUALITY                 = 0
AI_DEAD_BAND                = 0
GENERAL_DEAD_BAND           = 0
GENERAL_UPDATE_RATE         = 500
AI_UPDATE_RATE              = 500
OPC_SERVER_NAME             = 'AutomationDirect.KEPDirectServer'
MUT_PULSE_COUNT_NAME        = 'PE CAL SYS.PE CAL SYS.MUT PULSE COUNT'
MUT_AO_NAME                 = 'PE CAL SYS.PE CAL SYS.MUT AO'
REF_PULSE_COUNT_NAME        = 'PE CAL SYS.PE CAL SYS.REF PULSE COUNT'
RTD_1_NAME                  = 'PE CAL SYS.PE CAL SYS.RTD 1'
RTD_2_NAME                  = 'PE CAL SYS.PE CAL SYS.RTD 2'
RTD_3_NAME                  = 'PE CAL SYS.PE CAL SYS.RTD 3'
RTD_4_NAME                  = 'PE CAL SYS.PE CAL SYS.RTD 4'
TARGET_FLOW_RATE_NAME       = 'PE CAL SYS.PE CAL SYS.TARGET FLOW RATE'
REF_1_NAME                  = 'PE CAL SYS.PE CAL SYS.REF 1'
REF_2_NAME                  = 'PE CAL SYS.PE CAL SYS.REF 2'
REF_3_NAME                  = 'PE CAL SYS.PE CAL SYS.REF 3'
REF_4_NAME                  = 'PE CAL SYS.PE CAL SYS.REF 4'
TEST_TIME_NAME              = 'PE CAL SYS.PE CAL SYS.TEST TIME'
TARGET_TEST_TIME_NAME       = 'PE CAL SYS.PE CAL SYS.TARGET TEST TIME'
UPSTREAM_START_TEMP_NAME    = 'PE CAL SYS.PE CAL SYS.UPSTREAM START TEMP'
UPSTREAM_END_TEMP_NAME      = 'PE CAL SYS.PE CAL SYS.UPSTREAM END TEMP'
DOWNSTREAM_START_TEMP_NAME  = 'PE CAL SYS.PE CAL SYS.DOWNSTREAM START TEMP'
DOWNSTREAM_END_TEMP_NAME    = 'PE CAL SYS.PE CAL SYS.DOWNSTREAM END TEMP'
PLC_RELAY_C0                = 'PE CAL SYS.PE CAL SYS.RELAY C0'
PLC_RELAY_C1                = 'PE CAL SYS.PE CAL SYS.RELAY C1'
PLC_RELAY_C2                = 'PE CAL SYS.PE CAL SYS.RELAY C2'
PLC_RELAY_C3                = 'PE CAL SYS.PE CAL SYS.RELAY C3'
PLC_RELAY_C4                = 'PE CAL SYS.PE CAL SYS.RELAY C4'
PLC_RELAY_C5                = 'PE CAL SYS.PE CAL SYS.RELAY C5'

PLC_RELAY_C7                = 'PE CAL SYS.PE CAL SYS.RELAY C7'

PLC_RELAY_C11               = 'PE CAL SYS.PE CAL SYS.RELAY C11'
PLC_RELAY_C12               = 'PE CAL SYS.PE CAL SYS.RELAY C12'
PLC_RELAY_C13               = 'PE CAL SYS.PE CAL SYS.RELAY C13'
PLC_RELAY_C14               = 'PE CAL SYS.PE CAL SYS.RELAY C14'
PLC_RELAY_C15               = 'PE CAL SYS.PE CAL SYS.RELAY C15'

PLC_RELAY_C20               = 'PE CAL SYS.PE CAL SYS.RELAY C20'
PLC_RELAY_C21               = 'PE CAL SYS.PE CAL SYS.RELAY C21'
PLC_RELAY_C22               = 'PE CAL SYS.PE CAL SYS.RELAY C22'

PLC_RELAY_C24               = 'PE CAL SYS.PE CAL SYS.RELAY C24'
PLC_RELAY_C25               = 'PE CAL SYS.PE CAL SYS.RELAY C25'

PLC_RELAY_C30               = 'PE CAL SYS.PE CAL SYS.RELAY C30'
PLC_RELAY_C31               = 'PE CAL SYS.PE CAL SYS.RELAY C31'

PLC_RELAY_C32               = 'PE CAL SYS.PE CAL SYS.RELAY C32'
PLC_RELAY_C33               = 'PE CAL SYS.PE CAL SYS.RELAY C33'

# Numerical Data
MUT_PULSE_COUNT_ID          = 1
MUT_AO_ID                   = 2
REF_PULSE_COUNT_ID          = 3
RTD_1_ID                    = 4
RTD_2_ID                    = 5
RTD_3_ID                    = 6
RTD_4_ID                    = 7
TARGET_FLOW_RATE_ID         = 10
REF_1_ID                    = 11
REF_2_ID                    = 12
REF_3_ID                    = 13
REF_4_ID                    = 14
TEST_TIME_ID                = 15
TARGET_TEST_TIME_ID         = 16
PLC_RELAY_C0_ID             = 17
PLC_RELAY_C1_ID             = 20
UPSTREAM_START_TEMP_ID      = 21
UPSTREAM_END_TEMP_ID        = 22
DOWNSTREAM_START_TEMP_ID    = 23
DOWNSTREAM_END_TEMP_ID      = 24
# PLC Event Triggers
PLC_RELAY_C2_ID             = 25
PLC_RELAY_C3_ID             = 26
PLC_RELAY_C4_ID             = 27
PLC_RELAY_C5_ID             = 30 
PLC_RELAY_C7_ID             = 31
PLC_RELAY_C11_ID            = 32
PLC_RELAY_C12_ID            = 33
PLC_RELAY_C13_ID            = 34
PLC_RELAY_C14_ID            = 35
PLC_RELAY_C15_ID            = 36
# HMI Event Triggers
PLC_RELAY_C20_ID            = 37
PLC_RELAY_C21_ID            = 40
PLC_RELAY_C22_ID            = 41
PLC_RELAY_C24_ID            = 42
PLC_RELAY_C25_ID            = 43
PLC_RELAY_C30_ID            = 44
PLC_RELAY_C31_ID            = 45
PLC_RELAY_C32_ID            = 46
PLC_RELAY_C33_ID            = 47


#----------------------------------------------------------------------
# Thermal Correction and Uncertainty Constants
# (used in ThermalCorrection.py and myUncertainty.py)
#----------------------------------------------------------------------
# coverage factor
COVERAGE_FACTOR = 2.0
# storage volume lengths at 25 C, (m)
HF_SYS_UPSTREAM_STORAGE_LENGTH = 15.0*0.0254
HF_SYS_DOWNSTREAM_STORAGE_LENGTH = 9.6*0.0254
# storage volume lengths at 25 C, (m)
LF_SYS_UPSTREAM_STORAGE_LENGTH = 9.1*0.0254
LF_SYS_DOWNSTREAM_STORAGE_LENGTH = 7.0*0.0254
# storage volume diameter at 25 C, (m)
HF_SYS_UPSTREAM_STORAGE_DIAMETER = 0.402*0.0254
HF_SYS_DOWNSTREAM_STORAGE_DIAMETER = 0.652*0.0254
# storage volume diameter at 25 C, (m)
LF_SYS_UPSTREAM_STORAGE_DIAMETER = 0.152*0.0254
LF_SYS_DOWNSTREAM_STORAGE_DIAMETER = 0.402*0.0254
# storage volume at 25 C, (m^3)
HF_SYS_UPSTREAM_STORAGE_VOLUME = HF_SYS_UPSTREAM_STORAGE_LENGTH*0.25*PI*HF_SYS_UPSTREAM_STORAGE_DIAMETER**2
HF_SYS_DOWNSTREAM_STORAGE_VOLUME = HF_SYS_DOWNSTREAM_STORAGE_LENGTH*0.25*PI*HF_SYS_DOWNSTREAM_STORAGE_DIAMETER**2
LF_SYS_UPSTREAM_STORAGE_VOLUME = LF_SYS_UPSTREAM_STORAGE_LENGTH*0.25*PI*LF_SYS_UPSTREAM_STORAGE_DIAMETER**2
LF_SYS_DOWNSTREAM_STORAGE_VOLUME = LF_SYS_DOWNSTREAM_STORAGE_LENGTH*0.25*PI*LF_SYS_DOWNSTREAM_STORAGE_DIAMETER**2
# coefficient of thermal expansion for stainless steel (1/K)
CTE_SS = 1.6*10**-5
# coefficient of thermal expansion for water (1/K)
CTE_W = 2.761*10**-4      
# uncertainties for CTE of stainless steel
U_CTE_SS = 1.0*10**-6
# uncertainties for CTE of water
U_CTE_W = 2.761*10**-4 
# uncertainty of thermistor probe (K), see uncertainty analysis for PE Cal Sys
U_TEMP = 0.05
# uncertainty of storage volume (m^3)
# about 1.0 uncertainty in length measurements
U_LF_SYS_UPSTREAM_STORAGE_VOLUME = 1.0*0.0254*0.25*PI*LF_SYS_UPSTREAM_STORAGE_DIAMETER**2
U_LF_SYS_DOWNSTREAM_STORAGE_VOLUME = 1.0*0.0254*0.25*PI*LF_SYS_DOWNSTREAM_STORAGE_DIAMETER**2
U_HF_SYS_UPSTREAM_STORAGE_VOLUME = 1.0*0.0254*0.25*PI*HF_SYS_UPSTREAM_STORAGE_DIAMETER**2
U_HF_SYS_DOWNSTREAM_STORAGE_VOLUME = 1.0*0.0254*0.25*PI*HF_SYS_DOWNSTREAM_STORAGE_DIAMETER**2
# uncertainty of test time (s)
U_TIME = 0.1
# uncertainty of pulse count
U_PULSE_COUNT = 1.0
#----------------------------------
# Sound
#----------------------------------
SOUNDS_FAIL = SYSTEM_PATH + '\\SOUNDS\\fail.wav'
SOUNDS_PASS = SYSTEM_PATH + '\\SOUNDS\\pass.wav'
#----------------------------------
# Verification meters
#----------------------------------
# Calibrated HF reference meter on 03/13/2013:
# fsadc: 426.009, zradc: 0.60372
# Calibrated LF reference meter on 06/27/2013:
# fsadc:  286.215, zradc: 0.54904
# Calibrated LF reference meter on 05/13/2014:
# fsadc:  285.393, zradc: 0.21753
HF_VERIFICATION_FSADC = '426.009'
HF_VERIFICATION_ZRADC = '0.60372'
LF_VERIFICATION_FSADC = '285.393'
LF_VERIFICATION_ZRADC = '0.21753'
#----------------------------------
# Custom Multipoint
#----------------------------------
DEFAULT_PROFILE = SYSTEM_PATH + '\\Profiles\\DEFAULT PROFILE.txt'
