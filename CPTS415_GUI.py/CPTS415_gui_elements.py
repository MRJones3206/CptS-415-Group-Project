# Matthew R. Jones - SID 11566314
# CptS_415 Final Project Graphical Interface Code
# *_ui_elements.py

# *_ui_elements.py serves as a repository for the various UI element classes inside the GUI
# Each element must, at a minimum, declare an instance of 'draw', which will accept a display to blit itself to, and
# have an accessible positive integer value 'priority' to assign its drawing priority.

# All primitive objects should have a unique identifier provided for their id if initialized - values from 0 to 50,000 are reserved
# for my own GUI setup - use 'request_id()' to get one if you want to make your own to ensure that deletion attempts will find their target.
# Composite objects composed of multiple primitives should assign them their composite ID - the composit is responsible for managing their own
# objects, so deletion of the composit implicitly deletes the primitives used to make it.

# Also serves as repository for the GUI class - the actual data object that contains the GUI. This is puppeted by the _boot loop.
import pygame

# UID control for GUI Objects. Very crappily designed (deletion runs in O(N)) but since the GUI should never have more than about 150
# objects, and all deletions will usually ocurr from the front to the back of the queue, it will usually be fairly irrelevant.
ID_COUNTER = 50000
def request_id():
	global ID_COUNTER
	ID_COUNTER += 1
	return ID_COUNTER


# Default function value - does nothing.
def just_pass():
	pass

# Container for GUI elements. Responsible for determining hover and click successes and updating/drawing itself (flip is called in the
# _boot loop.)
class GUI:
	# Default GUI constructor. Builds a GUI out of the elements provided in _gui_elements 
	def __init__(self, display, database):
		self.display = display
		self.draw_queue = []
		self.draw_queue_markdirty = False
		self.hover_queue = []
		self.hover_queue_markdirty = False
		self.database = database

		# Display Building Goes Here...

		self.draw_queue.append(bkg)
		self.draw_queue += title_bar
		self.draw_queue += button_framing
		self.draw_queue += buttons

		self.hover_queue += buttons

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
				item.on_hover(self.display)
			else:
				item.on_un_hover(self.display)

# A basic decorator object. Used mostly for window dressing.
class DECORATOR:
	def __init__(self, x_size = 100, y_size = 100, x_pos = 0, y_pos = 0, color = (255, 255, 255), priority = 0, id = 0):
		self.surface = pygame.Surface((x_size, y_size))
		self.color = color
		self.surface.fill(color)
		self.rect = self.surface.get_rect()
		self.rect[0] = x_pos
		self.rect[1] = y_pos
		self.priority = priority
		self.id = id

	def draw(self, target):
		target.blit(self.surface, self.rect)

# Special decorator used to color the background of the screen. Always the lowest possible priority (aka -1)
# No need for ID's - you should only ever use one background anyway.
class BACKGROUND:
	def __init__(self, color = (220, 220, 220)):
		self.color = color
		self.priority = -1

	def draw(self, target):
		target.fill(self.color)

# Wildcard for hoverable and clickable objects. Must provide functionality for on_hover, on_un_hover or on_click, otherwise will pass.
class INTERACTABLE:
	def __init__(self, x_size = 100, y_size = 100, x_pos = 0, y_pos = 0, color = (255, 255, 255), priority = 0, on_hover = just_pass, on_click = just_pass, on_un_hover = just_pass, id = 0):
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
		self.id = id

	def draw(self, target):
		target.blit(self.surface, self.rect)

	def on_click(self):
		self.on_click_def

	def on_hover(self, target):
		self.on_hover_def

	def on_un_hover(self, target):
		self.on_un_hover_def

	def mouse_is_in(self):
		mousepos = pygame.mouse.get_pos()
		xcheck = self.rect[0] <= mousepos[0] and self.rect[0] + self.surface.get_size[0] >= mousepos[0]
		ycheck = self.rect[1] <= mousepos[1] and self.rect[1] + self.surface.get_size[1] >= mousepos[1]
		return xcheck and ycheck

