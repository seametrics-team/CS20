#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''
 1.08   2016/07/15  SPN     -Update Client.Open mehod: add assert statement so SQL errors are
                             more apparent
 1.07   2013/10/14  SPN     Add new Syteline field: Item Display for retrieving part number accurately
 1.06   2013/05/22  SPN     -Reinstate GetFail arg for GetCalibrationDataClient method
 1.05   2013/03/13/ SPN     -Updated PostCalibrationDataClient method to save all serial #'s to SyteLine
                            -Updated GetCalibrationDataClient method to retrieve cal data from SyteLine first.
                            If none found then try from Epicor
 1.04   2013/03/08  SPN     Updatd all GetCalibrationDataClient and PostCalibrationDataClient method read/write data
                            to SyteLine's Calibration Data table
 1.03   2013/03/07  SPN     -Updated GetCalibrationDataClient method to return top row only
                            -Updated GetProductDataClient method to accomodate longer serial # data from SyteLine
 1.02   2013/02/01  SPN     Updated GetProductDataClient method in order to receive results
                            for meters (mechanical meters) that don't have a job order from Epicor
 1.01   2013/01/08  SPN     Update GetCalibrationDataClient SQL query to sort by date descending
                            filtered with PASS only or PASS/FAIL result
    1   02/23/2011  JTP     -   Initial release
