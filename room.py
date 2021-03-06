from Box2D import b2
from tiles import *

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
		exit_coords = []
		for exit in exits:
			exit_pos = exit.values()[0]
			exit_coords.append((exit_pos[0]+1, exit_pos[1]))
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
			position = (tile[0] + 0.5, tile[1] + 0.5)
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

	def handle_collision(self, other):
		pass
