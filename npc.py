import entity
import game
import math_utils

class NPC(entity.Entity):
	visibility_distance = 30
	activation_distance = 30
	corpse_fall_sound = 'corpse/metal'

	def __init__(self, aggressive=True, ambient='monster/ambient', attack_sound='monster/attack', destroy_sound='monster/death', *args, **kwargs):
		super(NPC, self).__init__(destroy_sound=destroy_sound, *args, **kwargs)
		self.aggressive = aggressive
		self.ambient = ambient
		self.ambient_sound = None
		if ambient is not None:
			self.ambient_sound = game.sound_manager.play(self.ambient, source=self.sound_source, looping=True)
			self.ambient_sound.pause()
		self.attack_sound = attack_sound
		self.target = None
		self.attacking = False

	def tick(self):
		if math_utils.distance(self.position, game.player.position) > self.activation_distance:
			return
		if self.ambient_sound is not None and not self.ambient_sound.is_playing():
			self.ambient_sound.play()
		self.set_sound_position()
		if self.aggressive:
			self.find_target()
		if self.target:
			if not self.attacking:
				game.sound_manager.play(self.attack_sound, source=self.sound_source, position=self.position)
				self.attacking = True
			self.attack_target()
		else:
			self.act_normally()

	def find_target(self):
		if self.world.is_visible(self, game.player, self.visibility_distance):
			self.target = game.player

	def attack_target(self):
		self.face_target()
		self.perform_attack()

	def face_target(self):
		self.facing = math_utils.vec_to_angle(math_utils.vec_sub(self.target.position, self.position))

	def perform_attack(self):
		pass

	def act_normally(self):
		pass

	def destroy(self):
		game.map.npcs.remove(self)
		game.clock.schedule_once(self.play_corpse_fall, 0.1, position=self.position)
		super(NPC, self).destroy()

	def play_corpse_fall(self, t, position):
		game.sound_manager.play_async(self.corpse_fall_sound, *position)