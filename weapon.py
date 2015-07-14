import attr
import game
import game_object

@attr.s
class Weapon(game_object.GameObject):
	base_damage = attr.ib(default=1.0)
	range = attr.ib(default=0.5)
	cooldown = attr.ib(default=1.0)
	last_used = attr.ib(default=0)
	max_uses = attr.ib(default=0)
	current_uses = attr.ib(default=0)

	def can_use(self):
		if self.max_uses and self.current_uses >= self.max_uses:
			return False
		return self.last_used + self.cooldown < game.clock.time()

	def use(self):
		pass
