import random
import os
import libaudioverse
libaudioverse.initialize()

class SoundManager(object):
	SUPPORTED_EXTENSIONS = ('.wav', '.ogg')

	def __init__(self, output_device=-1, sounds_path='sounds'):
		self.sim = libaudioverse.Simulation()
		self.sim.set_output_device(output_device)
		self.convolver = libaudioverse.FftConvolverNode(self.sim, 2)
		self.world = libaudioverse.EnvironmentNode(self.sim, "default")
		self.world.default_panning_strategy =libaudioverse.PanningStrategies.hrtf
		self.world.default_distance_model = libaudioverse.DistanceModels.exponential
		self.world.default_max_distance = 1000
		self.world.output_channels.value= 2
		self.world.connect(0, self.convolver, 0)
		self.convolver.mul = 0.01
		self.world.mul = 0.99
		self.world.connect_simulation(0)
		self.convolver.connect_simulation(0)
		self.world.orientation=(0,1,0,0,0,1)
		self.sounds = {}
		self.sounds_path = sounds_path
		self.last_random = {}

	def play(self, filename, source, looping=False, position=(0, 0, 0)):
		if len(position) == 2:
			position = list(position)
			position.append(0)
		sound = libaudioverse.BufferNode(self.sim)
		sound_buffer = self.get_buffer(filename)
		sound.buffer = sound_buffer
		sound.connect(0, source, 0)
		if not looping:
			sound.end_event = _disconnecter
		sound.looping.value = looping
		self.sounds[filename] = sound_buffer
		return Sound(sound)

	def play_ambient(self, filename):
		sound = libaudioverse.BufferNode(self.sim)
		sound_buffer = self.get_buffer(filename)
		sound.buffer = sound_buffer
		self.sounds[filename] = sound_buffer
		sound.looping.value = True
		sound.connect_simulation(0)
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
			filename = self.select_random_sound(filename)
		sound_buffer = self.sounds.get(filename)
		if not sound_buffer:
			sound_buffer = libaudioverse.Buffer(self.sim)
			sound_buffer.load_from_file(filename)
		return sound_buffer

	def select_random_sound(self, folder):
		last_played = self.last_random.get(folder)
		files = self.list_sounds_in_directory(folder)
		if last_played and len(files) > 1:

			try:
				files.remove(last_played)
			except ValueError:
				pass
		to_play = random.choice(files)
		self.last_random[folder] = to_play
		return os.path.join(folder, to_play)

	def set_impulse_response(self, filename):
		self.convolver.set_response_from_file(filename, 0, 0)
		self.convolver.set_response_from_file(filename, 1, 1)

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

	def is_playing(self):
		return self.buffer_node.state == libaudioverse.NodeStates.playing

	def pause(self):
		self.buffer_node.state = libaudioverse.NodeStates.paused

	def play(self):
		self.buffer_node.state = libaudioverse.NodeStates.playing
