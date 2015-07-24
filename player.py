import math
import entity
import game
import radar
import room
import tiles
import weapon
import world
from math_utils import *


class Player(entity.Entity):
	TURN_RATE = 0.5
	FOOTSTEP_SPEED = 0.5
	FOOTSTEP_DELAY = 0.3
	footstep_multiplier = 3.0
	running_multiplier = 1.5
	ping_distance = 50
	approach_distance = 1.0

	def __init__(self, size=(0.5, 0.5), mass=100, *args, **kwargs):
		super(Player, self).__init__(size=size, mass=mass, *args, **kwargs)
		self.moving = False
		gun = weapon.ProjectileWeapon(world=self.world, name="Gun", ammo_type="bullet", use_sound='rifle', size=(1, 0.1), position=self.position, cooldown=0.5, mass=30)
		self.equip(gun)
		self.turning = None
		self.running = False
		self.last_footstep_time = 0
		self.attacking = False
		self.sound_source.head_relative = True
		self.radar = radar.Radar(looker=self)
		self.walking_toward = None


	def set_sound_position(self):
		position = list(self.position)
		position.append(0.0)
		game.sound_manager.world.position = position
		orientation = list(game.sound_manager.world.orientation.value)
		orientation[0], orientation[1] = angle_to_vec(self.facing)
		game.sound_manager.world.orientation = orientation

	def tick(self):
		self.radar.tick()
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
		speed = self.speed
		if self.running:
			speed *= self.running_multiplier
		if magnitude(*self.body.linearVelocity) >= self.FOOTSTEP_SPEED:
			if self.body.contacts and self.body.contacts[0].contact.fixtureB.body.userData == 'wall':
				return
			slowdown_multiplier = inverse_percentage(speed, 100)
			if self.last_footstep_time + (self.FOOTSTEP_DELAY*slowdown_multiplier) <= game.clock.time():
				self.footstep_sound = game.sound_manager.play(self.get_footstep_sound(), source=self.sound_source)
				self.last_footstep_time = game.clock.time()
		else:
			self.body.linearVelocity = (0, 0)
		if self.walking_toward:
			if distance(self.walking_toward, self.position) > self.approach_distance:
				self.moving = 'forward'
			else:
				self.moving = False
				self.walking_toward = None
		if self.moving:
			if self.moving == 'forward':
				facing = self.facing
			elif self.moving == 'right':
				facing = self.facing + 90 % 360
			elif self.moving == 'left':
				facing = self.facing - 90 % 360
			elif self.moving == 'backward':
				facing = (self.facing - 180) % 360
			self.body.linearVelocity = vec_mul(angle_to_vec(facing), percentage(self.footstep_multiplier, speed))
		else:
			self.body.linearVelocity = (0, 0)

	def equip(self, item):
		self.weapon = item
		self.world.world.CreateRevoluteJoint(bodyA=self.body, bodyB=item.body, anchorPoint=self.body.worldCenter)
		item.sound_source.head_relative = True
		item.sound_source.position = (0, 0, 0)

	def get_footstep_sound(self):
		return 'footsteps/metal'

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

	def start_running(self):
		self.running = True

	def stop_running(self):
		self.running = False

	def snap_left(self):
		if self.facing > 0 and self.facing <= 90:
			self.facing = 0
		elif self.facing > 90 and self.facing <= 180:
			self.facing = 90
		elif self.facing > 180 and self.facing <= 270:
			self.facing = 180
		elif self.facing > 270 or self.facing <= 0:
			self.facing = 270

	def snap_right(self):
		if self.facing < 90:
			self.facing = 90
		elif self.facing < 180:
			self.facing = 180
		elif self.facing < 270:
			self.facing = 270
		elif self.facing < 360:
			self.facing = 0


	def read_coordinates(self):
		game.output.output("%.2f, %.2f" % (self.position[0], self.position[1]))

	def read_facing(self):
		game.output.output("%d degrees" % self.facing)

	def do_ping(self):
		los = self.world.ray_cast(self.position, direction=self.facing, length=self.ping_distance)
		visible = []
		for item in los:
			position = item.position
			distance = magnitude(*vec_sub(self.position, position))
			if isinstance(item.userData, world.World):
				message = "wall: %.2f meters. %.2f, %.2f" % (distance, item.position[0], item.position[1])
				game.output.output(message)
				break
			else:
				name = item.userData.name
			game.output.output(name + ": %.2f meters. %.2f, %.2f" % (distance, item.position[0], item.position[1]), interrupt=False)

	def detect_exits(self):
		exits = game.map.nearby_exits(self.position)
		delay = 0.0
		for exit in exits:
			pos = game.map.get_physical_coordinates(exit)
			game.output.output(str(pos), interrupt=False)
			game.clock.schedule_once(self.play_exit_sound, delay=delay, x=pos[0], y=pos[1])
			delay += 0.55

	def play_exit_sound(self, t, x, y):
		game.sound_manager.play_async('beep.wav', x, y)

	def walk_toward(self, position):
		self.face(position)
		self.walking_toward = position


	def face(self, position):
		self.facing = angle_between(self.position, position)
