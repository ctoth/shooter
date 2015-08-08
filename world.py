from logging import getLogger
logger = getLogger('world')
import Box2D
from Box2D import b2
import game
import math_utils

class World(object):

	def __init__(self, framerate=60):
		self.framerate = framerate
		self.world = b2.world(doSleep=True, gravity=(0, 0))
		self.to_destroy = set()
		self.unused_bodies = set()
		self.objects_to_create_bodies_for = dict()
		self.collisions =dict()
		self.collision_callback = CollisionCallback(self)
		self.world.contactListener = self.collision_callback
		self.objects = set()
		self.objects_to_add = set()
		self.bodies = []

	def destroy(self, obj):
		self.to_destroy.add(obj)

	def remove_body_from_world(self, body):
		self.unused_bodies.add(body)

	def destroy_body(self, body):
		self.world.DestroyBody(body)

	def create_body_next_tick(self, obj, position=(0, 0)):
		self.objects_to_create_bodies_for[obj] = position

	def tick(self):
		with game.sound_manager.sim:
			self.world.Step(1.0 / self.framerate, 10, 10)
			self.objects .update(self.objects_to_add)
			self.objects_to_add.clear()
			for o in self.to_destroy:
				if o in self.objects:
					self.objects.remove(o)
				self.destroy_body(o.body)
			for body in self.unused_bodies:
				self.destroy_body(body)
			for obj, position in self.objects_to_create_bodies_for.iteritems():
				obj.create_body(position=position)
				obj.create_fixture()
			self.to_destroy.clear()
			self.objects_to_create_bodies_for.clear()
			self.unused_bodies.clear()
			for obj in self.objects:
				try:
					obj.tick()
				except Exception as e:
					logger.exception(u"Error with object tick for object %s with name %s" % (obj, obj.name))

	def add_object(self, obj):
		self.objects_to_add.add(obj)

	def create_wall_tile(self, position, size=(0.5, 0.5)):
		shape = b2.polygonShape(box=size)
		self.bodies.append(self.world.CreateStaticBody(shapes=shape, position=position, userData=self))

	def ray_cast(self, start, direction, length):
		"""Returns the list of game objects in order of distance from the given start at the given direction up to the given length"""
		end = math_utils.vec_mul(math_utils.angle_to_vec(direction), length)
		end = math_utils.vec_add(list(start), end)
		callback = RayCastCallback()
		self.world.RayCast(callback, start, end)
		callback.fixtures.sort()
		return [i[1].body for i in callback.fixtures]

	def count_objects_between(self, p1, p2):
		if p1 == p2:
			return 0
		callback = RayCastCallback()
		self.world.RayCast(callback, p1, p2)
		bodies = [i[1].body for i in callback.fixtures]
		return len([i for i in bodies if i.position != p1 and i.position != p2])

	def is_visible(self, looker, target, max_distance=0):
		start_point = looker.position
		angle = looker.facing
		end_point = target.position
		distance_between = math_utils.distance(start_point, end_point)
		if max_distance and math_utils.distance(start_point, end_point) > max_distance:
			return False
		angle_between = (math_utils.angle_between(target.position, looker.position) - looker.facing) % 360
		if angle_between < (looker.angle_of_visibility / 2.0) and angle_between < 360 - (looker.angle_of_visibility / 2.0):
			return False
		length = distance_between
		if length == 0:
			length = 2**32-1
		los = self.ray_cast(start_point, direction=angle, length=length)
		for item in los:
			if item.userData is game.world:
				return False
			return True
		return False

	def query(self, lower, upper):
		callback = QueryCallback()
		AABB = Box2D.b2AABB()
		AABB.lowerBound = lower
		AABB.upperBound = upper
		self.world.QueryAABB(callback, AABB)
		return callback


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
		if hasattr(a, 'handle_collision'):
			a.handle_collision(b)
		if hasattr(b, 'handle_collision'):
			b.handle_collision(a)

	def EndContact(self, contact):
		a, b = contact.fixtureA.body.userData, contact.fixtureB.body.userData
		if a > b:
			a, b = b, a
		try:
			del self.for_object.collisions[(a, b)]
		except KeyError as e:
			pass

class RayCastCallback(Box2D.b2RayCastCallback):

	def __init__(self):
		super(RayCastCallback, self).__init__()
		self.fixtures = []

	def ReportFixture(self, fixture, point, normal, fraction):
		result = (fraction, fixture)
		self.fixtures.append(result)
		return 1

class QueryCallback(Box2D.b2QueryCallback):

	def __init__(self):
		super(QueryCallback, self).__init__()
		self.fixtures = list()

	def ReportFixture(self, fixture):
		self.fixtures.append(fixture)
		return True
