from logging import getLogger
logger = getLogger('world')
import Box2D
from Box2D import b2
import collections
import game
from vector import Vector

collections.Sequence.register(Box2D.b2Vec2)

class World(object):

	def __init__(self):
		self.world = b2.world(doSleep=True, gravity=(0, 0))
		self.to_destroy = set()
		self.unused_bodies = set()
		self.objects_to_create_bodies_for = dict()
		self.collisions =dict()
		self.collision_callback = CollisionCallback(self)
		self.ray_cast_callback = RayCastCallback()
		self.closest_ray_cast_callback = ClosestRayCastCallback()
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
		self.world.Step(game.FRAMERATE, 3, 3)
		self.world.ClearForces()
		with game.sound_manager.server:
			self.objects .update(self.objects_to_add)
			self.objects_to_add.clear()
			for o in self.to_destroy:
				if o in self.objects:
					self.objects.remove(o)
				self.destroy_body(o.body)
			for body in self.unused_bodies:
				self.destroy_body(body)
			for obj, position in self.objects_to_create_bodies_for.items():
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

	def create_wall_tile(self, position, size=(0.5, 0.5), **kwargs):
		shape = b2.polygonShape(box=size)
		self.bodies.append(self.world.CreateStaticBody(shapes=shape, position=position, userData=self, **kwargs))

	def ray_cast(self, start, direction, length):
		"""Returns the list of game objects in order of distance from the given start at the given direction up to the given length"""

		unit = Vector.from_angle(direction)
		end = unit * length
		end = start + end
		callback = self.ray_cast_callback
		callback.fixtures = set()
		self.world.RayCast(callback, start, end)
		fixtures = sorted(callback.fixtures)
		return [i[1].body for i in fixtures]

	def ray_cast_to_first_item(self, start, direction, length):
		"""Returns the first game object in order of distance from the given start at the given direction up to the given length. Also returns the precise point at which it was hit."""
		unit = Vector.from_angle(direction)
		end = unit * length
		end = start + end
		callback = self.closest_ray_cast_callback
		callback.result = None
		self.world.RayCast(callback, start, end)
		if not callback.result:
			return
		frac_distance, fixture = callback.result
		distance = frac_distance * length
		hitpoint = unit * distance
		hitpoint = hitpoint + start
		return hitpoint, fixture.body

	def count_objects_between(self, p1, p2):
		if p1 == p2:
			return 0
		callback = self.ray_cast_callback
		callback.fixtures = set()
		self.world.RayCast(callback, p1, p2)
		return len([i for i in callback.fixtures if i[1].body.position not in {p1, p2}])

	def is_visible(self, looker, target, max_distance=0):
		start_point = looker.position
		angle = looker.facing
		end_point = target.position
		distance_between = start_point.distance(end_point)
		if max_distance and distance_between > max_distance:
			return False
		angle_between = (target.position.angle_between(looker.position) - looker.facing) % 360
		if angle_between < (looker.angle_of_visibility / 2.0) and angle_between < 360 - (looker.angle_of_visibility / 2.0):
			return False
		length = distance_between
		los = self.ray_cast(start_point, direction=angle, length=length)
		for item in los:
			if item.userData is game.world:
				return False
		else:
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
		if id(a) > id(b):
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
		if id(a) > id(b):
			a, b = b, a
		try:
			del self.for_object.collisions[(a, b)]
		except KeyError as e:
			pass


class RayCastCallback(Box2D.b2RayCastCallback):

	def __init__(self):
		super(RayCastCallback, self).__init__()
		self.fixtures = set()

	def ReportFixture(self, fixture, point, normal, fraction):
		result = (fraction, fixture)
		self.fixtures.add(result)
		return 1

class ClosestRayCastCallback(Box2D.b2RayCastCallback):

	def __init__(self, *args, **kwargs):
		super(ClosestRayCastCallback, self).__init__(*args, **kwargs)
		self.result = None

	def ReportFixture(self, fixture, point, normal, fraction):
		result = (fraction, fixture)
		self.result = result
		return fraction


class QueryCallback(Box2D.b2QueryCallback):

	def __init__(self):
		super(QueryCallback, self).__init__()
		self.fixtures = list()

	def ReportFixture(self, fixture):
		self.fixtures.append(fixture)
		return True
