import entity
import game
import game_object
import room
from math_utils import *

class Weapon(entity.Entity):

	def __init__(self, base_damage=1.0, range=1.0, cooldown=1.0, last_used=0, max_uses=0, current_uses=0, *args, **kwargs):
		super(Weapon, self).__init__(*args, **kwargs)
		self.base_damage = base_damage
		self.range = range
		self.cooldown = cooldown
		self.last_used = last_used
		self.max_uses = max_uses
		self.current_uses = current_uses

	def can_use(self):
		if self.max_uses and self.current_uses >= self.max_uses:
			return False
		return self.last_used + self.cooldown < game.clock.time()

	def use(self):
		super(Weapon, self).use()
		self.last_used = game.clock.time()

class Ammunition(game_object.GameObject):
	pass


class Projectile(entity.Entity):
	ricochet_sound = 'ricochet'

	def __init__(self, weapon=None, size=(0.01, 0.01), *args, **kwargs):
		super(Projectile, self).__init__(size=size, *args, **kwargs)
		self.weapon = weapon

	def create_body(self):
		super(Projectile, self).create_body()
		self.body.bullet = True
		self.box.friction = 0

	def handle_colision(self, other):
		self.set_sound_position()
		print other

		if other.destructable and hasattr(other, 'destroy'):
			other.destroy()
		elif isinstance(other, room.Room):
			game.sound_manager.play_async(self.ricochet_sound, *self.position)
		try:
			self.weapon.fired.remove(self)
		except KeyError: #happens because of double colisions sometimes
			pass
		self.destroy()

class ProjectileWeapon(Weapon):

	def __init__(self, ammo_type="", speed=300, *args, **kwargs):
		super(ProjectileWeapon, self).__init__(*args, **kwargs)
		self.ammo_type = ammo_type
		self.speed = speed
		self.fired = set()

	def use(self):
		super(ProjectileWeapon, self).use()
		position = list(self.position)
		position = vec_add(position, vec_mul(angle_to_vec(self.facing), self.size[0] + 0.1))
		bullet = Projectile(world=self.world, name=self.ammo_type, weapon=self, position=position, facing=self.facing)
		self.shoot(bullet) 
		return bullet

	def shoot(self, bullet):
		direction = angle_to_vec(self.facing)
		velocity = vec_mul(direction, self.speed)
		bullet.body.ApplyLinearImpulse(velocity, self.body.worldCenter, True)
		self.fired.add(bullet)

