import math
import entity
import weapon
import game
import libaudioverse
from math_utils import *


class Player(entity.Entity):
	TURN_RATE = 1.0
	FOOTSTEP_SPEED = 0.5
	FOOTSTEP_DELAY = 0.3
	footstep_multiplier = 3.0

	def __init__(self, size=(0.5, 0.5), mass=100, *args, **kwargs):
		super(Player, self).__init__(size=size, mass=mass, *args, **kwargs)
		self.moving = False
		gun = weapon.ProjectileWeapon(world=self.world, name="Gun", ammo_type="bullet", use_sound='rifle', size=(1, 0.1), position=self.position)
		self.equip(gun)
		self.turning = None
		self.last_footstep_time = 0
		self.attacking = False
		self.sound_source.head_relative = True

	def set_sound_position(self):
		position = list(self.position)
		position = [position[0], 0, position[1]]
		game.sound_manager.world.position.value = position
		orientation = list(game.sound_manager.world.orientation.value)
		orientation[0], orientation[2] = angle_to_vec(self.facing)
		game.sound_manager.world.orientation = orientation

	def tick(self):
		if self.attacking:
			if self.weapon.can_use():
				self.weapon.position = self.position
				self.weapon.facing = self.facing
				self.weapon.use()
		if self.turning == 'left':
			self.facing -= self.TURN_RATE
		elif self.turning == 'right':
			self.facing += self.TURN_RATE	
		self		.facing %= 360
		if magnitude(*self.body.linearVelocity) >= self.FOOTSTEP_SPEED:
			if self.body.contacts and self.body.contacts[0].contact.fixtureB.body.userData:
				print "hit a wall"
				return
			if self.last_footstep_time + self.FOOTSTEP_DELAY <= game.clock.time():
				self.footstep_sound = game.sound_manager.play('footstep.wav', source=self.sound_source)
				self.last_footstep_time = game.clock.time()
		else:
			self.body.linearVelocity = (0, 0)
		if self.moving:
			if self.moving == 'forward':
				facing = self.facing
			elif self.moving == 'right':
				facing = self.facing + 90 % 360
			elif self.moving == 'left':
				facing = self.facing - 90 % 360
			elif self.moving == 'backward':
				facing = (self.facing - 180) % 360
			self.body.linearVelocity = vec_mul(angle_to_vec(facing), self.footstep_multiplier)
		else:
			self.body.linearVelocity = (0, 0)

	def equip(self, item):
		self.weapon = item
		self.world.world.CreateRevoluteJoint(bodyA=self.body, bodyB=item.body, anchorPOint=self.body.worldCenter)
		item.sound_source.head_relative = True
		item.sound_source.position = (0, 0, 0)

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
		self.attacking = True


	def stop_attacking(self):
		self.attacking = False

	def strafe_left(self):
		self.moving = 'left'

	def strafe_right(self):
		self.moving = 'right'

	def stop_strafing(self):
		self.moving = None

	def read_coordinates(self):
		game.output.output("%.2f, %.2f" % (self.position[0], self.position[1]))

	def read_facing(self):
		game.output.output("%d degrees" % self.facing)

def magnitude(*v):
	return math.sqrt(sum([i**2 for i in v]))
