#----------------------------------------------------------------------
# Thermal Module For PE Calibration System
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

    1   2/19/08    JTP     -   Initial Release
    
'''

#-------------------------------------------------------
# modules
#-------------------------------------------------------
import numpy
from myHeader import *

#-------------------------------------------------------
# Volume of water as seen by MUT if MUT is
# UPSTREAM of reference. here we are correcting the
# reference volume. (see 'A Measurement Assurance Program for
# Flow Calibration by the Transfer Method') located
# in the PE Cal Sys Binder.
#
# note that the temp_change must be (start temp - end temp).
# it should **NOT** be (end temp - start temp), this would
# result in an incorrect themal correction.
#-------------------------------------------------------
def GetVolume1(temp_change, ref_volume, storage_volume):
    """Returns the volume of water as seen by MUT, given
    volume of water seen by reference meter and a temperature change"""
##    print storage_volume, 'storage volume'
##    print temp_change, 'temp change'
##    print (CTE_SS*temp_change*storage_volume + 3*CTE_W*temp_change*storage_volume)
##    print ref_volume
    V = ref_volume + (CTE_SS*temp_change*storage_volume + 3*CTE_W*temp_change*storage_volume)
    return V

#-------------------------------------------------------
# Volume of water as seen by MUT if MUT is
# DOWNSTREAM of reference. here we are correcting the
# reference volume. (see 'A Measurement Assurance Program for
# Flow Calibration by the Transfer Method') located
# in the PE Cal Sys Binder.
#
# note that the temp_change must be (start temp - end temp).
# it should **NOT** be (end temp - start temp), this would
# result in an incorrect themal correction.
#-------------------------------------------------------
def GetVolume2(temp_change, ref_volume, storage_volume):
    """Returns the volume of water as seen by MUT, given
    volume of water seen by reference meter and a temperature change"""
##    print storage_volume, 'storage volume'
##    print temp_change, 'temp change'
##    print (CTE_SS*temp_change*storage_volume + 3*CTE_W*temp_change*storage_volume)
##    print ref_volume
    V = ref_volume - (CTE_SS*temp_change*storage_volume + 3*CTE_W*temp_change*storage_volume)
    return V

def DigitalToTemp(count, b0, b1, b2, b3):
    """Return conversion from digital PLC input to temperature"""
    # voltage measured across thermistor
    Vo = count*5.0/65535.0
    # Thermistor resistance
    Rt = Vo*THERMAL_R1*THERMAL_R3/(THERMAL_V_S*(THERMAL_R2+THERMAL_R3))
    # Temperature
    N   = b0 + b1*numpy.log(Rt) + b2*numpy.log(Rt)**2 + b3*numpy.log(Rt)**3
    T   = 1.0/N
    return T - 273.15


def TestTemp():
    measured2 = 65534
    measured3 = 65534
    measured4 = 65534
    print 'Temp 2: %0.2f (C)'%DigitalToTemp(measured2,
                                            THERMAL_2_B0,
                                            THERMAL_2_B1,
                                            THERMAL_2_B2,
                                            THERMAL_2_B3)

    print 'Temp 3: %0.2f (C)'%DigitalToTemp(measured3,
                                            THERMAL_3_B0,
                                            THERMAL_3_B1,
                                            THERMAL_3_B2,
                                            THERMAL_3_B3)

    print 'Temp 4: %0.2f (C)'%DigitalToTemp(measured4,
                                            THERMAL_4_B0,
                                            THERMAL_4_B1,
                                            THERMAL_4_B2,
                                            THERMAL_4_B3)

