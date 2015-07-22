from __future__ import division
import math

def angle_to_vec(angle):
	return math.sin(math.radians(angle)), math.cos(math.radians(angle))

def vec_to_angle(vec):
	return math.degrees(math.atan2(*vec))


def vec_mul(vec, amount):
	return [i*amount for i in vec]

def vec_div(vec1, amount):
	return [i/amount for i in vec1]

def vec_add(vec1, vec2):
	return [i+j for i, j in zip(vec1, vec2)]

def vec_sub(vec1, vec2):
	return [i-j for i, j in zip(vec1, vec2)]

def percentage(what, percent):
	return (what / 100.0) * percent

def inverse_percentage(what, percent):
	return 100.0 / 100.0 / what * percent

def vec_round(vec):
	return [int(i) for i in vec]

def vec_dot(v1, v2):
  return sum([i*j for i,j in zip(v1, v2)])

def magnitude(*v):
	return math.sqrt(sum([i**2 for i in v]))

def vec_magnitude(v):
	return magnitude(*v)

def distance(v1, v2):
	return vec_magnitude(vec_sub(v2, v1))
