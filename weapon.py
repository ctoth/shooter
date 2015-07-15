import attr
import entity
import game
import game_object
from math_utils import *

@attr.s
class Weapon(entity.Entity):
	base_damage = attr.ib(default=1.0)
	range = attr.ib(default=1.0)
	cooldown = attr.ib(default=0.5)
	last_used = attr.ib(default=0)
	max_uses = attr.ib(default=0)
	current_uses = attr.ib(default=0)

	def can_use(self):
		if self.max_uses and self.current_uses >= self.max_uses:
			return False
		return self.last_used + self.cooldown < game.clock.time()

	def use(self):
		super(Weapon, self).use()
		self.last_used = game.clock.time()

@attr.s
class Ammunition(game_object.GameObject):
	shots = attr.ib(default=1)

class Projectile(entity.Entity):

	def __init__(self, weapon=None, size=(0.01, 0.01), *args, **kwargs):
		super(Projectile, self).__init__(size=size, *args, **kwargs)
		self.weapon = weapon

	def create_body(self):
		super(Projectile, self).create_body()
		self.body.bullet = True
		self.box.friction = 0

	def handle_colision(self, other):
		print self.position
		self.set_sound_position()
		print other
		hit_sound = other.damage_sound
		game.sound_manager.play(hit_sound, source=self.sound_source)
		self.destroy()


class ProjectileWeapon(Weapon):
	BULLET_DISCARD_DELAY = 10

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


