import entity
import game
import math_utils
import libaudioverse

class NPC(entity.Entity):
	visibility_distance = 30
	activation_distance = 30

	def __init__(self, aggressive=True, ambient='monster/ambient', attack_sound='monster/attack', corpse_fall_sound='corpse/generic', destroy_sound='monster/death', *args, **kwargs):
		super(NPC, self).__init__(destroy_sound=destroy_sound, *args, **kwargs)
		self.aggressive = aggressive
		self.ambient = ambient
		self.ambient_sound = None
		if ambient is not None:
			self.ambient_sound = game.sound_manager.play(self.ambient, source=self.occlusion_filter, looping=True)
			self.ambient_sound.pause()
		self.attack_sound = attack_sound
		self.corpse_fall_sound = corpse_fall_sound
		self.target = None
		self.attacking = False
		self.is_being_attacked = False

	def tick(self):
		if math_utils.distance(self.position, game.player.position) > self.activation_distance:
			self.sound_source.state = libaudioverse.NodeStates.paused
			if self.weapon is not None:
				self.weapon.sound_source.state = libaudioverse.NodeStates.paused
			return
		self.sound_source.state = libaudioverse.NodeStates.playing
		if self.weapon is not None:
			self.weapon.sound_source.state = libaudioverse.NodeStates.playing
		if self.ambient_sound is not None and not self.ambient_sound.is_playing():
			self.ambient_sound.play()
		super(NPC, self).tick()
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
		else:
			self.target = None

	def attack_target(self):
		self.face_target()
		self.perform_attack()

	def face_target(self):
		self.facing = math_utils.vec_to_angle(math_utils.vec_sub(self.target.position, self.position))

	def perform_attack(self):
		self.fire_weapon()

	def act_normally(self):
		pass

	def destroy(self):
		try:
			game.map.npcs.remove(self)
		except ValueError:
			pass
		position = self.position
		game.clock.schedule_once(self.play_corpse_fall, 0.5, position=position)
		super(NPC, self).destroy()

	def take_damage(self, amount):
		self.is_being_attacked = True
		super(NPC, self).take_damage(amount)

	def play_corpse_fall(self, t, position):
		game.sound_manager.play_async(self.corpse_fall_sound, *position)
