import attr

@attr.s
class GameObject(object):
	name = attr.ib(default="")
	size = attr.ib(default=attr.Factory(lambda: [1, 1]))
	world = attr.ib(default=None)
	sound = attr.ib(default=None)
	fixed = attr.ib(default=False)
