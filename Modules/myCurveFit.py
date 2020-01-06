#----------------------------------------------------------------------
# myCurveFit module
# Author: Steve Nguyen
# Date: 12/12/2016
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''
  1.0   2016/12/12  SPN     -Initial release
'''

import numpy

def GetCorrectionFactor(self, poly_coef, flow_rate):
    curvefit_poly = numpy.poly1d(poly_coef)
    curvefit_error = curvefit_poly(flow_rate)
    curvefit_correction = 1 - curvefit_error/100

    print 'curve fit % error', curvefit_error
    print 'curve fit currection factor', curvefit_correction

    return curvefit_correction
