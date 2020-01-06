from random import randint, random
import Modules.myDatabase as myDatabase
from Modules.myHeader import *

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------

db = myDatabase.Database()
db.Load()
date = 730000.0

for label in METER_LABELS:
    for i in range(1000):
        db_item = myDatabase.Item(label, str(randint(10000000, 99999999)))
        db_item.SetFSADC(random() + 300)
        db_item.SetZRADC(random()*0.5)
        db_item.SetDate(date+i*1.0)
        for j in range(2):
            test = myDatabase.Test()            
            test.SetRefPulseCount(randint(1000, 10000))
            test.SetMUTPulseCount(j*50+randint(1000, 1100))
            test.SetTime(random()*0.1 + 60.0)
            test.SetRefVolume(random() + 20)
            test.SetTemp(random()+20)
            db_item.AppendCalTest(j, test)
        db.AppendItem(db_item, db_item.GetSerialNum())
db.Save()
