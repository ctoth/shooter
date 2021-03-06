import math
import game_object
import entity
import game
import math_utils
import radar
import room
import screens
from vector import Vector
import tiles
import weapon
import world

HEALTH_OK, HEALTH_BAD, HEALTH_TERRIBLE = range(3)

class Player(entity.Entity):
	FOOTSTEP_SPEED = 0.75
	FOOTSTEP_DELAY = 0.3
	footstep_multiplier = 3.0
	running_multiplier = 1.5
	ping_distance = 50
	approach_distance = 1.0
	reach = 1.5
	wall_collision_sound = 'wall.wav'

	def __init__(self, world=None, position=None, shape='circle', size=(0.1, 0.1), damage_sound='hit', mass=100, head_relative=True, *args, **kwargs):
		#gun = weapon.ProjectileWeapon(world=world, name="Gun", ammo_type="bullet", use_sound='rifle', size=(1, 0.1), position=position, cooldown=0.5, mass=30, base_damage=50)
		#gun = weapon.ProjectileWeapon(world=world, name="m240", ammo_type='bullet', use_sound='machine_gun', size=(1, 0.2), cooldown=0.04, mass=50,base_damage=10)
		sword = weapon.BladedWeapon(world=world, name="Sword", use_sound='sword/swing', hit_sound='sword/hit', hit_wall_sound='sword/wall', mass=10, size=[1.0, 0.1], cooldown=0.4)
		super(Player, self).__init__(world=world, position=position, shape=shape, size=size, mass=mass, damage_sound=damage_sound, weapon=sword, head_relative=head_relative, *args, **kwargs)
		self.moving = False
		self.turning = None
		self.running = False
		self.attacking = False

		self.radar = radar.Radar(looker=self)
		self.sweeping_radar = radar.SweepingRadar(self)
		self.walking_toward = None
		self.injured_sound = None
		self.health_state = HEALTH_OK


	def set_sound_position(self):
		position = list(self.position)
		position.append(0.0)
		game.sound_manager.set_listener_position(position)
		orientation = list(game.sound_manager.world.orientation.value)
		orientation[0], orientation[1] = Vector.from_angle(self.facing)
		game.sound_manager.set_orientation(orientation)
		room = game.map.find_room_containing(self.position)
		t60 = 0
		if room:
			t60 = tiles.area_of_room(room) / 8.0
		game.sound_manager.reverb.t60.cancel_automators(0.0)
		game.sound_manager.reverb.t60.linear_ramp_to_value(0.3, t60)

	def tick(self):
		if self.health > 75 and self.health_state != HEALTH_OK:
			self.injured_sound.stop()
			self.injured_sound = None
			self.health_state = HEALTH_OK
		if self.health < 75 and self.health > 50 and self.health_state != HEALTH_BAD:
			if self.injured_sound:
				self.injured_sound.stop()
			self.injured_sound = self.play_sound('Heartbeat Slow.ogg', looping=True)
			self.health_state = HEALTH_BAD
		elif self.health < 50 and self.health_state != HEALTH_TERRIBLE:
			if self.injured_sound:
				self.injured_sound.stop()
			self.injured_sound = self.play_sound('Heartbeat Fast.ogg', looping=True)
			self.health_state = HEALTH_TERRIBLE
		elif self.health <= 0:
			if self.injured_sound:
				self.injured_sound.stop()
			self.injured_sound = None
		self.radar.tick()
		self.sweeping_radar.tick()
		self.set_sound_position()
		if self.attacking:
			self.fire_weapon()
		if self.turning == 'left':
			self.facing -= self.turn_rate
		elif self.turning == 'right':
			self.facing += self.turn_rate
		self		.facing %= 360
		speed = self.speed
		if self.running:
			speed *= self.running_multiplier
		slowdown_multiplier = math_utils.inverse_percentage(speed, 100)
		if self.velocity.magnitude() >= self.FOOTSTEP_SPEED:
			self.only_play_every(self.FOOTSTEP_DELAY* slowdown_multiplier, self.get_footstep_sound())
		else:
			self.velocity = (0, 0)
		if self.walking_toward:
			if distance(self.walking_toward, self.position) > self.approach_distance:
				self.moving = 'forward'
			else:
				self.moving = False
				self.walking_toward = None
		if self.moving:
			facing = self.facing
			if self.moving == 'forward':
				facing = facing
			elif self.moving == 'backward':
				facing = (facing - 180) % 360
			if self.moving == 'right':
				facing = facing + 90 % 360
			elif self.moving == 'left':
				facing = facing - 90 % 360
			self.velocity = Vector.from_angle(facing) * math_utils.percentage(self.footstep_multiplier, speed)
		else:
			self.body.linearVelocity = (0, 0)

	def equip(self, item):
		super(Player, self).equip(item)
		item.head_relative = True
		if item.sound_source:
			item.set_sound_position()
		if item.equip_sound is not None:
			self.play_sound(item.equip_sound, position=self.position)

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
			distance = self.position.distance(position)
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
			pos = game.map.get_physical_coordinates(Vector(*exit))
			game.output.output(str(pos), interrupt=False)
			game.clock.schedule_once(self.play_exit_sound, delay=delay, x=pos[0], y=pos[1])
			delay += 0.55

	def play_exit_sound(self, t, x, y):
		game.sound_manager.play_async('beep.wav', x, y)

	def walk_toward(self, position):
		self.face(position)
		self.walking_toward = position


	def face(self, position):
		self.facing = self.position.angle_between(position)

	def destroy(self):
		game.clock.unschedule(game.tick)
		game.sound_manager.play_async('death', *self.position)

	def interact_with_target(self):
		obj = self.radar.current_item()
		if not isinstance(obj, game_object.GameObject):
			return
		if self.position.distance(obj.position) > self.reach:
			return
		if obj.fixed:
			if obj.can_use():
				obj.use(user=self)
			return
		self.hold(obj)
		game.sound_manager.play('pickup.wav', source=self.sound_source, position=self.position)
		if obj is self.radar.tracking:
			self.radar.stop_tracking()
			self.radar.tracking = None

	def read_health(self):
		game.output.output(str(self.health))

	def show_inventory(self):
		game.screens.push(screens.InventoryScreen(prompt="Inventory", choices=self.contents, selection_sound='menu/select.wav'))
