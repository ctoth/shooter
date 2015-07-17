import Box2D
from Box2D import b2
import game


class World(object):

	def __init__(self, framerate=60):
		self.framerate = framerate
		self.world = b2.world(doSleep=True, gravity=(0, 0))
		self.to_destroy = set()
		self.collisions =dict()
		self.collision_callback = CollisionCallback(self)
		self.world.contactListener = self.collision_callback

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


#This class allows us to detect collisions. With it, we can build a list.
class CollisionCallback(Box2D.b2ContactListener):
	"""Used to listen for collisions.
	
	Appends the userdata off both bodies to for_objects.collisions, or removes them when they no longer touch.
	it is assumed that for_object.collisions is a dict.  The keys are tuples of touching items and the values the approximate position of the collision.
	
	for_object.per_tick_collisions is the same, but is not automatically cleared; use it to detect that something happened, rather than that something is happening."""

	def __init__(self, for_object):
		super(CollisionCallback, self).__init__()
		self.for_object=for_object

	def BeginContact(self, contact):
		a, b=contact.fixtureA.body.userData, contact.fixtureB.body.userData
		if a > b:
			a, b = b, a
		if (a, b) in self.for_object.collisions:
			return #already handled
		self.for_object.collisions[(a, b)] = contact.worldManifold.points[0]
		a.handle_colision(b)
		b.handle_colision(a)

	def EndContact(self, contact):
		a, b = contact.fixtureA.body.userData, contact.fixtureB.body.userData
		if a > b:
			a, b = b, a
		try:
			del self.for_object.collisions[(a, b)]
		except KeyError as e:
			pass
