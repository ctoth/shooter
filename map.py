class Map(object):
	def __init__(self, rooms=None):
		if rooms is None:
			rooms = []
		self.rooms = rooms
