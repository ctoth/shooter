from __future__ import division
import game
from Box2D import b2

class GameObject(object):

	def __init__(self, name="", world=None, shape='box', size=(1, 1), location=None, position=(2, 2), facing=0, mass=1, fixed=True, sound_source=None, sound=None, use_sound=None, destroy_sound=None, destructable=True, *args, **kwargs):
		super(GameObject, self).__init__(*args, **kwargs)
		self.world = world
		self.name = name
		self.shape = shape
		self.size = tuple(size)
		self.location = location
		self.contents = []
		self.fixed = fixed
		self.body = None
		self.mass = mass
		if location is None:
			self.create_body(position=position)
			self.create_fixture()
		if sound_source is None:
			sound_source = game.sound_manager.create_source()
		self.sound_source = sound_source
		if sound is not None:
			sound = game.sound_manager.play(sound, source=self.sound_source, looping=True)
		self.sound = sound
		self.destroy_sound = destroy_sound
		self.use_sound = use_sound
		self.position = position
		self.facing = facing
		self.destructable = destructable

	def create_body(self, position=None):
		size = self.size[0] / 2, self.size[1] / 2
		if position is None:
			position = (0, 0)
		self.body = self.world.world.CreateStaticBody(userData=self, position=position)

	def create_fixture(self):
		density=1
		friction=1.0
		restitution=0.0
		if self.shape == 'circle':
			self.fixture = self.body.CreateCircleFixture(radius=self.size[0], density=density, friction=friction, restitution=restitution)
		elif self.shape == 'box':
			self.fixture= self.body.CreatePolygonFixture(box=self.size, density=density, friction=friction, restitution=restitution)
		self.body.mass = self.mass

	@property
	def position(self):
		if self.location is not None:
			return self.location.position
		return tuple(self.body.position)

	@position.setter
	def position(self, position):
		self.body.position = tuple(position)
		self.set_sound_position()

	def set_sound_position(self):
		if self.sound_source.head_relative.value:
			return
		position = [float(i) for i in self.position]
		position.append(0.0)
		self.sound_source.position = position

	@property
	def facing(self):
		if self.location is not None:
			return self.location.facing
		return self.body.angle

	@facing.setter
	def facing(self, facing):
		self.body.angle = facing

	def destroy(self):
		[self.remove(i) for i in self.contents]
		if self.destroy_sound is not None:
			game.sound_manager.play_async(self.destroy_sound, *self.position)
		if game.player.radar.tracking is self:
			game.player.radar.stop_tracking()
			game.player.radar.tracking = None
		if self.location is not None:
			self.location.remove_item(self)
		self.world.destroy(self)

	def handle_collision(self, other):
		print "collision", self.position, self, other

	def use(self, user):
		if self.use_sound is not None:
			game.sound_manager.play(self.use_sound, source=self.sound_source)

	def take_damage(self, amount):
		if self.destructable:
			self.destroy()

	def destroy_body(self):
		game.world.remove_body_from_world(self.body)
		self.body = None

	def hold(self, other):
		if other.body is not None:
			other.destroy_body()
		self.contents.append(other)
		other.location = self


	def remove(self, other):
		self.contents.remove(other)
		other.location = self.location
		game.world.create_body_next_tick(other, position=self.position)

