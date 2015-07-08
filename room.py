from Box2D import b2

class Room(object):

	def __init__(self, world, name=None, size=(1, 1), exits=None, floor=None, contents=None):
		self.world = world
		self.name = name
		corners = [
			(1, 1),
			(1, size[0]),
			size,
			(size[1], 1)
			]
		self.floor = floor
		if exits is None:
			exits = []
		exits.sort()
		vertices = [b2.vec2(*i) for i in corners]
		self.shape = b2.chainShape(vertices=vertices)
		self.ground_body = self.world.world.CreateStaticBody(position=(1, 1,) shapes=self.shape)
		#dictionary of {coords: object}
		if contents is None:
			contents = {}
		self.contents = contents
