#----------------------------------------------------------------------
# Serial Communication Module
''' author: Jeff Peery '''
# date: 2/1/2008
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------


# Revision Log
#
# Rev   Date            Author  Description    
#----------------------------------------------------------------------
'''

    1   02/01/2008      JTP     -   Initial Release
    2   12/12/2008      JTP     -   Include InWaiting() method
    
'''

#----------------------------------------------------------------------
# Modules
#----------------------------------------------------------------------
import serial
import time
#----------------------------------------------------------------------
# Methods
#----------------------------------------------------------------------
def PrintAvailablePorts():
    "scan for available ports. return a list of strings"
    for i in range(256):
        try:
            s = serial.Serial(i)
            print i, s.portstr
            s.close()   #explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass

def GetAvailablePortStrings():
    "scan for available ports. return a list of strings"
    ports = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            ports.append(s.portstr)
            s.close()   #explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return ports

def GetAvailablePortNums():
    "scan for available ports. return a list of integers"
    ports = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            ports.append(i)
            s.close()   #explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return ports

#----------------------------------------------------------------------
# Classes
#----------------------------------------------------------------------               
class mySerial:
    def __init__(self, port, baud_rate, byte_size, parity, stop_bits, time_out):
        assert type(stop_bits) == int
        assert type(port) == int
        assert type(byte_size) == int
        assert type(baud_rate) == int
        assert type(time_out) in [int, float]
        
        # serial connection
        self.ser = None
        # serial port 
        self.port = port
        # serial baud rate
        self.baud_rate = baud_rate
        # byte size
        self.byte_size = byte_size
        # parity
        self.parity = parity
        # stop bits
        self.stop_bits = stop_bits
        # time out
        self.time_out = time_out

    #--------------------------------------
    # General Serial Communication Methods
    #--------------------------------------
    def PrintAvailablePorts(self):
        return PrintAvailablePorts()
    
    def GetAvailablePortStrings(self):
        return GetAvailablePortStrings()
    
    def GetAvailablePortNums(self):
        return GetAvailablePortNums()
    
    def SetPort(self, port):
        assert port in range(256)
        self.port = port

    def ReadLine(self):
        "read one line"
        assert self.ser.isOpen()
        return self.ser.readline()

    def WriteThenRead(self, value, length):
        "write string, Returns response string of length length"
        assert self.ser != None, "Serial object must not be NoneType"
        assert self.ser.isOpen()
        assert type(length) == int
        assert type(value) == str
        self.Write(value)
        return self.Read(length)        
        
    def Write(self, value):
        "Write string"
        assert self.ser != None, "Serial object must not be NoneType"
        assert self.ser.isOpen()
        assert type(value) == str
        self.ser.write(value)
        
    def Read(self, length):
        "Get string of length length"
        assert self.ser != None, "Serial object must not be NoneType"
        assert self.ser.isOpen()
        assert type(length) == int
        return self.ser.read(length)

    def Open(self):
        "Open connection"
        try:
            s = serial.Serial(self.port, self.baud_rate, bytesize=self.byte_size,
                               parity=self.parity, timeout=self.time_out, stopbits=self.stop_bits)
        except:
            s = None            
        self.ser = s
        
    def Close(self):
        "Close connection"
        try:
            self.ser.close()
            return True
        except:
            return False

    def IsOpen(self):
        "Test for open connection"
        if self.ser == None: return False
        else: return self.ser.isOpen()

    def FlushInput(self):
        if self.ser != None:
            self.ser.flushInput()

    def FlushOutput(self):
        if self.ser != None:
            self.ser.flushOutput()

    def InWaiting(self):
        assert self.ser != None
        return int(self.ser.inWaiting())
            
##def GetString(myFloat):
##    import numpy
##    "Format input into appropriate form for floating point input"
##    # set decimal precision  
##    myString = '%0.6f'%myFloat
##    if numpy.absolute(myFloat) > 9.999999: myString = '%0.5f'%myFloat 
##    if numpy.absolute(myFloat) > 99.99999: myString = '%0.4f'%myFloat      
##    if numpy.absolute(myFloat) > 999.9999: myString = '%0.3f'%myFloat
##    if numpy.absolute(myFloat) > 9999.999: myString = '%0.2f'%myFloat    
##    # if value is negative reduce length by 1 to account for sign
##    if numpy.sign(myFloat) == -1: myString = myString[0:-1]        
##    # start from right side
##    max = len(myString)
##    # meter may only receive 7 digits (not including decimal)
##    s=''
##    for i in range(max): s+=myString[max-i-1]
##    return s

def PrepareCom(s):
    x=''
    s.Write('#')
    time.sleep(0.5)
    if s.InWaiting() >= 2:
        x = s.Read(s.InWaiting())
        print x
        if '!x' in x or '!t' in x or '!o' in x:
            s.FlushInput()
            s.FlushOutput()
            return True
    return False
            
def Test():
    import myHex2Float
    s = mySerial(2, 2400, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, 10)
    s.Open()

##    # prep serial com
##    for i in range(5):
##        if PrepareCom(s):
##            break

    # exe multiple commands
    for j in range(1):
        print 'Query Software Version...'
        s.Write('#')
        time.sleep(0.75)
        s.Write('#')
        time.sleep(0.75)
##        s.Write('#')
##        time.sleep(0.75)
##        s.Write('S$333.335\r')
##        s.Write('e\r')
##        time.sleep(1)
##        print s.Read(s.InWaiting())
        s.Write('A')
        time.sleep(5)
        x = s.Read(s.InWaiting())
        print x
##        print myHex2Float.Hex2Float(x)
##        # prep serial com
##        for i in range(10):
##            if PrepareCom(s):
##                break
        
        s.FlushInput()
        s.FlushOutput()
        
    s.Close()


def Test1():
    s = mySerial(2, 2400, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, 10)
    s.Open()

    s.FlushInput()
    s.FlushOutput()
    s.Write('#')
    time.sleep(0.75)
    s.Write('#')
    time.sleep(0.75)
    s.Write('#')
    time.sleep(0.75)
##    s.Write('S$0.6601\r')
##    s.Write('C$00100.0\r')
    s.Write('e\r')
    
    for i in range(40):
        time.sleep(0.25)
        if s.InWaiting():
            print s.Read(s.InWaiting())
            break

    s.Close()



##Test1()
##Test()
