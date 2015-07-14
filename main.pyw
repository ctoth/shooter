import game
import pyglet
game.window = pyglet.window.Window()
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
	pyglet.clock.schedule_interval(lambda dt: game.world.tick(), framerate)
	pyglet.clock.schedule_interval(lambda dt: game.player.tick(), framerate)
	pyglet.clock.schedule_interval(lambda dt: game.player.set_sound_position(), framerate)

	pyglet.app.run()

@game.window.event
def on_key_press(symbol, modifiers):
	if symbol == pyglet.window.key.UP:
		game.player.start_forward()
	elif symbol == pyglet.window.key.DOWN:
		game.player.start_backward()
	elif symbol == pyglet.window.key.LEFT:
		game.player.turn_left()
	elif symbol == pyglet.window.key.RIGHT:
		game.player.turn_right()
	elif modifiers == pyglet.window.key.MOD_CTRL:
		game.player.start_attacking()


@game.window.event
def on_key_release(symbol, modifiers):
	if symbol == pyglet.window.key.UP or symbol == pyglet.window.key.DOWN:
		game.player.stop_moving()
	elif symbol == pyglet.window.key.LEFT or symbol == pyglet.window.key.RIGHT:
		game.player.stop_turning()
	elif modifiers == pyglet.window.key.MOD_CTRL:
		game.player.stop_attacking()


if __name__ == '__main__':
	main()

