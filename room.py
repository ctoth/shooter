from Box2D import b2

class Room(object):
	destructable = False

	def __init__(self, world, name=None, size=(1, 1), exits=None, floor=None, contents=None):
		self.world = world
		self.name = name
		corners = [
			(0, 0),
			(0, size[0] + 1),
			(size[1] + 1, size[0] + 1),
			(size[1] + 1, 0)
		]
		exit_coords = [tuple([j+1 for j in i.values()[0]]) for i in exits]
		filled_tiles = []
		filled_tiles.extend(tiles_for_wall(corners[0], corners[1], exit_coords))
		filled_tiles.extend(tiles_for_wall(corners[1], corners[2], exit_coords))
		filled_tiles.extend(tiles_for_wall(corners[2], corners[3], exit_coords))
		filled_tiles.extend(tiles_for_wall(corners[3], corners[0], exit_coords))
		self.exit_coords = exit_coords
		self.filled_tiles = filled_tiles
		self.floor = floor
		if exits is None:
			exits = []
		exits.sort()
		self.exits = exits
		bodies = []
		for tile in filled_tiles:
			position = (tile[0] - 0.5, tile[1] - 0.5)
			shape = b2.polygonShape(box=(0.5, 0.5))
			bodies.append(self.world.world.CreateStaticBody(shapes=shape, position=position, userData=self))
		self.bodies = bodies
		#dictionary of {coords: object}
		if contents is None:
			contents = {}
		for i in contents.values():
			i.location = self
		self.contents = contents

	def remove_item(self, item):
		for key, val in dict(self.contents).iteritems():
			if val is item:
				del self.contents[key]

	def handle_colision(self, other):
		pass

def point_on_line(point, line_start, line_end):
	line_start, line_end = sorted([line_start, line_end])
	if line_start[0] == line_end[0]:
		if point[0] == line_start[0] and point[1] >= line_start[1] and point[1] <= line_end[1]:
			return True
	elif line_start[1] == line_end[1]:
		if point[1] == line_start[1] and point[0] >= line_start[0] and point[0] <= line_end[0]:
			return True
	return False

def points_for_line(line_start, line_end):
	line_start, line_end = sorted([line_start, line_end])
	if line_start[0] == line_end[0]:
		for i in xrange(line_start[1], line_end[1] + 1):
			yield (line_start[0]+0.5, i+0.5)
			yield (line_start[0]+0.5, i+0.5)
	elif line_start[1] == line_end[1]:
		for i in xrange(line_start[0], line_end[0] + 1):
			yield (i, line_start[1])
	else:
		raise ValueError("Only generates strait lines")

def tiles_for_wall(wall_start, wall_end, exits):
	for point in points_for_line(wall_start, wall_end):
		if point in exits:
			continue
		yield point
