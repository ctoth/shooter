import math

def angle_to_vec(angle):
	return math.sin(math.radians(angle)), math.cos(math.radians(angle))

def vec_mul(vec, amount):
	return [i*amount for i in vec]

def vec_add(vec1, vec2):
	return [i+j for i, j in zip(vec1, vec2)]
