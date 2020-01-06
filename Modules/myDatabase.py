#----------------------------------------------------------------------
# Database Program
''' author: Jeff Peery '''
# date: 02/26/2008
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------


#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''
 1.02   14/01/28    SPN     Added GetTestRefKFactor method used for saving test results to Syteline database
 1.01   13/02/19    SPN     Add SERIAL_NUMBER_LENGTH2 to Item class and HasItem, AppendItem methods
    1   12/02/08    JTP     -   Initial Release
    
'''

#----------------------------------------------------------------------
# Modules
#----------------------------------------------------------------------
from numpy import *
from string import *
import myUtil
from re import *
from datetime import datetime
from matplotlib.dates import date2num, num2date
import string
import myDateTime
from myHeader import *
try:
    import cpickle as pickle
except:
    import pickle
import os

#----------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------
class Test:
    """
    A calibration test object. A 'Test' object contains attributes
    relating to the calibration test.
    """
    def __init__(self):
        self.ref_pulse_count = None
        self.mut_pulse_count = None
        self.ref_volume = None
        self.time = None
        self.temp = None
        # uncertainty of measured k-factor
        self.u_k = None
        # uncertainty of measured flow rate
        self.u_q = None
        # uncertainty of measured volume
        self.u_v = None
    
    def GetTemp(self):
        """
        Returns floating point temperature difference between
        test start and test end
        """
##        assert self.temp != None, 'invalid value'
        return self.temp
        
    def SetTemp(self, temp):
        """
        Sets floating point temperature difference between
        test start and test end
        """
        assert type(temp) == float, 'invalid type'
        self.temp = temp
        
    def GetRefPulseCount(self):
        """
        Returns integer pulst count
        """
        assert self.ref_pulse_count != None, 'invalid value'
        return self.ref_pulse_count

    def SetRefPulseCount(self, pulse_count):
        """
        Sets integer pulst count
        """
        assert type(pulse_count) == float, 'invalid type'
        assert pulse_count >= 0, 'invalid value'
        self.ref_pulse_count = pulse_count

    def GetMUTPulseCount(self):
        """
        Returns integer pulst count
        """
        assert self.mut_pulse_count != None, 'invalid value'
        return self.mut_pulse_count

    def SetMUTPulseCount(self, pulse_count):
        """
        Sets integer pulst count
        """
        assert type(pulse_count) == float, 'invalid type'
        assert pulse_count >= 0, 'invalid value'
        self.mut_pulse_count = pulse_count

    def GetUncertainties(self):
        """
        Returns floating point uncertainty of k-factor,
        volume, and flow rate
        """
        assert self.u_k != None, 'invalid type'
        assert self.u_v != None, 'invalid type'
        assert self.u_q != None, 'invalid type'
        return self.u_v, self.u_q, self.u_k

    def SetUncertainties(self, u):
        """
        Sets floating point uncertainty of k-factor,
        volume, and flow rate
        """
        (u_v, u_q, u_k) = u
        assert u_k != None, 'invalid type'
        assert u_v != None, 'invalid type'
        assert u_q != None, 'invalid type'
        self.u_v = u_v
        self.u_q = u_q
        self.u_k = u_k
        
    def GetRefVolume(self):
        """
        Returns floating point volume
        """
        assert self.ref_volume != None, 'invalid type'
        return self.ref_volume

    def SetRefVolume(self, volume):
        """
        Sets floating point volume
        """
        assert type(volume) == float, 'invalid type'
        assert volume != None
        self.ref_volume = volume
        
    def GetTime(self):
        """
        Return floating point time
        """
        assert self.time != None, 'invalid value'
        return self.time

    def SetTime(self, time):
        """
        Sets floating point time
        """
        assert type(time) == float, 'invalid type'
        assert time != None, 'invalid value'
        self.time = time
        
    def GetKFactor(self):
        """
        Return floating point k-factor
        """
        assert self.GetMUTPulseCount() > 0, 'invalid value'
        assert self.GetRefVolume() > 0, 'invalid value'
        assert self.GetMUTPulseCount() != None, 'invalid value'
        assert self.GetRefVolume() != None, 'invalid value'
        return self.GetMUTPulseCount()/self.GetRefVolume()

    def GetRefFlowRate(self):
        """
        Return floating point flow rate
        """
        assert self.GetRefVolume() > 0, 'invalid value'
        assert self.GetTime() > 0, 'invalid value'
        assert self.GetRefVolume() != None, 'invalid value'
        assert self.GetTime() != None, 'invalid value'
        return SEC_PER_MIN*self.GetRefVolume()/self.GetTime()      

    def GetTestRefKFactor(self):
        """
        !!! NOTE !!! the kfactors here are the reference meter kfactors used for the FS test
        and the LS test. The KFactors MAY BE THE SAME for FS Test as for LS Test!!
        Again, KFactor here is the k-factor used for the TEST, it is NOT the physical kfactor
        for a specific reference meter. This is necessary
        because (for example) the reference meter kfactor for the LS test is NOT neccessarily the Kfactor
        for the LS reference meter. For example if the mut is calibrated at two points above the transition flow rate,
        then the kfactor for the FS test and the kfactor for the LS test used to determine new calibration values are only
        the FS reference kfactors. Anything else will cause big errors.
        """
        try:
            return self.GetRefPulseCount()/self.GetRefVolume()
        except:
            return 0.0

class Item:
    """
    A calibrated flow meter object. An 'Item' object contains attributes
    holding name of meter, FSADC and ZRADC, serial number, and a list of test objects
    (see Test class)
    """    
    def __init__(self, label, serial_num):
        assert type(serial_num) == str or type(serial_num) == unicode
        assert type(label) == str or type(label) == unicode
        assert len(serial_num) == SERIAL_NUMBER_LENGTH or len(serial_num) == SERIAL_NUMBER_LENGTH2
        # name of product
        self.label = label
        # serial number
        self.serial_num = serial_num
        # FSADC programed in meter EEPROM
        # for calibration. floating point number
        self.fsadc = None
        # ZRADC programed in meter EEPROM
        # for calibration. floating point number
        self.zradc = None
        # list of tuples where each tuple
        # contains flow rate, k-factor, temp, and time respectively
        # units are m^3, pulses/m^3, celsius, and seconds respectively
        #
        # test_data = [(date_0, q_0, k_0, T_0, t_0), (date_1, q_1, k_1, T_1, t_1), ..., (date_n, q_n, k_n, T_n, t_n)]
        #
        # NOTE: There are two positions: DB_FS_INDEX and DB_LS_INDEX
        # each indes holds a test instance
        self.test_data = [None, None]
        self.date = myDateTime.GetToday()

    def AppendCalTest(self, index, test):
        """
        Append a calibration test to the list of calibration tests.
        """
        assert type(index) == int
        assert index in [DB_FS_INDEX, DB_LS_INDEX]
        self.test_data[index] = test

    def SetFSADC(self, fsadc):
        """
        Set FSADC calibration value
        """ 
        assert type(fsadc) == float
        self.fsadc = fsadc

    def SetZRADC(self, zradc):
        """
        Set ZRADC calibration value
        """ 
        assert type(zradc) == float
        self.zradc = zradc
        
    def GetFSADC(self):
        """
        Returns FSADC calibration value
        """
        return self.fsadc

    def GetZRADC(self):
        """
        Returns ZRADC calibration value
        """
        return self.zradc
    
    def SetDate(self, date):
        assert type(date) == float
        self.date = date
        
    def GetDate(self):
        assert self.date != None, 'invalid value'
        return self.date
    
    def SetLabel(self, label):
        """
        Set meter label (a string that spells out the meter type)
        """ 
        assert type(label) == str or type(label) == unicode
        self.label = label

    def GetLabel(self):
        """
        Returns the meter label (a string that spells out the meter type)
        """
        assert self.label != None, 'invalid type'
        return self.label

    def GetSerialNum(self):
        """
        Returns the item serial number
        """
        assert self.serial_num != None, 'invalid value'
        return self.serial_num

    def GetFSTestData(self):
        """
        Returns the FS calibration data
        """
        assert self.test_data[DB_FS_INDEX] != None, 'invalid value'
        return self.test_data[DB_FS_INDEX]

    def GetLSTestData(self):
        """
        Returns the LS calibration data
        """
        assert self.test_data[DB_LS_INDEX] != None, 'invalid value'
        return self.test_data[DB_LS_INDEX]
    
    def GetTestData(self):
        """
        Returns the calibration object
        """
        assert self.test_data[DB_FS_INDEX] != None, 'invalid value'
        assert self.test_data[DB_LS_INDEX] != None, 'invalid value'
        return self.test_data
        
class Database:
    """
    A database class. A database object contains attributes
    holding calibrated items (see Item class), and check_standard
    calibration data (see CalData class).
    """  
    def __init__(self):
        # dictionary of calibrated
        # order items. Data includes only
        # production ordered units, ie no
        # engineering test data is recorded.
        # the dictionary key value pairs are { serial_num:Item(), ...}
        self.production_items = {}

    def GetDate(self, date):
        """
        convert a date in the form of a string, to a floating point number that can
        be used in the datetime module
        """
        assert type(date) == str or type(serial_num) == unicode
        try:
            return myDateTime.GetDateFromString(date)
        except:
            raise TypeError, 'Received invalid format for date/time string.'

    def GetDateRange(self, item_label):
        assert len(self.GetItems().values()) > 0
        max_date = self.GetItems().values()[0].GetDate()
        min_date = self.GetItems().values()[0].GetDate()
            
        for item in self.GetItems().values():
            if item.GetLabel() == item_label:
                if item.GetDate() > max_date:
                    max_date = item.GetDate()
                if item.GetDate() < min_date:
                    min_date = item.GetDate()   
        return min_date, max_date
    
    def Load(self):
        """
        Load database.
        """
        if not os.path.exists(PRODUCTION_ITEMS_DATABASE_PATH):
            myUtil.ErrorDialog(None, 'database path does not exist.')
            return False
        
        try:
            fh = open(PRODUCTION_ITEMS_DATABASE_PATH, 'r')
            self.production_items = pickle.load(fh)
            fh.close()
            return True
            
        except:
            myUtil.ErrorDialog(None, 'Error in load method: mydatabase.py')
            self.production_items = {}
            self.check_standard_items = []
            return False
                          
    def Save(self):
        """
        Save Database
        """
        if not os.path.exists(PRODUCTION_ITEMS_DATABASE_PATH):
            myUtil.ErrorDialog(None, 'database path does not exist.')
            return
        
        try:
            fh = open(PRODUCTION_ITEMS_DATABASE_PATH, 'w')
            pickle.dump(self.GetItems(), fh)
            fh.close()
        except:
            myUtil.ErrorDialog(None, 'Error in save method: mydatabase.py')

    def GetItems(self):
        """
        return all production Item objects
        """
        return self.production_items

    def GetItemsByType(self, unit_type):
        """
        return all production units of type unit_type
        """
        items = []
        
        for item in self.GetItems().values():
            if item.GetLabel() == unit_type:
                items.append(item)
        return items
    
    def HasItem(self, serial_num):
        assert type(serial_num) == str or type(serial_num) == unicode
        assert len(serial_num) == SERIAL_NUMBER_LENGTH or len(serial_num) == SERIAL_NUMBER_LENGTH2
        return self.GetItems().has_key(serial_num)
    
    def GetItem(self, serial_num):
        if self.HasItem(serial_num):
            return self.GetItems()[serial_num]
        else:
            return None

    def AppendItem(self, item, serial_num):
        assert type(serial_num) == str or type(serial_num) == unicode
        assert len(serial_num) == SERIAL_NUMBER_LENGTH or len(serial_num) == SERIAL_NUMBER_LENGTH2
        """
        Append database production item to dictionary
        """
        self.GetItems()[serial_num] = item

    def PrintContents(self):
        for item in self.GetItems().values():
            print 'product label:', item.label
            print 'serial number:', item.serial_num
            print 'FSADC:', item.fsadc
            print 'ZRADC', item.zradc
            print 'date', myDateTime.NumToDate(item.GetDate())
            for i in item.test_data:
                print '--- new test ---'
                print 'flow rate (m^3/s)', i.GetRefFlowRate()
                print 'k-factor (pulse/m^3)', i.GetKFactor()
                print 'temperature (C)', i.GetTemp()
                print 'time (s)', i.GetTime()
                print '\n'
