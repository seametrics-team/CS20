#----------------------------------------------------------------------
# Graphics/Plotting Module
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
import matplotlib
matplotlib.interactive(False)
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import Toolbar
import matplotlib.mlab as mlab
from matplotlib.artist import setp
from myHeader import *
import wx
from numpy import arange

class Figure(wx.Panel):
    def __init__(self, parent):
        #----------------------------------
        # Attributes
        #----------------------------------
        self.axes = None
        self.parent = parent
        #----------------------------------
        # GUI Ctrl Id's
        #----------------------------------
        FIGURE_ID   = wx.NewId()
        PANEL_ID    = wx.NewId()
        #----------------------------------
        # GUI Ctrl Definitions
        #----------------------------------
        wx.Panel.__init__(self, id=PANEL_ID, parent=self.parent, style = wx.BORDER_SUNKEN)
        self.figure = matplotlib.figure.Figure(dpi=FIGURE_DPI, figsize=FIGURE_SIZE)
        self.CreateAxes()
        self.canvas = FigureCanvas(self, FIGURE_ID, self.figure)
        self.toolbar = Toolbar(self.canvas)
        self.toolbar.Realize()
        #----------------------------------
        # GUI Sizers
        #----------------------------------
        self.boxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.boxSizer.Add(self.canvas, 1, border=0, flag=wx.EXPAND)
        self.boxSizer.Add(self.toolbar, 0, border=5, flag=wx.BOTTOM|wx.EXPAND)
        self.SetSizer(self.boxSizer)
        self.Fit()
        #----------------------------------
        # GUI Setup
        #----------------------------------
        self.boxSizer.Layout()
        self.toolbar.update()

    def CreateAxes(self):
        self.axes = self.figure.add_axes([0.085, 0.2, 0.85, 0.7])

    def SetYLabel(self, label):
        self.axes.set_ylabel(label)

    def SetXLabel(self, label):
        self.axes.set_xlabel(label)

    def SetXLimits(self, upper_limit, lower_limit):
        self.axes.set_xlim((lower_limit, upper_limit))

    def SetYLimits(self, upper_limit, lower_limit):
        self.axes.set_ylim((lower_limit, upper_limit))

    def SetFigureColor(self, color):
        self.figure.set_facecolor(color)
        self.axes.set_axis_bgcolor(color)

    def EnableGrid(self, value):
        self.axes.grid(value)

    def EnableFrame(self, value):
        self.axes.set_frame_on(value)
    
    def ClearAxes(self):
        self.axes.clear()

    def onEraseBackground(self, evt):
        # this is supposed to prevent redraw flicker on some X servers...
        pass

    def TickLeft(self):
        self.axes.yaxis.tick_left()
        
    def TickBottom(self):
        self.axes.xaxis.tick_bottom()

    def ClearAxes(self):
        self.axes.clear()

    def Draw(self):
        self.toolbar.update()
        self.canvas.draw()
        
    def Title(self, title):
        assert type(title) == str
        self.axes.set_title(title)

    def SaveFigure(self, path):
        assert type(path) == str or type(path) == unicode
        # savefig cannot handle unicode. we must cast the path as a str
        self.figure.savefig(str(path),
                            facecolor='w',
                            edgecolor='w',
                            dpi = FIGURE_DPI,
                            figsize = FIGURE_SIZE)

    def GetAxesLimits(self):
        (xmin,xmax) = self.axes.get_xlim()
        (ymin,ymax) = self.axes.get_ylim()
        return xmax, xmin, ymax, ymin
    
    def PlotSpecLimits(self, spec, allowance, fs_flow_rate):
        """plots spec limits (upper, target, lower) as function of flow rate (zero:FS) 
        given a spec, allowance, and fs flow rate"""
        assert type(spec) == int or type(spec) == float
        assert type(allowance) == int or type(allowance) == float
        assert type(fs_flow_rate) == int or type(fs_flow_rate) == float
        # draw limits
        x = arange(2.0,500.0,1.0)/500.0
        usl = spec + (100.0*allowance/fs_flow_rate)/x
        lsl = -spec - (100.0*allowance/fs_flow_rate)/x
        xs, ys = mlab.poly_between(x*100, usl, lsl)
        self.axes.fill(xs, ys, 'g', alpha=0.1)
        # draw center line
        self.axes.axhline(0, linewidth = 0.25, color = 'k', linestyle = '--')
        self.SetXLimits(UPPER_X_LIMIT, LOWER_X_LIMIT)
        self.SetYLimits(UPPER_Y_LIMIT, LOWER_Y_LIMIT)
        # draw labels
        xmax, xmin, ymax, ymin = self.GetAxesLimits()
        self.axes.text(99, spec, 'usl', fontsize=10)
        self.axes.text(99, 0, 'target', fontsize=10)
        self.axes.text(99, -spec, 'lsl', fontsize=10)

    def PlotSpecLimitsLines(self, spec, allowance, flow_rate, fs_flow_rate):
        """plots spec limits at a given flow rate (upper, target, lower)
        given an accuracy, allowance, flow rate, and fs flow rate"""
        assert type(spec) == int or type(spec) == float
        assert type(allowance) == int or type(allowance) == float
        assert type(fs_flow_rate) == int or type(fs_flow_rate) == float
        assert type(flow_rate) == int or type(flow_rate) == float
        # draw limits
        usl = spec + (100.0*allowance/fs_flow_rate)/flow_rate
        lsl = -spec - (100.0*allowance/fs_flow_rate)/flow_rate
        target = 0.0
        xs, ys = mlab.poly_between(flow_rate*100/fs_flow_rate, usl, lsl)
        self.axes.fill(xs, ys, 'g', alpha=0.1)
        # draw center line
        self.axes.axhline(0, linewidth = 0.25, color = 'k', linestyle = '--')
        # draw labels
        self.axes.text(101, spec, 'usl', fontsize=10)
        self.axes.text(101, target, 'target', fontsize=10)
        self.axes.text(101, -spec, 'lsl', fontsize=10)
        
    def Initialize(self):
        self.ClearAxes()
        self.EnableFrame(FRAME_ON)
        self.EnableGrid(GRID_ON)
        self.SetFigureColor(FIGURE_COLOR)
        self.TickBottom()
        self.TickLeft()

    def Plot(self, x_data, y_data, marker_shape, marker_size, marker_color, line_style, line_width, alpha):
        assert len(x_data) == len(y_data)
        if len(x_data) > 0:
            self.axes.plot(x_data,
                           y_data,
                           marker = marker_shape,
                           markerfacecolor = marker_color,
                           markeredgewidth = MARKER_EDGE_WIDTH,
                           markersize = marker_size,
                           linestyle = line_style,
                           linewidth = line_width,
                           alpha = alpha)

    def PlotDate(self, x_data, y_data, marker_style, marker_size, marker_color, line_style, line_width, alpha):
        assert len(x_data) == len(y_data)
        if len(x_data) > 0:
            self.axes.plot_date(x_data,
                           y_data,
                           marker = MARKER_SHAPE,
                           markerfacecolor = MARKER_FACE_COLOR,
                           markeredgewidth = MARKER_EDGE_WIDTH,
                           markersize = 3,
                           linestyle = '-',
                           linewidth = 1,
                           alpha = alpha)
            
    def Scatter(self, x_data, y_data, marker_shape, marker_size, marker_face_color, marker_edge_color, marker_edge_width, alpha):
        assert len(x_data) == len(y_data)
        if len(x_data) > 0:
            self.axes.plot(x_data,
                           y_data,
                           marker = marker_shape,
                           markerfacecolor = marker_face_color,
                           markeredgecolor = marker_edge_color,
                           markeredgewidth = marker_edge_width,
                           markersize = marker_size,
                           color = LINE_COLOR,
                           linewidth = 0,
                           alpha = alpha)

    def GetNumHistCells(self, length):
        if length <= 100:
            return 10
        elif length > 100 and length <= 200:
            return 15
        elif length > 200:
            return 20
        else:
            raise ValueError, 'received invalid length'
        
    def Histogram(self, y_data, facecolor):
        if len(y_data) > 0:
            self.axes.hist(y_data,
                           bins = self.GetNumHistCells(len(y_data)),
                           normed = False,
                           align='center',
                           orientation = 'vertical',
                           alpha = 0.25,
                           log = False,
                           edgecolor = 'k',
                           facecolor = facecolor)
        
