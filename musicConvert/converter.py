#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from variable import Variable
from pitch import Pitch
from playmidi import *
def nextIndex(index) :
    index[0] += 1
    return index[0]
index = [-1]
nonesymbol = nextIndex(index)
backslash = nextIndex(index) 
letter = nextIndex(index)
number = nextIndex(index)
pitchsymbols = nextIndex(index)
pitchoption = nextIndex(index)
point = nextIndex(index)
quote = nextIndex(index)
space = nextIndex(index)
equal = nextIndex(index)
opening = nextIndex(index)
closing = nextIndex(index)
openchord = nextIndex(index)
closchord = nextIndex(index)
anysym = nextIndex(index)
sharp = nextIndex(index)
endsymbol = nextIndex(index)
sLastSymbol = '$'

end = -2
various = -3
variousGiveAway = -4
command = -5
def isVarious(flag) :
    return flag==various or flag==variousGiveAway

buffer = ""
cursymbol = 0
class State :
    def state(self) :
        return self.state_
    def __init__(self,num = 0, v = 0) :
        self.var = v
        self.state_ = num
    def __str__(self) :
        return 's'+str(self.state_)
    def copy(self) :
        return State(self.state_,self.var)
        
class Repeat(Variable) :
    def __init__(self) :
        Variable.__init__(self)
        self.bVolta = 0

class Header(Variable) :
    def __init__(self) :
        Variable.__init__(self)
        self.values = {}

class StaffGroup(Variable) :
    def __init__(self) :
        Variable.__init__(self)
        self.stafs = []

class Staff(Variable) :
    def __init__(self) :
        Variable.__init__(self)
        self.settings = {}
        self.voices = []

class TabStaff(Staff) :
    def __init__(self) :
        Staff.__init__(self)

class Voice(Variable) :
    def __init__(self) :
        Variable.__init__(self)
        self.sClef = ""

class Score(Variable) :
    def __init__(self) :
        Variable.__init__(self)

varClassByName = {"StaffGroup" : StaffGroup, "Staff" : Staff, "TabStaff" : TabStaff, "Voice" : Voice, "Score" : Score}

def createVariable(name) :
   return varClassByName[name]()

curstate = State()
statestack = []
instance = {}
variables = {}
args = [""]
curpitch = Pitch()
oldpitch = 0
curvar = 0
nextvar = 0
bNextvar = 0

#pb -- push to buffer
#pa -- push to argument buffer
#na -- next argument
#nv -- new variable
#nfn -- new variable from next variable
#rc -- run command
#bc -- back carret
#op -- opening
#cl -- closing
#pnname -- read name of pitch
#pnpich -- read pitch octave information in "." and "'"
#pndurt -- read pitch duration
#pnsave -- save pitch
#co -- chord open
#np -- next pitch
#cc -- chord closed
def pb() :
    global buffer
    buffer += text[cursymbol]
def pa() :
    global args
    global argsindex
    args[argsindex] += text[cursymbol]
def na() :
    global args
    global argsindex
    argsindex += 1
    args.append("")
def nv() :
    global buffer
    global variables
    global curvar
    curvar = variables[buffer] = Variable()
    curstate.var = curvar
    buffer = ""
def nfn() :
    global bNextvar
    bNextvar = 1
def rc() :
    return
def bc() :
    global cursymbol
    cursymbol -= 1
def op() :
    global argsindex
    global buffer
    global statestack
    global curvar
    global nextvar
    global bNextvar
    curstate.var = curvar
    statestack.append(curstate.copy())
    args.append("")
    if bNextvar : curvar = nextvar
    bNextvar = 0
    buffer = ""
def cl() :
    global curvar
    oldcurvar = curvar
    curvar = statestack.pop().var
    if curvar and oldcurvar and curvar!=oldcurvar :
        for time in range(oldcurvar.times) :
            curvar.addVariable(oldcurvar)
def pnname() :
    global buffer
    global curpitch
    curpitch.changePitch(buffer)
    curpitch.bOctaveChanged_ = 0
    buffer = ""
def pnpich() :
    global buffer
    global curpitch
    curpitch.changeOctave(buffer,curvar.bRelative,oldpitch)
    buffer = ""
def pndurt() :
    global buffer
    global curpitch
    curpitch.changeDuration(buffer)
    buffer = ""
def pnsave() :
    global curpitch
    global oldpitch
    if curvar.bRelative and not curpitch.bOctaveChanged_ :
        pnpich()
    if curpitch.firstPitch()!="pause" :
        oldpitch = curpitch.firstPitch()
    curvar.addPitch(curpitch.copy())
    curpitch = curpitch.newWithSameDuration()
