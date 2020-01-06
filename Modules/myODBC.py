#----------------------------------------------------------------------
# ODBC Module
''' author: Jeff Peery '''
# date: 07/30/2010
# email: JeffPeery@yahoo.com
# copyright 2011, property of Jeff Peery
#----------------------------------------------------------------------


# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''
 1.02   2013/06/12  SPN     Updated ExecuteSQL method to append "SET NOCOUNT ON;" before SQL query to accomodate for
                            SyteLine change preventing meter configuration data from being retreived
 1.01   2013/03/07  SPN     Updated GetData method to accomodate SyteLine data
    1   07/30/2010    JTP     -   Initial Release
    
'''
import numpy
import types
import pyodbc
import string
import myRegistryWalk

pyodbc.threadsafety = 1
pyodbc.paramstyle = 'qmark'

DESCRIPTION_LABEL_INDEX = 0

ERROR_NONE_TYPE_CURSOR = 0
ERROR_NO_COLUMN_DATA = 1

DSN_DRIVER_LABEL = 'DRIVER'
DSN_PWD_LABEL = 'PWD'
DSN_USER_LABEL = 'UID'
DSN_PATH_LABEL = 'DATABASE'
DSN_SERVER_LABEL = 'SERVER'
DSN_LOCAL_HOST = 'localhost'
#----------------------------------------------------------------------
# Methods
#----------------------------------------------------------------------


#----------------------------------------------------------------------
# Classes
#----------------------------------------------------------------------               
class Client:
    def __init__(self):
        # odbc connection
        self.conn = None
        self.cursor = None  
        # the SQL query to fetch data
        self.sql = None
        # driver label for DSN
        self.driver = None
        # database path for DSN
        self.db_path = None
        # dsn
        self.dsn = ''
        # user name
        self.user_name = ''
        # password
        self.pwd = ''
        # user_name and password enabled
        self.security_enabled = False
        # server
        self.server = DSN_LOCAL_HOST
        
    #--------------------------------------
    # General Methods
    #--------------------------------------
    def Open(self):
        "Open connection"
        try:
            if 'EXCEL' in self.dsn.upper():                
                # excel require autocommit == true
                self.conn = pyodbc.connect(self.dsn, autocommit=True)
            else:
                self.conn = pyodbc.connect(self.dsn)
            self.cursor = self.conn.cursor()
            return True
        except:
            self.conn = None
            self.cursor = None
            return False
        
    def Close(self):
        "Close connection"
        try:
            if self.IsCursor():
                self.cursor.close()
                self.cursor = None
            if self.IsOpen():
                self.conn.close()
                self.conn = None
            return True
        except:
            return False

    def IsOpen(self):
        "Test for open connection"
        return self.conn != None

    def IsCursor(self):
        if not self.IsOpen():
            return False
        elif self.cursor == None:
            return False
        else:
            return True

    def CreateDSN(self, dsn, driver, db_path, uid, pwd, server=DSN_LOCAL_HOST):
        assert type(driver) in types.StringTypes
        assert type(db_path) in types.StringTypes
        assert type(uid) in types.StringTypes
        assert type(pwd) in types.StringTypes
        assert type(dsn) in types.StringTypes

        dsn = dsn.split(';')
        for i in range(len(dsn)):
            if DSN_DRIVER_LABEL in dsn[i]:
                dsn[i] = DSN_DRIVER_LABEL+'=%s;'%driver
            elif DSN_SERVER_LABEL in dsn[i]:
                dsn[i] = DSN_SERVER_LABEL+'=%s;'%server
            elif DSN_PWD_LABEL in dsn[i]:
                dsn[i] = DSN_PWD_LABEL+'=%s;'%pwd
            elif DSN_USER_LABEL in dsn[i]:
                dsn[i] = DSN_USER_LABEL+'=%s;'%uid
            elif DSN_PATH_LABEL in dsn[i]:
                dsn[i] = DSN_PATH_LABEL+'=%s;'%db_path
            else: 
                dsn[i] = dsn[i]+';'
                
        dsn = string.join(dsn,' ')

        if DSN_DRIVER_LABEL not in dsn:
            dsn = DSN_DRIVER_LABEL+'=%s;'%driver + dsn
        for i in string.whitespace:
            x = pwd.replace(i,'')
            y = uid.replace(i,'')
        if self.IsSecurityEnabled():
            if x != '' and DSN_USER_LABEL not in dsn:
                dsn+=' UID=%s;'%uid
            if y != '' and DSN_PWD_LABEL not in dsn:
                dsn+=' PWD=%s;'%pwd
        if DSN_SERVER_LABEL not in dsn:
            dsn += ' '+DSN_SERVER_LABEL+'=%s;'%server
        if DSN_PATH_LABEL not in dsn:
            dsn += ' '+DSN_PATH_LABEL+'=%s;'%db_path   

        return dsn
            
    def ExecuteSQL(self):
        try:
            noCount = 'SET NOCOUNT ON; '
            self.cursor.execute(noCount + self.sql)
            return True
        except:
            return False

    def Commit(self):
        try:
            self.conn.commit()
            return True
        except:
            return False
    
    def GetData(self, description_labels):
        assert type(description_labels) == types.ListType
        
        if not self.IsCursor():
            return ERROR_NONE_TYPE_CURSOR

        rows = self.cursor.fetchall()

        if rows == None:
            return {}
        elif len(rows) == 0:
            return {}
        
##        row = rows[0]
        
        data_dict = {}
        for key in description_labels:
            values = []
            for row in rows:
                if type(row[self.GetLabelIndex(key)]) in types.StringTypes:
                    row[self.GetLabelIndex(key)] = row[self.GetLabelIndex(key)].encode("utf-8")

                value = string.upper(str(row[self.GetLabelIndex(key)]))

                if not value in values:
                    values.append(value)
                    
            values = '-'.join(values)
            data_dict[key] = values

##                if data_dict.has_key(key) and not value in data_dict[key]:
##                    data_dict[key] += '-' + value
##                else:
##                    data_dict[key] = value
                    
##        print 'data dict::', data_dict
        return data_dict
        
    def GetLabelIndex(self, label):
        assert type(label) in types.StringTypes
        
        if not self.IsCursor():
            return None
        i=0
        try:
            for s in self.cursor.description:
                if string.upper(s[DESCRIPTION_LABEL_INDEX]) == string.upper(label):
                    return i
                i+=1
            return None
        except:
            return None

    def GetRegisteredDBLabels(self):
        return myRegistryWalk.GetDBLabels()
    
    def SetDriverLabel(self, s):
        assert type(s) in types.StringTypes
        self.driver = s
        return True

    def GetDriverLabel(self):
        return self.driver
    
    def SetDBPath(self, s):
        assert type(s) in types.StringTypes
        self.db_path = s
        return True

    def GetDBPath(self):
        return self.db_path
        
    def GetSQL(self):
        return self.sql

    def SetSQL(self, s):
        assert type(s) in types.StringTypes
        self.sql = s
        return True
        
    def GetDSN(self):
        return self.dsn

    def SetDSN(self, s):
        assert type(s) in types.StringTypes
        self.dsn = s
        return True

    def SetUserName(self, s):
        assert type(s) in types.StringTypes
        self.user_name = s
        return True

    def GetUserName(self):
        return self.user_name
    
    def SetPassword(self, s):
        assert type(s) in types.StringTypes
        self.pwd = s
        return True

    def GetPassword(self):
        return self.pwd

    def EnableSecurity(self, enable):
        assert type(enable) == types.BooleanType
        self.security_enabled = enable
        return True

    def IsSecurityEnabled(self):
        return self.security_enabled
    
    def GetServer(self):
        return self.server

    def SetServer(self, s):
        assert type(s) in types.StringTypes
        self.server = s
        return True

#-------------------------------------------------------------------
def Test():
    UID = 'bench'
    PWD = 'bench'
    SERVER = 'seadc04'
    DRIVER = 'SQL Native Client'
    DSN = 'Trusted_Connection=no'
    DB_PATH = 'epicor904'

    client = Client()
    client.EnableSecurity(True)
    dsn = client.CreateDSN(DSN, DRIVER, DB_PATH, UID, PWD, server=SERVER)
    client.SetDSN(dsn)
    client.EnableSecurity(True)
    client.Open()
    
    client.SetSQL("EXECUTE [epicor904].[dbo].[SI_SerialNumberLookup] '03123893', 2")
    client.ExecuteSQL()
    print client.cursor.fetchall()
    
    client.Close()
    
#-------------------------------------------------------------------
def Test2():
    UID = 'bench'
    PWD = 'bench'
    SERVER = 'seadc04'
    DRIVER = 'SQL Native Client'
    DSN = 'Trusted_Connection=no'
    DB_PATH = 'BenchData'

    client = Client()
    client.EnableSecurity(True)
    dsn = client.CreateDSN(DSN, DRIVER, DB_PATH, UID, PWD, server=SERVER)
    client.SetDSN(dsn)
    client.EnableSecurity(True)
    client.Open()
    
    client.SetSQL('SELECT * FROM CalibrationData')
    client.ExecuteSQL()
    rows = client.cursor.fetchall()

    import pprint
    pprint.pprint(rows)
    
    client.Close()
    
#-------------------------------------------------------------------
def Test3():
    UID = 'bench'
    PWD = 'bench'
    SERVER = 'seadc04'
    DRIVER = 'SQL Native Client'
    DSN = 'Trusted_Connection=no'
    DB_PATH = 'BenchData'

    client = Client()
    client.EnableSecurity(True)
    dsn = client.CreateDSN(DSN, DRIVER, DB_PATH, UID, PWD, server=SERVER)
    client.SetDSN(dsn)
    client.EnableSecurity(True)
    client.Open()
    
    client.SetSQL("""USE BenchData
INSERT INTO CalibrationData([SERIAL_NUMBER], [V_Q3_1], [V_Q3_2], [V_Q3_3], [V_Q1_1], [V_Q1_2], [V_Q1_3], [K_Q3_1], [K_Q3_2], [K_Q3_3], [K_Q1_1], [K_Q1_2], [K_Q1_3], [U_K], [REF_K_Q3], [REF_K_Q1], [TEST_TIME_Q3], [TEST_TIME_Q1], [FSADC], [ZRADC], [DATE_TIME], [PASS])
VALUES('03123893','1000.0','1000.0','1000.0','100.0','100.0','100.0','1.01','1.02','1.03','0.97','0.98','0.99','0.3','100.0','10.0','60.0','120.0','1234.0','0.01','07-21-1990','1')""")
    client.ExecuteSQL()
    client.Commit()
    client.Close()

#-------------------------------------------------------------------
def Test4():
    UID = 'bench'
    PWD = 'bench'
    SERVER = 'seadc04'
    DRIVER = 'SQL Native Client'
    DSN = 'Trusted_Connection=no'
    DB_PATH = 'BenchData'

    client = Client()
    client.EnableSecurity(True)
    dsn = client.CreateDSN(DSN, DRIVER, DB_PATH, UID, PWD, server=SERVER)
    client.SetDSN(dsn)
    client.EnableSecurity(True)
    client.Open()
    
    client.SetSQL("""SELECT * FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'CalibrationData')""")
    client.ExecuteSQL()
    print client.cursor.fetchall()
    client.Commit()
    client.Close()

#-------------------------------------------------------------------
def Test5():
    UID = 'bench'
    PWD = 'bench'
    SERVER = 'seadc04'
    DRIVER = 'SQL Native Client'
    DSN = 'Trusted_Connection=no'
    DB_PATH = 'BenchData'

    client = Client()
    client.EnableSecurity(True)
    dsn = client.CreateDSN(DSN, DRIVER, DB_PATH, UID, PWD, server=SERVER)
    client.SetDSN(dsn)
    client.EnableSecurity(True)
    client.Open()
    
    client.SetSQL('SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = CalibrationData')
    client.ExecuteSQL()
    rows = client.cursor.fetchall()

    import pprint
    pprint.pprint(rows)
    
    client.Close()
    
##Test5()
    
