# queue items
#
#                                   ID,     LABEL,                          DATA
#---------------------------------------------------------------------------------
import copy

ITEM_ID = 0
def NewItemId():
    global ITEM_ID
    ITEM_ID += 1
    return copy.deepcopy(ITEM_ID)

class QueueItem():
    def __init__(self, id, msg, data):
        self.msg = msg
        self.ID = id
        self.data = data       

#---------------------------------------------------------------------------------
# queue items
#---------------------------------------------------------------------------------
ABORT_THREAD = QueueItem(NewItemId(),  'ABORT THREAD', None)
STOP_THREAD = QueueItem(NewItemId(),  'STOP THREAD', None)
POST_BUSY_INFO = QueueItem(NewItemId(), 'POST BUSY INFO', None)
KILL_BUSY_INFO = QueueItem(NewItemId(), 'KILL BUSY INFO', None)

# MESSAGES SENT FROM EPICORECLIENT TO WXAPP
SERVER_DATA_READY = QueueItem(NewItemId(), 'SERVER_DATA_READY', None)
SERVER_DATA_POSTED = QueueItem(NewItemId(), 'SERVER_DATA_POSTED', None)

# MESSAGES SENT TO FLOW METER MANAGER THREAD FROM WXAPP
ABORT_FLOW_METER_THREADS = QueueItem(NewItemId(), 'ABORT ALL FLOW METER THREAEDS', None)
CONFIGURE_FLOW_METER_OBJECTS = QueueItem(NewItemId(), 'CONFIGURE FLOW METER OBJECTS', None)
SET_CALIBRATION_ATTRIBUTES = QueueItem(NewItemId(), 'SET CALIBRATION ATTRIBUTES', None)
SET_PRODUCTION_ATTRIBUTES = QueueItem(NewItemId(), 'SET PRODUCTION ATTRIBUTES', None)
SWITCH_DIRECTIONS = QueueItem(NewItemId(), 'SWITCH DIRECTIONS', None)
DISCONNECT_SERIAL_PORTS = QueueItem(NewItemId(), 'DISCONNECT SERIAL PORTS', None)

# MESSAGES SENT TO MUT THREADS FROM FLOW METER MANAGER THREAD
DISCONNECT_SERIAL_PORT = QueueItem(NewItemId(), 'DISCONNECT_SERIAL_PORT', None)
SWITCH_DIRECTION = QueueItem(NewItemId(), 'WRITE SWITCH DIRECTION', None)
CALIBRATE = QueueItem(NewItemId(), 'CALIBRATE', None)

# MESSAGES SENT TO WXAPP FROM FLOW METER MANAGER THREAD
FLOW_DIRECTIONS_SET = QueueItem(NewItemId(), 'FLOW DIRECTION SET', None)
CONFIGURE_FLOW_METER_OBECTS_ERROR = QueueItem(NewItemId(), 'CONFIGURE FLOW METER OBJECTS ERROR', None)
FLOW_METER_OBJECTS_CONFIGURED = QueueItem(NewItemId(), 'FLOW METER OBJECTS CONFIGURED', None)
CALIBRATION_ATTRIBUTES_SET = QueueItem(NewItemId(), 'CALIBRATION ATTRIBUTES SET', None)
PRODUCTION_ATTRIBUTES_SET = QueueItem(NewItemId(), 'PRODUCTION ATTRIBUTES SET', None)
FLOW_METERS_CALIBRATED = QueueItem(NewItemId(), 'FLOW METERS CALIBRATED', None)

# MESSAGES SENT TO WXAPP FROM FLOW METER THREADS
ERROR = QueueItem(NewItemId(), 'ERROR', None)
ENABLE_BANJO = QueueItem(NewItemId(),  'ENABLE BANJO', None)
CALIBRATION_DATE_SET = QueueItem(NewItemId(), 'CALIBRATION DATE SET', None)
CALIBRATED = QueueItem(NewItemId(), 'CALIBRATED', None)
CLASS_LABEL_SET = QueueItem(NewItemId(),  'CLASS LABEL SET', None)
PRODUCT_LABEL_SET = QueueItem(NewItemId(),  'PRODUCT LABEL SET', None)
NOMINAL_SIZE_SET = QueueItem(NewItemId(),  'NOMINAL SIZE SET', None)
SERIAL_NUMBER_SET = QueueItem(NewItemId(),  'SERIAL NUMBER SET', None)
RATE_UNIT_SET = QueueItem(NewItemId(),  'RATE UNIT SET', None)
TOTAL_UNIT_SET = QueueItem(NewItemId(),  'TOTAL UNIT SET', None)
OPTIONS_SET = QueueItem(NewItemId(),  'OPTIONS SET', None)
