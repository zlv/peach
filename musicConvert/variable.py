def strList(theList):
    string = "["
    for index, item in enumerate(theList):
        string += str(item)
        if index != len(theList)-1:
            string += ", "
    return string + "]"
    
def strDict(theDict):
    string = "{"
    index = 0
    for key, item in theDict.items() :
        string += str(key) + " : " + str(item)
        if index != len(theDict)-1:
            string += ", "
        index += 1
    return string + "}"

class Variable :
    def __init__(self) :
        self.pitches_ = []
        self.bRelative = 0
        self.key = "n/a"
        self.bMajor = 0
        self.temposize = 4
        self.tempo = -1
        self.times = 1
    def addPitch(self,pitch) :
        self.pitches_.append(pitch)
    def __str__(self) :
        return strList(self.pitches_)
    def addVariable(self,var) :
        if self.tempo==-1 :
            self.tempo = var.tempo
        for pitch in var.pitches_ :
            self.addPitch(pitch)
