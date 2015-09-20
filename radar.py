import game
import npc

class Radar(object):
	track_ping_delay = 0.5

	def __init__(self, looker):
		self.looker = looker
		self.index = 0
		self.tracking = None
		self.last_track_time = 0

	def get_surrounding_npcs(self):
		return [i for i in self.get_surrounding_items() if isinstance(i, npc.NPC)]

	def get_surrounding_items(self):
		position = self.looker.position
		room = game.map.find_room_containing(position)
		if room is None:
			return []
		query = game.world.query(room[0], room[2])
		items = [i.body.userData for i in query.fixtures if i.body.userData is not game.world and self.looker.position.distance(i.body.position) > 0]
		def sort_by_distance(k):
			return self.looker.position.distance(k.position)
		return sorted(items, key=sort_by_distance)

	def get_surrounding_exits(self):
		def sort_by_distance(k):
			return self.looker.position.distance(k)
		return sorted(game.map.nearby_exits(self.looker.position), key=sort_by_distance)

	def current_item(self):
		items = self.get_surrounding_items() + self.get_surrounding_exits()
		if not items:
			return
		self.index %= len(items)
		return items[self.index]

	def next_item(self):
		self.index += 1
		return self.current_item()

	def previous_item(self):
		self.index -= 1
		return self.current_item()

	def read_current(self):
		item = self.current_item()
		if item is None:
			return
		if isinstance(item, tuple):
			name = "exit"
			position = item
		else:
			name = item.name
			position = item.position
		angle = self.looker.position.angle_between(position)
		direction = (angle - self.looker.facing) % 360
		distance = self.looker.position.distance(position)
		game.output.output("%s %.1f at %d" % (name, distance, direction))
		game.sound_manager.play_async('radar_ping.ogg', *position, in_world=False)

	def read_next(self):
		self.next_item()
		self.read_current()

	def read_previous(self):
		self.previous_item()
		self.read_current()

	def tick(self):
		if self.tracking is None:
			return
		if self.last_track_time + self.track_ping_delay > game.clock.time():
			return
		position = self.tracking
		if not isinstance(position, tuple):
			position = position.position
		self.last_track_time = game.clock.time()
		game.sound_manager.play_async('tracker.wav', *position, in_world=False)

	def start_tracking(self):
		self.tracking = self.current_item()

	def stop_tracking(self):
		self.tracking = None

	def summarize_room(self):
		room = game.map.find_room_containing(self.looker.position)
		if room is None:
			return
		dimensions = room[1][0] - room[0][0], room[2][1] - room[1][1]
		contents= self.get_surrounding_items()
		exits = self.get_surrounding_exits()
		npcs = self.get_surrounding_npcs()
		description = "%d by %d meters, %d npcs, %d exits" % (dimensions[0], dimensions[1], len(npcs), len(exits))
		game.output.output(description)

class SweepingRadar(object):

	def __init__(self, looker, step_size=2, arc=180, sweep_delay=0.01, reset_delay=0.3, range=20):
		self.looker = looker
		self.arc = arc
		self.sweeping = False
		self.step_size = step_size
		self.sweep_Delay = sweep_delay
		self.reset_delay = reset_delay
		self.current_degree = None
		self.reset()
		self.last_ping_time = 0
		self.last_reset_time = 0
		self.range = range

	def reset(self):
		self.current_degree = 0 - (self.arc / 2.0)
		self.last_reset_time = game.clock.time()

	def should_reset(self):
		if self.current_degree >= (self.arc / 2.0) + 1:
			return True
		return False

	def sweep(self):
		if not self.can_ping():
			return
		self.ping()
		if self.should_reset():
			self.reset()
		self.current_degree += self.step_size

	def ping(self):
		self.last_ping_time = game.clock.time()
		direction = (self.looker.facing + self.current_degree) % 360
		what = game.world.ray_cast_to_first_item(self.looker.position, direction, self.range)
		if not what:
			return
		hitpoint, item = what
		game.sound_manager.play_async('radar_ping.ogg', *hitpoint, in_world=False)

	def can_ping(self):
		if game.clock.time() - self.last_ping_time > self.sweep_Delay:
			if game.clock.time() - self.last_reset_time > self.reset_delay:
				return True
		return False

	def tick(self):
		if self.sweeping:
			self.sweep()

	def start(self):
		self.sweeping = True

	def stop(self):
		self.sweeping = False
		self.reset()
