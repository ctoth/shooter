import dungeon
import game

SIZE_RATIO = 2.0

def load_dungeon(world, max_x, max_y, cell_size=5):
	map, room_coords = dungeon.generate(max_x, max_y, cell_size)
	game.room_coords = room_coords
	for tile_coord in map:
		if map[tile_coord] == 'w':
			position = tile_coord[0] * SIZE_RATIO, tile_coord[1] * SIZE_RATIO
			size = 0.5 * SIZE_RATIO, 0.5 * SIZE_RATIO
			world.create_wall_tile(position=position, size=size)
		if map[tile_coord] == 'u':
			start = tile_coord[0] * SIZE_RATIO, tile_coord[1] * SIZE_RATIO
	game.map = map
	return start

def find_room_containing(coords):
	for room in game.room_coords:
		if room_contains(room, coords):
			return room

def room_contains(room, coords):
	return False
