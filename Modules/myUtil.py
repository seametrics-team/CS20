#----------------------------------------------------------------------
# Utility Module
''' author: Jeff Peery '''
# date: 02/28/2008
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
"""
 1.09   2017/01/05  SPN     -Added GetCorrectedVolume method
 1.08   2016/12/29  SPN     -Updated FileDialog method: added style, path args
 1.07   2016/12/19  SPN     -Updated IsVerificationMeter method:
                             Display error msg if ADC values can't be read from MUT
                             Display error msg if ADC values match verify meter
                            -Added GetCorrectionFactor method
 1.06   2016/12/16  SPN     -Udated IsVerificationMeter method: assume com port is already open when
                             when invoked during initialization of calibration or pretest
 1.05   2016/12/13  SPN     -Udated IsVerificationMeter method: ensure com port is opened before
                             communicating with MUT
 1.04   2014/10/14  SPN     -Updated FileDialog method: designate .txt file type as default (wildcard)
                            rather than *.png file type
 1.03   2014/01/24  SPN     Added MessageFrame method to implement MessageMiniFrame modeless diaglog box
 1.02   2013/9/25   SPN     Added IsVerificationMeter method to determine if MUT is verification meter
 1.01   2013/9/6    SPN     Updated FloatSlider method to add missing validator arg and variable name errors
    1   08/21/2008  JTP     Initial Release
"""
#-------------------------------------------------------------------------
# Modules
#-------------------------------------------------------------------------
import numpy
from myHeader import *
import string
import BusyMiniFrame
import MessageMiniFrame
import wx
import KeypadFrame
from time import sleep as sleep

#-------------------------------------------------------------------------
# Useful dialogs
#-------------------------------------------------------------------------
def BusyInfo(parent, msg):
    dlg = BusyMiniFrame.Frame(parent, msg)
    dlg.Show()
    return dlg

def MsgDialog(parent, msg):
    dlg = wx.MessageDialog(parent, msg, 'Message', wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP )
    dlg.ShowModal()
    dlg.Destroy()

def MessageFrame(parent, msg):
    dlg = MessageMiniFrame.Frame(parent, msg)
    dlg.Show()

def FileDialog(parent, msg, style=wx.FD_DEFAULT_STYLE, folder=""):
    folder = folder.encode('string-escape')
    path = None
    dlg = wx.FileDialog(parent,
                        message = msg,
                        wildcard = "Text files (*.txt)|*.txt",
                        style = style,
                        defaultDir=folder)

    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    dlg.Destroy()
    return path

def ErrorDialog(parent, msg):
    dlg = wx.MessageDialog(parent, msg,'Error', wx.OK | wx.ICON_EXCLAMATION | wx.STAY_ON_TOP)
    dlg.ShowModal()
    dlg.Destroy()

def YesNoDialog(parent, msg):
    return wx.MessageDialog(parent, msg, 'Warning', wx.YES_NO | wx.ICON_EXCLAMATION | wx.STAY_ON_TOP)
    
##def ErrorDialog(parent, msg):
##    return wx.MessageDialog(parent, msg, 'Error', wx.OK | wx.ICON_EXCLAMATION | wx.STAY_ON_TOP)
            
def PassDialog(parent):
    return wx.MessageDialog(parent, 'Calibration was successful!', 'Meter Passed Test!', wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP )
                    
def FailDialog(parent):
    return wx.MessageDialog(parent, 'Meter did not pass test.', 'Meter Failed Test!', wx.OK  | wx.ICON_EXCLAMATION | wx.STAY_ON_TOP )

def SerialNumEntryDialog(parent):
    """
    Dialog for prompting numbers
    """
    dlg = KeypadFrame.Keypad(parent, 'Enter Serial...')
    dlg.period_button.Enable(False)
    if dlg.ShowModal() == wx.ID_OK:
        value = dlg.GetValue()
        dlg.Destroy()
        return value
    else:
        return None
    if dlg: dlg.Destroy()

def NumEntryDialog(parent):
    """
    Dialog for prompting numbers
    """
    dlg = KeypadFrame.Keypad(parent, 'Enter Number...')
    if dlg.ShowModal() == wx.ID_OK:
        value = dlg.GetValue()
        dlg.Destroy()
        return value
    else:
        return None
    if dlg: dlg.Destroy()


