#----------------------------------------------------------------------
# PE Calibration System HMI Program- Verification on Demand
''' author: Steve Nguyen '''
# date: 10/02/2013
# email: Steven@seametrics.com
#----------------------------------------------------------------------

'''
    NOTES:

    This wxApp is a subclass of the PECalSysApp (i.e., its methods and
    attributes and properties are inherited from the PECalSysApp). This
    wxApp is intended for VERIFICATION purposes only.

'''
#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''

    1   2013/10/02  JTP     (1) Initial Release

'''
#----------------------------------------------------------------------
# Modules
#----------------------------------------------------------------------
import wx
import VerificationDirectoryFrame
import PECalSysApp

#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------
def main():       
    application = PECalSysApp.PECalSysApp(0)    
    print "Loading GUI..."
    application.directory = VerificationDirectoryFrame.Frame(None, application)
    application.directory.Show()
    application.SetTopWindow(application.directory)
    application.MainLoop()

if __name__ == '__main__':
    main()


