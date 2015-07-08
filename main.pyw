import events
import game
import loader
import player
import sound
import window
import world
import libaudioverse
import pygame

def main():
	libaudioverse.initialize()
	pygame.init()
	game.sound_manager = sound.SoundManager()
	game.world = world.World()
	game.player = player.Player(world=game.world)
	game.map = loader.load_map(game.world, 'map.yml')
	game.clock = pygame.time.Clock()
	game.window = window.GameWindow(title="Shooter")
	main_loop()
	pygame.quit()
	libaudioverse.shutdown()

def main_loop():
	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				running = False
			if event.type == pygame.KEYDOWN:
				events.keydown.send(key=event.key)
			elif event.type == pygame.KEYUP:
				events.keyup.send(key=event.key)
		game.world.tick()
		game.clock.tick(game.world.framerate)

if __name__ == '__main__':
	main()
