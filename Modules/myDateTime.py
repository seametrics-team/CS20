#-------------------------------------------------------------------------------
# DateTime.py                                                             
''' author: Jeff Peery '''
# date: 04/29/2008                                                              
# email: Jeff@AvanceControl.com                                                 
# Copyright Avance Control, 2008                                                
#-------------------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''
1.01    2014/05/08  SPN     Added GetISOFormatSec method
'''
#-------------------------------------------------------------------------------
# Modules                                                                       
#-------------------------------------------------------------------------------
import datetime
from dateutil.parser import parse
import myUtil
import string
import numpy
from pytz import timezone
#-------------------------------------------------------------------------------
# Constants                                                                       
#-------------------------------------------------------------------------------
HOURS_PER_DAY = 24.
MINUTES_PER_DAY  = 60.*HOURS_PER_DAY
SECONDS_PER_DAY =  60.*MINUTES_PER_DAY
MUSECONDS_PER_DAY = 1e6*SECONDS_PER_DAY
SEC_PER_MIN = 60
SEC_PER_HOUR = 3600
SEC_PER_DAY = SEC_PER_HOUR * 24
SEC_PER_WEEK = SEC_PER_DAY * 7
UTC = timezone('UTC')
MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THURSDAY = 4
FRIDAY = 5
SATURDAY = 6
SUNDAY = 7
#-------------------------------------------------------------------------------
# Methods                                                                       
#-------------------------------------------------------------------------------
def DateToNum(d):
    """
    d is either a datetime instance or a sequence of datetimes

    return value is a floating point number (or sequence of floats)
    which gives number of days (fraction part represents hours,
    minutes, seconds) since 0001-01-01 00:00:00 UTC
    """
    if not myUtil.iterable(d): return _to_ordinalf(d)
    else: return numpy.asarray([_to_ordinalf(val) for val in d])

def Weekday():
    """
    returns the day of the week as integer
    Monday = 1
    Tuesday = 2
    ...
    Sunday = 7
    """
    return datetime.datetime.today().isoweekday()
    
def NumToDate(x, tz=UTC):
    """
    x is a float value which gives number of days (fraction part
    represents hours, minutes, seconds) since 0001-01-01 00:00:00 UTC

    Return value is a datetime instance in timezone tz

    if x is a sequence, a sequence of datetimes will be returned
    """
    if not myUtil.iterable(x): return _from_ordinalf(x, tz)
    else: return [_from_ordinalf(val, tz) for val in x]
    
def GetToday():
    """
    Returns datetime number for current time
    """
    return DateToNum(datetime.datetime.today())
    
def GetISOFormat(value):
    """
    Returns iso format of input
    input is datetime.datetime object or float
    """
    assert type(value) in [float, datetime.datetime]
    if type(value) == float:
        value = NumToDate(value)
    return value.isoformat(' ').split(' ')[0]

def GetISOFormatSec(value):
    """
    Returns iso format of input
    input is datetime.datetime object or float
    """
    assert type(value) in [float, datetime.datetime]
    if type(value) == float:
        value = NumToDate(value)
    return value.isoformat(' ').split(' ')[1]
    
def GetDateFromString(value):
    """
    Returns datetime object from input
    input is string representation of date
    """
    return parse(str(value))
    
def IsDateTimeInstance(value):
    """
    Returns True if input is datetime object
    otherwise False
    """
    if type(value) == datetime.datetime:
        return True
    else:
        return False
    
def IsStringDate(value):
    """
    Returns True if string is a date representation
    otherwise False
    """
    if type(value) not in [str, unicode]:
        return False
    
    if string.upper(value) in ['A','M','T','AM','AT']:
        return False       
    try:
        if value.replace(' ','') == '':
            return False 
        else:
            GetDateFromString(value)
            return True
    except:
        return False

def _to_ordinalf(dt):
    """
    convert datetime to the Gregorian date as UTC float days,
    preserving hours, minutes, seconds and microseconds.  return value
    is a float
    """

    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        delta = dt.tzinfo.utcoffset(dt)
        if delta is not None:
            dt -= delta

    base =  float(dt.toordinal())
    if hasattr(dt, 'hour'):
        base += (dt.hour/HOURS_PER_DAY + dt.minute/MINUTES_PER_DAY +
                 dt.second/SECONDS_PER_DAY + dt.microsecond/MUSECONDS_PER_DAY
                 )
    return base

def _from_ordinalf(x, tz=UTC):
    """
    convert Gregorian float of the date, preserving hours, minutes,
    seconds and microseconds.  return value is a datetime
    """
    ix = int(x)
    dt = datetime.datetime.fromordinal(ix)
    remainder = float(x) - ix
    hour, remainder = divmod(24*remainder, 1)
    minute, remainder = divmod(60*remainder, 1)
    second, remainder = divmod(60*remainder, 1)
    microsecond = int(1e6*remainder)
    if microsecond<10: microsecond=0 # compensate for rounding errors
    dt = datetime.datetime(
        dt.year, dt.month, dt.day, int(hour), int(minute), int(second),
        microsecond, tzinfo=UTC).astimezone(tz)

    if microsecond>999990:  # compensate for rounding errors
        dt += datetime.timedelta(microseconds=1e6-microsecond)

    return dt
