#----------------------------------------------------------------------
# myString.py
''' author: Jeff Peery '''
# date: 02/28/2008
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------

#-------------------------------------------------------------------------
# Modules
#-------------------------------------------------------------------------
from myHeader import *
import string

def IsNumber(value):
    """Returns True if input string is numerical"""
    try:
        string.atof(value)/2.0
        return True
    except:
        return False

