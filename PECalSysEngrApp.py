#----------------------------------------------------------------------
# PE Calibration System HMI Program
''' author: Jeff Peery '''
# date: 11/29/2007
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------

'''
    NOTES:

    This wxApp is a subclass of the PECalSysApp (i.e., its methods and
    attributes and properties are inherited from the PECalSysApp). This
    wxApp is intended for ENGINEERING purposes only.

'''
#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''

    1   08/06/08    JTP     (1) Initial Release

'''
#----------------------------------------------------------------------
# Modules
#----------------------------------------------------------------------
import wx
import Modules.myOPC as myOPC
import time
import EngineeringDirectoryFrame
import CalibrationFrame
import PECalSysApp
import Modules.myDatabase as myDatabase
import Modules.myUtil as myUtil
import Modules.myThermal as myThermal
from Modules.myHeader import *

#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------
def main():
    application = PECalSysApp.PECalSysApp(0)
    print "Loading GUI..."
    application.directory = EngineeringDirectoryFrame.Frame(None, application)
    application.directory.Show()
    application.SetTopWindow(application.directory)
    application.MainLoop()

if __name__ == '__main__':
    main()

