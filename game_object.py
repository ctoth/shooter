from __future__ import division
from logging import getLogger
logger = getLogger('game_object')
from math import sqrt
import collections
import game

from Box2D import b2
from vector import Vector

class GameObject(object):

	def __init__(self, name="", world=None, shape='box', size=(0.5, 0.5), location=None, position=(2, 2), facing=0, mass=1, fixed=True, solid=True, sound=None, use_sound=None, destroy_sound=None, destructable=True, collide_sound=None, head_relative=False, *args, **kwargs):
		super(GameObject, self).__init__(*args, **kwargs)
		self.world = world
		self.world.add_object(self)
		self.name = name
		self.shape = shape
		self.size = tuple(size)
		self.location = location
		self.contents = []
		self.fixed = fixed
		self.solid = solid
		self.head_relative = head_relative
		self.body = None
		self.mass = mass
		if location is None:
			self.create_body(position=position)
			self.create_fixture()
		self.last_played_times = collections.defaultdict(int)
		self.sound_source = None
		if sound is not None:
			sound = self.play_sound(sound, looping=True)
		self.sound = sound
		self.destroy_sound = destroy_sound
		self.use_sound = use_sound
		self.collide_sound = collide_sound
		self.position = position
		self.facing = facing
		self.destructable = destructable

	def create_body(self, position=None):
		size = self.size[0] / 2, self.size[1] / 2
		if position is None:
			position = (0, 0)
		self.body = self.world.world.CreateStaticBody(userData=self, position=position)

	def create_fixture(self):
		size = self.size[0] / 2, self.size[1] / 2
		density=1
		friction=1.0
		restitution=0.0
		if self.shape == 'circle':
			self.fixture = self.body.CreateCircleFixture(radius=size[0], density=density, friction=friction, restitution=restitution)
		elif self.shape == 'box':
			self.fixture= self.body.CreatePolygonFixture(box=size, density=density, friction=friction, restitution=restitution)
		self.fixture.sensor = not self.solid
		self.body.mass = self.mass

	@property
	def position(self):
		if self.location is not None:
			return self.location.position
		return Vector(*self.body.position)

	@position.setter
	def position(self, position):
		self.body.position = tuple(position)
		if self.sound_source is not None:
			self.set_sound_position()

	@property
	def velocity(self):
		return Vector(*self.body.linearVelocity)

	@velocity.setter
	def velocity(self, velocity):
		self.body.linearVelocity = velocity

	def set_sound_position(self):
		if self.head_relative:
			self.sound_source.head_relative.value = self.head_relative
			self.sound_source.position = (0, 0, 0)
			return
		position = self.position
		self.sound_source.position.value = position[0], position[1], 0.0

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
			self.play_async_after(0.0, self.destroy_sound, *self.position)
		if game.player.radar.tracking is self:
			game.player.radar.stop_tracking()
			game.player.radar.tracking = None
		if self.location is not None:
			self.location.remove_item(self)
		self.world.destroy(self)

	def handle_collision(self, other):
		logger.debug("collision: %s %s %s" % (self.position, self, other))

	def use(self, user):
		if self.use_sound is not None:
			self.play_sound(self.use_sound)

	def can_use(self):
		return False

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

	def __unicode__(self):
		return self.name

	def __str__(self):
		return self.name

	def play_async_after(self, delay, *args, **kwargs):
		game.clock.schedule_once(lambda dt,: game.sound_manager.play_async(*args, **kwargs), delay)

	def tick(self):
		if self.sound_source is not None:
			self.set_sound_position()
			self.update_audio_occlusion()

	def update_audio_occlusion(self):
		location = self.location
		if location is not None:
			value = location.sound_source.occlusion.value
			self.sound_source.occlusion.value = value
			return
		pos, playerpos = self.position, game.player.position
		if pos == playerpos:
			return
		distance = sqrt((pos[0] - playerpos[0])**2+(pos[1]-playerpos[1])**2)
		if distance  > game.MAX_AUDIO_DISTANCE:
			return
		count = game.world.count_objects_between(pos, playerpos)
		value= min(1.0, 0.15 * count)
		self.sound_source.occlusion.value = value

	def play_sound(self, sound, *args, **kwargs):
		if self.sound_source is None:
			self.setup_sound()
		return game.sound_manager.play(sound, source=self.sound_source, **kwargs)

	def setup_sound(self):
		self.sound_source = game.sound_manager.create_source()
		self.sound_source.head_relative.value = self.head_relative
		self.set_sound_position()

	def only_play_every(self, delay, sound, *args, **kwargs):
		last_played = self.last_played_times[sound]
		if game.clock.time() - last_played < delay:
			return
		self.play_sound(sound, *args, **kwargs)
		self.last_played_times[sound] = game.clock.time()
