import pygame

class GameWindow(object):

	def __init__(self, title="", width=800, height=600):
		self.screen = pygame.display.set_mode((width, height), 0, 32)
		pygame.display.set_caption(title)
