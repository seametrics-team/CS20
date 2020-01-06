import myFlowMeters as fm
import myHeader

t = fm.TURBINE_REV_A()

isok = t.SerialConnect(myHeader.MUT_SERIAL_PORT)
if isok == None:
    print 'Unable to open serial port %d'%myHeader.MUT_SERIAL_PORT
elif isok == False:
    print 'MUT serial connection is not open.'
t.SetSerialReadyState()
print t.ReadFSCount()
t.SerialDisconnect()
