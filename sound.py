import random
import os
import libaudioverse
libaudioverse.initialize()

class SoundManager(object):
	SUPPORTED_EXTENSIONS = ('.wav', '.ogg')

	def __init__(self, output_device=-1, sounds_path='sounds'):
		self.sim = libaudioverse.Simulation()
		self.sim.set_output_device(output_device)
		self.world = libaudioverse.EnvironmentNode(self.sim, "default")
		self.world.default_panning_strategy.value=libaudioverse.PanningStrategies.hrtf
		self.world.output_channels.value= 2
		self.world.connect_simulation(0)
		self.world.orientation=(0,1,0,0,0,1)
		self.sounds = {}
		self.sounds_path = sounds_path

	def play(self, filename, source, looping=False, position=(0, 0, 0)):
		sound = libaudioverse.BufferNode(self.sim)
		sound_buffer = self.get_buffer(filename)
		sound.buffer = sound_buffer
		sound.connect(0, source, 0)
		if not looping:
			sound.end_event = _disconnecter
		sound.looping.value = looping
		self.sounds[filename] = sound_buffer
		return Sound(sound)

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

	def get_buffer(self, filename):
		filename = os.path.join(self.sounds_path, filename)
		if os.path.isdir(filename):
			filename = os.path.join(filename, random.choice(self.list_sounds_in_directory(filename)))
		sound_buffer = self.sounds.get(filename)
		if not sound_buffer:
			sound_buffer = libaudioverse.Buffer(self.sim)
			sound_buffer.load_from_file(filename)
		return sound_buffer

	def play_async(self, filename, x=0, y=0, z=0):
		buffer = self.get_buffer(filename)
		self.world.play_async(buffer, x=x, y=y, z=z)


def _disconnecter(node):
	node.disconnect(0)

class Sound(object):

	def __init__(self, buffer_node):
		self.buffer_node = buffer_node

	def stop(self):
		self.buffer_node.state = libaudioverse.NodeStates.stop
