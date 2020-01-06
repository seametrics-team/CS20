#----------------------------------------------------------------------
# Keypad Module
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
import wx
import sys
print sys.path, 'hello'

from Modules.myHeader import *

class Keypad(wx.Dialog):
    def __init__(self, parent, label):
        #----------------------------------
        # Attributes
        #----------------------------------
        #----------------------------------
        # GUI Ctrl Id's
        #----------------------------------
        BUTTON_ZERO_ID      = wx.NewId()
        BUTTON_ONE_ID       = wx.NewId()
        BUTTON_TWO_ID       = wx.NewId()
        BUTTON_THREE_ID     = wx.NewId()
        BUTTON_FOUR_ID      = wx.NewId()
        BUTTON_FIVE_ID      = wx.NewId()
        BUTTON_SIX_ID       = wx.NewId()
        BUTTON_SEVEN_ID     = wx.NewId()
        BUTTON_EIGHT_ID     = wx.NewId()
        BUTTON_NINE_ID      = wx.NewId()
        ENTER_BUTTON_ID     = wx.NewId()
        DEL_BUTTON_ID       = wx.NewId()
        TEXTCTRL_ID         = wx.NewId()
        PANEL_ID            = wx.NewId()
        DIALOG_ID           = wx.NewId()
        TEXT_ID             = wx.NewId()
        #----------------------------------
        # GUI Ctrl Definitions
        #----------------------------------
        wx.Dialog.__init__(self, id=DIALOG_ID, parent=parent, style=wx.STAY_ON_TOP|wx.DEFAULT_FRAME_STYLE, name=label)
        self.SetIcon(wx.Icon('Images\\horse.ico', wx.BITMAP_TYPE_ICO))
        self.panel = wx.Panel(id=PANEL_ID, name='panel', parent=self, size=wx.Size(166, 290),
                              style=wx.TAB_TRAVERSAL)
        self.panel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.text = wx.StaticText(id=TEXT_ID, parent=self.panel, label=label, size=wx.Size(100, 25))
        self.text.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD, False,'MS Shell Dlg 2'))

        self.textCtrl = wx.TextCtrl(id=TEXTCTRL_ID, parent=self.panel, size=wx.Size(100, 25),
                                    style=wx.TE_NO_VSCROLL | wx.TE_MULTILINE | wx.TE_RICH2)
        self.textCtrl.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))
                                      
        self.button_zero = wx.Button(id=BUTTON_ZERO_ID, label='0', parent=self.panel, size=wx.Size(KEYPAD_BUTTON_WIDTH, KEYPAD_BUTTON_HEIGHT))
        self.button_zero.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.button_one = wx.Button(id=BUTTON_ONE_ID, label='1', parent=self.panel, size=wx.Size(KEYPAD_BUTTON_WIDTH, KEYPAD_BUTTON_HEIGHT))
        self.button_one.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.button_two = wx.Button(id=BUTTON_TWO_ID, label='2', parent=self.panel, size=wx.Size(KEYPAD_BUTTON_WIDTH, KEYPAD_BUTTON_HEIGHT))
        self.button_two.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.button_three = wx.Button(id=BUTTON_THREE_ID, label='3', parent=self.panel, size=wx.Size(KEYPAD_BUTTON_WIDTH, KEYPAD_BUTTON_HEIGHT))
        self.button_three.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.button_four = wx.Button(id=BUTTON_FOUR_ID, label='4', parent=self.panel, size=wx.Size(KEYPAD_BUTTON_WIDTH, KEYPAD_BUTTON_HEIGHT))
        self.button_four.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.button_five = wx.Button(id=BUTTON_FIVE_ID, label='5', parent=self.panel, size=wx.Size(KEYPAD_BUTTON_WIDTH, KEYPAD_BUTTON_HEIGHT))
        self.button_five.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.button_six = wx.Button(id=BUTTON_SIX_ID, label='6', parent=self.panel, size=wx.Size(KEYPAD_BUTTON_WIDTH, KEYPAD_BUTTON_HEIGHT))
        self.button_six.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.button_seven = wx.Button(id=BUTTON_SEVEN_ID, label='7', parent=self.panel, size=wx.Size(KEYPAD_BUTTON_WIDTH, KEYPAD_BUTTON_HEIGHT))
        self.button_seven.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.button_eight = wx.Button(id=BUTTON_EIGHT_ID, label='8', parent=self.panel, size=wx.Size(KEYPAD_BUTTON_WIDTH, KEYPAD_BUTTON_HEIGHT))
        self.button_eight.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.button_nine = wx.Button(id=BUTTON_NINE_ID, label='9', parent=self.panel, size=wx.Size(KEYPAD_BUTTON_WIDTH, KEYPAD_BUTTON_HEIGHT))
        self.button_nine.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.enter_button = wx.Button(id=ENTER_BUTTON_ID, label='Ent', parent=self.panel, size=wx.Size(KEYPAD_BUTTON_WIDTH, KEYPAD_BUTTON_HEIGHT))
        self.enter_button.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))
        self.enter_button.SetForegroundColour(wx.GREEN)

        self.del_button = wx.Button(id=DEL_BUTTON_ID, label='Del', parent=self.panel, size=wx.Size(KEYPAD_BUTTON_WIDTH, KEYPAD_BUTTON_HEIGHT))
        self.del_button.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        #----------------------------------
        # GUI Sizers
        #----------------------------------
        '''Sizer layout'''
        # frame
        # Panel
        # |------------------------------------------|
        # | static text                             0|
        # | textbox                                  |
        # | |---------------------------------------||
        # | |  |---------||----------||----------| 1||
        # | |  |        2||         3||         4|  ||
        # | |  |seven    ||eight     ||nine      |  ||
        # | |  |four     ||five      ||six       |  ||  
        # | |  |one      ||two       ||three     |  ||  
        # | |  |zero     ||del       ||enter     |  || 
        # | |  |---------||----------||----------|  ||
        # | |---------------------------------------||
        # |                                          |
        # |------------------------------------------|
        # status bar
        #
        self.boxSizer0 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.boxSizer2 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer3 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer4 = wx.BoxSizer(orient=wx.VERTICAL)
        
        self.boxSizer1.Add(self.boxSizer2, 0, border=0, flag=wx.EXPAND|wx.ALL)
        self.boxSizer1.Add(self.boxSizer3, 0, border=0, flag=wx.EXPAND|wx.ALL)
        self.boxSizer1.Add(self.boxSizer4, 0, border=0, flag=wx.EXPAND|wx.ALL)
        
        self.boxSizer2.Add(self.button_seven, 0, border=1, flag=wx.EXPAND|wx.ALL)
        self.boxSizer2.Add(self.button_four, 0, border=1, flag=wx.EXPAND|wx.ALL)
        self.boxSizer2.Add(self.button_one, 0, border=1, flag=wx.EXPAND|wx.ALL)
        self.boxSizer2.Add(self.button_zero, 0, border=1, flag=wx.EXPAND|wx.ALL)

        self.boxSizer3.Add(self.button_eight, 0, border=1, flag=wx.EXPAND|wx.ALL)
        self.boxSizer3.Add(self.button_five, 0, border=1, flag=wx.EXPAND|wx.ALL)
        self.boxSizer3.Add(self.button_two, 0, border=1, flag=wx.EXPAND|wx.ALL)
        self.boxSizer3.Add(self.del_button, 0, border=1, flag=wx.EXPAND|wx.ALL)
        
        self.boxSizer4.Add(self.button_nine, 0, border=1, flag=wx.EXPAND|wx.ALL)
        self.boxSizer4.Add(self.button_six, 0, border=1, flag=wx.EXPAND|wx.ALL)
        self.boxSizer4.Add(self.button_three, 0, border=1, flag=wx.EXPAND|wx.ALL)
        self.boxSizer4.Add(self.enter_button, 0, border=1, flag=wx.EXPAND|wx.ALL)


        self.boxSizer0.Add(self.text, 0, border=6, flag=wx.EXPAND|wx.ALL)
        self.boxSizer0.Add(self.textCtrl, 0, border=6, flag=wx.EXPAND|wx.ALL)
        self.boxSizer0.Add(self.boxSizer1, 1, border=5, flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTER)

        self.panel.SetSizer(self.boxSizer0)
        #----------------------------------
        # Event Definitions
        #----------------------------------
        self.button_zero.Bind(wx.EVT_BUTTON, self.OnButton0)
        self.button_one.Bind(wx.EVT_BUTTON, self.OnButton1)
        self.button_two.Bind(wx.EVT_BUTTON, self.OnButton2)
        self.button_three.Bind(wx.EVT_BUTTON, self.OnButton3)
        self.button_four.Bind(wx.EVT_BUTTON, self.OnButton4)
        self.button_five.Bind(wx.EVT_BUTTON, self.OnButton5)
        self.button_six.Bind(wx.EVT_BUTTON, self.OnButton6)
        self.button_seven.Bind(wx.EVT_BUTTON, self.OnButton7)
        self.button_eight.Bind(wx.EVT_BUTTON, self.OnButton8)
        self.button_nine.Bind(wx.EVT_BUTTON, self.OnButton9)
        self.enter_button.Bind(wx.EVT_BUTTON, self.OnEnterButton)
        self.del_button.Bind(wx.EVT_BUTTON, self.OnDelButton)
