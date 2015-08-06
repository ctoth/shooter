import entity
import game
import game_object
import room
import world
from math_utils import *

class Weapon(entity.Entity):

	def __init__(self, base_damage=10.0, range=1.0, cooldown=1.0, last_used=0, max_uses=0, current_uses=0, fixed=False, hit_sound=None, hit_wall_sound=None, equip_sound='hands.ogg', *args, **kwargs):
		super(Weapon, self).__init__(fixed=fixed, *args, **kwargs)
		self.base_damage = base_damage
		self.range = range
		self.cooldown = cooldown
		self.last_used = last_used
		self.max_uses = max_uses
		self.current_uses = current_uses
		self.hit_sound = hit_sound
		self.hit_wall_sound = hit_wall_sound
		self.equip_sound = equip_sound


	def can_use(self):
		if self.max_uses and self.current_uses >= self.max_uses:
			return False
		return self.last_used + self.cooldown < game.clock.time()

	def use(self, user):
		super(Weapon, self).use(user)
		self.last_used = game.clock.time()

	def did_hit(self, target, position):
		if hasattr(target, 'take_damage'):
			if self.hit_sound is not None:
				game.sound_manager.play_async(self.hit_sound, *position)
			target.take_damage(self.base_damage)
		elif isinstance(target, world.World):
			if self.hit_wall_sound is not None:
				game.sound_manager.play_async(self.hit_wall_sound, *position)

class Ammunition(game_object.GameObject):
	pass


class Projectile(entity.Entity):

	def __init__(self, weapon=None, size=(0.01, 0.01), shape='circle', mass=0.1, *args, **kwargs):
		super(Projectile, self).__init__(size=size, shape=shape, mass=mass, *args, **kwargs)
		self.weapon = weapon

	def create_body(self, position=None):
		super(Projectile, self).create_body(position=position)
		self.body.bullet = True

	def handle_collision(self, other):
		self.set_sound_position()
		self.weapon.did_hit(other, self.position)
		try:
			self.weapon.fired.remove(self)
		except KeyError: #happens because of double collisions sometimes
			pass
		self.destroy()

class ProjectileWeapon(Weapon):

	def __init__(self, ammo_type="", speed=300, hit_wall_sound='ricochet', *args, **kwargs):
		super(ProjectileWeapon, self).__init__(hit_wall_sound=hit_wall_sound, *args, **kwargs)
		self.ammo_type = ammo_type
		self.speed = speed
		self.fired = set()
		self.body.fixtures[0].sensor = True

	def use(self, user):
		super(ProjectileWeapon, self).use(user)
		position = list(self.position)
		position = vec_add(position, vec_mul(angle_to_vec(self.facing), self.size[0] + 0.1))
		bullet = Projectile(world=self.world, name=self.ammo_type, weapon=self, position=position, facing=self.facing)
		self.shoot(bullet) 
		return bullet

	def shoot(self, bullet):
		direction = angle_to_vec(self.facing)
		velocity = vec_mul(direction, self.speed)
		bullet.body.ApplyLinearImpulse(velocity, self.position, True)
		self.fired.add(bullet)

class DirectWeapon(Weapon):

	def use(self, user):
		super(DirectWeapon, self).use(user)
		targets = self.world.ray_cast(self.position, direction=self.facing, length=self.range)
		if not targets:
			return
		target = targets[0]
		other = target.userData
		self.did_hit(other, target.position)

class BeamWeapon(DirectWeapon):
	pass

class BladedWeapon(DirectWeapon):
	pass

