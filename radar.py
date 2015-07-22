import game
import math_utils

class Radar(object):

	def __init__(self, looker):
		self.looker = looker
		self.index = 0

	def get_surrounding_items(self):
		position = self.looker.position
		room = game.map.find_room_containing(position)
		if room is None:
			return
		query = game.world.query(room[0], room[2])
		items = [i.body.userData for i in query.fixtures if i.body.userData is not game.world and math_utils.distance(i.body.position, self.looker.position) > 0]
		return items

	def current_item(self):
		items = self.get_surrounding_items()
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
		name = item.name
		position = item.position
		position_vector = math_utils.vec_sub(position, self.looker.position)
		direction = (math_utils.vec_to_angle(position_vector) - self.looker.facing) % 360
		distance = math_utils.distance(self.looker.position, item.position)
		game.output.output("%s: %.2f meters at %d degrees" % (name, distance, direction))
		game.sound_manager.play_async('beep.wav', *position)

	def read_next(self):
		self.next_item()
		self.read_current()

	def read_previous(self):
		self.previous_item()
		self.read_current()
