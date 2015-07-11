import attr
import game

@attr.s
class Weapon(object):
	base_damage = attr.ib(default=0)
	range = attr.ib(default=0)
	cooldown = attr.ib(default=0.0)
	last_used = attr.ib(default=0)

	def can_use(self):
		return self.last_used + self.cooldown < game.clock.time()
