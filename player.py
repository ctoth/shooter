import math
import attr
import entity
import game
import libaudioverse


class Player(entity.Entity):
	TURN_RATE = 1.0
	FOOTSTEP_SPEED = 0.5
	FOOTSTEP_DELAY = 0.3
	footstep_multiplier = 3.0

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
		if self.moving is None:
			self.body.linearVelocity = (0, 0)
		if magnitude(*self.body.linearVelocity) >= self.FOOTSTEP_SPEED:
			if self.last_footstep_time + self.FOOTSTEP_DELAY <= game.clock.time():
				self.footstep_sound = game.sound_manager.play('footstep.wav', source=self.sound_source)
				self.last_footstep_time = game.clock.time()
		else:
			self.body.linearVelocity = (0, 0)
		if self.moving == 'forward':
			self.body.linearVelocity = self.footstep_multiplier * math.cos(math.radians(self.facing)), self.footstep_multiplier * math.sin(math.radians(self.facing))
		elif self.moving == 'backward':
			facing = (self.facing - 180) % 360
			self.body.linearVelocity = self.footstep_multiplier * math.cos(math.radians(facing)), self.footstep_multiplier * math.sin(math.radians(facing))

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

	def start_attacking(self):
		pass

	def stop_attacking(self):
		pass

	def read_coordinates(self):
		game.output.output("%.2f, %.2f" % (self.position[0], self.position[1]))

def magnitude(*v):
	return math.sqrt(sum([i**2 for i in v]))
