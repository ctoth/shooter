from __future__ import division
import game
from Box2D import b2

class GameObject(object):

	def __init__(self, name="", world=None, size=(1, 1), location=None, position=(2, 2), facing=0, mass=1, fixed=True, sound_source=None, sound=None, use_sound=None, destroy_sound=None, destructable=True, *args, **kwargs):
		super(GameObject, self).__init__(*args, **kwargs)
		self.world = world
		self.name = name
		self.size = tuple(size)
		self.location = location
		self.fixed = fixed
		self.create_body()
		self.body.mass = mass
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


	def create_body(self):
		size = self.size[0] / 2, self.size[1] / 2
		self.shape = b2.polygonShape(box=size)
		self.body = self.world.world.CreateStaticBody(shapes=self.shape, userData=self)

	@property
	def position(self):
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
		return self.body.angle

	@facing.setter
	def facing(self, facing):
		self.body.angle = facing

	def destroy(self):
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

	def use(self):
		if self.use_sound is not None:
			game.sound_manager.play(self.use_sound, source=self.sound_source)

	def take_damage(self, amount):
		if self.destructable:
			self.destroy()

