from collections import defaultdict

class Map(object):
	def __init__(self, rooms=None, size=(100, 100)):
		if rooms is None:
			rooms = []
		self.rooms = rooms
		self.size = size
		self.tiles = {}

	def fill(self):
		for i in xrange(self.size[0]):
			for j in xrange(self.size[1]):
				self.tiles[(i, j)] = True
