#----------------------------------------------------------------------
# Hex-Floating Point Conversion Module
''' author: Jeff Peery '''
# date: 11/29/2007
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''

    1   2/1/08    JTP     -   Initial Release
    
'''

#-------------------------------------------------------------------------
# Modules
#-------------------------------------------------------------------------
import numpy
import string
import re

#-------------------------------------------------------------------------
# Methods
#-------------------------------------------------------------------------
def Hex2Float(data):
    """Hex2Float converts a hexidecial value to floating point. parameter 'data' is a
    string value representing a hexidecimal number"""
    assert type(data) in [str, unicode]

    print 'hex2float data:', data
    
    #this is the binary equivalent for 0 to 15
    BINARY          = {'0':[0,0,0,0],'1':[0,0,0,1],'2':[0,0,1,0],'3':[0,0,1,1],'4':[0,1,0,0],'5':[0,1,0,1],'6':[0,1,1,0],'7':[0,1,1,1],'8':[1,0,0,0],'9':[1,0,0,1],'A':[1,0,1,0],'B':[1,0,1,1],'C':[1,1,0,0],'D':[1,1,0,1],'E':[1,1,1,0],'F':[1,1,1,1]}
    
    # get the sign from exponent
    #
    # if the first element of the exponent is and integer less than 8 then
    # the sign is positive, otherwise the sign is negative
    try:
        # if this value can be converted into an integer
        # and is less than 8 then the sign is positive
        # here an expection will be raised if the value is non numeric and we know
        # the value is not less than 8 so we set the sign to -1 in the exception method
        sign = string.atoi(data[0])
        if sign < 8:
            sign = 1.0
        else:
            sign = -1.0
    except:
        sign = -1.0
    
    # convert hexidecimal exponent to binary
    exponent_b=[]        
    for i in range(0,2):
        exponent_b  = exponent_b+BINARY[data[i]]
    
    # convert binary exponent to decimal
    exponent_d = 0
    for i in range(1,8):
        if exponent_b[i] == 1:
            exponent_d = exponent_d + exponent_b[i]*2**(7-i)
    exponent_d = exponent_d-64
    
    # Convert hexidecimal mantissa to binary
    mantissa_b = []
    for i in range(2,8):
        mantissa_b  = mantissa_b + BINARY[data[i]]
    
    # if value is negative convert from twos compliment
    if sign == -1:                    
        # invert digits
        for i in range(0,len(mantissa_b)):
            if mantissa_b[i] == 1: 
                mantissa_b[i] = 0
            else: 
                mantissa_b[i] = 1                    
            
        # add 1 to binary. 'add' is a variable 
        # used to hold the carry over value during subtraction
        add = 1
        for i in range(0,len(mantissa_b)):                        
            n = len(mantissa_b)-i-1
            if (mantissa_b[n]+add) == 2:
                mantissa_b[n] = 0
                add = 1
            elif (mantissa_b[n]+add) == 1:
                mantissa_b[n] = 1 
                add = 0                    
    
    # reset the testData value then sum the base two binary numbers and save
    decout = 0
    decimalScale = -1*numpy.arange(1,24)
    
    for i in range(0,23):
        if mantissa_b[i]==1:                
            decout = decout + sign*mantissa_b[i]*2**(decimalScale[i]+exponent_d)

    return decout

##print Hex2Float('C607ED42')
