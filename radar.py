import game
import math_utils

class Radar(object):
	track_ping_delay = 0.5

	def __init__(self, looker):
		self.looker = looker
		self.index = 0
		self.tracking = None
		self.last_track_time = 0

	def get_surrounding_items(self):
		position = self.looker.position
		room = game.map.find_room_containing(position)
		if room is None:
			return []
		query = game.world.query(room[0], room[2])
		items = [i.body.userData for i in query.fixtures if i.body.userData is not game.world and math_utils.distance(i.body.position, self.looker.position) > 0]
		def sort_by_distance(k):
			return math_utils.distance(self.looker.position, k.position)
		return sorted(items, key=sort_by_distance)

	def get_surrounding_exits(self):
		def sort_by_distance(k):
			return math_utils.distance(self.looker.position, k)
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
		angle = math_utils.angle_between(self.looker.position, position)
		direction = (angle - self.looker.facing) % 360
		distance = math_utils.distance(self.looker.position, position)
		game.output.output("%s: %.2f meters at %d degrees" % (name, distance, direction))
		game.sound_manager.play_async('beep.wav', *position)

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
		game.sound_manager.play_async('tracker.wav', *position)

	def start_tracking(self):
		self.tracking = self.current_item()

	def stop_tracking(self):
		self.tracking = None
