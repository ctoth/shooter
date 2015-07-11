import math
import attr
import entity
import game
import libaudioverse


class Player(entity.Entity):
	TURN_RATE = 1.0
	FOOTSTEP_SPEED = 1.0
	FOOTSTEP_DELAY = 0.31

	def __init__(self, size=(0.5, 0.5), *args, **kwargs):
		super(Player, self).__init__(size=size, *args, **kwargs)
		self.moving = False
		self.turning = None
		self.last_footstep_time = 0

	def set_sound_position(self):
		position = self.position
		game.sound_manager.world.position.value = [position[0], 0, position[1]]
		orientation = list(game.sound_manager.world.orientation.value)
		orientation[0] = math.cos(math.radians(self.facing))
		orientation[2] = math.sin(math.radians(self.facing))
		game.sound_manager.world.orientation.value = orientation
		super(Player, self).set_sound_position()


	def tick(self):
		if self.turning == 'left':
			self.facing -= self.TURN_RATE
		elif self.turning == 'right':
			self.facing += self.TURN_RATE
		self.facing %= 360
		if not self.moving:
			return
		if magnitude(*self.body.linearVelocity) >= self.FOOTSTEP_SPEED:
			if self.last_footstep_time + self.FOOTSTEP_DELAY <= game.clock.time():
				self.footstep_sound = game.sound_manager.play('footstep.wav', source=self.sound_source)
				self.last_footstep_time = game.clock.time()
		if self.moving == 'forward':
			self.body.linearVelocity = math.cos(math.radians(self.facing)), math.sin(math.radians(self.facing))
		elif self.moving == 'backward':
			facing = (self.facing - 180) % 360
			self.body.linearVelocity = math.cos(math.radians(facing)), math.sin(math.radians(facing))

	def start_forward(self):
		self.moving = 'forward'

	def stop_moving(self):
		self.moving = None

	def start_backward(self):
		self.moving = 'backward'


	def turn_left(self):
		self.turning = 'left'

	def turn_right(self):
		self.turning = 'right'

	def stop_turning(self):
		self.turning = None

def magnitude(*v):
	return math.sqrt(sum([i**2 for i in v]))
