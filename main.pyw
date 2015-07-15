import game
import pyglet
game.window = pyglet.window.Window()
from pyglet.window import key
import loader
import player
import sound
import world
import libaudioverse
import ingress
from accessible_output2.outputs import auto


def main():
	libaudioverse.initialize()
	game.clock = pyglet.clock.get_default()
	game.sound_manager = sound.SoundManager()
	game.output = auto.Auto()
	game.world = world.World()
	game.player = player.Player(world=game.world, position=(4, 4))
	game.map = loader.load_map(game.world, 'map.yml')
	ingress.install(port=4263, env={'game': game})
	main_loop()
	libaudioverse.shutdown()

def main_loop():
	framerate = 1/60.0
	pyglet.clock.schedule_interval(tick, framerate)
	pyglet.app.run()

@game.window.event
def on_key_press(symbol, modifiers):
	if symbol == key.UP:
		game.player.start_forward()
	if symbol == key.DOWN:
		game.player.start_backward()
	if symbol == key.LEFT:
		if modifiers == key.MOD_SHIFT:
			game.player.strafe_left()
		elif modifiers == key.MOD_ALT:
			game.player.snap_left()
		else:
			game.player.turn_left()
	if symbol == key.RIGHT:
		if modifiers == key.MOD_SHIFT:
			game.player.strafe_right()
		elif modifiers == key.MOD_ALT:
			game.player.snap_right()
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


def tick(dt):
	with game.sound_manager.sim:
		game.world.tick()
		game.player.tick()
		game.player.set_sound_position()


if __name__ == '__main__':
	main()

