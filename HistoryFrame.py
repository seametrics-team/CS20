#----------------------------------------------------------------------
# History Program
''' author: Jeff Peery '''
# date: 03/06/2008
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
import string
import numpy
from os.path import exists
import Modules.myDatabase as myDatabase
import Modules.myPlot as myPlot
import Modules.myUtil as myUtil
import Modules.myHTMLReport as myReport
import Modules.myPrinter as myPrinter
import Modules.myFlowMeters as myFlowMeters
from Modules.myHeader import *
from Modules import myDateTime as myDateTime
from matplotlib.dates import date2num, num2date


#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------
class Frame(wx.Frame):
    def __init__(self, parent):
        #----------------------------------
        # GUI Ctrl Id's
        #----------------------------------
        FRAME_ID            = wx.NewId()
        PANEL_ID            = wx.NewId()
        EXIT_BUTTON_ID      = wx.NewId()
        PRINT_BUTTON_ID     = wx.NewId() 
        CHOICE_ID           = wx.NewId() 
        CHOICE2_ID          = wx.NewId()
        CHECKBOX_ID         = wx.NewId()  
        STATUS_BAR_ID       = wx.NewId() 
        TEXT2_ID            = wx.NewId()
        TEXT3_ID            = wx.NewId()
        TEXT_CTRL_ID        = wx.NewId()
        TEXT_CTRL2_ID       = wx.NewId()
        STATIC_BOX1_ID      = wx.NewId()
        STATIC_BOX2_ID      = wx.NewId()
        STATIC_BOX3_ID      = wx.NewId()
        STATIC_BOX4_ID      = wx.NewId()
        STATIC_BOX5_ID      = wx.NewId()
        #----------------------------------
        # GUI Ctrl Definitions
        #----------------------------------
        wx.Frame.__init__(self, id=FRAME_ID, parent=parent,
                              pos=wx.Point(184, 300), size=wx.Size(989, 550),
                              style=wx.FRAME_FLOAT_ON_PARENT)
        self.Maximize() # keep maximize here to reduce flickering on screen

        self.statusBar = wx.StatusBar(id=STATUS_BAR_ID, parent=self, style=wx.ALWAYS_SHOW_SB)
        self.SetStatusBar(self.statusBar)
        
        self.panel = wx.Panel(id=PANEL_ID, parent=self, style=wx.TAB_TRAVERSAL)
        self.panel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.figure1 = myPlot.Figure(self.panel)
        self.figure2 = myPlot.Figure(self.panel)

        self.choice = wx.Choice(id=CHOICE_ID, parent=self.panel, size=wx.Size(100,25), choices=myFlowMeters.METER_LABELS)
        self.choice2 = wx.Choice(id=CHOICE2_ID, parent=self.panel, size=wx.Size(100,25), choices=ALL_VARIABLES)
  
        self.exit_button = wx.Button(id=EXIT_BUTTON_ID, label='Exit', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.exit_button.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))
        self.print_button = wx.Button(id=PRINT_BUTTON_ID, label='Print', parent=self.panel, size=wx.Size(BUTTON_WIDTH, BUTTON_HEIGHT), style=0)
        self.print_button.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.check_box = wx.CheckBox(id=CHECKBOX_ID, label='Use date range', parent=self.panel, size=wx.Size(CHECKBOX_WIDTH, CHECKBOX_HEIGHT), style=0)
            
        self.label2 = wx.StaticText(id=TEXT2_ID,label='From:', parent=self.panel, size=wx.Size(30, STATIC_TEXT_HEIGHT), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.label3 = wx.StaticText(id=TEXT3_ID,label='To:', parent=self.panel, size=wx.Size(30, STATIC_TEXT_HEIGHT), style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)

        self.staticBox1 = wx.StaticBox(id=STATIC_BOX1_ID, label='Histogram', parent=self.panel, size=wx.Size(400, 200), style=0 )
        self.staticBox2 = wx.StaticBox(id=STATIC_BOX2_ID, label='Chronological', parent=self.panel, size=wx.Size(400, 200), style=0 )
        self.staticBox3 = wx.StaticBox(id=STATIC_BOX3_ID, label='Select Meter...', parent=self.panel, size=wx.Size(100, 200), style=0 )
        self.staticBox4 = wx.StaticBox(id=STATIC_BOX4_ID, label='Select Variable...', parent=self.panel, size=wx.Size(100, 200), style=0 )
        self.staticBox5 = wx.StaticBox(id=STATIC_BOX5_ID, label='Date Range', parent=self.panel, size=wx.Size(100, 200), style=0 )

        self.text_ctrl = wx.TextCtrl(parent=self.panel, id=TEXT_CTRL_ID, value='', size = wx.Size(100,TEXT_CTRL_HEIGHT), style = wx.TE_PROCESS_ENTER)
        self.text_ctrl2 = wx.TextCtrl(parent=self.panel, id=TEXT_CTRL2_ID, value='', size = wx.Size(100,TEXT_CTRL_HEIGHT), style = wx.TE_PROCESS_ENTER)
        #----------------------------------
        # GUI Sizers
        #----------------------------------
        '''Sizer layout'''
        # frame
        # Panel
        # ---------------------------------------------------------
        # |   |-------------------|  |-------------------------| 1|
        # |   |                  2|  |                        3|  |
        # |   |choice             |  |                         |  |
        # |   |choice2            |  |                         |  |
        # |   |                   |  |                         |  |
        # |   |print              |  |                         |  |
        # |   |exit               |  |   figure1               |  |
        # |   |check_box          |  |                         |  |
        # |   ||staticbox3-------||  |   figure2               |  |
        # |   ||label2 textctrl  ||  |                         |  |
        # |   ||label3 textctrl2 ||  |                         |  |
        # |   ||-----------------||  |                         |  |
        # |   |-------------------|  |-------------------------|  |
        # ---------------------------------------------------------
        # status bar
        #
        self.boxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.boxSizer2 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer3 = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer5 = wx.StaticBoxSizer(box = self.staticBox1, orient=wx.VERTICAL)
        self.boxSizer6 = wx.StaticBoxSizer(box = self.staticBox2, orient=wx.VERTICAL)
        self.boxSizer7 = wx.StaticBoxSizer(box = self.staticBox3, orient=wx.VERTICAL)
        self.boxSizer8 = wx.StaticBoxSizer(box = self.staticBox4, orient=wx.VERTICAL)
        self.boxSizer9 = wx.StaticBoxSizer(box = self.staticBox5, orient=wx.VERTICAL)
        self.boxSizer10 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.boxSizer11 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizer1.Add(self.boxSizer2, 0, border=10, flag=wx.ALL | wx.RIGHT | wx.EXPAND | wx.ALIGN_TOP )
        self.boxSizer1.Add(self.boxSizer3, 1, border=0, flag=wx.ALL | wx.EXPAND)

        self.boxSizer2.Add(self.print_button, 0, border=20, flag=wx.TOP)
        self.boxSizer2.Add(self.exit_button, 0, border=20, flag=wx.TOP)
        self.boxSizer2.Add(self.boxSizer7, 0, border=20, flag=wx.TOP | wx.EXPAND)
        self.boxSizer2.Add(self.boxSizer8, 0, border=20, flag=wx.TOP | wx.EXPAND)
        self.boxSizer2.Add(self.check_box, 0, border=20, flag=wx.TOP | wx.EXPAND)
        self.boxSizer2.Add(self.boxSizer9, 0, border=20, flag=wx.EXPAND)
        
        self.boxSizer3.Add(self.boxSizer5, 1, border=10, flag=wx.ALL | wx.EXPAND)
        self.boxSizer3.Add(self.boxSizer6, 1, border=10, flag=wx.ALL |wx.EXPAND)

        self.boxSizer5.Add(self.figure1, 1, border=10, flag=wx.ALL | wx.EXPAND)
        self.boxSizer6.Add(self.figure2, 1, border=10, flag=wx.ALL | wx.EXPAND)
        
        self.boxSizer7.Add(self.choice, 0, border=5, flag=wx.ALL | wx.EXPAND )
        self.boxSizer8.Add(self.choice2, 0, border=5, flag=wx.ALL | wx.EXPAND )
        
        self.boxSizer9.Add(self.boxSizer10, 1, border=0, flag=wx.ALL | wx.EXPAND)
        self.boxSizer9.Add(self.boxSizer11, 1, border=0, flag=wx.ALL | wx.EXPAND)
        
        self.boxSizer10.Add(self.label2, 0, border=5, flag=wx.ALL | wx.EXPAND )
        self.boxSizer10.Add(self.text_ctrl, 0, border=5, flag=wx.ALL | wx.EXPAND )

        self.boxSizer11.Add(self.label3, 0, border=5, flag=wx.ALL | wx.EXPAND )
        self.boxSizer11.Add(self.text_ctrl2, 0, border=5, flag=wx.ALL | wx.EXPAND )
        
        self.panel.SetSizer(self.boxSizer1)
        self.panel.Layout()
        
        #----------------------------------
        # Event Definitions
        #----------------------------------
        self.exit_button.Bind(wx.EVT_BUTTON, self.OnExitButton)
        self.print_button.Bind(wx.EVT_BUTTON, self.OnPrintButton)
        self.choice.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.choice2.Bind(wx.EVT_CHOICE, self.OnChoice2)
        self.check_box.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)
        self.text_ctrl.Bind(wx.EVT_TEXT_ENTER, self.OnTextCtrl)
        self.text_ctrl2.Bind(wx.EVT_TEXT_ENTER, self.OnTextCtrl2)
        self.Bind(wx.EVT_CLOSE, self.OnExitButton)
        #----------------------------------
        # Attributes
        #----------------------------------
        # database instance
        # use call later here to allow the page
        # to show up before loading data
        wx.CallLater(500, self.GetDb)
        # items selected from database
        self.db_items = []
        # a print object for printing reports
        self.print_obj = myPrinter.Printer()
        # variable selected to plot
        self.var_label = None
        # meter selected to plot
        self.meter_label = None
        #----------------------------------
        # GUI Ctrl Initializations
        #----------------------------------
        self.print_button.Enable(False)
        self.choice2.Enable(False)
        self.choice.Enable(False)
        self.check_box.Enable(False)
        self.exit_button.SetForegroundColour(wx.Colour(250, 0, 0))
        self.print_button.SetForegroundColour(wx.Colour(0, 0, 250))
        self.check_box.SetValue(False)
        self.label2.Enable(False)
        self.label3.Enable(False)
        self.text_ctrl.Enable(False)
        self.text_ctrl2.Enable(False)
        self.InitializePlot()
        
    #----------------------------------
    # Event Handler Methods
    #----------------------------------
    def OnOPCDataChange(self, evt):
        """
        Event handler for OPC Data Change events
        """
        # do nothing
        pass
    
    def OnExitButton(self, event):
        """
        Frame Close event
        """
        self.Destroy()

    def OnTextCtrl(self, event):
        """
        TextCtrl event
        Receives lower date range limit
        """
        self.Draw()

    def OnTextCtrl2(self, event):
        """
        TextCtrl2 event
        Receives upper date range limit
        """
        self.Draw()

    def OnCheckBox(self, event):
        """
        Check box event
        Enables date filter
        """
        self.text_ctrl.Enable(self.check_box.GetValue())
        self.text_ctrl2.Enable(self.check_box.GetValue())
        self.label2.Enable(self.check_box.GetValue())
        self.label3.Enable(self.check_box.GetValue())
        if self.var_label != None:
            self.Draw()
        
    def OnChoice(self, event):
        """
        Choice event
        Selects flowmeter
        """
        dlg = myUtil.BusyInfo(self, '')
        dlg.SetLabel('Loading Database Items...')
        self.SetStatus('Loading Database Items...')
        self.meter_label = self.choice.GetStringSelection()
        self.db_items = self.db.GetItemsByType(self.meter_label)
        self.SetDateRange(self.meter_label)
        self.choice2.Enable(True)
        if self.var_label != None:
            self.Draw()
        self.SetStatus('Items Loaded')
        dlg.Destroy()

    def OnChoice2(self, event):
        """
        Choice2 event
        Selects variable
        """
        dlg = myUtil.BusyInfo(self, '')
        dlg.SetLabel('Loading Variable...')
        self.SetStatus('Loading Variable...')
        self.var_label = self.choice2.GetStringSelection()
        self.Draw()
        self.SetStatus('%s Data Loaded'%self.var_label)
        dlg.Destroy()
        
    def OnPrintButton(self, event):
        """
        Button event
        Prints control charts and histograms
        """
        self.SetStatus('Printing...')
        path = self.FileDialog("Choose a file for Figure 1")
        if path != None:
            self.figure1.SaveFigure(path)
        path = self.FileDialog("Choose a file for Figure 2")
        if path != None:
            self.figure2.SaveFigure(path)    
        self.SetStatus('Printing Successful') 
        
    #----------------------------------
    # GUI Methods
    #----------------------------------
    def Draw(self):
        """
        Draw control charts and histogram
        """
        self.figure1.Initialize()
        self.figure2.Initialize()
        if self.var_label == 'FSADC' or self.var_label == 'ZRADC':
            x,y = self.GetData(self.var_label, use_date_filter = self.check_box.GetValue())            
            self.figure1.Histogram(y, 'r')   
            self.figure2.PlotDate(x,
                              y,
                              HISTORY_MARKER_SHAPE,
                              HISTORY_MARKER_SIZE,
                              HISTORY_MARKER_FACE_COLOR,
                              HISTORY_LINE_STYLE,
                              HISTORY_LINE_WIDTH,
                              HISTORY_ALPHA_LINE)
        else:
            x_fs, y_fs = self.GetData(self.var_label, index = DB_FS_INDEX, use_date_filter = self.check_box.GetValue())
            x_ls, y_ls = self.GetData(self.var_label, index = DB_LS_INDEX, use_date_filter = self.check_box.GetValue())   
            self.figure2.PlotDate(x_fs,
                              y_fs,
                              HISTORY_MARKER_SHAPE,
                              HISTORY_MARKER_SIZE,
                              HISTORY_MARKER_FACE_COLOR,
                              HISTORY_LINE_STYLE,
                              HISTORY_LINE_WIDTH,
                              HISTORY_ALPHA_LINE)
            self.figure2.PlotDate(x_ls,
                              y_ls,
                              HISTORY_MARKER_SHAPE,
                              HISTORY_MARKER_SIZE,
                              HISTORY_MARKER_FACE_COLOR,
                              HISTORY_LINE_STYLE,
                              HISTORY_LINE_WIDTH,
                              HISTORY_ALPHA_LINE)         
            self.figure1.Histogram(y_fs, HISTORY_HISTOGRAM_COLOR_1)
            self.figure1.Histogram(y_ls, HISTORY_HISTOGRAM_COLOR_2)
        self.figure1.SetYLabel('Occurence')
        self.figure1.SetXLabel(self.var_label)
        self.figure2.SetYLabel(self.var_label)
        self.figure2.SetXLabel('Time')
        self.figure1.Draw()
        self.figure2.Draw()
        
    def SetStatus(self, msg):
        """
        Set status label text
        """
        self.statusBar.SetStatusText(msg)

    def InitializePlot(self):
        """
        Clear and re-draw figures
        """
        self.figure1.Initialize()
        self.figure2.Initialize()
        self.figure1.Draw()
        self.figure2.Draw()
            
    #----------------------------------
    # Database Methods
    #----------------------------------
    def GetData(self, var_label, index = None, use_date_filter = False):
        """
        Returns specified data from database
        """
        if var_label in [K_FACTOR, FLOW_RATE, TEMP, TIME]:
            assert index!=None
        if use_date_filter: min_date, max_date = self.GetDateRange()
        
        y = []
        x = []
        for i in self.db_items:
            if use_date_filter:
                if i.GetDate() < min_date or i.GetDate() > max_date:
                    continue

            if var_label == DATE:                
                y.append(i.GetDate())
            elif var_label == TIME:
                y.append(i.GetTestData()[index].GetTime())
            elif var_label == TEMP:
                y.append(i.GetTestData()[index].GetTemp())
            elif var_label == FSADC:
                if i.GetFSADC() == None:
                    continue
                y.append(i.GetFSADC())
            elif var_label == ZRADC:
                if i.GetZRADC() == None:
                    continue
                y.append(i.GetZRADC())
            elif var_label == FLOW_RATE:
                y.append(i.GetTestData()[index].GetRefFlowRate())
            elif var_label == K_FACTOR:
                y.append(i.GetTestData()[index].GetKFactor())
            else:
                raise TypeError, 'Received unknown variable'

            x.append(i.GetDate())
            x,y = myUtil.SortLists(x,y)
        return x, y

    def GetDateRange(self):
        """
        Returns specified date range from GUI ctrls
        """
        d1 = self.text_ctrl.GetValue()
        d2 = self.text_ctrl2.GetValue()
        if not myDateTime.IsStringDate(d1) or not myDateTime.IsStringDate(d2):
            return None, None
        else:
            return myDateTime.DateToNum(myDateTime.GetDateFromString(d1)), myDateTime.DateToNum(myDateTime.GetDateFromString(d2))

    def SetDateRange(self, meter_label):
        """
        Sets mix, max dates in date range ctrls
        """ 
        min_date, max_date = self.db.GetDateRange(meter_label)
        self.text_ctrl.SetValue(myDateTime.GetISOFormat(min_date))
        self.text_ctrl2.SetValue(myDateTime.GetISOFormat(max_date))
        
    def GetDb(self):
        """
        Gets database and shows busy dialog
        """
        dlg = myUtil.BusyInfo(self, '')
        dlg.SetLabel('Loading Database...')
        self.db = myDatabase.Database()
        self.db.Load()
        dlg.Destroy()
        self.choice.Enable(True)
        self.check_box.Enable(True)
        
    def GetDbItems(self):
        """
        Returns the database items
        """
        return self.db_items
