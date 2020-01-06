#----------------------------------------------------------------------
# Message Mini Frame
''' author: Jeff Peery '''
# date: 10/26/2011
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------

#-------------------------------------------------------------------------
# MODULES
#-------------------------------------------------------------------------
import wx
import myHeader as myHeader

CTRL_HEIGHT = 35

#-------------------------------------------------------------------------
# Main Thread
#-------------------------------------------------------------------------
class Frame(wx.MiniFrame):
    def __init__(self, parent, msg):
        #----------------------------------
        # GUI Ctrl Definitions
        #----------------------------------
        if parent == None:
            wx.MiniFrame.__init__(self, parent=parent, size=wx.Size(450, 200),
                                  style=wx.THICK_FRAME | wx.STAY_ON_TOP, title='Message')
        else:
            wx.MiniFrame.__init__(self, parent=parent, size=wx.Size(400,200),
                              style=wx.ICON_INFORMATION | wx.THICK_FRAME | wx.FRAME_FLOAT_ON_PARENT | wx.STAY_ON_TOP, title='Message')
        self.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD,False, 'Tahoma'))
        
        self.panel = wx.Panel(parent=self, size=wx.Size(166, 350))
        self.ok_button = wx.Button(parent=self.panel, label='OK', size=wx.Size(myHeader.CTRL_WIDTH,  CTRL_HEIGHT))
        self.label = wx.StaticText(parent=self.panel, size=wx.Size(myHeader.CTRL_WIDTH,  CTRL_HEIGHT), style=0)
        
        #----------------------------------
        # GUI Sizers
        #----------------------------------
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.button_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.sizer.Add(self.label, 1, border=5, flag = wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add(self.button_sizer, 0, border=0)
        w = (self.GetSize()[0] - self.ok_button.GetSize()[0])/2.0
        self.button_sizer.AddSpacer((w,25), 1)
        self.button_sizer.Add(self.ok_button, 0, border=myHeader.CTRL_SPACING, flag=wx.ALL)
        self.button_sizer.AddSpacer((w,25), 1)
        
        self.panel.SetSizer(self.sizer)

        #----------------------------------
        # GUI Setup
        #----------------------------------
        self.label.SetLabel(msg)
        self.sizer.Layout()
        self.panel.Layout()
        self.CenterOnScreen()
        
        # twiddle size to layout ctrls
        s = self.GetSize()
        self.SetSize(wx.Size(s[0]+1, s[1]+1))
        self.SetSize(wx.Size(s[0], s[1]))
        
        #----------------------------------
        # Event Definitions
        #----------------------------------
        self.ok_button.Bind(wx.EVT_BUTTON, self.OnOkButton)

    #----------------------------------
    # Events
    #----------------------------------
    def OnOkButton(self, evt):
        self.Destroy()
        
    def SetLabel(self, msg):
        assert type(msg) == str or type(msg) == unicode
        self.label.SetLabel(msg)
        self.label.Layout()

##class App(wx.App):
##    def OnInit(self):
##        wx.InitAllImageHandlers()
##        return True
##
##def main():
##    app = App(0)
##    success = [True, True, False, True]
##    msg = 'Calibration Process Complete.\n\n'
##    for i in range(len(success)):
##        msg += 'Meter %d: %s\n'%(i+1, ['FAIL', 'PASS'][success[i]]) 
##    frame = Frame(None, msg)
##    frame.Show()
##    app.MainLoop()
##    
##if __name__ == '__main__':
##    main()
