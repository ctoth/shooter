import game_object
import game

class HealthBoost(game_object.GameObject):

	def __init__(self, uses=1, heal_amount=25, *args, **kwargs):
		super(HealthBoost, self).__init__(*args, **kwargs)
		self.uses = uses
		self.current_uses = 0
		self.heal_amount  = heal_amount

	def can_use(self):
		return self.current_uses < self.uses

	def use(self, user):
		user.health += self.heal_amount
		self.current_uses += 1

class Staircase(game_object.GameObject):

	def can_use(self):
		return True

	def use(self, user):
		game.output.output("Used the staircase, yea!")

