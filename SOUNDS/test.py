import sys
import winsound

def beep(sound):
    winsound.PlaySound('%s.wav'%sound, winsound.SND_FILENAME)

beep('pass')
