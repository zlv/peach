from variable import Variable
from pitch import Pitch
import sys
def durFromTime(time) :
    return time
def from_midi(stream) :
    import midi
    m = midi.MidiFile()
    m.open(stream)
    m.read()
    m.close()
    trackvar = []
    
    for track in m.tracks :
        curvar = Variable()
        trackvar.append(curvar)
        curpitch = Pitch()
        for ev in track.events :
            if ev.type == "NOTE_OFF" or ev.type == "NOTE_ON" :
                if curpitch.havePitches() : 
                    if curpitch.duration_ : 
                        print curpitch.duration_
                        curvar.addPitch(curpitch.copy())
                curpitch.duration_ = 0
            if ev.type == "DeltaTime": curpitch.duration_ = ev.time#curpitch.plusDuration(durFromTime(ev.time))
            elif ev.type == "NOTE_OFF" or ev.type == "NOTE_ON" and ev.velocity==0 : 
                if curpitch.havePitches() : 
                    curpitch.removePitch(ev.pitch-60)
            elif ev.type == "NOTE_ON": 
                curpitch.addPitch(ev.pitch-60)
            elif ev.type == "SET_TEMPO": print "BUGAGA", ev# TODO (?) ...
            else:
                print "midi warning: event", ev, "ignored"

from_midi(sys.argv[1])
