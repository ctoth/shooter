from __future__ import division
import collections
import math
from functools import update_wrapper
try:
	from functools import singledispatch
except ImportError:
	from singledispatch import singledispatch

def methdispatch(func):
	dispatcher = singledispatch(func)
	def wrapper(*args, **kw):
		return dispatcher.dispatch(args[1].__class__)(*args, **kw)
	wrapper.register = dispatcher.register
	update_wrapper(wrapper, func)
	return wrapper

class Vector(object):
	__slots__ = ('x', 'y')

	def __init__(self, x=0, y=0):
		self.x=x
		self.y = y

	def __repr__(self):
		return "(%s, %s)" % (self.x, self.y)

	__str__ = __repr__

	@methdispatch
	def __add__(self, other):
		return self.__class__(self.x + other.x, self.y + other.y)

	@__add__.register(collections.Sequence)
	def __add_seq__(self, other):
		return self + self.__class__(*other)

	@methdispatch
	def __radd__(self, other):
		return self.__class__(other.x + self.x, other.y + self.y)

	@__radd__.register(collections.Sequence)
	def __radd_seq(self, other):
		return self.__class__(*other) + self

	@methdispatch
	def __mul__(self, other):
		return self.__class__(self.x * other.x, self.y * other.y)

	@__mul__.register(collections.Sequence)
	def __mul_seq__(self, other):
		return self * Vector(*other)

	@__mul__.register(int)
	@__mul__.register(float)
	def __mul_num__(self, other):
		return self.__class__(self.x * other, self.y * other)

	@methdispatch
	def __sub__(self, other):
		return self.__class__(self.x - other.x, self.y - other.y)

	@__sub__.register(collections.Sequence)
	def __sub_seq__(self, other):
		return self - self.__class__(*other)

	@methdispatch
	def __rsub__(self, other):
		return self.__class__(other.x - self.x, other.y - self.y)

	@__rsub__.register(collections.Sequence)
	def __rsub_seq(self, other):
		return self.__class__(*other) - self


	@methdispatch
	def __truediv__(self, other):
		return self.__class__(self.x / other.x, self.y / other.y)

	__div__ = __truediv__

	@__truediv__.register(int)
	@__truediv__.register(float)
	def __div_num__(self, other):
		return self.__class__(self.x / other, self.y / other)

	@__truediv__.register(collections.Sequence)
	def __truediv_seq__(self, other):
		return self / self.__class__(*other)

	@methdispatch
	def __rtruediv__(self, other):
		return self / other

	@__rtruediv__.register(float)
	@__rtruediv__.register(int)
	def __rdiv_num__(self, other):
		return self.__class__(other / self.x, other / self.y)

	@methdispatch
	def dot(self, other):
		return self.x * other.x + self.y * other.y

	@dot.register(collections.Sequence)
	def dot_seq(self, other):
		return self.dot(self.__class__(*other))

	def to_angle(self):
		return math.degrees(math.atan2(self.x, self.y)) % 360

	@classmethod
	def from_angle(cls, angle):
		return cls(*(math.sin(math.radians(angle)), math.cos(math.radians(angle))))

	def angle_between(self, other):
		return (other - self).to_angle()

	def magnitude(self):
		return math.sqrt(self.x **2 + self.y ** 2)

	def distance(self, other):
		return (self - other).magnitude()

	def normalize(self):
		return self / self.magnitude()

	def __getitem__(self, index):
		if index < 0 or index > 1:
			raise IndexError("This is only a 2d vector")
		return self.x if not index else self.y

	def __len__(self):
		return 2

	def as_ints(self):
		return int(self.x), int(self.y)

if __name__ == '__main__':
	v = Vector(1, 1)
	v = v * 2
