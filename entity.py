import attr
import game_object

class Entity(game_object.GameObject):

	def __init__(self, health=100, speed=100, position=(0, 0), facing=0, *args, **kwargs):
		super(Entity, self).__init__(*args, **kwargs)
		self.health = health
		self.speed = speed
		self.facing = facing
		self.body = self.world.world.CreateDynamicBody(position=position, angle=self.facing)
		self.box= self.body.CreatePolygonFixture(box=self.size, density=1, friction=0.3)


	@property
	def position(self):
		return self.body.position

	@position.setter
	def position(self, position):
		self.body.position = position

Entity = attr.s(these = {
	'health': attr.ib(default=100),
	'speed': attr.ib(default=100),
	'facing': attr.ib(default=0),
	'position': attr.ib(default=None),
	},
init = False)(Entity)


