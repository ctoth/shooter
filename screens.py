import pyglet
from pyglet.window import key, mouse
import game
import weapon

class Screen(object):

	def activate(self):
		if hasattr(game, 'screen'):
			game.screen.deactivate()
		game.screen = self
		game.window.push_handlers(self)

	def deactivate(self):
		game.window.remove_handlers(self)

class GameScreen(Screen):

	def activate(self):
		super(GameScreen, self).activate()
		self.joystick = None
		joystick = pyglet.input.get_joysticks()
		if joystick:
			joystick = joystick[0]
			joystick.open()
			joystick.push_handlers(self.on_joybutton_press, self.on_joybutton_release)
			self.joystick = joystick

	def on_key_press(self, symbol, modifiers):
		if symbol == key.I:
			game.player.show_inventory()
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
		if symbol == key.ESCAPE:
			self.pause()
			return True
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
			game.player.stop_running()
		if symbol == key.LEFT or symbol == key.RIGHT:
			game.player.stop_turning()
			game.player.stop_strafing()
		if symbol in (key.LSHIFT, key.RSHIFT):
			game.player.stop_strafing()
			game.player.stop_running()

	def on_mouse_motion(self, x, y, dx, dy):
		dx /= game.MOUSE_SENSITIVITY
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

	def deactivate(self):
		super(GameScreen, self).deactivate()
		self.joystick.close()

	def pause(self):
		screen = PauseScreen()
		screen.activate()

class PauseScreen(Screen):

	def activate(self):
		super(PauseScreen, self).activate()
		game.clock.unschedule(game.tick)

	def deactivate(self):
		super(PauseScreen, self).deactivate()
		game.clock.schedule_interval(game.tick, game.FRAMERATE)

class MenuScreen(Screen):

	def __init__(self, prompt="", choices=None, callback=None, string_callback=None, selection_sound=None, activation_sound=None, boundary_sound=None):
		super(MenuScreen, self).__init__()
		self.prompt = prompt
		if choices is None:
			choices = []
		self.choices = choices
		self.callback = callback
		self.selection_sound = selection_sound
		self.activation_sound = activation_sound
		self.boundary_sound = boundary_sound
		self.index = 0

	def current_item(self):
		if not self.choices:
			return
		self.index %= len(self.choices)
		return self.choices[self.index]

	def next_item(self):
		if self.index + 1 >= len(self.choices):
			self.play_boundary()
		self.index += 1
		self.read_current_item()

	def previous_item(self):
		if self.index - 1 < 0:
			self.play_boundary()
		self.index -= 1
		self.read_current_item()

	def read_current_item(self, interrupt=True):
		item = self.current_item()
		if item is None:
			return
		self.play_selection()
		game.output.output(unicode(item), interrupt)

	def first_item(self):
		self.index = 0
		self.read_current_item()

	def last_item(self):
		self.index = len(self.choices)
		self.read_current_item()

	def activate(self):
		super(MenuScreen, self).activate()
		self.read_prompt()
		self.read_current_item(interrupt=False)

	def read_prompt(self):
		game.output.output(self.prompt)


	def on_key_press(self, symbol, modifiers):
		if symbol == key.DOWN:
			self.next_item()
		elif symbol == key.UP:
			self.previous_item()
		elif symbol == key.HOME:
			self.first_item()
		elif symbol == key.END:
			self.last_item()
		elif symbol == key.ENTER:
			self.activate_item()
		char = key.symbol_string(symbol).lower()
		for num, item in enumerate(self.choices):
			if unicode(item).lower().startswith(char):
				self.index = num
				self.read_current_item()

	def activate_item(self):
		item = self.current_item()
		if item is None:
			return
		self.play_activation()
		if self.callback is not None:
			self.callback(item)

	def play_boundary(self):
			if self.boundary_sound:
				game.sound_manager.play_UI_queue(self.boundary_sound)

	def play_selection(self):
		if self.selection_sound is not None:
			game.sound_manager.play_UI_queue(self.selection_sound)

	def play_activation(self):
		if self.activation_sound is not None:
			game.sound_manager.play_UI_queue(self.activation_sound)

class InventoryScreen(MenuScreen):

	def activate_item(self):
		super(InventoryScreen, self).activate_item()
		item = self.current_item()
		print item
		if item is None:
			return
		if isinstance(item, weapon.Weapon):
			game.player.equip(item)
		elif hasattr(item, 'use'):
			item.use(game.player)

	def on_key_press(self, symbol, modifiers):
		item = self.current_item()
		if symbol == key.D and item is not None:
			game.player.drop(item)
			return
		if symbol == key.ESCAPE:
			self.deactivate()
			screen = GameScreen()
			screen.activate()
			return True
		return super(InventoryScreen, self).on_key_press(symbol, modifiers)

	def translate_item(self, item):
		if isinstance(item, basestring):
			return item
		if self.string_callback is not None:
			return self.string_callback(item)
		return unicode(item)
