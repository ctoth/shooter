import attr
import game_object

class Entity(game_object.GameObject):

	def __init__(self, health=100, speed=100, *args, **kwargs):
		super(Entity, self).__init__(*args, **kwargs)
		self.health = health
		self.speed = speed

	def create_body(self):
		self.body = self.world.world.CreateDynamicBody()
		self.box= self.body.CreatePolygonFixture(box=self.size, density=1, friction=0.3, restitution=0.0)

Entity = attr.s(these = {
	'health': attr.ib(default=100),
	'speed': attr.ib(default=100),
	'facing': attr.ib(default=0),
	'position': attr.ib(default=None),
	},
init = False)(Entity)