class FONT_OBJECT:
	def __init__(self, x_pos = 0, y_pos = 0, bkgcolor = (0, 0, 0), color = (255, 0, 0), priority = 1, fontname = None, fontsize = 16, textstring = "no text here", no_parse = False, id = 0):
		if not pygame.font.get_init():
			pygame.font.init()
		self.font = pygame.font.SysFont(fontname, fontsize)
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.color = color
		self.priority = priority
		self.rawtext = textstring
		self.no_parse = no_parse
		self.id = id

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

# Basically just a DECORATOR, an INTERACTABLE, and a FONT_OBJECT and some built in behavioral functionality so they behave pretty
# when called by the GUI. Lets me override the on_hover, on_un_hover, and on_click locally without needing external functions cluttering
# up the GUI main namespace. These were NOT built with the intention of being used by other people, (Stick with the primitives if you want
# to make your own custom GUI stuff), but you are welcome to steal them and declare your own class. Since they are custom made, a lot of
# what would otherwise be initialization behavior is hardcoded.
class BUTTON_PRIMITIVE:
	def __init__(self, x_size = 100, y_size = 100, x_pos = 0, y_pos = 0, buttontext="bingbong",
				 button_flavortext = "Some Flavortext Please!", priority = 100, id = 0, on_click_override = just_pass):
		# Build the shell of the buttons.
		self.btn_state_unselected = pygame.Surface((x_size, y_size))
		self.btn_state_unselected.fill((128,128,128))
		unselected_inner = pygame.Surface((x_size - 8, y_size - 8))
		unselected_inner.fill((220, 220, 220))
		self.btn_state_unselected.blit(unselected_inner, (4, 4))

		self.btn_state_selected = pygame.Surface((x_size, y_size))
		self.btn_state_selected.fill((128,128,128))
		selected_inner = pygame.Surface((x_size - 8, y_size - 8))
		selected_inner.fill((200, 200, 200))
		self.btn_state_selected.blit(selected_inner, (4, 4))

		# Just reuse the FONT_OBJECT init and steal the surface it generates.
		font_obj_unselected = FONT_OBJECT(0,0, (220,220,220), (0,0,0), 101, None, 24, buttontext, False, id)
		font_obj_selected = FONT_OBJECT(0,0, (200,200,200), (0,0,0), 101, None, 24, buttontext, False, id)

		self.btn_state_unselected.blit(font_obj_unselected.renderobj, (4 + (x_size - font_obj_unselected.renderobj.get_rect()[2])/2, 4 + (y_size - font_obj_unselected.renderobj.get_rect()[3])/2))
		self.btn_state_selected.blit(font_obj_selected.renderobj, (4 + (x_size - font_obj_selected.renderobj.get_rect()[2])/2, 4 + (y_size - font_obj_selected.renderobj.get_rect()[3])/2))
		self.btn_surface = self.btn_state_unselected
		self.rect = self.btn_state_unselected.get_rect()
		self.x_size = x_size
		self.y_size = y_size
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.id = id
		self.priority = priority
		self.tooltip = TOOLTIP(tooltip=button_flavortext)

		self.click_override = on_click_override
		

	def draw(self, target):
		target.blit(self.btn_surface, (self.x_pos, self.y_pos))

	def on_click(self):
		self.click_override()

	def on_hover(self, target):
		self.btn_surface = self.btn_state_selected
		self.tooltip.draw(target)

	def on_un_hover(self, target):
		self.btn_surface = self.btn_state_unselected

	def mouse_is_in(self):
		mousepos = pygame.mouse.get_pos()
		xcheck = self.x_pos <= mousepos[0] and self.x_pos + self.x_size >= mousepos[0]
		ycheck = self.y_pos <= mousepos[1] and self.y_pos + self.y_size >= mousepos[1]
		return xcheck and ycheck

# A fancy descriptor. Used to describe various operations when certain objects are hovered over. As with BUTTON_PRIMITIVE, some functionality
# is built in. No direct need to use ID or priority - the element is drawn only when specified by the implementer, and will be overwritten.
class TOOLTIP:
	def __init__(self, bkgcolor = (220, 220, 220), textcolor = (0, 0, 0), tooltip = "Nothing to see here... yet.", priority = -1):
		self.priority = 100
		self.id = request_id()
		# Just steal the surface from a decorator...
		basestate = DECORATOR(580, 392, 1134, 566, bkgcolor, priority=-1, id=-1)
		basestate = basestate.surface
		# And then a FONT_OBJECT.
		fontstate = FONT_OBJECT(bkgcolor = bkgcolor, color = textcolor, fontname = None, fontsize = 18, textstring = tooltip, no_parse = False, id = -1)
		basestate.blit(fontstate.renderobj, (4, 4))
		self.surface = basestate
	
	def draw(self, target):
		target.blit(self.surface, (1134, 566))
