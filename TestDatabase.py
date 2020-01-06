import Modules.myDatabase as myDatabase
from Modules.myHeader import *
import Modules.myDateTime as myDateTime
import os

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------

def Test():
    dbi = myDatabase.Database()
    dbi.Load()
    dbi.PrintContents()

def GetItemContents(serial_num):
    dbi = myDatabase.Database()
    dbi.Load()
    item = dbi.GetItem(serial_num)
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
        
##GetItemContents('00000000')
##Test()

##dbi = myDatabase.Database()
##dbi.Load()
##items = dbi.GetItems().values()
##for item in items:
##    if item.GetFSADC() == None:
##        print item.GetSerialNum()
##    elif item.GetZRADC() == None:
##        print item.GetSerialNum()

import pickle

PRODUCTION_ITEMS_DATABASE_PATH = 'S:\\Calibration Bench\\CS20\\Bench Data\\PE\\PE CAL SYS PRODUCTION DATABASE.txt.bad'        
fh = pickle.load(open(PRODUCTION_ITEMS_DATABASE_PATH, 'r'))
