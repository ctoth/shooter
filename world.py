from Box2D import b2
import game

class World(object):

	def __init__(self, framerate=60):
		self.framerate = framerate
		self.world = b2.world(doSleep=True, gravity=(0, 0))
		self.to_destroy = set()

	def destroy(self, obj):
		self.to_destroy.add(obj)

	def destroy_body(self, body):
		self.world.DestroyBody(body)

	def tick(self):
		with game.sound_manager.sim:
			self.world.Step(1.0 / self.framerate, 10, 10)
			for obj in self.to_destroy:
				self.destroy_body(obj.body)
		self.to_destroy.clear()