#-------------------------------------------------------------------------
# useful controls
#-------------------------------------------------------------------------
class FloatSlider(wx.Slider):

    def __init__(self, parent, id, value, minValue, maxValue, res,
                 size=wx.DefaultSize, style=wx.SL_HORIZONTAL, validator=wx.DefaultValidator,
                 name='floatslider'):
        self._value = value
        self._min = minValue
        self._max = maxValue
        self._res = res
        ival, imin, imax = [round(v/res) for v in (value, minValue, maxValue)]
        self._islider = super(FloatSlider, self)
        self._islider.__init__(
            parent, id, ival, imin, imax, size=size, style=style, validator=validator, name=name
        )
        self.Bind(wx.EVT_SCROLL, self._OnScroll)

    def _OnScroll(self, event):
        ival = self._islider.GetValue()
        imin = self._islider.GetMin()
        imax = self._islider.GetMax()
        if ival == imin:
            self._value = self._min
        elif ival == imax:
            self._value = self._max
        else:
            self._value = ival * self._res
        event.Skip()
        print 'OnScroll: value=%f, ival=%d' % (self._value, ival)

    def GetValue(self):
        return self._value

    def GetMin(self):
        return self._min

    def GetMax(self):
        return self._max

    def GetRes(self):
        return self._res

    def SetValue(self, value):
        self._islider.SetValue(round(value/self._res))
        self._value = value

    def SetMin(self, minval):
        self._islider.SetMin(round(minval/self._res))
        self._min = minval

    def SetMax(self, maxval):
        self._islider.SetMax(round(maxval/self._res))
        self._max = maxval
        self.Refresh()

    def SetRes(self, res):
        self._islider.SetRange(round(self._min/res), round(self._max/res))
        self._islider.SetValue(round(self._value/res))
        self._res = res

    def SetRange(self, minval, maxval):
        self._islider.SetRange(round(minval/self._res), round(maxval/self._res))
        self._min = minval
        self._max = maxval

#-------------------------------------------------------------------------
# array methods
#-------------------------------------------------------------------------
def iterable(obj):
    try: len(obj)
    except: return 0
    return 1

def SortLists(master, slave):
    """
    Returns sorted lists.
    master is a list to control the sorting of slave.
    """
    assert len(master) == len(slave)
    assert type(master) == list
    assert type (slave) == list
    x = zip(master, slave)
    x.sort()
    master, slave = zip(*x)
    master = list(master)
    slave = list(slave)
    return master, slave

#-------------------------------------------------------------------------
# Flowmeter methods
#-------------------------------------------------------------------------
def GetFlowRange(N, start, end, linear = True):
    """
    Method returns the flow range given a start (maximum flow rate),
    stop (minimum flow rate), and N (number of flow rates).

    keyword 'linear' is used to indicate whether to return
    an exponential distribution or a linear distribution
    assert type(N) == int
    assert type(start) == int or type(start) == float
    assert type(end) == int or type(end) == float
    """
    assert type(N) == int
    assert type(start) == int or type(start) == float
    assert type(end) == int or type(end) == float
    assert start != end
    assert N > 1
    start   = float(start)
    end     = float(end)
    step    = (start-end)/float(N-1)
    q       = numpy.zeros(N, dtype=float) + start
    x       = start - end
    if linear:
        for i in range(1, N):
            x = x-step
            q[i] = x + end
    else:
        for i in range(1, N):
            x = x/WEIGHTING_FACTOR
            q[i] = x + end

    assert len(q) == N
    assert q[0] == start
    return q

def DigitalToMilliAmps(BCD_value):
    """
    Returns digital value converted to mA
    BCD_value is double_word, string
    """
    assert type(BCD_value) == int
    mA = (20.0-4.0)*BCD_value/4095.0 + 4.0
    assert type(mA) == float
    assert mA >= 0
    assert mA <= 4095
    return mA

def DigitalToFlowRate(BCD_value, max_flow_rate):
    """
    Returns digital value converted to mA
    BCD_value is double_word, string
    """
    assert type(max_flow_rate) == float
    assert max_flow_rate > 0
    assert type(BCD_value) == int
    return max_flow_rate*BCD_value/4095.0

def GetError(observed, expected):
    """
    Returns error between two intpus
    """
    return 100.0*(observed - expected)/expected

