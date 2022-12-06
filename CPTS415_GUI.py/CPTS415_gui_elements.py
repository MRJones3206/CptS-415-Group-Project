# Matthew R. Jones - SID 11566314
# CptS_415 Final Project Graphical Interface Code
# *_ui_elements.py

# *_ui_elements.py serves as a repository for the various UI element classes inside the GUI
# Each element must, at a minimum, declare an instance of 'draw', which will accept a display to blit itself to, and
# have an accessible positive integer value 'priority' to assign its drawing priority.

# Also serves as repository for the GUI class - the actual data object that contains the GUI. This is puppeted by the _boot loop.
import pygame

# Default function value - does nothing.
def just_pass():
	pass

# Container for GUI elements. Responsible for determining hover and click successes and updating/drawing itself (flip is called in the
# _boot loop.)
class GUI:
	# Default GUI constructor. Builds a GUI out of the elements provided in _gui_elements 
	def __init__(self, display):
		self.display = display
		self.draw_queue = []
		self.draw_queue_markdirty = False
		self.hover_queue = []
		self.hover_queue_markdirty = False

		# Display Building Goes Here...

		self.draw_queue.append(bkg)
		self.draw_queue += title_bar

	def draw(self):
		if self.draw_queue_markdirty:
			self.draw_queue.sort(key = lambda x: x[0])
			self.draw_queue_markdirty = False
		for item in self.draw_queue:
			item.draw(self.display)

	def hover(self):
		if self.hover_queue_markdirty:
			self.hover_queue.sort(key = lambda x: x[0])
			self.hover_queue_markdirty = False
		for item in self.hover_queue:
			if item.mouse_is_in():
				item.on_hover()
			else:
				item.on_un_hover()

# A basic decorator object. Used mostly for window dressing.
class DECORATOR:
	def __init__(self, x_size = 100, y_size = 100, x_pos = 0, y_pos = 0, color = (255, 255, 255), priority = 0):
		self.surface = pygame.Surface((x_size, y_size))
		self.color = color
		self.surface.fill(color)
		self.rect = self.surface.get_rect()
		self.rect[0] = x_pos
		self.rect[1] = y_pos
		self.priority = priority

	def draw(self, target):
		target.blit(self.surface, self.rect)

# Special decorator used to color the background of the screen. Always the lowest possible priority (aka -1)
class BACKGROUND:
	def __init__(self, color = (220, 220, 220)):
		self.color = color
		self.priority = -1

	def draw(self, target):
		target.fill(self.color)

# Wildcard for hoverable and clickable objects. Must provide functionality for on_hover, on_un_hover or on_click, otherwise will pass.
class INTERACTABLE:
	def __init__(self, x_size = 100, y_size = 100, x_pos = 0, y_pos = 0, color = (255, 255, 255), priority = 0, on_hover = just_pass, on_click = just_pass, on_un_hover = just_pass):
		self.surface = pygame.Surface((x_size, y_size))
		self.color = color
		self.surface.fill(color)
		self.rect = self.surface.get_rect()
		self.rect[0] = x_pos
		self.rect[1] = y_pos
		self.priority = priority
		self.on_hover_def = on_hover
		self.on_click_def = on_click
		self.on_un_hover_def = on_un_hover

	def draw(self, target):
		target.blit(self.surface, self.rect)

	def on_click(self):
		self.on_click_def

	def on_hover(self):
		self.on_hover_def

	def on_un_hover(self):
		self.on_un_hover_def

	def mouse_is_in(self):
		mousepos = pygame.mouse.get_pos()
		xcheck = self.rect[0] <= mousepos[0] and self.rect[0] + self.surface.get_size[0] >= mousepos[0]
		ycheck = self.rect[1] <= mousepos[1] and self.rect[1] + self.surface.get_size[1] >= mousepos[1]
		return xcheck and ycheck

class FONT_OBJECT:
	def __init__(self, x_pos = 0, y_pos = 0, bkgcolor = (0, 0, 0), color = (255, 0, 0), priority = 1, fontname = None, fontsize = 16, textstring = "no text here", no_parse = False):
		if not pygame.font.get_init():
			pygame.font.init()
		self.font = pygame.font.SysFont(fontname, fontsize)
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.color = color
		self.priority = priority
		self.rawtext = textstring
		self.no_parse = no_parse

		# Font render does not support null chars or the newline '\n' char. Handle them manually, unless 'no_parse' is set to True.
		# This will just display everything as a single line, trusting the caller to have done parsing already.
		# This is faster, but has no error checking.
		if no_parse:
			fontobj = self.font.render(self.rawtext, True, self.color)
			frect = fontobj.get_rect()
			surf = pygame.Surface((frect[2], frect[3]))
			surf.fill(bkgcolor)
			surf.blit(fontobj, (frect[2], frect[3]))
			self.renderobj = surf

		else:
			# Build a multi-line font object from a bunch of strings split up by newlines.
			formatstrings = self.rawtext.strip().split('\n')
			renderbases = []
			xmax = 0
			ytotal = 0
			for string in formatstrings:
				# Fix an inconsistency with rendering - if we have '\n\n' we want visual space, but font.render reads the resulting string
				# '' as an empty string and instead returns a zero-height surface, which we don't want.
				if len(string) == 0:
					fontobj = self.font.render(' ', True, self.color)
					renderbases.append((fontobj, ytotal))
					fontrect = fontobj.get_rect()
					if fontrect[2] > xmax:
						xmax = fontrect[2]
					ytotal += fontrect[3]
				else:
					fontobj = self.font.render(string, True, self.color)
					renderbases.append((fontobj, ytotal))
					fontrect = fontobj.get_rect()
					if fontrect[2] > xmax:
						xmax = fontrect[2]
					ytotal += fontrect[3]
			surf = pygame.Surface((xmax, ytotal))
			surf.fill(bkgcolor)
			for render in renderbases:
				surf.blit(render[0], (0, render[1]))
			self.renderobj = surf

	def draw(self, target):
		target.blit(self.renderobj, (self.x_pos, self.y_pos))



### Building the GUI ###


# DECORATOR (self, x_size = 100, y_size = 100, x_pos = 0, y_pos = 0, color = (255, 255, 255), priority = 0):
# FONT OBJECT (self, x_pos = 0, y_pos = 0, bkgcolor = (0, 0, 0), color = (255, 0, 0), priority = 1, fontname = None, fontsize = 16, textstring = "no text here", no_parse = False):
# INTERACTABLE (self, x_size = 100, y_size = 100, x_pos = 0, y_pos = 0, color = (255, 255, 255), priority = 0, on_hover = just_pass, on_click = just_pass, on_un_hover = just_pass):

# Make a basic background (1728 x 972)
bkg = BACKGROUND()
# Title Bar Box Elements
t_bar_outer = DECORATOR(1708, 60, 10, 10, color=(128,128,128), priority=1)
t_bar_inner = DECORATOR(1700, 52, 14, 14, color=(220,220,220), priority=2)
t_bar_title = FONT_OBJECT(32, 32, (220,220,220), (0,0,0), 3, None, 32, "Welcome to the Clueless Idiots' Graphical User Interface", False)
title_bar = [t_bar_outer, t_bar_inner, t_bar_title]

