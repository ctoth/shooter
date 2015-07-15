import random
import os
import libaudioverse
libaudioverse.initialize()

class SoundManager(object):
	SUPPORTED_EXTENSIONS = ('.wav', '.ogg')

	def __init__(self, output_device=-1, sounds_path='sounds'):
		self.sim = libaudioverse.Simulation()
		self.sim.set_output_device(output_device)
		self.world = libaudioverse.SimpleEnvironmentNode(self.sim, "default")
		self.world.default_panning_strategy.value=libaudioverse.PanningStrategies.hrtf
		self.world.output_channels.value= 2
		self.world.default_max_distance.value = 20
		self.world.connect_simulation(0)
		self.sounds = {}
		self.sounds_path = sounds_path

	def play(self, filename, source, looping=False, position=(0, 0, 0)):
		filename = os.path.join(self.sounds_path, filename)
		if os.path.isdir(filename):
			filename = os.path.join(filename, random.choice(self.list_sounds_in_directory(filename)))
		sound = self.sounds.get(filename)
		if not sound:
			sound = libaudioverse.BufferNode(self.sim)
			sound_buffer = libaudioverse.Buffer(self.sim)
			sound_buffer.load_from_file(filename)
			sound.set_buffer(sound_buffer)
		sound.connect(0, source, 0)
		sound.looping.value = looping
		return sound

	def list_sounds_in_directory(self, directory):
		res = []
		if not directory.startswith(self.sounds_path):
			directory = os.path.join(self.sounds_path, directory)
		for fname in os.listdir(directory):
			if fname.lower().endswith(self.SUPPORTED_EXTENSIONS):
				res.append(fname)
		return res

	def create_source(self):
		return libaudioverse.SourceNode(self.sim, self.world)
