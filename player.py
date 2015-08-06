import math
import game_object
import entity
import game
import radar
import room
import screens
import tiles
import weapon
import world
from math_utils import *


class Player(entity.Entity):
	TURN_RATE = 0.8
	FOOTSTEP_SPEED = 0.5
	FOOTSTEP_DELAY = 0.3
	footstep_multiplier = 3.0
	running_multiplier = 1.5
	ping_distance = 50
	approach_distance = 1.0
	reach = 1.0

	def __init__(self, world=None, position=None, shape='circle', size=(0.1, 0.1), hit_sound='hit', mass=100, *args, **kwargs):
		#gun = weapon.ProjectileWeapon(world=world, name="Gun", ammo_type="bullet", use_sound='rifle', size=(1, 0.1), position=position, cooldown=0.5, mass=30, base_damage=50)
		#gun = weapon.ProjectileWeapon(world=world, name="m240", ammo_type='bullet', use_sound='machine_gun', size=(1, 0.2), cooldown=0.04, mass=50,base_damage=10)
		sword = weapon.BladedWeapon(world=world, name="Sword", use_sound='sword/swing', hit_sound='sword/hit', hit_wall_sound='sword/wall', mass=10, size=[1.0, 0.1], cooldown=0.4)
		super(Player, self).__init__(world=world, position=position, shape=shape, size=size, mass=mass, hit_sound=hit_sound, weapon=sword, *args, **kwargs)
		self.moving = False
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
		game.sound_manager.set_listener_position(position)
		orientation = list(game.sound_manager.world.orientation.value)
		orientation[0], orientation[1] = angle_to_vec(self.facing)
		game.sound_manager.set_orientation(orientation)

	def tick(self):
		self.radar.tick()
		if self.attacking:
			self.fire_weapon()
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
		super(Player, self).equip(item)
		item.sound_source.head_relative = True
		item.sound_source.position = (0, 0, 0)

	def get_footstep_sound(self):
		return game.map.footstep

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

	def destroy(self):
		game.clock.unschedule(game.tick)
		game.sound_manager.play_async('death', *self.position)

	def pick_up_obj(self):
		obj = self.radar.current_item()
		if not isinstance(obj, game_object.GameObject):
			return
		if obj.fixed:
			return
		if distance(self.position, obj.position) > self.reach:
			return
		self.hold(obj)
		game.sound_manager.play('pickup.wav', source=self.sound_source, position=self.position)
		if obj is self.radar.tracking:
			self.radar.stop_tracking()
			self.radar.tracking = None

	def read_health(self):
		game.output.output(unicode(self.health))

	def show_inventory(self):
		screen = screens.InventoryScreen(prompt="Inventory", choices=self.contents, selection_sound='menu/select.wav')
		screen.activate()
