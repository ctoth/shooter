import random
import dungeon
import game	
import math_utils
import tiles

class Map(object):

	def __init__(self, world, name="", x_cells=8, y_cells=5, cell_size=8, size_ratio=1.0, ambience=None, random_state=None):
		self.world = world
		self.name = name
		self.x_cells, self.y_cells = x_cells, y_cells
		self.cell_size = cell_size
		self.size_ratio = size_ratio
		self.ambience = ambience
		self.ambience_sound = None
		self.random = random.Random()
		if random_state is not None:
			self.random.setstate(random_state)
		self.map, self.room_vertices, self.corridors = dungeon.generate(x_cells, y_cells, cell_size)
		self.starting_coordinates = None
		self.fill_wall_tiles()

	def fill_wall_tiles(self):
		tile_size=(0.5, 0.5)
		physical_tile_size = math_utils.vec_mul(tile_size, self.size_ratio)
		for tile_coord, tile_type in self.map.items():
			if tile_type == 'w':
				physical_position = self.get_physical_coordinates(tile_coord)
				physical_position= math_utils.vec_add(physical_position, physical_tile_size)
				self.world.create_wall_tile(position=physical_position, size=physical_tile_size)
			elif tile_type == 'u':
				for neighbor in dungeon.neighbors(tile_coord):
					if self.map[neighbor] == 'r':
						self.starting_coordinates = self.get_physical_coordinates(neighbor)
						break

	def get_physical_coordinates(self, coordinates):
		return math_utils.vec_mul(coordinates, self.size_ratio)

	def get_real_coordinates(self, physical_coordinates):
		coordinates = math_utils.vec_div(physical_coordinates, self.size_ratio)
		return coordinates

	def enter(self, player):
		if self.ambience is not None:
			self.ambience_sound = game.sound_manager.play_ambient(self.ambience)
		print "setting player position to %.2f, %.2f" % tuple(self.starting_coordinates)
		player.position = self.starting_coordinates

	def get_exits(self):
		return [k for k, v in self.map.items() if v == 'e']

	def find_room_containing(self, position):
		for room in self.room_vertices:
			if tiles.point_in_room(position, room):
				return room


	def corridor_exits(self, position):
		corridor = self.find_corridor_containing(position)
		exits = self.get_exits()
		return [exit for exit in exits if exit in corridor]

	def find_corridor_containing(self, position):
		position = tuple(math_utils.vec_round(position))
		for corridor in self.corridors:
			for tile in corridor:
				if position == tile:
					return corridor
