import pyglet

class GameWindow(object):

	def __init__(self, title="", width=800, height=600):
		self.screen = pyglet.window.Window(width, height, caption=title)
