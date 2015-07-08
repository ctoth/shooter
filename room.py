
class Room(object):

	def __init__(self, world, name=None, size=(1, 1), exits=None, floor=None, contents=None):
		self.world = world
		self.name = name
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
		#dictionary of {coords: object}
		if contents is None:
			contents = {}
		self.contents = contents
