import random
import os
import multiprocessing
import libaudioverse


libaudioverse.initialize()


class SoundManager(object):
	SUPPORTED_EXTENSIONS = ('.wav', '.ogg')

	def __init__(self, output_device=-1, sounds_path='sounds'):
		self.sim = libaudioverse.Simulation()
		self.sim.threads = multiprocessing.cpu_count() - 1 or 1
		self.sim.set_output_device(output_device)
		self.reverb = libaudioverse.FdnReverbNode(self.sim)
		self.world = self.create_world()
		self.reverb_send = self.world.add_effect_send(channels = 4, is_reverb = True, connect_by_default = True)
		self.world.connect(self.reverb_send, self.reverb, 0)
		self.set_orientation((0,1,0,0,0,1))
		self.sounds = {}
		self.sounds_path = sounds_path
		self.last_random = {}

	def start(self):
		self.world.connect_simulation(0)
		self.reverb.connect_simulation(0)

	def stop(self):
		self.world.disconnect(0)
		self.reverb.disconnect(0)

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
		return Sound(sound)

	def play_ambient(self, filename):
		sound = self.play_default(filename)
		sound.buffer_node.looping.value = True
		return sound

	def play_default(self, filename):
		sound = libaudioverse.BufferNode(self.sim)
		sound_buffer = self.get_buffer(filename)
		sound.buffer = sound_buffer
		sound.connect_simulation(0)
		return Sound(sound)

	play_UI_queue = play_default

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
			filename = filename.encode('mbcs')
			sound_buffer.load_from_file(filename)
			self.sounds[filename] = sound_buffer
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

	def play_async(self, filename, x=0, y=0, z=0, in_world=True):
		buffer = self.get_buffer(filename)
		dry = not in_world
		self.world.play_async(buffer, x=x, y=y, z=z, is_dry=dry)

	def create_world(self):
		world = libaudioverse.EnvironmentNode(self.sim, b'default')
		world.default_panning_strategy =libaudioverse.PanningStrategies.hrtf
		world.default_max_distance = 20
		world.default_distance_model = libaudioverse.DistanceModels.exponential
		world.output_channels.value= 2
		return world

	def create_occlusion_filter(self):
		filter = libaudioverse.BiquadNode(self.sim, 1)
		filter.filter_type = libaudioverse.BiquadTypes.highshelf
		filter.frequency = 800
		return filter


	def set_listener_position(self, position):
		self.world.position = position

	def set_orientation(self, orientation):
		self.world.orientation = orientation


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
