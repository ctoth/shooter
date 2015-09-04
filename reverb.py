import libaudioverse

class Reverb(object):

	def __init__(self, simulation):
		self.simulation = simulation
		self.reverb = libaudioverse.FdnReverbNode(self.simulation)
		self.input_node = libaudioverse.GainNode(self.simulation, channels = 2)
		self.splitter = libaudioverse.ChannelSplitterNode(self.simulation, channels = 2)
		self.merger = libaudioverse.ChannelMergerNode(self.simulation, channels = 4)
		#Set up the graph.
		self.input_node.connect(0, self.splitter, 0)
		#The splitter and merger circumvent mixing matrix logic.
		for i in xrange(4):
			self.splitter.connect(i%2, self.merger, i)
		self.merger.connect(0, self.reverb, 0)

	@property
	def t60(self):
		return self.reverb.t60

	@t60.setter
	def t60(self, val):
		self.reverb.t60 = val

	@property
	def cutoff_frequency(self):
		return self.reverb.cutoff_frequency

	@cutoff_frequency.setter
	def cutoff_frequency(self, val):
		self.reverb.cutoff_frequency = val

	@property
	def mul(self):
		return self.reverb.mul

	@mul.setter
	def mul(self, val):
		self.reverb.mul = val

	@property
	def density(self):
		return self.reverb.density

	@density.setter
	def density(self, val):
		self.reverb.density = val

	def connect(self, output, other, input):
		self.reverb.connect(output, other, input)

	def connect_simulation(self, output):
		self.reverb.connect_simulation(output)

	def disconnect(self, output):
		self.reverb.disconnect(output)
