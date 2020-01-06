#----------------------------------------------------------------------
# PE Calibration System HMI Program
''' author: Jeff Peery '''
# date: 11/29/2007
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------

#-------------------------------------------------------------------------
# Modules
#-------------------------------------------------------------------------
import wx

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------

#-------------------------------------------------------------------------
# Main Thread
#-------------------------------------------------------------------------
class Frame(wx.MiniFrame):
    def __init__(self, parent, msg):
        #----------------------------------
        # GUI Ctrl Id's
        #----------------------------------
        FRAME_ID    = wx.NewId()
        THROB_ID    = wx.NewId()
        TEXT_ID     = wx.NewId() 
        PANEL_ID    = wx.NewId() 

        #----------------------------------
        # GUI Ctrl Definitions
        #----------------------------------
        if parent == None:
            wx.MiniFrame.__init__(self, id=FRAME_ID, name='', parent=parent,
                                  pos=wx.Point(500, 301), size=wx.Size(400, 275),
                                  style=wx.THICK_FRAME | wx.STAY_ON_TOP, title='MiniFrame1')
        else:
            wx.MiniFrame.__init__(self, id=FRAME_ID, parent=parent,
                              pos=wx.Point(500, 301), size=wx.Size(300, 250),
                              style=wx.THICK_FRAME | wx.FRAME_FLOAT_ON_PARENT | wx.STAY_ON_TOP)
            
        self.panel = wx.Panel(id=PANEL_ID, parent=self, size=wx.Size(166, 350))
        self.label = wx.StaticText(id=TEXT_ID,label=msg, parent=self.panel,size=wx.Size(350, 25), style=wx.ALIGN_CENTER_VERTICAL|wx.ST_NO_AUTORESIZE)
        self.label.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD,False, 'Tahoma'))
        
        #----------------------------------
        # GUI Sizers
        #----------------------------------
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)        
        self.sizer.Add(self.label, 1, border=5, flag = wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
        self.panel.SetSizer(self.sizer)
        self.sizer.Fit(self)

        #----------------------------------
        # GUI Setup
        #----------------------------------
        self.sizer.Layout()
        self.CenterOnScreen()
        
    def SetLabel(self, msg):
        assert type(msg) == str or type(msg) == unicode
        self.label.SetLabel(msg)
        self.label.Layout()
