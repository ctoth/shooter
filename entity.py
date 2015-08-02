from __future__ import division
import game
import game_object

class Entity(game_object.GameObject):

	def __init__(self, health=100, speed=100, angle_of_visibility=180, hit_sound=None, weapon=None, *args, **kwargs):
		super(Entity, self).__init__(*args, **kwargs)
		self.health = health
		self.speed = speed
		self.angle_of_visibility = angle_of_visibility
		self.weapon = None
		if weapon is not None:
			self.equip(weapon)
		self.hit_sound = hit_sound

	def create_body(self, position=None):
		if position is None:
			position = (0, 0)
		self.body = self.world.world.CreateDynamicBody(userData=self, position=position, angularDamping=1.0)

	def equip(self, item):
		self.hold(item)
		self.weapon = item

		item.location = self


	def fire_weapon(self):
		if self.weapon is not None and self.weapon.can_use():
			self.weapon.use(user=self)

	def take_damage(self, amount):
		self.health -= amount
		if self.health <= 0:
			self.destroy()
		else:
			if self.hit_sound is not None:
				game.clock.schedule_once(self.play_hit_sound, 0.1)

	def play_hit_sound(self, t):
		game.sound_manager.play(self.hit_sound, source=self.sound_source, position=self.position)