### Building the GUI ###


# DECORATOR (self, x_size = 100, y_size = 100, x_pos = 0, y_pos = 0, color = (255, 255, 255), priority = 0):
# FONT OBJECT (self, x_pos = 0, y_pos = 0, bkgcolor = (0, 0, 0), color = (255, 0, 0), priority = 1, fontname = None, fontsize = 16, textstring = "no text here", no_parse = False):
# INTERACTABLE (self, x_size = 100, y_size = 100, x_pos = 0, y_pos = 0, color = (255, 255, 255), priority = 0, on_hover = just_pass, on_click = just_pass, on_un_hover = just_pass):

# Make a basic background (1728 x 972)
bkg = BACKGROUND()
# Title Bar Box Elements
t_bar_outer = DECORATOR(1708, 60, 10, 10, color=(128,128,128), priority=1, id=0)
t_bar_inner = DECORATOR(1700, 52, 14, 14, color=(220,220,220), priority=2, id=1)
t_bar_title = FONT_OBJECT(32, 32, (220,220,220), (0,0,0), 3, None, 32, "Welcome to the Clueless Idiots' Graphical User Interface", False, id=2)
title_bar = [t_bar_outer, t_bar_inner, t_bar_title]

# Remember - screen size is (1728 x 972)
# Button Framings
bgr_left_outer = DECORATOR(400, 872, 10, 90, color=(128,128,128), priority=1, id=3)
bgr_left_inner = DECORATOR(392, 864, 14, 94, color=(220,220,220), priority=2, id=4)

bgr_center_outer = DECORATOR(700, 872, 420, 90, color=(128,128,128), priority=1, id=5)
bgr_center_inner = DECORATOR(692, 864, 424, 94, color=(220,220,220), priority=2, id=6)

bgr_right_contextmenu_outer = DECORATOR(588, 400, 1130, 562, color=(128,128,128), priority=1, id=7)
bgr_right_contextmenu_inner = DECORATOR(580, 392, 1134, 566, color=(220,220,220), priority=2, id=8)

bgr_right_datamenu_outer = DECORATOR(588, 456, 1130, 90, color=(128,128,128), priority=1, id=9)
bgr_right_datamenu_inner = DECORATOR(580, 448, 1134, 94, color=(220,220,220), priority=2, id=10)

button_framing = [bgr_left_outer, bgr_left_inner, bgr_center_outer, bgr_center_inner, bgr_right_contextmenu_outer, bgr_right_contextmenu_inner, bgr_right_datamenu_outer, bgr_right_datamenu_inner]

# Give me some BUTTONS
test_btn = BUTTON_PRIMITIVE(380, 100, 20, 100, "TEST BUTTON PLEASE IGNORE", "Button Flavortext Goes Here\nOr here...\n\n\nOr possibly here.", 100, 11, lambda: print("button click noise"))
test_btn2 = BUTTON_PRIMITIVE(380, 100, 20, 220, "TEST BUTTON 2", "Button Flavortext part two electric boogaloo", 100, 11, lambda: print("button click noise 2"))
test_btn3 = BUTTON_PRIMITIVE(380, 100, 20, 340, "TEST BUTTON 3", "Button Flavortext 3", 100, 11, lambda: print("button click noise 3"))
test_btn4 = BUTTON_PRIMITIVE(380, 100, 20, 460, "TEST BUTTON 4", "Button Flavortext 4", 100, 11, lambda: print("button click noise 4"))
test_btn5 = BUTTON_PRIMITIVE(380, 100, 20, 580, "TEST BUTTON 5", "Button Flavortext 5", 100, 11, lambda: print("button click noise 5"))
test_btn6 = BUTTON_PRIMITIVE(380, 100, 20, 700, "TEST BUTTON 6", "Button Flavortext 6", 100, 11, lambda: print("button click noise 6"))

buttons = [test_btn, test_btn2, test_btn3, test_btn4, test_btn5, test_btn6]