def co() :
    global curpitch
    curpitch.bChord = 1
def np() :
    global oldpitch
    if (curvar.bRelative and not curpitch.bOctaveChanged_) :
        pnpich()
    if curpitch.lastPitch()!="pause" :
        oldpitch = curpitch.lastPitch()
    curpitch.nextPitch()
def cc() :
    curpitch.checkLastPitch()
funcs = [[0, op,nv,0, op,                0, [op,pb]],\
         [rc,pb,0, 0, rc,                0, 0],\
         [0, 0, 0, 0, 0,                 0, 0],\
         [0, op,0, 0, 0,                 0, 0,       0,          0],\
         [cl,op,0, 0, 0,                 pb,0,       0,          0,         bc,\
          co,0, 0, 0, [nfn,bc],0, 0, 0, bc],\
         [0, 0, 0, 0, [bc,pnname,pnsave],pb,0,       [pnname,pb],[pnname,pb]],\
         [0, 0, nv,0, 0,                 0, pb],\
         [0, 0, 0, 0, [bc,pndurt,pnsave],0, 0,       pb,         0],\
         [0, 0, 0, 0, [bc,pnpich,pnsave],0, 0,       [pnpich,pb],pb],\
         [cl,op,0, bc,0,                 0, 0,       0,          0,         0],\
#10:
         [0,0,0,0,0,0,0,0,0,0,\
          0,          pb,0,          cc,         0, 0, [nfn,bc]],\
         [0,0,0,0,0,0,0,0,0,0,\
          [pnname,np],pb,[pnname,pb],[pnname,cc]],\
         [0,0,0,0,0,0,0,0,0,0,\
          [pnpich,np],0, pb,         [pnpich,cc]],\
         [0, 0, 0, 0, [bc,pnsave],       0, 0,       pb],\
         [0, 0, 0, 0, op,                0, 0,       0,          0,         0,\
          0,          0, 0,          0,          0, bc],\
         [0, 0, 0, 0, cl],\
         [0, 0, 0, 0, 0,                 0, 0,       0,          0,         0,\
          0,          0, 0,          0,          0, 0, 0,bc],\
         [cl,0, 0, 0, cl],
         [cl,0, 0, 0, 0,                 0, 0,       0,          0,         0,\
          0,          0, 0,          0,         bc, 0, 0,0]]
"""first level, before anything"""
"""reading command"""
"""found variable"""
"""variable is equal to"""
"""code block"""
"""reading a pitch"""
table = [\
        {backslash : 1, letter : 6, space : 0, opening : 4, endsymbol : end}, \
        {letter : 1, opening : command, space : command, backslash : command},\
        {space : 2, equal : 9},\
        {backslash : 1, space : 3, opening : 4, openchord : 10},\
        {backslash : 1, opening : 14, space : 4, letter : 5, openchord : 10, closing : 18, closchord : 17 },\
        {space : 4, closing : 4, letter : 5, number : 7, point : 7, pitchoption : 7, pitchsymbols : 8},\
        {letter : 6, space : 2},\
        {space : 4, closing : 4, number : 7, point : 7, pitchoption : 7},\
        {space : 4, closing : 4, number : 7, point : 7, pitchoption : 7, pitchsymbols : 8},\
        {backslash : 1, space : 9, opening : 3, closing : 0, openchord : 10},\
        #10:
        {space : 10, letter : 11, closchord : 13, openchord : 16},\
        {space : 10, letter : 11, pitchsymbols : 12, closchord : 13},\
        {space : 10, pitchsymbols : 12, closchord : 13},\
        {space : 4, closing : 4, number : 7, point : 7, pitchoption : 7},
        {opening : 4, closing : 15},\
        {closing : 4},\
        {openchord : 4, closchord : 17},\
        {closchord : various},
        {closing : various}]
lastInTable = len(table)-1

