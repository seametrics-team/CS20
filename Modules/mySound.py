import sys
import os
import winsound

class Sound():
    def __init__(self):
        pass

    def PlaySound(self, file_path):
        """play .wav file"""
        assert os.path.exists(file_path)
        winsound.PlaySound(file_path, winsound.SND_FILENAME)

##s_obj = Sound()
##s_obj.PlaySound('fail')