def GetStorageVolumeUncert(system_type, flow_rate):
    """
    Returns uncertainty of storage volume 
    between MUT and REF
    """
    assert IsNumber(flow_rate)
    assert system_type in [HF_SYSTEM, LF_SYSTEM]
    
    if system_type == HF_SYSTEM:
        if flow_rate > HF_TRANSITION_FLOW_RATE:
            return U_HF_SYS_UPSTREAM_STORAGE_VOLUME
        else:
            return U_HF_SYS_DOWNSTREAM_STORAGE_VOLUME
        
    elif system_type == LF_SYSTEM:
        if flow_rate > LF_TRANSITION_FLOW_RATE:
            return U_LF_SYS_UPSTREAM_STORAGE_VOLUME
        else:
            return U_LF_SYS_DOWNSTREAM_STORAGE_VOLUME
        
    else:
        raise TypeError, 'receive unknown system type'

def GetTransitionFlowRate(system_type):
    """
    Returns transition flow rate.
    transition flow rate is flow rate that changes
    between upstream and downstream reference meter.
    """
    assert system_type in [HF_SYSTEM, LF_SYSTEM]
    
    if system_type == HF_SYSTEM:
        return HF_TRANSITION_FLOW_RATE
    elif system_type == LF_SYSTEM:
        return LF_TRANSITION_FLOW_RATE
    else:
        raise TypeError, 'receive unknown system type'
    
def GetStorageVolume(system_type, flow_rate):
    """
    Returns storage volume between MUT and REF
    """
    assert IsNumber(flow_rate)
    assert system_type in [HF_SYSTEM, LF_SYSTEM]
    
    if system_type == HF_SYSTEM:
        if flow_rate > HF_TRANSITION_FLOW_RATE:
            return HF_SYS_UPSTREAM_STORAGE_VOLUME
        else:
            return HF_SYS_DOWNSTREAM_STORAGE_VOLUME
        
    elif system_type == LF_SYSTEM:
        if flow_rate > LF_TRANSITION_FLOW_RATE:
            return LF_SYS_UPSTREAM_STORAGE_VOLUME
        else:
            return LF_SYS_DOWNSTREAM_STORAGE_VOLUME
        
    else:
        raise TypeError, 'receive unknown system type'

def CalValuesAreOk(ref_count, mut_count, test_time, temp_change):
    """
    Check that test results are valid
    """
    assert ref_count != None
    assert mut_count != None
    assert test_time != None
    assert temp_change != None
    
    if ref_count <= 0:
        return False
    elif mut_count <= 0:
        return False
    elif test_time <= 0:
        return False
    elif abs(temp_change) > MAX_TEMP_CHANGE:
        return False
    else:
        return True

def IsNumber(value):
    try:
        dummy = value/2.0
        return True
    except:
        return False
    
def IsVerificationMeter(mut):
    """
    If MUT's ADC values match verification meter return true
    """
    try:
        for i in range(3):   # Attempt to read fsadc up to 3 times
            fsadc = str(mut.ReadFSADC())[0:7]
            if len(fsadc):
                break
            sleep(1)

        for i in range(3):   # Attempt to read zradc up to 3 times
            zradc = str(mut.ReadZRADC())[0:7]
            if len(zradc):
                break
            sleep(1)
    except:
        ErrorDialog(None, 'Unable to read MUT ADC values')
        return True

    if (fsadc == HF_VERIFICATION_FSADC and zradc == HF_VERIFICATION_ZRADC)\
        or (fsadc == LF_VERIFICATION_FSADC and zradc == LF_VERIFICATION_ZRADC):
        ErrorDialog(None, 'MUT recognized as verification meter and cannot be calibrated')
        return True

    return False

def GetCorrectionFactor(poly_coef, flow_rate):
    curvefit_poly = numpy.poly1d( numpy.array(poly_coef) )
    curvefit_error = curvefit_poly(flow_rate)
    curvefit_correction = 1 - curvefit_error/100

    print 'curve fit % error', curvefit_error
    print 'curve fit correction factor', curvefit_correction

    return curvefit_correction

def GetCorrectedVolume(ref_volume, thermal_volume, test_time, poly_coef):
    print 'ref volume', ref_volume * GAL_PER_CUBIC_METER
    print 'thermal volume', thermal_volume * GAL_PER_CUBIC_METER
    # Apply curve fit correction
    uncorrected_flow_rate       = ref_volume/test_time * GAL_PER_CUBIC_METER * SEC_PER_MIN     # convert to gpm
    print 'uncorrected flow rate', uncorrected_flow_rate
    corr_factor     = GetCorrectionFactor(poly_coef, uncorrected_flow_rate)
    corrected_ref_volume      = ref_volume * corr_factor - thermal_volume     # corrected ref volume (m^3)
    return corrected_ref_volume
