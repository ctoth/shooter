from Box2D import b2

class World(object):

	def __init__(self, framerate=60):
		self.framerate = framerate
		self.world = b2.world(doSleep=True)

	def tick(self):
		self.world.Step(1.0 / self.framerate, 10, 10)
