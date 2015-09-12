from platform_utils import blackhole
import logger_setup
logger_setup.setup_logging(debug_log='shooter.log')
import logging
logging.basicConfig()
import game
import screens
import pyglet
game.window = pyglet.window.Window()
import map
import map_loader
import player
import sound
import world
import libaudioverse
import sys
import libloader.com
libloader.com.prepare_gencache()
from accessible_output2.outputs import auto
import faulthandler
#import profile

def main():
#	profile.setup()
	libaudioverse.initialize()
	game.clock = pyglet.clock.get_default()
	game.window.set_exclusive_mouse(True)
	window_caption = "{name} - {version}".format(name=game.NAME, version=game.VERSION)
	game.window.set_caption(window_caption)
	game.sound_manager = sound.SoundManager()
	game.output = auto.Auto()
	game.world = world.World()
	game.map = map_loader.load_template('map.yml', world=game.world)
	#map.Map(world=game.world, name="Deck 13", ambience='ambience.ogg', x_cells=3, y_cells=10, cell_size=8, npc_density=0.33)
	game.player = player.Player(world=game.world, position=game.map.starting_coordinates)
	game.map.enter(game.player)
	game.tick = tick
	if not getattr(sys, 'frozen', False):
		faulthandler.enable()
		import ingress
		ingress.install(port=4263, env=game.__dict__)
	screen = screens.GameScreen()
	screen.activate()
	main_loop()
	libaudioverse.shutdown()

def main_loop():
	pyglet.clock.schedule_interval(tick, game.FRAMERATE)
	game.sound_manager.start()
	pyglet.app.run()

def tick(dt):
	with game.sound_manager.sim:
		game.world.tick()
		game.player.set_sound_position()

if __name__ == '__main__':
	main()

