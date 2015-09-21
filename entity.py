from __future__ import division
import game
import game_object

class Entity(game_object.GameObject):
	turn_rate = 0.8

	def __init__(self, health=100, speed=100, angle_of_visibility=180, damage_sound=None, weapon=None, *args, **kwargs):
		super(Entity, self).__init__(*args, **kwargs)
		self.health = health
		self.speed = speed
		self.angle_of_visibility = angle_of_visibility
		self.weapon = None
		if weapon is not None:
			self.equip(weapon)
		self.damage_sound = damage_sound

	def create_body(self, position=None):
		if position is None:
			position = (0, 0)
		self.body = self.world.world.CreateDynamicBody(userData=self, position=position, angularDamping=1.0, fixedRotation=True)

	def equip(self, item):
		if item not in self.contents:
			self.hold(item)
		self.weapon = item

	def fire_weapon(self):
		if self.weapon is not None and self.weapon.can_use():
			self.weapon.use(user=self)

	def take_damage(self, amount):
		self.health -= amount
		if self.health <= 0:
			self.destroy()
		else:
			if self.damage_sound is not None:
				game.clock.schedule_once(self.play_damage_sound, 0.15, self.position)

	def play_damage_sound(self, t, position):
		game.sound_manager.play(self.damage_sound, source=self.sound_source, position=position)
