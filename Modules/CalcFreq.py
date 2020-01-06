#-------------------------------------------------------------------------
# Modules
#-------------------------------------------------------------------------
import myFlowMeters

meter = myFlowMeters.PE102_REV_J()
meters = [meter.SetIdentity075, meter.SetIdentity075_270, meter.SetIdentity075_277, \
          meter.SetIdentity038, meter.SetIdentity038_270, meter.SetIdentity038_277]
for m in meters:
    m()
    
    print ''
    print 'meter type:', meter.GetLabel()
    print 'test kfactor:', meter.GetTestKFactor()
    print 'kfactor:', meter.GetKFactor()
    print 'max flowrate:', meter.GetMaxFlowRate()
    print 'FS freq:', meter.GetFSFreq()
    print 'FS freq (reverse float):', meter.ReadString(meter.GetFSFreq())
    

