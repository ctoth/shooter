import yaml
from game_object import GameObject
from room import Room
from map import Map

def load_map(world, filename):
	with open(filename, 'rb') as fp:
		map_dict = yaml.load(fp)
	rooms = []
	objects = {}
	for obj in map_dict['objects']:
		objects[obj['name']] = obj
	for room in map_dict['rooms']:
		room_objects = {}
		for room_obj in room.get('contents', {}):
			for obj_name, coords in room_obj.iteritems():
				coords = tuple(coords)
				room_objects[coords] =	 GameObject(**objects[obj_name])
		room['contents'] = room_objects
		rooms.append(Room(world=world, **room))
	map = Map(rooms=rooms)
	return map
