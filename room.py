
class Room(object):

	def __init__(self, world, size=(1, 1), exits=None, floor=None):
		self.world = world
		corners = [
			(1, 1),
			(1, size[0]),
			size,
			(size[1], 1)
			]
		self.floor = floor
		if exits is None:
			exits = []
		exits.sort()
		