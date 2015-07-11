import attr
import entity
import game

class Player(entity.Entity):

	def __init__(self, size=(0.5, 0.5), *args, **kwargs):
		super(Player, self).__init__(size=size, *args, **kwargs)

	def set_sound_position(self):
		super(Player, self).set_sound_position()
		position = self.position
		game.sound_manager.world.position.value = [position[0], 0, position[1]]
