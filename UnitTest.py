#----------------------------------------------------------------------
# UnitTest.py
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

    1   12/02/08    JTP     -   Initial Release
    
'''

#----------------------------------------------------------------------
# Modules
#----------------------------------------------------------------------
import unittest
import Modules.myDateTime as myDateTime
import Modules.myUtil as myUtil
from Modules.myHeader import *
import datetime
from matplotlib.dates import date2num, num2date

#----------------------------------------------------------------------
# myDateTime
#----------------------------------------------------------------------
class TestMyDateTime(unittest.TestCase):
    """
    Test myDateTime.py Methods
    """
    def setUp(self):
        pass

    def testDateToNum(self):
        """
        Confirm DateToNum returns correct number
        """
        today = datetime.datetime.today()
        observed = myDateTime.DateToNum(today)
        expected = date2num(today)
        self.assert_(expected==observed)

    def testNumToDate(self):
        """
        Confirm NumToDate returns correct datetime object
        """
        expected = datetime.datetime.today()
        observed = str(myDateTime.NumToDate(date2num(expected))).split('.')[0]
        self.assert_(str(expected).split('.')[0]==observed)

    def test_to_ordinalf(self):
        """
        Confirm _to_ordinalf returns correct float
        """
        today = datetime.datetime.today()
        expected = date2num(today)        
        observed = myDateTime._to_ordinalf(today)
        self.assert_(expected==observed)

    def test_from_ordinalf(self):
        """
        Confirm _from_ordinalf returns correct datetime object
        """
        today = datetime.datetime.today()
        expected = date2num(today)        
        observed = myDateTime._to_ordinalf(today)
        self.assert_(expected==observed)
        
    def testGetToday(self):
        """
        Confirm GetToday returns correct number
        """
        expected = date2num(datetime.datetime.today())
        observed = myDateTime.GetToday()
        self.assert_(expected==observed)

    def testGetISOFormat(self):
        """
        Confirm GetISOFormat returns correct number
        """
        today = datetime.datetime.today()
        expected = today.isoformat(' ').split(' ')[0]
        observed = myDateTime.GetISOFormat(today)
        self.assert_(expected==observed)

        today = datetime.datetime.today()
        expected = today.isoformat(' ').split(' ')[0]
        observed = myDateTime.GetISOFormat(date2num(today)).split(' ')[0]
        self.assert_(expected==observed)

    def testGetDateFromString(self):
        """
        Confirm GetDateFromString returns correct datetime object
        """
        expected = datetime.datetime(2007, 1, 5)
        for date in ['Jan 5, 2007', '1/5/2007', '1-5-2007', '5, January 2007']:
            observed = myDateTime.GetDateFromString(date)
            self.assert_(expected==observed)

        for date in ['a', 'A']:
            observed = myDateTime.GetDateFromString(date)
            self.assert_(expected!=observed)

    def testIsDateTimeInstance(self):
        """
        Confirm IsDateTimeInstance returns correct boolean
        """
        expected = True
        observed = myDateTime.IsDateTimeInstance(datetime.datetime.today())
        self.assert_(expected==observed)

        expected = False
        observed = myDateTime.IsDateTimeInstance(None)
        self.assert_(expected==observed) 

        expected = False
        observed = myDateTime.IsDateTimeInstance('Jan. 2007')
        self.assert_(expected==observed)

        expected = False
        observed = myDateTime.IsDateTimeInstance('1/5/2008')
        self.assert_(expected==observed)

    def testIsStringDate(self):
        """
        Confirm IsStringDate returns correct boolean
        """
        expected = True
        observed = myDateTime.IsStringDate('1/2/07')
        self.assert_(expected==observed)

        expected = True
        observed = myDateTime.IsStringDate('1-2-07')
        self.assert_(expected==observed)

        expected = True
        observed = myDateTime.IsStringDate('jan 5 2008')
        self.assert_(expected==observed)

        expected = False
        observed = myDateTime.IsStringDate('730000')
        self.assert_(expected==observed)

        expected = False
        observed = myDateTime.IsStringDate('A')
        self.assert_(expected==observed)

        expected = False
        observed = myDateTime.IsStringDate(123456)
        self.assert_(expected==observed)

        expected = False
        observed = myDateTime.IsStringDate(None)
        self.assert_(expected==observed)

        expected = False
        observed = myDateTime.IsStringDate('1/234.5/67')
        self.assert_(expected==observed)

#----------------------------------------------------------------------
# MyUtil
#----------------------------------------------------------------------
class TestMyUtil(unittest.TestCase):
    """
    Test myUtil.py Methods
    """
    def setUp(self):
        pass

    def testSortLists(self):
        a = range(10)
        a.reverse()
        b = range(10)
        b.reverse()
        master, slave = myUtil.SortLists(a, b)
        a.sort()
        b.sort()
        self.assert_(a == master)
        self.assert_(slave == b)
        
    def testGetFlowRangeLinear(self):
        """
        Confirm GetFlowRange returns correct
        linear range
        """
        N       = 10
        start   = 20
        end     = 1
        # test linear output
        observed = myUtil.GetFlowRange(N, start, end, linear=True)
        expected = [20.0, 17.88888889, 15.77777778, 13.66666667, 11.55555556, 9.44444444, 7.33333333, 5.22222222, 3.11111111, 1.0]
        self.assert_(len(expected) == len(observed))
        for i in range(len(expected)):
            self.assertAlmostEquals(observed[i], expected[i], 5)

    def testGetFlowRangeExponential(self):
        """
        Confirm GetFlowRange returns correct
        exponential range
        """
        N       = 10
        start   = 20
        end     = 1
        # test exponential output
        observed = myUtil.GetFlowRange(N, start, end, linear=False)
        expected = [20.0, 10.5, 5.75, 3.375, 2.1875, 1.59375, 1.296875, 1.1484375, 1.07421875, 1.03710938]
        self.assert_(len(expected) == len(observed))
        for i in range(len(expected)):
            self.assertAlmostEquals(observed[i], expected[i], 5)

    def testDigitalToMilliAmps(self):
        """
        Confirm DigitalToMilliAmps returns correct
        milliamp value
        """
        BCD_value = 4095
        observed = myUtil.DigitalToMilliAmps(BCD_value)
        expected = 20.0
        self.assert_(expected == observed)

        BCD_value = 0
        observed = myUtil.DigitalToMilliAmps(BCD_value)
        expected = 4.0
        self.assert_(expected == observed)

    def testGetError(self):
        """
        Confirm GetError returns correct error value
        """
        a = 10.0
        b = 1.0
        observed = myUtil.GetError(a,b)
        expected = 900.0
        self.assert_(expected == observed)

        a = 1.0
        b = 1.0
        observed = myUtil.GetError(a,b)
        expected = 0.0
        self.assert_(expected == observed)

    def testGetStorageVolumeUncert(self):
        """
        Confirm GetStorageVolumeUncert returns correct uncertainty
        """
        observed = myUtil.GetStorageVolumeUncert(HF_SYSTEM)
        expected = U_HF_SYS_STORAGE_VOLUME
        self.assert_(expected == observed)

        observed = myUtil.GetStorageVolumeUncert(LF_SYSTEM)
        expected = U_LF_SYS_STORAGE_VOLUME
        self.assert_(expected == observed)

    def testGetStorageVolume(self):
        """
        Confirm GetStorageVolume returns correct volume
        """
        observed = myUtil.GetStorageVolume(HF_SYSTEM)
        expected = HF_SYS_STORAGE_VOLUME
        self.assert_(expected == observed)

        observed = myUtil.GetStorageVolume(LF_SYSTEM)
        expected = LF_SYS_STORAGE_VOLUME
        self.assert_(expected == observed)

    def testCalValuesAreOk(self):
        """
        Confirm CalValuesAreOk returns correct value
        """
        ref_count   = 100.0
        mut_count   = 1000.0
        test_time   = 60.0
        temp_change = 0
        observed = myUtil.CalValuesAreOk(ref_count, mut_count, test_time, temp_change)
        expected = True
        self.assert_(expected==observed)

        ref_count   = 100.0
        mut_count   = 1000.0
        test_time   = 60.0
        temp_change = MAX_TEMP_CHANGE + 1
        observed = myUtil.CalValuesAreOk(ref_count, mut_count, test_time, temp_change)
        expected = False
        self.assert_(expected==observed)

        ref_count   = 0.0
        mut_count   = 1000.0
        test_time   = 60.0
        temp_change = MAX_TEMP_CHANGE
        observed = myUtil.CalValuesAreOk(ref_count, mut_count, test_time, temp_change)
        expected = False
        self.assert_(expected==observed)

        ref_count   = 100.0
        mut_count   = 0.0
        test_time   = 60.0
        temp_change = MAX_TEMP_CHANGE
        observed = myUtil.CalValuesAreOk(ref_count, mut_count, test_time, temp_change)
        expected = False
        self.assert_(expected==observed)

        ref_count   = 100.0
        mut_count   = 100.0
        test_time   = 0.0
        temp_change = MAX_TEMP_CHANGE
        observed = myUtil.CalValuesAreOk(ref_count, mut_count, test_time, temp_change)
        expected = False
        self.assert_(expected==observed)
        
if __name__ == '__main__':
    unittest.main()
