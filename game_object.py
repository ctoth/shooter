import game
from Box2D import b2

class GameObject(object):

	def __init__(self, world=None, name="", size=(1, 1), position=(2, 2), facing=0, fixed=True, sound=None, *args, **kwargs):
		super(GameObject, self).__init__(*args, **kwargs)
		self.name = name
		self.world = world
		self.size = size
		self.fixed = fixed
		self.create_body()
		self.sound_source = game.sound_manager.create_source()
		if sound is not None:
			sound = game.sound_manager.play(sound, source=self.sound_source, looping=True)
		self.sound = sound
		self.position = position
		self.facing = facing

	def create_body(self):
		self.shape = b2.polygonShape(box=self.size)
		self.body = self.world.world.CreateStaticBody(shapes=self.shape)

	@property
	def position(self):
		return self.body.position

	@position.setter
	def position(self, position):
		self.body.position = position
		self.set_sound_position()


	def set_sound_position(self):
		position = [float(i) for i in self.position]
		position.insert(1, 0.0)
		self.sound_source.position.value = position

	@property
	def facing(self):
		return self.body.angle

	@facing.setter
	def facing(self, facing):
		self.body.angle = facing