index = [-1]
pitchType = nextIndex(index)
varType = nextIndex(index)
numberType = nextIndex(index)
equalSymbolType = nextIndex(index)
stringType = nextIndex(index)
stringTypeSimple = nextIndex(index)
stringVersionType = nextIndex(index)
valuesType = nextIndex(index)
classPointPropertyTypeEqualSharpString = nextIndex(index)
commandsForType = {\
        pitchType : [\
            {space : 0, letter : 1},\
            {letter : 1, pitchsymbols : 2, opening : variousGiveAway, space : various},\
            {pitchsymbols : 3, opening : variousGiveAway, space : various}],\
        varType : [\
            {space : 0, backslash : 1},\
            {anysym : 1, opening : variousGiveAway, space : various}],
        numberType : [\
            {space : 0, number : 1},\
            {number : 1, space : various}],\
        equalSymbolType : [\
            {space : 0, equal : various}],\
        stringType : [\
            {space : 0, quote : 1},\
            {anysym : 1, quote : various}],\
        stringTypeSimple : [\
            {space : 0, letter : 1},\
            {letter : 1, space : various}],\
        stringVersionType : [\
            {space : 0, quote : 1},\
            {number : 1, point : 1, quote : various}],
        valuesType : [\
            {space : 0, opening : 1},\
            {space : 1, letter : 2, closing : various},\
            {letter : 2, space : 3, equal : 4},\
            {space : 3, equal : 4},\
            {space : 4, quote : 5},\
            {anysym : 5, quote : 1}],
        classPointPropertyTypeEqualSharpString : [\
            {space : 0, letter : 1},\
            {letter : 1, point : 2},\
            {letter : 2, space : 3, equal : 4},\
            {space : 3, equal : 4},\
            {space : 4, sharp : 5},\
            {quote : 6},\
            {anysym : 6, quote : various}]}
funcsForType = {\
        pitchType : [\
            [0, pb, 0],\
            [0, pb, [pnname,pb]],\
            [0, 0,  pb]],
        stringType : [\
            [0, 0],\
            [0, pa]],
        equalSymbolType : [\
            [0, 0]],\
        stringTypeSimple : [\
            [0, pa],\
            [0, pa]],\
        valuesType : [\
            [],\
            [0,0, pa],\
            [0,0, pa,na,na],\
            [],\
            [],\
            [0,na,0, 0, 0,pa]],
        classPointPropertyTypeEqualSharpString : [\
            [0,pa],\
            [0,pa,na],\
            [0,0, pa,na,na],\
            [],\
            [],\
            [],\
            [0,0, 0, 0, 0,0,pa]]}
funcsForType[varType] = funcsForType[stringVersionType] = funcsForType[stringType]
funcsForType[numberType] = funcsForType[stringTypeSimple]
def getSymbol(symbol,symbindex) :
    if symbindex==2 :
        return anysym
    if symbol=="\\" :
        return backslash
    if symbol==" " or symbol=="\n" :
        return space
    if symbol=="." :
        return point
    if symbol=='"' :
        return quote
    if symbol=="=" :
        return equal
    if symbol=="{" :
        return opening
    if symbol=="}" :
        return closing
    if symbol=="<" :
        return openchord
    if symbol==">" :
        return closchord
    if symbol==sLastSymbol :
        return endsymbol
    if symbol=="#" :
        return sharp
    if symbol.isalpha() and symbindex==0 :
        return letter
    if symbol.isdigit() and symbindex==0 :
        return number
    if symbol=="'" or symbol==',' :
        return pitchsymbols
    if symbol=='~' :
        return pitchoption
class Command :
    def __init__(self,com,nargs,begin) :
        self.com_ = com
        self.nargs_ = nargs
        self.begin_ = begin
    def run(self) :
        self.com_()
    def state(self) :
        return self.begin_
commands = {}
def createNewFunctions(func,bLast,bHasVarious,com) :
    newFunc = []
    for i in range(lastInTable+1) :
        newFunc.append(0)
    newFunc+=func
    if not bLast :
        newFunc.append(na)
    elif bHasVarious :
        newFunc[0] = newFunc[3] = newFunc[4] = newFunc[9] = [com,cl]
    return newFunc
def addArgToTable(arg, bLast,com) :
    global lastInTable
    index = 0
    for curcommand in commandsForType[arg] :
        newCommand = curcommand.copy()
        bHasVarious = 0
        for key, value in newCommand.items() :
            if not isVarious(newCommand[key]) :
                newCommand[key] += lastInTable+1
            else :
                bHasVarious = 1
                if not bLast :
                    newCommand[key] = lastInTable+2+index
        table.append(newCommand)
        funcs.append(createNewFunctions(funcsForType[arg][index],bLast,bHasVarious,com))
        index += 1
    lastInTable += index 
    
def defCommand(name, com, args) :
    if len(args) :
        begin = lastInTable+1
    else :
        begin = -1
    commands[name] = Command(com,len(args),begin)
    index = 0
    for arg in args :
        bLast = index==(len(args)-1)
        addArgToTable(arg,bLast,com)
        index += 1
def defInstanceVariable(name) :
    global instance
    instance[name] = args[0]
    args[0] = ""
def defInstanceVariableWithValue(name,value) :
    global instance
    instance[name] = value
    args[0] = ""
def version() :
    defInstanceVariable("version")
def language() :
    defInstanceVariable("language")
def relative() :
    global oldpitch
    if not curpitch.havePitches() :
        pnname()
    else :
        pnpich()
    curvar.bRelative = 1
    curvar.relatePitch = curpitch
    oldpitch = curpitch.firstPitch()
