import attr
import entity
import game

class Player(entity.Entity):
	pass

	def set_sound_position(self):
		super(Player, self).set_sound_position()
		position = self.position
		game.sound_manager.world.position.value = [position[0], 0, position[1]]