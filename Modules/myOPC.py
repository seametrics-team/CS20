######################################################################################
# myOPC.py                                                                       #
######################################################################################
''' autor : Katarzyna Gebal
            Narrow Gate Logic
            www.nglogic.com
            
                &

            Jeff Peery
            '''
######################################################################################
''' OPC Client project file'''    
######################################################################################


#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------
'''

    1   12/02/08    JTP     (1) Included Server and Group DataChange
                                event methods.
                            (2) Included SetUpdateRate.

'''

#-------------------------------------------------------------------------
# Modules
#-------------------------------------------------------------------------
import win32com.client
import win32api
import pythoncom
import sys
import time
import wx.lib.newevent

#-------------------------------------------------------------------------
# Event Class
#-------------------------------------------------------------------------
# This creates a new Event class and a EVT binder function
(OPCEvent, EVT_OPC_DATA_CHANGE) = wx.lib.newevent.NewEvent()

#-------------------------------------------------------------------------------
# OPC Event Classes
#-------------------------------------------------------------------------------
class ServerEvents:
    def __init__(self):
        print 'init Server Events'
         
    def OnServerShutDown(self, Reason):
        print 'Server Shutdown at',time.ctime()

class GroupEvents:
    def __init__(self):
        self.parent = None
        print 'On __Init__ OPC DataChange Events'
         
    def OnDataChange(self,TransactionID,NumItems,ClientHandles,ItemValues,Qualities,TimeStamps):
        assert self.parent != None
        for item in range(int(NumItems)):
            wx.PostEvent(self.parent, OPCEvent(msg=int(ClientHandles[item]), value=int(ItemValues[item]), quality=int(Qualities[item])))
                         
    def SetParent(self, parent):
        self.parent = parent
        
#-------------------------------------------------------------------------------
# OPC Funcitons
#-------------------------------------------------------------------------------

# The function gets access to the the OPC automation object.
# computerName parameter is given when we want to make remote connection by using DCOM. 
# The function returns OPCServer object.
def connectCOMOPC(computerName=None):
     if computerName == None:
        opcServer = win32com.client.Dispatch('OPC.Automation.1')
     else:
        # can connect to remote computer
        opcServer = win32com.client.DispatchEx('OPC.Automation.1',computerName,clsctx=pythoncom.CLSCTX_ALL)
     return opcServer

# The function returns the tuple of names (ProgIDs) of the registered OPC Servers.
# This names are used when we connect to the server.
# computerName parameter is given when we want to make remote connection by using DCOM.
def getServerList(computerName=None):
    try:
        return connectCOMOPC(computerName).GetOPCServers()
    except Exception:
        return None
  

# The function connects to an opc server.
# It creates one private OPCGroup. This group will be used to to access items.   
# It returns the tuple of OPCServer object and the OPCGroup object.
def connectServer(serverName,computerName=None):
    try:
        opcServer = connectCOMOPC(computerName)
        opcServer.Connect(serverName)
        groups = opcServer.OPCGroups
        group = groups.Add() 
        group.IsActive = 1   
        group.IsSubscribed = 1
        return (opcServer,group,groups)
    except Exception:
        return (None,None,None)
        

# The function disconects from the OPC Server.
def disconnectServer(opcServer):
    opcServer.OPCGroups.RemoveAll() # cleaning up
    opcServer.Disconnect()
    opcServer = None

def SetGroupEvents(group):
    return win32com.client.DispatchWithEvents(group, GroupEvents)

# maximum rate to return events to OnDataChange.
# if the data is changing faster than this rate
# then the most recent value will be sent to the
# data change.
#
# Note that if the data changes, then changes back to
# its original value then no data change event will occur.
def SetGroupUpdateRate(group, rate):
    group.UpdateRate = rate

# minimum change required (as percent full scale, ie 0-100)
# to produce an OnDataChange event
def SetGroupDeadBand(group, band):
    group.DeadBand = band
    
# The function traverses recursively the hierarchical structure of item's namespaces.
# It appends all found items to the list. 
def opcAppendLeafs(browser,list):
    browser.ShowLeafs()
    for leaf in browser:
        list.append(browser.GetItemID(leaf))
    browser.ShowBranches()
    for branch in browser:
        browser.MoveDown(branch)
        opcAppendLeafs(browser,list)
        browser.MoveUp()
        

# Function tries to get the items that exist in the opcServer. 
# It uses OPCbrowser object.
# Sometimes it is not possible to get all existing item names. 
# The ability of browsing depends on the server configuration.
def getOPCItemsList(opcServer):
    try:
        list = []
        browser = opcServer.CreateBrowser()
        browser.AccessRights = 3
        browser.MoveToRoot()
        opcAppendLeafs(browser,list)
        return list
    except Exception:
        return None


# Adds item to the private group group
def addItem(itemID, group, num):
    try:
        pythoncom.PumpWaitingMessages()
        return group.OPCItems.AddItem(itemID, num)
    except Exception:
        return None

# Adds items to the private group group
def addItems(count, itemIDs, group, clientHandles):
    try:
        pythoncom.PumpWaitingMessages()
        return group.OPCItems.AddItems(count, itemIDs, clientHandles)
    except Exception:
        return None

# Function reads value quality and timestamp of the item  
# 0x1 means that values are read from the OPCcache
# The second possible option (0x2) is reading directly from the device.
# Function returns the tuple of the value, quality and the time stamp
def readItemValue(opcItem):
    pythoncom.PumpWaitingMessages()
    time.sleep(1)
    return opcItem.Read(0x2)
        

# Function writes value to the opc server
# An error appears if the conversion of value type to the required 
# item type is not possible.
def writeItemValue(opcItem,value):
    pythoncom.PumpWaitingMessages()
    opcItem.Write(value)
    pythoncom.PumpWaitingMessages()
    time.sleep(0.75)
