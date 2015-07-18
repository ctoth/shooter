import game
import pyglet
game.window = pyglet.window.Window()
from pyglet.window import key
import loader
import player
import sound
import world
import libaudioverse
import sys
from accessible_output2.outputs import auto


def main():
	libaudioverse.initialize()
	game.clock = pyglet.clock.get_default()
	game.sound_manager = sound.SoundManager()
	game.output = auto.Auto()
	game.world = world.World()
	game.player = player.Player(world=game.world, position=(4, 4))
	game.map = loader.load_map(game.world, 'map.yml')
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
		game.world.tick()
		game.player.tick()
		game.player.set_sound_position()


if __name__ == '__main__':
	main()

