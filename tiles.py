import random
from vector import Vector

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
			yield (line_start[0], i)
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

def point_in_room(point, room_corners):

	max_x, max_y = room_corners[2]
	return point_in_shape(point, room_corners[0], room_corners[2])

def point_in_shape(point, min_coords, max_coords):
	x, y = point
	min_x, min_y = min_coords
	max_x, max_y = max_coords
	return min_x <= x <= max_x and min_y <= y <= max_y

def exit_on_wall(room, exit):
	return any([point_on_line(exit, room[0], room[1]), point_on_line(exit, room[1], room[2]), point_on_line(exit, room[2], room[3]), point_on_line(exit, room[3], room[0])])

def center_of_room(room):
	room_base = room[0]
	relative = Vector(room[1][0] - room[0][0], room[2][1] - room[0][1])
	relative_center = relative / 2
	center = room_base + relative_center
	return center

def random_point_in_room(room):
	return random.randrange(room[0][0], room[1][0]), random.randrange(room[0][1], room[2][1])

def area_of_room(room):
  return (room[1][0] - room[0][0]) * (room[2][1] - room[0][1])

class TileType(object):

	def __init__(self, name, footstep_sound):
		self.name = name
		self.footstep_sound = footstep_sound
