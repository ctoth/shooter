import game_object

class Entity(game_object.GameObject):

	def __init__(self, health=100, speed=100, *args, **kwargs):
		super(Entity, self).__init__(*args, **kwargs)
		self.health = health
		self.speed = speed

	def create_body(self):
		self.body = self.world.world.CreateDynamicBody(userData=self)
		self.box= self.body.CreatePolygonFixture(box=self.size, density=1, friction=1.0, restitution=0.0)