##        self.textCtrl.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
        #----------------------------------
        # GUI Setup
        #----------------------------------
##        self.SetLabel(label)
        self.SetClientSize(self.panel.GetSize())
        self.panel.Layout()
        self.CenterOnScreen()
        
    def OnButton0(self, event):
        self.textCtrl.SetValue(self.textCtrl.GetValue()+'0')

    def OnButton1(self, event):
        self.textCtrl.SetValue(self.textCtrl.GetValue()+'1')

    def OnButton2(self, event):
        self.textCtrl.SetValue(self.textCtrl.GetValue()+'2')

    def OnButton3(self, event):
        self.textCtrl.SetValue(self.textCtrl.GetValue()+'3')

    def OnButton4(self, event):
        self.textCtrl.SetValue(self.textCtrl.GetValue()+'4')

    def OnButton5(self, event):
        self.textCtrl.SetValue(self.textCtrl.GetValue()+'5')

    def OnButton6(self, event):
        self.textCtrl.SetValue(self.textCtrl.GetValue()+'6')

    def OnButton7(self, event):
        self.textCtrl.SetValue(self.textCtrl.GetValue()+'7')

    def OnButton8(self, event):
        self.textCtrl.SetValue(self.textCtrl.GetValue()+'8')

    def OnButton9(self, event):
        self.textCtrl.SetValue(self.textCtrl.GetValue()+'9')

    def OnDelButton(self, event):
        self.textCtrl.SetValue(self.textCtrl.GetValue()[0:-1])

    def OnEnterButton(self, event):
        s = self.textCtrl.GetValue().strip('\n')
        self.textCtrl.SetValue(s)
        self.EndModal(wx.ID_OK)
        
##    # this event doesn't work well
##    def OnTextEnter(self, event):
##        self.EndModal(wx.ID_OK)
    
    def GetValue(self):
        return self.textCtrl.GetValue()
