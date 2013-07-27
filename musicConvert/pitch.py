import math
pitchIndexes = {'c' : 0, 'd' : 2, 'e' : 4, 'f' : 5, 'fis' : 6, 'g' : 7, 'a' : 9, 'b' : 10, 'h' : 11, 'r' : 'pause'}
pitchIndexes['do'] = pitchIndexes['c']
pitchIndexes['re'] = pitchIndexes['d']
pitchIndexes['mi'] = pitchIndexes['e']
pitchIndexes['fa'] = pitchIndexes['f']
pitchIndexes['sol'] = pitchIndexes['g']
pitchIndexes['la'] = pitchIndexes['a']
pitchIndexes['si'] = pitchIndexes['h']

class Pitch :
    octaveInc_ = 12
    def __init__(self,pitch=[],last=0,duration=1.,bLegato = 0) :
        self.pitch_ = pitch
        self.last_ = last
        self.duration_ = duration
        self.bOctaveChanged_ = 0
        self.bChord = 0
        self.bLegato_ = bLegato
    def changePitch(self,sPitch) :
        global pitchIndexes
        newPitch = pitchIndexes[sPitch]
        if newPitch!="pause" :
            newPitch -= self.octaveInc_
        if len(self.pitch_)<=self.last_ :
            self.pitch_.append(newPitch)
        else :
            self.pitch_[self.last_] = newPitch 
    def addPitch(self,newPitch) :
        self.nextPitch()
        self.pitch_.append(newPitch)
    def removePitch(self,oldPitch) :
        self.pitch_.remove(oldPitch)
        self.checkLastPitch()
    def changeDuration(self,sDur) :
        legato = sDur.find('~')
        if legato!=-1 :
            self.bLegato_ = 1
            sDur = sDur[:legato]+sDur[legato+1:]
        if len(sDur) :
            self.duration_ = 1./float(sDur)
        if '.' in sDur :
            self.duration_ *= 1.5
    def plusDuration(self,dur) :
        self.duration_ += dur
    def changeOctave(self,sOctave,bRelative,oldpitch) :
        if self.pitch_[self.last_]=="pause" :
            return
        self.bOctaveChanged_ = 1
        higherCount = 0
        lowerCount = 0
        for ch in sOctave :
            if ch=="'" :
                higherCount += 1
            elif ch=="," :
                lowerCount += 1
        if higherCount and lowerCount :
            raise SyntaxError()
        oldIndex = 0
        if bRelative :
            dif = self.lastPitch()-oldpitch
            oldIndex = int(math.ceil(abs(dif)/(self.octaveInc_/2)/2.))
            if dif<0 :
                oldIndex = -oldIndex
        index = higherCount - lowerCount - oldIndex
        self.pitch_[self.last_] += self.octaveInc_*index
    def __str__(self) :
        return str(self.pitch_)+"*"+str(self.duration_)
    def copy(self) :
        return Pitch(self.pitch_[:],self.last_,self.duration_,self.bLegato_)
    def firstPitch(self) :
        return self.pitch_[0]
    def lastPitch(self) :
        return self.pitch_[self.last_]
    def nextPitch(self) :
        self.last_ += 1
    def checkLastPitch(self) :
        self.last_ = len(self.pitch_)-1
    def newWithSameDuration(self) :
        return Pitch([],0,self.duration_)
    def havePitches(self) :
        return len(self.pitch_)
