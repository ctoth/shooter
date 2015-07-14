from Box2D import b2
import game

class World(object):

	def __init__(self, framerate=60):
		self.framerate = framerate
		self.world = b2.world(doSleep=True, gravity=(0, 0))

	def tick(self):
		with game.sound_manager.sim:
			self.world.Step(1.0 / self.framerate, 10, 10)
