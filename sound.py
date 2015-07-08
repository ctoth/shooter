import os
import libaudioverse
libaudioverse.initialize()

class SoundManager(object):
	SUPPORTED_EXTENSIONS = ('.wav', '.ogg')

	def __init__(self, output_device=-1, sounds_path='sounds'):
		self.sim = libaudioverse.Simulation()
		self.sim.set_output_device(output_device)
		self.world = libaudioverse.SimpleEnvironmentNode(self.sim, "default")
		self.world.connect_simulation(0)
		self.listener = libaudioverse.SourceNode(self.sim, self.world)
		self.sounds = {}
		self.sounds_path = sounds_path

	def play(self, filename, looping=False):
		filename = os.path.join(self.sounds_path, filename)
		sound = self.sounds.get(filename)
		if not sound:
			sound = libaudioverse.BufferNode(self.sim)
			sound_buffer = libaudioverse.Buffer(self.sim)
			sound_buffer.load_from_file(filename)
			sound.buffer.value = sound_buffer
		sound.connect(0, self.listener, 0)
		sound.looping.value = looping
		return sound

	def list_sounds_in_directory(self, directory):
		res = []
		directory = os.path.join(self.sounds_path, directory)
		for fname in os.listdir(directory):
			if fname.lower().endswith(self.SUPPORTED_EXTENSIONS):
				res.append(fname)
		return res
