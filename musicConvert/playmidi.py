#!/usr/bin/python

import wave
from decode import *
#from soundutils import *
#import sys
import subprocess

def eventsToMp3(midievents) :
    rawpcm = midievents_to_rawpcm(midievents)
    swav = 'test.wav'
    file = wave.open(swav,"wb")
    file.setnchannels(1)
    file.setframerate(44100)
    file.setsampwidth(4)
    for sdata in rawpcm :
        file.writeframes(sdata)
    cmd = 'lame --quiet %s' % swav
    subprocess.call(cmd, shell=True)
