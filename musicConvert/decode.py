# code under GPLv3
# Albert Zeyer - 2010-12-06

#import os
#from struct import *

def midievents_to_rawpcm(stream, gain=0.5):
	# install fluidsynth
	# e.g. on Mac: brew install fluidsynth
	# get a soundfont. e.g.: http://www.schristiancollins.com/generaluser.php http://sourceforge.net/apps/trac/fluidsynth/wiki/SoundFont
	import fluidsynth
	fs = fluidsynth.Synth(gain=gain)

	# create a symlink or just copy such a file there
	sfid = fs.sfload("midisoundfont.sf2")
	fs.program_select(0, sfid, 0, 0)
	
	for cmd in stream:
		f = cmd[0]
		args = cmd[1:]
		if f == "play":
			len, = args
			# FluidSynth assumes an output rate of 44100 Hz.
			# The return value will be a Numpy array of samples.
			len = 44100 * len / 1000
			if len > 0: yield fs.get_mono_samples(len)
		else: getattr(fs, f)(*args)

	fs.delete()
