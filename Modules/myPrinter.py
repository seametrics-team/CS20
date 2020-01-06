#----------------------------------------------------------------------
# HTML Printing Module
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
from wx.html import HtmlEasyPrinting
import wx
from win32com.client import Dispatch
import win32com
from time import sleep

class Printer(HtmlEasyPrinting):
    def __init__(self):
        HtmlEasyPrinting.__init__(self)
        self.SetupMargins()
        
    def GetHtmlText(self,text):
        "Simple conversion of text."
        html_text = text.replace('\n\n','<P>')
        html_text = text.replace('\n', '<BR>')
        return html_text

    def PrintText(self, text, doc_name):
        self.SetHeader(doc_name)
        self.PrintText(self.GetHtmlText(text),doc_name)

    def SetupMargins(self):
        page_setup_object = self.GetPageSetupData()
        page_setup_object.SetMarginTopLeft(wx.Point(5,12))
        page_setup_object.SetMarginBottomRight(wx.Point(5,12))
        
    def Print(self, doc_name): 
        ie = win32com.client.Dispatch("InternetExplorer.Application")
        ie.Visible = 0
        ie.Navigate(doc_name)

        # wait for ie to open before printing
        i=0
        while 1:
            if i>30: break
            sleep(0.1)
            wx.Yield()
            i+=1
        # wait if ie busy
        i=0
        while ie.Busy:
            if i>60: break
            sleep(0.5)
            i+=1
            
        try:
            # print the current IE document without prompting
            # the user for the printerdialog
            # Attention: use the makepy.py utility on the "Microsoft Internet Controls (1.1)" object library
            # to get early binding !!! Otherwise you cannot print !
            ie.ExecWB(win32com.client.constants.OLECMDID_PRINT, win32com.client.constants.OLECMDEXECOPT_DONTPROMPTUSER)
            # use call later here to allow time to print
            wx.CallLater(30000, ie.Quit)
            return True
        except:
            ie.Quit
            return False

        
    def PreviewText(self, text, doc_name):
        self.SetHeader(doc_name)
        HtmlEasyPrinting.PreviewText(self, self.GetHtmlText(text))

def PrintTest():
    ie = win32com.client.Dispatch("InternetExplorer.Application")
    ie.Visible = 0
    doc_name = 's:\\Calibration Bench\\CS20\\Bench Data\\PE\Calibration Reports\\00000001.htm'
    ie.Navigate(doc_name)
    if ie.Busy:
       sleep(2)
    # print the current IE document without prompting the user for the printerdialog
    ie.ExecWB(win32com.client.constants.OLECMDID_PRINT, win32com.client.constants.OLECMDEXECOPT_DONTPROMPTUSER)

##PrintTest()
