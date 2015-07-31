import copy

class ObjectTemplate(object):

	def __init__(self, object_type, probability=0, placement='random', **object_characteristics):
		self.object_type = object_type
		self.object_characteristics = object_characteristics
		self.probability = probability
		self.placement = placement

	def spawn(self, world=None, *args, **extra_kwargs):
		characteristics = copy.deepcopy(self.object_characteristics)
		characteristics.update(extra_kwargs)
		for name, value in characteristics.items():
			if isinstance(value, ObjectTemplate):
				characteristics[name] = value.spawn(world=world)
		return self.object_type(world=world, *args, **characteristics)


