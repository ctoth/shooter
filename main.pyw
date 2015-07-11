import game
import loader
import player
import sound
import window
import world
import libaudioverse
import pyglet

def main():
	libaudioverse.initialize()
	game.sound_manager = sound.SoundManager()
	game.world = world.World()
	game.player = player.Player(world=game.world, position=(4, 4))
	game.map = loader.load_map(game.world, 'map.yml')
	game.window = window.GameWindow(title="Shooter")
	main_loop()
	libaudioverse.shutdown()

def main_loop():
	framerate = 1/60.0
	pyglet.clock.schedule_interval(lambda dt: game.world.tick(), framerate)
	pyglet.clock.schedule_interval(lambda dt: game.player.set_sound_position(), framerate)
	pyglet.app.run()

if __name__ == '__main__':
	main()
