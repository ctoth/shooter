from __future__ import division
import game
import pyglet
game.window = pyglet.window.Window()
from pyglet.window import key, mouse
import map
import player
import sound
import world
import libaudioverse
import sys
import libloader.com
libloader.com.prepare_gencache()
from accessible_output2.outputs import auto

MOUSE_SENSITIVITY = 20

def main():
	libaudioverse.initialize()
	game.clock = pyglet.clock.get_default()
	game.window.set_exclusive_mouse(True)
	game.sound_manager = sound.SoundManager()
	game.output = auto.Auto()
	game.world = world.World()
	game.map = map.Map(world=game.world, name="Deck 13", ambience='ambience.ogg', x_cells=3, y_cells=10, cell_size=8, npc_density=0.33)
	game.player = player.Player(world=game.world, position=game.map.starting_coordinates)
	game.map.enter(game.player)
	if not getattr(sys, 'frozen', False):
		import ingress
		ingress.install(port=4263, env=game.__dict__)
	main_loop()
	libaudioverse.shutdown()

def main_loop():
	framerate = 1/60.0
	pyglet.clock.schedule_interval(tick, framerate)
	pyglet.app.run()

@game.window.event
def on_key_press(symbol, modifiers):
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
	if symbol == key.P:
		game.player.do_ping()
	if symbol == key.D:
		game.player.detect_exits()
	if symbol == key.TAB:
		if key.MOD_SHIFT & modifiers:
			game.player.radar.read_previous()
		else:
			game.player.radar.read_next()
	if symbol in (key.LCTRL, key.RCTRL):
		game.player.start_attacking()

@game.window.event
def on_key_release(symbol, modifiers):
	if symbol in (key.LCTRL, key.RCTRL):
		game.player.stop_attacking()
	if symbol == key.UP or symbol == key.DOWN:
		game.player.stop_moving()
	if symbol == key.LEFT or symbol == key.RIGHT:
		game.player.stop_turning()
	if symbol in (key.LSHIFT, key.RSHIFT):
		game.player.stop_strafing()
		game.player.stop_running()


def tick(dt):
	with game.sound_manager.sim:
		game.player.tick()
		game.map.tick()
		game.world.tick()
		game.player.set_sound_position()

@game.window.event
def on_mouse_motion(x, y, dx, dy):
	dx /= MOUSE_SENSITIVITY
	game.player.facing += dx

@game.window.event
def on_mouse_press(x, y, button, modifiers):
	if button == mouse.LEFT:
		game.player.start_attacking()

@game.window.event
def on_mouse_release(x, y, button, modifiers):
	if button == mouse.LEFT:
		game.player.stop_attacking()


if __name__ == '__main__':
	main()

