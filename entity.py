from __future__ import division
import game
import game_object

class Entity(game_object.GameObject):

	def __init__(self, health=100, speed=100, hit_sound=None, *args, **kwargs):
		super(Entity, self).__init__(*args, **kwargs)
		self.health = health
		self.speed = speed
		self.weapon = None
		self.hit_sound = hit_sound

	def create_body(self):
		self.body = self.world.world.CreateDynamicBody(userData=self)
		size = self.size[0] / 2, self.size[1] / 2
		self.box= self.body.CreatePolygonFixture(box=size, density=1, friction=1.0, restitution=0.0)

	def equip(self, item):
		self.weapon = item
		self.world.world.CreateRevoluteJoint(bodyA=self.body, bodyB=item.body, anchorPoint=self.body.worldCenter)

	def fire_weapon(self):
		if self.weapon is not None and self.weapon.can_use():
			self.weapon.position = self.position
			self.weapon.facing = self.facing
			self.weapon.use()

	def take_damage(self, amount):
		self.health -= amount
		if self.health <= 0:
			self.destroy()
		else:
			if self.hit_sound is not None:
				game.clock.schedule_once(self.play_hit_sound, 0.3)

	def play_hit_sound(self, t):
		game.sound_manager.play(self.hit_sound, source=self.sound_source, position=self.position)
