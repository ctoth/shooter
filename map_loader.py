from logging import getLogger
logger = getLogger('map_loader')
import collections
import os
import yaml
import game_object
import items
import map
import npc
import template
import weapon

OBJECT_TYPES = {
	i.__name__: i
	for i in (
		game_object.GameObject, weapon.ProjectileWeapon, weapon.BeamWeapon, items.HealthBoost,
	)
}

class ConsistencyError(KeyError):
	pass

class LoadError(ValueError):
	pass

class IncludeLoader(yaml.Loader):
	"""Class to support including text directly into a YAML file"""

	def __init__(self, stream):
		self._root = os.path.split(stream.name)[0]
		super(IncludeLoader, self).__init__(stream)

	def include(self, node):
		filename = os.path.join(self._root, self.construct_scalar(node))
		with open(filename, 'r') as f:
			return yaml.load(f, IncludeLoader)

IncludeLoader.add_constructor('!include', IncludeLoader.include)

def percentage_values(d):
	res = {}
	str_type = str

	for k, v in d.items():
		if hasattr(v, 'endswith') and v.endswith('%'):
			res[k] = float(v[:-1]) / 100.0
		elif isinstance(v, collections.MutableMapping):
			res[k] = percentage_values(v)
		else:
			res[k] = v
	return res

def check_consistency(data, working=None):
	if working is None:
		working = data
	for key, value in working.items():
		if not isinstance(value, collections.MutableMapping):
			continue
		check_consistency(data, working=value)
		for subkey, subvalue in value.items():
			if subkey not in data:
				continue
			templates = data[subkey]
			if subvalue is None:
				continue
			for innermost_key in subvalue:
				if innermost_key not in templates:
					raise ConsistencyError("Item %s not defined in %s section" % (innermost_key, subkey))

def create_map(map_template, world):
	name = map_template['name']
	cell_size=map_template.get('max_room_dimension', 0)
	x_rooms = map_template.get('x_rooms', 0)
	y_rooms = map_template.get('y_rooms', 0)
	footstep=map_template['footstep']
	ambience = map_template.get('ambient')
	loading = map.Map(world=world, name=name, x_cells=x_rooms, y_cells=y_rooms, cell_size=cell_size, ambience=ambience, footstep=footstep)
	for npc_template, density in map_template.get('npcs', {}).items():
		if density != 'single':
			loading.place_npcs(npc_template, density)
	for object_template, density in map_template.get('objects', {}).items():
		logger.info("placing %s with density of %f" % (object_template.object_type, density))
		loading.place_objects(object_template, density)
	return loading

def load_objects(object_type, objects):
	res = {}
	for name, characteristics in objects.items():
		is_a = characteristics.pop('is_a', None)
		if is_a:
			try:	
				object_type = OBJECT_TYPES[is_a]
			except KeyError:
				raise LoadError("Unable to create object with name %s as a subclass of %s as %s is not in the object types registry" % (name, is_a, is_a))
		res[name] = template.ObjectTemplate(object_type, name=name, **characteristics)
	return res

def load_npcs(data):
	npcs = []
	for npc_template in data.get('npcs', {}).values():
		if 'weapon' in npc_template:
			npc_template['weapon'] = data['weapons'][npc_template['weapon']]
	npcs = load_objects(npc.NPC, data.get('npcs', {}))
	return npcs

def extract_templates(data):
	map_template = {}
	for key, val in data['map'].items():
		if key not in data:
			map_template[key] = val
			continue
		map_template[key] = {}
		if val is None:
			continue
		for subkey, subval in val.items():
			map_template[key][data[key][subkey]] = subval
	return map_template

def load_template(filename, world=None):
	with open(filename, 'r') as f:
		data = yaml.load(f, IncludeLoader)
	check_consistency(data)
	#pass 1: convert percentages to decimal ratios of 1, so that 25% becomes 0.25
	data = percentage_values(data)
	#pass 2: Convert dictionaries to object templates
	data['objects'] = load_objects(game_object.GameObject, data.get('objects', {}))
	data['weapons'] = load_objects(weapon.ProjectileWeapon, data.get('weapons', {}))
	data['npcs'] = load_npcs(data)
	#pass 3: Move templates into the map
	map_template = extract_templates(data)
	#pass 4: create the map
	loaded_map = create_map(map_template, world)
	return loaded_map

