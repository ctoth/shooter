import pyglet
from pyglet.window import key, mouse
import game

class GameScreen(object):

	def __init__(self):
		super(GameScreen, self).__init__()
		self.joystick = None
		joystick = pyglet.input.get_joysticks()
		if joystick:
			joystick = joystick[0]
			joystick.open()
			joystick.push_handlers(self.on_joybutton_press, self.on_joybutton_release)
			self.joystick = joystick

	def on_key_press(self, symbol, modifiers):
		if symbol == key.UP:
			if key.MOD_SHIFT & modifiers:
				game.player.start_running()
			game.player.start_forward()
		if symbol == key.DOWN:
			game.player.start_backward()
		if symbol == key.LEFT:
			if key.MOD_SHIFT & modifiers or key.MOD_ALT & modifiers:
				if key.MOD_ALT & modifiers:
					game.player.snap_left()
				if key.MOD_SHIFT & modifiers:
					game.player.strafe_left()
			else:
				game.player.turn_left()
		if symbol == key.RIGHT:
			if key.MOD_SHIFT & modifiers or key.MOD_ALT & modifiers:
				if key.MOD_ALT & modifiers:
					game.player.snap_right()
				if key.MOD_SHIFT & modifiers:
					game.player.strafe_right()
			else:
				game.player.turn_right()
		if symbol == key.C:
			game.player.read_coordinates()
		if symbol == key.F:
			game.player.read_facing()
		if symbol == key.L:
			game.player.do_ping()
		if symbol == key.P:
			game.player.pick_up_obj()
		if symbol == key.D:
			game.player.detect_exits()
		if symbol == key.TAB:
			if key.MOD_SHIFT & modifiers:
				game.player.radar.read_previous()
			else:
				game.player.radar.read_next()
		if symbol == key.T:
			if game.player.radar.tracking:
				game.player.radar.stop_tracking()
			else:
				game.player.radar.start_tracking()
		if symbol == key.R:
			game.player.radar.summarize_room()
		if symbol == key.H:
			game.player.read_health()
		if symbol in (key.LCTRL, key.RCTRL):
			game.player.start_attacking()

	def on_key_release(self, symbol, modifiers):
		if symbol in (key.LCTRL, key.RCTRL):
			game.player.stop_attacking()
		if symbol == key.UP or symbol == key.DOWN:
			game.player.stop_moving()
		if symbol == key.LEFT or symbol == key.RIGHT:
			game.player.stop_turning()
			game.player.stop_strafing()
		if symbol in (key.LSHIFT, key.RSHIFT):
			game.player.stop_strafing()
			game.player.stop_running()

	def on_mouse_motion(self, x, y, dx, dy):
		dx /= MOUSE_SENSITIVITY
		game.player.facing += dx

	def on_mouse_press(self, x, y, button, modifiers):
		if button == mouse.LEFT:
			game.player.start_attacking()

	def on_mouse_release(self, x, y, button, modifiers):
		if button == mouse.LEFT:
			game.player.stop_attacking()

	def on_joybutton_press(self, joystick, button):
		if button == 0: #trigger
			game.player.start_attacking()

	def on_joybutton_release(self, joystick, button):
		if button == 0: #trigger
			game.player.stop_attacking()

	def __del__(self):
		self.joystick.close()

class PauseScreen(object):
	pass