def key() :
    curvar.key = args[0]
    args[0] = ""
def major() :
    curvar.major = 1
def minor() :
    curvar.major = 0
def repeat() :
    global nextvar
    nextvar = Repeat()
    nextvar.volta = args[0]=="volta"
    nextvar.times = int(args[1])
    args[0] = args[1] = ""
def tempo() :
    curvar.temposize = int(args[0])
    curvar.tempo = int(args[1])
    args[0] = args[1] = ""
def header() :
    global nextvar
    nextvar = Header()
    index = 0
    while index<len(args)-1 :
        nextvar.values[args[index]]=args[index+1]
        index += 2
def new() :
    global nextvar
    global bNextvar
    nextvar = createVariable(args[0])
    bNextvar = 1
    args[0] = ""
def set() :
    curvar.settings[args[0]+'.'+args[1]] = args[2]
    args[0] = args[1] = args[2] = ""
def clef() :
    curvar.sClef = args[0]
    args[0] = ""
def score() :
    args[0] = "Score"
    new()
def empty() :
    global nextvar
    nextvar = Variable()
def unfoldRepeats() :
    global curvar
    global variables
    curvar = variables[args[0]]
def generateNoteOn(onepitch) :
    return ('noteon', 0, 60+onepitch, 127)
def generatePlay(dur,tempo,size) :
    return ('play', int(1000*tempo/60*dur*4/size))
def generateNoteOff(onepitch) :
    return ('noteoff', 0, 60+onepitch)
def convertToMidiEvents(var) :
    tempo = 120
    if var.tempo!=-1 : tempo = var.tempo
    bContinue = 0
    for pitch in var.pitches_ :
        if bContinue :
            bContinue = 0
        else :
            for onepitch in pitch.pitch_ :
                if onepitch!='pause' :
                    yield generateNoteOn(onepitch)
        yield generatePlay(pitch.duration_,tempo,var.temposize)
        if not pitch.bLegato_ :
            for onepitch in pitch.pitch_ :
                if onepitch!='pause' :
                    yield generateNoteOff(onepitch)
        else :
            bContinue = 1
def midi() :
    eventsToMp3(convertToMidiEvents(curvar))

defCommand("version", version, [stringVersionType])
defCommand("language", language, [stringType])
defCommand("relative", relative, [pitchType])
defCommand("key", key, [stringTypeSimple])
defCommand("major", major, [])
defCommand("minor", minor, [])
defCommand("repeat", repeat, [stringTypeSimple,numberType])
defCommand("tempo", tempo, [numberType,equalSymbolType,numberType])
defCommand("header", header, [valuesType])
defCommand("new", new, [stringTypeSimple])
defCommand("set", set, [classPointPropertyTypeEqualSharpString])
defCommand("clef", clef, [stringType])
defCommand("score", score, [])
defCommand("layout", empty, [])
defCommand("unfoldRepeats", unfoldRepeats, [varType])
defCommand("midi", midi, [])
def commandToRun() :
    global args
    global argsindex
    args = [""]
    argsindex = 0
    if buffer in commands :
        state = State(commands[buffer].state())
        if state.state()==-1 :
            commands[buffer].run()
            state = statestack[-1]
            cl()
        return state
    else :
        curvar.addVariable(variables[buffer])
        state = statestack[-1]
        cl()
        return state
def coolIndexForFuncs(curindex,newindex) :
    return funcs[curstate.state()] and newindex<len(funcs[curstate.state()]) and newindex>=0 and funcs[curstate.state()][newstate.state()]
text = sys.stdin.read()
text += sLastSymbol
maxvsymbol = 3
while curstate!=end :
    symbindex = 0
    symbol = nonesymbol
    while symbindex!=maxvsymbol :
        symbol = getSymbol(text[cursymbol],symbindex)
        symbindex += 1
        if symbol in table[curstate.state()] :
            break
    newstate = State(table[curstate.state()][symbol])
    if newstate.state()==end :
        break
    if newstate.state()==command :
        newstate = commandToRun()
        bc()
        buffer = ""
    if isVarious(newstate.state()) :
        if newstate.state()==variousGiveAway :
            cb()
        newstate = statestack[-1]
    #print text[cursymbol], " ", symbol, " ", curstate, " -> ", newstate
    if coolIndexForFuncs(curstate.state(),newstate.state()) :
        if type(funcs[curstate.state()][newstate.state()])==type([]) :
            for func in funcs[curstate.state()][newstate.state()] :
                func()
        else :
            funcs[curstate.state()][newstate.state()]()
    cursymbol += 1
    curstate = newstate