'''

import time
import threading
import types
import string
import wx
import copy
import myODBC
import myQueueItems

#-------------------------------------------------------------------
class Client(threading.Thread):
    UID = 'bench'
    PWD = 'bench'
    SERVER = 'seadc04'
    SERVER_SL = 'seasql01'
    DRIVER = 'SQL Native Client'
    DSN = 'Trusted_Connection=no'
    DB_PATH = 'epicor904'
    DB_PATH_SL = 'seametrics'
    SQL = ''

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._want_abort = 0
        self.is_running = False

    #--------------------------------
    def run(self):
        self.is_running = False
        
    #--------------------------------
    def IsRunning(self):
        return self.is_running

    #--------------------------------
    def Put(self, q, item, data, msg=None):        
        item.data = data
        if msg != None:
            item.msg = msg
        q.put(copy.deepcopy(item))

    #--------------------------------
    def Abort(self):    
        self._want_abort = 1
        
    #--------------------------------
    def Open(self):
        self.client = myODBC.Client()
        self.client.EnableSecurity(True)
        dsn = self.client.CreateDSN(self.DSN, self.DRIVER, self.DB_PATH, self.UID, self.PWD, server=self.SERVER)
##        print 'dsn:: ', dsn
        self.client.SetDSN(dsn)
        self.client.EnableSecurity(True)
        client_open = self.client.Open()
        assert client_open
        
        return client_open

    #--------------------------------
    def Close(self):
        self.client.Close()
        return True


#-------------------------------------------------------------------
DESCRIPTION_LABEL_INDEX = 0
SERIAL_NUMBER_LABEL = 'serialnumber'
COMPANY_NAME_LABEL = 'name'
ORDER_NUM_LABEL = 'ordernum'
LINE_ORDER_LABEL = 'orderline'
ORDER_REL_NUM_LABEL = 'orderrelnum'
PART_NUM_LABEL = 'partnum'
LINE_DESCRIPTION_LABEL = 'linedesc'
DESCRIPTION_LABELS = [SERIAL_NUMBER_LABEL,
                      COMPANY_NAME_LABEL,
                      ORDER_NUM_LABEL,
                      LINE_ORDER_LABEL,
                      ORDER_REL_NUM_LABEL,
                      PART_NUM_LABEL,
                      LINE_DESCRIPTION_LABEL,
                      ]
# SyteLine labels
SERIAL_NUMBER_LABEL_SL = 'ser_num'
COMPANY_NAME_LABEL_SL = 'name'
CO_NUM_LABEL_SL = 'co_num'
CO_LINE_LABEL_SL = 'co_line'
DESCRIPTION_LABEL_SL = 'description'
ITEM_LABEL_SL = 'item'
ITEM_DISPLAY_LABEL_SL = 'Item Display'
CUST_ITEM_LABEL_SL = 'cust_item'
JOB_LABEL_SL = 'job'
SUFFIX_LABEL_SL = 'suffix'
PULSE_RATE_LABEL_SL = 'Uf_CalibrationPulseRate'
RATE_UNIT_LABEL_SL = 'Uf_CalibrationRate'
TOTAL_UNIT_LABEL_SL = 'Uf_CalibrationTotal'
METER_FAMILY_LABEL_SL = 'MeterFamily'
METER_FAMILY_DESC_SL = 'MeterFamilyDesc'
METER_SIZE_LABEL_SL = 'MeterSize'
METER_SIZE_DESC_LABEL_SL = 'MeterSizeDesc'
OPTION_CODES_LABEL_SL = 'Uf_ItemOptionCode'
DESCRIPTION_LABELS_SL = [SERIAL_NUMBER_LABEL_SL,
                         COMPANY_NAME_LABEL_SL,
                         CO_NUM_LABEL_SL,
                         CO_LINE_LABEL_SL,
                         DESCRIPTION_LABEL_SL,
                         ITEM_LABEL_SL,
                         ITEM_DISPLAY_LABEL_SL,
                         CUST_ITEM_LABEL_SL,
                         JOB_LABEL_SL,
                         SUFFIX_LABEL_SL,
                         PULSE_RATE_LABEL_SL,
                         RATE_UNIT_LABEL_SL,
                         TOTAL_UNIT_LABEL_SL,
                         METER_FAMILY_LABEL_SL,
                         METER_FAMILY_DESC_SL,
                         METER_SIZE_LABEL_SL,
                         METER_SIZE_DESC_LABEL_SL,
                         OPTION_CODES_LABEL_SL,]

SERVER_QUERY_TYPE_KEY = 'SERVER_QUERY_TYPE_KEY'
SERVER_QUERY_TYPE_PRODUCT_DATA = 'SERVER_QUERY_TYPE_PRODUCT_KEY'
SERVER_QUERY_TYPE_CALIBRATION_DATA = 'SERVER_QUERY_TYPE_CALIBRATION_KEY'

class GetProductDataClient(Client):
    UID = 'bench'
    PWD = '#AnkB3Nc#h@lly'
    SERVER = 'seadc04'
    SERVER_SL = 'seasql01'
    DRIVER = 'SQL Native Client'
    DSN = 'Trusted_Connection=no'
    DB_PATH = 'epicor904'
    DB_PATH_SL = 'seametrics'
    DESCRIPTION_LABELS = DESCRIPTION_LABELS
    PLACE_HOLDER = '*SERIAL_NUM*'
    SQL = "EXECUTE [epicor904].[dbo].[SI_SerialNumberLookup] '%s', 2"%PLACE_HOLDER
    # SyteLine query
    SQL_SL = "EXECUTE [SI_BenchCalibrationSetup] '%s'"%PLACE_HOLDER
##    SQL = "EXECUTE [epicor904].[dbo].[SI_SerialNumberLookup] '%s', 1"%PLACE_HOLDER

    """
    Class to get sales order entry data from Epicore servers
    data is used to configure flow meters during calibration
    """
    def __init__(self, serial_num, wx_q):
        Client.__init__(self)
        self.wx_q = wx_q
        self.serial_num = serial_num

        # Use different desc labels and sql query for 12 digit serial #'s in SyteLine
        if len(self.serial_num) == 12:
            self.SERVER = self.SERVER_SL
            self.DB_PATH = self.DB_PATH_SL
            self.DESCRIPTION_LABELS = DESCRIPTION_LABELS_SL
            self.SQL = self.SQL_SL
        
    #--------------------------------
    def run(self):
        self.is_running = True
        if self.Open():
            self.Put(self.wx_q, myQueueItems.SERVER_DATA_READY, self.GetDataDict(SERVER_QUERY_TYPE_PRODUCT_DATA))
            self.Close()
        self.is_running = False
        
    #--------------------------------
    def GetDataDict(self, label):
        """
        returns dictionary of order/product data from order entry
        """
        self.client.SetSQL(self.SQL.replace(self.PLACE_HOLDER, self.serial_num))
##        print 'sql query::', self.SQL

        d = {}
##        print 'sql data::', self.client.ExecuteSQL()
        if self.client.ExecuteSQL():
            d = self.client.GetData(self.DESCRIPTION_LABELS)
            if type(d) == types.DictType:
                d = self.CleanDataDict(d)
            
        d[SERVER_QUERY_TYPE_KEY] = label
        return d
            

    #--------------------------------
    def CleanDataDict(self, data_dict):
        for key in data_dict:
            if data_dict[key] != None:
                data_dict[key] = string.upper(data_dict[key])

        if data_dict.has_key(LINE_DESCRIPTION_LABEL):
            data_dict[LINE_DESCRIPTION_LABEL] = data_dict[LINE_DESCRIPTION_LABEL].split(',')[0]

        return data_dict
        

#-------------------------------------------------------------------
TEST_RESULT_BENCH_ID_KEY = 'Bench'
TEST_RESULT_SERIAL_NUMBER_KEY = 'SERIAL_NUMBER'
TEST_RESULT_DATE_TIME_KEY = 'DATE_TIME'
TEST_RESULT_FSADC_KEY = 'FSADC'
TEST_RESULT_ZRADC_KEY = 'ZRADC'
# units gal
TEST_RESULT_V_Q3_1_KEY = 'V_Q3_1'
TEST_RESULT_V_Q3_2_KEY = 'V_Q3_2'
TEST_RESULT_V_Q3_3_KEY = 'V_Q3_3'
TEST_RESULT_V_Q1_1_KEY = 'V_Q1_1'
TEST_RESULT_V_Q1_2_KEY = 'V_Q1_2'
TEST_RESULT_V_Q1_3_KEY = 'V_Q1_3'
# units sec
TEST_RESULT_T_Q3_1_KEY = 'T_Q3_1'
TEST_RESULT_T_Q3_2_KEY = 'T_Q3_2'
TEST_RESULT_T_Q3_3_KEY = 'T_Q3_3'
TEST_RESULT_T_Q1_1_KEY = 'T_Q1_1'
TEST_RESULT_T_Q1_2_KEY = 'T_Q1_2'
TEST_RESULT_T_Q1_3_KEY = 'T_Q1_3'
# units ppg
TEST_RESULT_K_Q3_1_KEY = 'K_Q3_1'
TEST_RESULT_K_Q3_2_KEY = 'K_Q3_2'
TEST_RESULT_K_Q3_3_KEY = 'K_Q3_3'
TEST_RESULT_K_Q1_1_KEY = 'K_Q1_1'
TEST_RESULT_K_Q1_2_KEY = 'K_Q1_2'
TEST_RESULT_K_Q1_3_KEY = 'K_Q1_3'
TEST_RESULT_PASS_KEY = 'PASS'
TEST_RESULT_UNCERTAINTY_KEY = 'U_K'
# units ppg
TEST_RESULT_REF_K_Q3_KEY = 'REF_K_Q3'
TEST_RESULT_REF_K_Q1_KEY = 'REF_K_Q1'
# units sec
TEST_RESULT_TEST_TIME_Q3_KEY = 'TEST_TIME_Q3'
TEST_RESULT_TEST_TIME_Q1_KEY = 'TEST_TIME_Q1'

CALIBRATION_LABELS = [TEST_RESULT_SERIAL_NUMBER_KEY,
                      TEST_RESULT_V_Q3_1_KEY,
                      TEST_RESULT_V_Q3_2_KEY,
                      TEST_RESULT_V_Q3_3_KEY,
                      TEST_RESULT_V_Q1_1_KEY,
                      TEST_RESULT_V_Q1_2_KEY,
                      TEST_RESULT_V_Q1_3_KEY,                      
                      TEST_RESULT_T_Q3_1_KEY,
                      TEST_RESULT_T_Q3_2_KEY,
                      TEST_RESULT_T_Q3_3_KEY,
                      TEST_RESULT_T_Q1_1_KEY,
                      TEST_RESULT_T_Q1_2_KEY,
                      TEST_RESULT_T_Q1_3_KEY,                      
                      TEST_RESULT_K_Q3_1_KEY,
                      TEST_RESULT_K_Q3_2_KEY,
                      TEST_RESULT_K_Q3_3_KEY,
                      TEST_RESULT_K_Q1_1_KEY,
                      TEST_RESULT_K_Q1_2_KEY,
                      TEST_RESULT_K_Q1_3_KEY,
                      TEST_RESULT_UNCERTAINTY_KEY,
                      TEST_RESULT_REF_K_Q3_KEY,
                      TEST_RESULT_REF_K_Q1_KEY,
                      TEST_RESULT_FSADC_KEY,
                      TEST_RESULT_ZRADC_KEY,
                      TEST_RESULT_DATE_TIME_KEY,
                      TEST_RESULT_PASS_KEY,]
CALIBRATION_LABELS_SL = CALIBRATION_LABELS[:]
CALIBRATION_LABELS_SL.append(TEST_RESULT_BENCH_ID_KEY)

class PostCalibrationDataClient(Client):
    """
    Class to post calibration test results to Epicore servers
    """
    UID = 'bench'
    PWD = 'bench'
    SERVER = 'seadc04'
    SERVER_SL = 'seasql01'
    DRIVER = 'SQL Native Client'
    DSN = 'Trusted_Connection=no'
    DB_PATH = 'BenchData'
    DB_PATH_SL = 'seametrics'
    SQL = """USE BenchData
INSERT INTO CalibrationData([SERIAL_NUMBER], [V_Q3_1], [V_Q3_2], [V_Q3_3], [V_Q1_1], [V_Q1_2], [V_Q1_3], [T_Q3_1], [T_Q3_2], [T_Q3_3], [T_Q1_1], [T_Q1_2], [T_Q1_3], [K_Q3_1], [K_Q3_2], [K_Q3_3], [K_Q1_1], [K_Q1_2], [K_Q1_3], [U_K], [REF_K_Q3], [REF_K_Q1], [FSADC], [ZRADC], [DATE_TIME], [PASS])
VALUES(%s)"""
    SQL_SL = """USE seametrics
INSERT INTO SI_CalibrationData([ser_num], [V_Q3_1], [V_Q3_2], [V_Q3_3], [V_Q1_1], [V_Q1_2], [V_Q1_3], [T_Q3_1], [T_Q3_2], [T_Q3_3], [T_Q1_1], [T_Q1_2], [T_Q1_3], [K_Q3_1], [K_Q3_2], [K_Q3_3], [K_Q1_1], [K_Q1_2], [K_Q1_3], [U_K], [REF_K_Q3], [REF_K_Q1], [FSADC], [ZRADC], [DATE_TIME], [PASS], [Bench])
VALUES(%s)"""

    def __init__(self, data):
        Client.__init__(self)
        # dictionary to hold test data
        self.data = data

        # Refence SyteLine db for all serial #'s
##        if len(self.data[TEST_RESULT_SERIAL_NUMBER_KEY]) == 12:
        self.SERVER = self.SERVER_SL
        self.DB_PATH = self.DB_PATH_SL
        self.SQL = self.SQL_SL

    #--------------------------------
    def run(self):
        self.is_running = True
        if self.Open():
            self.SetData()
            assert self.Post()
            self.Close()
        self.is_running = False
    
    #--------------------------------
    def SetData(self):
        assert type(self.data) == types.DictType
        
        # build insert string
        # must be in order: SERIAL_NUMBER, V_Q3_1, V_Q3_2, V_Q3_3, V_Q1_1, V_Q1_2, V_Q1_3, T_Q3_1, T_Q3_2, T_Q3_3, T_Q1_1, T_Q1_2, T_Q1_3, K_Q3_1, K_Q3_2, K_Q3_3, K_Q1_1, K_Q1_2, K_Q1_3, U_K, REF_K_Q3, REF_K_Q1, FSADC, ZRADC, DATE_TIME, PASS, Bench    
        s= "'%s',"%self.data[TEST_RESULT_SERIAL_NUMBER_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_V_Q3_1_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_V_Q3_2_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_V_Q3_3_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_V_Q1_1_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_V_Q1_2_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_V_Q1_3_KEY]
        
        s+= "'%s',"%self.data[TEST_RESULT_T_Q3_1_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_T_Q3_2_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_T_Q3_3_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_T_Q1_1_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_T_Q1_2_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_T_Q1_3_KEY]
        
        s+= "'%s',"%self.data[TEST_RESULT_K_Q3_1_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_K_Q3_2_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_K_Q3_3_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_K_Q1_1_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_K_Q1_2_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_K_Q1_3_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_UNCERTAINTY_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_REF_K_Q3_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_REF_K_Q1_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_FSADC_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_ZRADC_KEY]
        s+= "'%s',"%self.data[TEST_RESULT_DATE_TIME_KEY]
        
##        if len(self.data[TEST_RESULT_SERIAL_NUMBER_KEY]) == 12:
        s+= "'%s',"%int(self.data[TEST_RESULT_PASS_KEY])
        s+= "'%s'"%self.data[TEST_RESULT_BENCH_ID_KEY]
##        else:
##            s+= "'%s'"%self.data[TEST_RESULT_PASS_KEY]
            
##        print 'sql::', self.SQL%s
        self.client.SetSQL(self.SQL%s)
        
    #--------------------------------
    def Post(self):
        """
        posted test data to server database
        returns True if successful, else False
        """
        if not self.client.ExecuteSQL():
            return False
        elif not self.client.Commit():
            return False
        else:
            return True


#-------------------------------------------------------------------
class GetCalibrationDataClient(Client):
    """
    Class to post calibration test results to Epicore servers
    """
    UID = 'bench'
    PWD = 'bench'
    SERVER_EPICOR = 'seadc04'
    SERVER_SL = 'seasql01'
    DRIVER = 'SQL Native Client'
    DSN = 'Trusted_Connection=no'
    DB_PATH_EPICOR = 'BenchData'
    DB_PATH_SL = 'seametrics'
##    SQL = "SELECT * FROM CalibrationData WHERE [SERIAL_NUMBER] = '%s' ORDER BY CreateDate DESC"
    SQL_EPICOR = "SELECT TOP 1 * FROM CalibrationData WHERE [SERIAL_NUMBER] = '%s' AND [PASS] = 'TRUE' ORDER BY created DESC"
    # Retrieve newest pass or fail data
    SQL_SL = "SELECT TOP 1 ser_num 'SERIAL_NUMBER',CreateDate 'DATE_TIME',FSADC,ZRADC,V_Q3_1,V_Q3_2,V_Q3_3,V_Q1_1,V_Q1_2,V_Q1_3,T_Q3_1,T_Q3_2,T_Q3_3,T_Q1_1,T_Q1_2,T_Q1_3,K_Q3_1,K_Q3_2,K_Q3_3,K_Q1_1,K_Q1_2,K_Q1_3,PASS,U_K,REF_K_Q3,REF_K_Q1,Bench FROM SI_CalibrationData WHERE [SER_NUM] = '%s' ORDER BY CreateDate DESC"
##    SQL = "SELECT * FROM CalibrationData WHERE [SERIAL_NUMBER] = %s"
##    CALIBRATION_LABELS = CALIBRATION_LABELS

    def __init__(self, serial_num, wx_q, GetFail=False):
        Client.__init__(self)
        self.wx_q = wx_q
        self.serial_num = serial_num
##        print 'serial num::', self.serial_num

        # Initally refence SyteLine db all serial #'s
##        if len(self.serial_num) == 12:
        self.SERVER = self.SERVER_SL
        self.DB_PATH = self.DB_PATH_SL
        self.SQL = self.SQL_SL%self.serial_num
        self.CALIBRATION_LABELS = CALIBRATION_LABELS_SL
##        else:
##            self.SQL = self.SQL%self.serial_num
##            self.CALIBRATION_LABELS = CALIBRATION_LABELS

##        if not GetFail:
##            self.SQL = "SELECT TOP 1 * FROM CalibrationData WHERE [SERIAL_NUMBER] = '%s' AND [PASS] = 'TRUE' ORDER BY created DESC"
##        self.SQL = self.SQL%self.serial_num

        # Retrieve lateset pass result
        if not GetFail:
            self.SQL = "SELECT TOP 1 ser_num 'SERIAL_NUMBER',CreateDate 'DATE_TIME',FSADC,ZRADC,V_Q3_1,V_Q3_2,V_Q3_3,V_Q1_1,V_Q1_2,V_Q1_3,T_Q3_1,T_Q3_2,T_Q3_3,T_Q1_1,T_Q1_2,T_Q1_3,K_Q3_1,K_Q3_2,K_Q3_3,K_Q1_1,K_Q1_2,K_Q1_3,PASS,U_K,REF_K_Q3,REF_K_Q1,Bench FROM SI_CalibrationData WHERE [SER_NUM] = '%s' AND [PASS] = '1' ORDER BY CreateDate DESC"
        self.SQL = self.SQL%self.serial_num

        
    #--------------------------------
    def run(self):
        self.is_running = True
        if self.Open():
            self.Put(self.wx_q, myQueueItems.SERVER_DATA_READY, self.GetDataDict(SERVER_QUERY_TYPE_CALIBRATION_DATA))
            self.Close()
        self.is_running = False
        
    #--------------------------------
    def GetDataDict(self, label):
        """
        returns dictionary of order/product data from order entry
        """
        self.client.SetSQL(self.SQL)
##        print 'sql::', self.SQL

        d = {}
##        print 'exec sql::', self.client.ExecuteSQL()
##        assert self.client.ExecuteSQL()

        if self.client.ExecuteSQL():
            d = self.client.GetData(self.CALIBRATION_LABELS)
            #If no results returned then try Epicor server
            if d == {}:
                self.SERVER = self.SERVER_EPICOR
                self.DB_PATH = self.DB_PATH_EPICOR
                self.SQL = self.SQL_EPICOR%self.serial_num
                self.CALIBRATION_LABELS = CALIBRATION_LABELS
                if self.Open():
                    self.client.SetSQL(self.SQL)

                    if self.client.ExecuteSQL():
                        d = self.client.GetData(self.CALIBRATION_LABELS)
                
        d[SERVER_QUERY_TYPE_KEY] = label
        return d


#-------------------------------------------------------------------

def WriteTest():
    print 'running WriteTest()'
    import Queue
    from datetime import datetime
##    import myDbClientApp as myDbClientApp

    q = Queue.Queue()
    date = datetime.today().isoformat(' ')
    date = date.split('.')[0]

    # build insert string
    # must be in order: [SERIAL_NUMBER], [V_Q3_1], [V_Q3_2], [V_Q3_3], [V_Q1_1], [V_Q1_2], [V_Q1_3], [T_Q3_1], [T_Q3_2], [T_Q3_3], [T_Q1_1], [T_Q1_2], [T_Q1_3], K_Q3_1, K_Q3_2, K_Q3_3, K_Q1_1, K_Q1_2, K_Q1_3, U_K, REF_K_Q3, REF_K_Q1, FSADC, ZRADC, DATE_TIME, PASS    
    data = {}
    data[TEST_RESULT_SERIAL_NUMBER_KEY] = '00000001'

    data[TEST_RESULT_K_Q3_1_KEY] = 1
    data[TEST_RESULT_K_Q3_2_KEY] = 1
    data[TEST_RESULT_K_Q3_3_KEY] = 1
    data[TEST_RESULT_K_Q1_1_KEY] = 1
    data[TEST_RESULT_K_Q1_2_KEY] = 1
    data[TEST_RESULT_K_Q1_3_KEY] = 1

    data[TEST_RESULT_T_Q3_1_KEY] = 10
    data[TEST_RESULT_T_Q3_2_KEY] = 10
    data[TEST_RESULT_T_Q3_3_KEY] = 10
    data[TEST_RESULT_T_Q1_1_KEY] = 10
    data[TEST_RESULT_T_Q1_2_KEY] = 10
    data[TEST_RESULT_T_Q1_3_KEY] = 10

    data[TEST_RESULT_V_Q3_1_KEY] = 100
    data[TEST_RESULT_V_Q3_2_KEY] = 100
    data[TEST_RESULT_V_Q3_3_KEY] = 100
    data[TEST_RESULT_V_Q1_1_KEY] = 100
    data[TEST_RESULT_V_Q1_2_KEY] = 100
    data[TEST_RESULT_V_Q1_3_KEY] = 100

    data[TEST_RESULT_UNCERTAINTY_KEY] = .3
    data[TEST_RESULT_REF_K_Q3_KEY] = 10.0
    data[TEST_RESULT_REF_K_Q1_KEY] = 100.0

    data[TEST_RESULT_FSADC_KEY] = 111
    data[TEST_RESULT_ZRADC_KEY] = .01
    data[TEST_RESULT_DATE_TIME_KEY] = date
    data[TEST_RESULT_PASS_KEY] = True
    data[TEST_RESULT_BENCH_ID_KEY] = 2
    
    client = PostCalibrationDataClient(data)
    client.start()

def ReadTest():
    print 'running ReadTest()'
    import Queue
    q = Queue.Queue()
##    client = GetProductDataClient('02131856', q)
    client = GetProductDataClient('022015000216', q)
    client.start()
    print 'client finished::'
    item = q.get()
    print '---meter data---'
    print item.msg, item.ID, item.data
    q.task_done()    

    q = Queue.Queue()
##    client = GetCalibrationDataClient('02131856', q)
    client = GetCalibrationDataClient('032013000931', q)
    client.start()
    item = q.get()
    print '---calibration data---'
    print item.msg, item.ID, item.data
    q.task_done()

##ReadTest()
##WriteTest()
