import attr

@attr.s(init=False)
class GameObject(object):
	name = attr.ib(default="")
	size = attr.ib(default=attr.Factory(lambda: (1, 1)))
	world = attr.ib(default=None)
	fixed = attr.ib(default=False)

	def __init__(self, world=None, name="", size=(1, 1), fixed=True, sound=None, *args, **kwargs):
		super(GameObject, self).__init__(*args, **kwargs)
		self.name = name
		self.world = world
		self.size = size
		self.fixed = fixed
		if sound is not None:
			sound = game.sound_manager.play(sound, looping=True)
		self.sound = sound
