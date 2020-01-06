#----------------------------------------------------------------------
# Uncertainty Module For PE Calibration System
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
# MODULES
#-------------------------------------------------------
import numpy
from myHeader import *

#-------------------------------------------------------
# METHODS
#-------------------------------------------------------
"""
GET UNCERTAINTY:
Returns the % measurement uncertainty for k-factor
flow rate, and volume measurments (see 'A Measurement Assurance Program for
# Flow Calibration by the Transfer Method' in PE Cal Sys binder for
uncertainty analysis). Input units are metric. Outputs are %.
"""
def GetUncertainty(temp_change, test_time, storage_volume,
                   ref_volume, pulse_count, u_ref, u_storage_volume):
##    print temp_change, 'temp change'
##    print test_time, 'test time'
##    print storage_volume, 'storage volume'
##    print ref_volume, 'ref volume'
##    print pulse_count, 'pulse count'
##    print u_ref, 'u ref'
##    print u_storage_volume, 'u_storage_volume'
    
    # partials of volume water seen by MUT
    dV_da_s     = -(temp_change*storage_volume)
    dV_ddelT_s  = -(CTE_SS*storage_volume + 3*CTE_W*storage_volume)
    dV_dV_s     = -(CTE_SS*temp_change + 3*CTE_W*temp_change)
    dV_da_w     = -(3*temp_change*storage_volume)
    dV_dV_r     = -1.0
    # partials of flow rate seen by MUT
    dQ_dV_mut   = 1.0/test_time
    dQ_dt       = -ref_volume/test_time**2
    # partials of K-factor for MUT
    dK_dpulses  = 1.0/ref_volume
    dK_dV_mut   = -pulse_count/ref_volume**2
    # uncertainties of measurements
    u_V         = numpy.sqrt((dV_da_s*U_CTE_SS)**2 +
                             (dV_ddelT_s*U_TEMP)**2 +
                             (dV_dV_s*u_storage_volume)**2 +
                             (dV_da_w*U_CTE_W)**2 +
                             (dV_dV_r*u_ref)**2)
    u_Q         = numpy.sqrt((dQ_dt*U_TIME)**2 +
                             (dQ_dV_mut*u_V)**2)
    u_K         = numpy.sqrt((dK_dpulses*U_PULSE_COUNT)**2 +
                             (dK_dV_mut*u_V)**2)

    return 100.0*u_V*COVERAGE_FACTOR/ref_volume, 100.0*COVERAGE_FACTOR*u_Q/(ref_volume/test_time), 100.0*u_K*COVERAGE_FACTOR*ref_volume/pulse_count
    

