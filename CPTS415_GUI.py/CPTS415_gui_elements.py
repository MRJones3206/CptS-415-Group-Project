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
from CPTS415_dbase import *
from CPTS415_interface import *

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

# A basic hoverable object. Invisible and never rendered, but can be used to detect mouse hovering.
# Will always be overwritten by other hoverable objects. Used to display tooltips for UI bits made with decorators.
class HOVER_OBJECT:
	def __init__ (self, x_size = 100, y_size = 100, x_pos = 100, y_pos = 100, tooltip = None):
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.x_size = x_size
		self.y_size = y_size
		self.priority = -1
		self.tooltip = tooltip

	def on_hover(self, target):
		self.tooltip.draw(target)

	def on_un_hover(self, target):
		pass

	def mouse_is_in(self):
		mousepos = pygame.mouse.get_pos()
		xcheck = self.x_pos <= mousepos[0] and self.x_pos + self.x_size >= mousepos[0]
		ycheck = self.y_pos <= mousepos[1] and self.y_pos + self.y_size >= mousepos[1]
		return xcheck and ycheck

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
		self.x_pos = x_pos
		self.y_pos = y_pos
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
		xcheck = self.x_pos <= mousepos[0] and self.x_pos + self.surface.get_size()[0] >= mousepos[0]
		ycheck = self.y_pos <= mousepos[1] and self.y_pos + self.surface.get_size()[1] >= mousepos[1]
		return xcheck and ycheck

class FONT_OBJECT:
	def __init__(self, x_pos = 0, y_pos = 0, bkgcolor = (0, 0, 0), color = (255, 0, 0), priority = 1, fontname = None, fontsize = 16, textstring = "no text here", no_parse = False, id = 0, force_linecount = -1):
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
			linecount = force_linecount
			for string in formatstrings:
				if linecount != 0:
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
					linecount -= 1
				# Enforce strict line count, if specified. Will pass through if linecount is met or unlimited.
			while linecount > 0:
				fontobj = self.font.render(' ', True, self.color)
				renderbases.append((fontobj, ytotal))
				fontrect = fontobj.get_rect()
				if fontrect[2] > xmax:
					xmax = fontrect[2]
				ytotal += fontrect[3]
				linecount -= 1
			# Build the surface
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
				 button_flavortext = "Some Flavortext Please!", priority = 100, id = 0, on_click_override = just_pass, gui=None):
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
		self.gui = gui

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

# Container class for the display of NODE's
# Actually a more complicated primitive, since it has its own unique priority value, but is has some slightly complicated bits
# that makes it special. Interactivity for on_hover is overloaded here to enable hover-scrolling.
class NODE_CONTAINER:
	def __init__(self):
		# Handle the setup of the container framework (the scrollups and scrolldowns)
		self.top_interactable = INTERACTABLE(692, 40, 424, 90, (180, 180, 180), 100, self.bumpup, just_pass, just_pass, -1)
		self.btm_interactable = INTERACTABLE(692, 40, 424, 918, (180, 180, 180), 100, self.bumpdown, just_pass, just_pass, -1)
		self.surf_composite = pygame.Surface((692, 864))
		self.surf_composite.fill((220,220,220))
		self.surf_composite.blit(self.top_interactable.surface, (0, 0))
		self.surf_composite.blit(self.btm_interactable.surface, (0, 824))
		self.x_pos = 424
		self.y_pos = 90
		self.x_size = 692
		self.y_size = 864
		self.rect = self.surf_composite.get_rect()
		self.has_contents = False
		self.contents_summary = []
		self.contents_detail = []
		self.contents_yoffset = 0
		self.contents_count = 0
		self.contents_surface = None
		self.tooltip_scrollbars = TOOLTIP(tooltip="Hover on these to scroll up and down large node lists.\n\nYou will, obviously, need a node list to do this.\nNodes are displayed with only a summary of their data, you\ncan hover over them to see more details, if relevant.")
		self.tooltip_display = TOOLTIP(tooltip="Once a query is executed, nodes matching that query\nwill show up here. Use the grey bars above and below to\nscroll through the results. Hover over them to see\nadditional data, if any.")
		self.tooltip_node_hover = TOOLTIP(tooltip="It's a node. Some more information might be shown in the data menu above.")
	def bumpup(self):
		if self.contents_yoffset > 0:
			self.contents_yoffset -= 6
	def bumpdown(self):
		if self.contents_yoffset <= 70*self.contents_count - 784 - 4*self.contents_count:
			self.contents_yoffset += 6

	def draw(self, target):
		# No contents? No problem, just render the frame.
		if not self.has_contents:
			target.blit(self.surf_composite, (424, 94))
		else:
			target.blit(self.contents_surface, (428, 134), (0, self.contents_yoffset, 684, self.contents_yoffset + 784))
			target.blit(self.top_interactable.surface, (424, 94))
			target.blit(self.btm_interactable.surface, (424, 918))

			# A hacky fix to some collision issues, but I can't figure out why they are happening...
			surf_fix_1 = pygame.Surface((692, 4))
			surf_fix_1.fill((128,128,128))
			surf_fix_2 = pygame.Surface((692, 10))
			surf_fix_2.fill((220,220,220))
			target.blit(surf_fix_1, (424, 958))
			target.blit(surf_fix_2, (424, 962))

	def on_click(self):
		pass

	def on_hover(self, target):
		if self.top_interactable.mouse_is_in():
			self.bumpup()
			self.tooltip_scrollbars.draw(target)
		if self.btm_interactable.mouse_is_in():
			self.bumpdown()
			self.tooltip_scrollbars.draw(target)
		if self.has_contents:
			mouseposy_onsurf = pygame.mouse.get_pos()[1] - 134
			entry_guess = (int)((self.contents_yoffset + mouseposy_onsurf)/(66))
			if entry_guess < self.contents_count and mouseposy_onsurf > 0:
				target.blit(self.contents_detail[entry_guess], (1138, 94))
				self.tooltip_node_hover.draw(target)
			
		if not (self.top_interactable.mouse_is_in() or self.btm_interactable.mouse_is_in() or self.has_contents):
			self.tooltip_display.draw(target)

	def on_un_hover(self, target):
		pass

	def mouse_is_in(self):
		mousepos = pygame.mouse.get_pos()
		xcheck = self.x_pos <= mousepos[0] and self.x_pos + self.x_size >= mousepos[0]
		ycheck = self.y_pos <= mousepos[1] and self.y_pos + self.y_size >= mousepos[1]
		return xcheck and ycheck
	
	def clear(self):
		self.has_contents = False
		self.contents_summary = []
		self.contents_detail = []

	def populate_content(self, stringlist, stringlist_summary):
		fontobjsummarylist = []
		fontobjdetaillist = []
		if len(stringlist) != len(stringlist_summary):
			print("Can't work with a node list and a node summary list of differing lengths!")
			return
		for k in range(len(stringlist)):
			string = stringlist[k]
			summary = stringlist_summary[k]
			# Build the summary objects
			fontobj = FONT_OBJECT(0,0,(220,220,220), (0,0,0), -1, None, 18, summary, False, -1, 3).renderobj
			base_template = DECORATOR(684, 70, 0, 0, (128,128,128), -1, -1).surface
			deco_inner = DECORATOR(676, 62, 0, 0, (220,220,220), -1, -1).surface
			base_template.blit(deco_inner, (4,4))
			base_template.blit(fontobj, (8, 8))
			fontobjsummarylist.append(base_template)

			# Build the detail objects.
			detail_fontobj = FONT_OBJECT(0,0,(220,220,220), (0,0,0), -1, None, 18, string, False, -1).renderobj
			detail_base_template = DECORATOR(572,448,1134,94,(220,220,220), -1, -1).surface
			detail_base_template.blit(detail_fontobj, (4,4))
			fontobjdetaillist.append(detail_base_template)

		# Build the visual representation of the summaries.
		summary_surface = pygame.Surface((684, (len(fontobjsummarylist)*70) + 4))
		summary_surface.fill((220,220,220))
		for i in range(len(fontobjsummarylist)):
			summary_surface.blit(fontobjsummarylist[i], (0, 66*i))

		self.contents_count = len(fontobjsummarylist)
		self.contents_detail = fontobjdetaillist
		self.contents_summary = fontobjsummarylist
		self.contents_surface = summary_surface
		self.contents_yoffset = 0
		self.has_contents = True
			

### Building the GUI ###

# DECORATOR (self, x_size = 100, y_size = 100, x_pos = 0, y_pos = 0, color = (255, 255, 255), priority = 0):
# FONT OBJECT (self, x_pos = 0, y_pos = 0, bkgcolor = (0, 0, 0), color = (255, 0, 0), priority = 1, fontname = None, fontsize = 16, textstring = "no text here", no_parse = False):
# INTERACTABLE (self, x_size = 100, y_size = 100, x_pos = 0, y_pos = 0, color = (255, 255, 255), priority = 0, on_hover = just_pass, on_click = just_pass, on_un_hover = just_pass):

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

		# the one on the bottom
		bgr_right_contextmenu_outer = DECORATOR(588, 400, 1130, 562, color=(128,128,128), priority=1, id=7)
		bgr_right_contextmenu_inner = DECORATOR(580, 392, 1134, 566, color=(220,220,220), priority=2, id=8)

		# the one on the top
		bgr_right_datamenu_outer = DECORATOR(588, 456, 1130, 90, color=(128,128,128), priority=1, id=9)
		bgr_right_datamenu_inner = DECORATOR(580, 448, 1134, 94, color=(220,220,220), priority=2, id=10)

		button_framing = [bgr_left_outer, bgr_left_inner, bgr_center_outer, bgr_center_inner, bgr_right_contextmenu_outer, bgr_right_contextmenu_inner, bgr_right_datamenu_outer, bgr_right_datamenu_inner]

		# Declaration of button functions here.
		def trigger_nodelist_update():
			dlist_1 = ["data 1-2", "data 2", "data 3", "data 4", "data 5", "data 1", "data 2", "data 3", "data 4", "data 5", "data 1", "data 2", "data 3", "data 4", "data 5", "data 1", "data 2", "data 3", "data 4", "data 5", "data 1", "data 2", "data 3", "data 4", "data 5", "data 1", "data 2", "data 3", "data 4", "data 5"]
			dlist_2 = ["data test\ndsd", "data 2\nj\nk\nl\nm", "data 3", "data 4", "data 5", "data 1", "data 2", "data 3", "data 4", "data 5", "data 1", "data 2", "data 3", "data 4", "data 5","data 1", "data 2\nj\nk\nl\nm", "data 3", "data 4", "data 5", "data 1", "data 2", "data 3", "data 4", "data 5", "data 1", "data 2", "data 3", "data 4", "data 5"]
			self.update_node_container(dlist_1, dlist_2)

		def execute_search_top():
			# Get user inputs here.
			data = search_top(count = 5, category = 'age', filterSign = '<=', value = 400)
			arrayOne = []
			arrayTwo = []
			for x in data:
				entry = "Node ID = " + x['_key'] + "\nNode Uploader = " + x['uploader'] + "\nNode Category = " + x['category']
				arrayOne.append(entry)
				entryTwo = "Node ID = " + x['_key'] + "\nNode Uploader = " + x['uploader'] + "\nNode Category = " + x['category'] \
					+ "\nNode Age = " + str(x['age']) + "\nNode Length = " + str(x['length']) + "\nNode Views = " + str(x['views']) \
					+ "\nNode Rate = " + str(x['rate']) + "\nNode Ratings = " +str(x['ratings']) + "\nNode Comments = " + str(x['comments'])
				arrayTwo.append(entryTwo)
				
			self.update_node_container(arrayTwo, arrayOne)

		def execute_search_range():
			# Get user inputs here.
			data = search_range(category = 'age', lowRange = 500, highRange = 600)
			arrayOne = []
			arrayTwo = []
			for x in data:
				entry = "Node ID = " + x['_key'] + "\nNode Uploader = " + x['uploader'] + "\nNode Category = " + x['category']
				arrayOne.append(entry)
				entryTwo = "Node ID = " + x['_key'] + "\nNode Uploader = " + x['uploader'] + "\nNode Category = " + x['category'] \
					+ "\nNode Age = " + str(x['age']) + "\nNode Length = " + str(x['length']) + "\nNode Views = " + str(x['views']) \
					+ "\nNode Rate = " + str(x['rate']) + "\nNode Ratings = " +str(x['ratings']) + "\nNode Comments = " + str(x['comments'])
				arrayTwo.append(entryTwo)
			self.update_node_container(arrayTwo, arrayOne)

		def execute_get_stats():
			data = get_stats()
			resultList = [(key, value) for key, value in data.items()]
			self.update_node_container([str(x[1]) for x in resultList], list(data))
		
		def execute_pagerank():
			# Get user inputs here.
			data = pagerank(20)
			arrayOne = []
			arrayTwo = []
			
			# for x in data:
			# 	arrayOne.append(entry)
			# 	entry = "Node ID = " + x['_key'] + "\nNode Uploader = " + x['uploader'] + "\nNode Category = " + x['category']
			# 	entryTwo = "Node ID = " + x['_key'] + "\nNode Uploader = " + x['uploader'] + "\nNode Category = " + x['category'] \
			# 		+ "\nNode Age = " + str(x['age']) + "\nNode Length = " + str(x['length']) + "\nNode Views = " + str(x['views']) \
			# 		+ "\nNode Rate = " + str(x['rate']) + "\nNode Ratings = " +str(x['ratings']) + "\nNode Comments = " + str(x['comments'])
			# 	arrayTwo.append(entryTwo)
			
			# for x in data:
			# 	entry = "Node ID = " + x['_key'] + "\nNode Uploader = " + x['uploader'] + "\nNode Category = " + x['category']
			# 	arrayOne.append(entry)
			# 	entryTwo = "Node ID = " + x['_key'] + "\nNode Uploader = " + x['uploader'] + "\nNode Category = " + x['category'] \
			# 		+ "\nNode Age = " + str(x['age']) + "\nNode Length = " + str(x['length']) + "\nNode Views = " + str(x['views']) \
			# 		+ "\nNode Rate = " + str(x['rate']) + "\nNode Ratings = " +str(x['ratings']) + "\nNode Comments = " + str(x['comments'])
			# 	arrayTwo.append(entryTwo)
			self.update_node_container(arrayTwo, arrayOne)
		
		# Give me some BUTTONS
		test_btn = BUTTON_PRIMITIVE(380, 100, 20, 100, "TEST BUTTON PLEASE IGNORE", "Button Flavortext Goes Here\nOr here...\n\n\nOr possibly here.", 100, 11, lambda: print("button click noise"), gui=self)
		test_btn2 = BUTTON_PRIMITIVE(380, 100, 20, 220, "Search Top", "Search for top stuff", 100, 12, execute_search_top, gui=self)
		test_btn3 = BUTTON_PRIMITIVE(380, 100, 20, 340, "Search Range", "search for rangey stuff", 100, 13, execute_search_range,gui=self)
		test_btn4 = BUTTON_PRIMITIVE(380, 100, 20, 460, "PageRank", "Execute a pagerank job", 100, 14, execute_pagerank,gui=self)
		test_btn5 = BUTTON_PRIMITIVE(380, 100, 20, 580, "Get Statistics", "Button Flavortext 5", 100, 15, execute_get_stats,gui=self)
		test_btn6 = BUTTON_PRIMITIVE(380, 100, 20, 700, "TEST BUTTON 6", "Button Flavortext 6", 100, 16, trigger_nodelist_update,gui=self)

		buttons = [test_btn, test_btn2, test_btn3, test_btn4, test_btn5, test_btn6]

		# Node Container
		node_container = NODE_CONTAINER()
		self.node_container = node_container

		# Extra Tooltips
		menu_tooltip = TOOLTIP(tooltip="Proudly made by the Clueless Idiots listed here...\n\nMatthew R. Jones - 11566414\nPut your names here nerds.")
		datamenu_tooltip = TOOLTIP(tooltip="The data menu. Once you have results for non-node queries, they are\ndumped directly into this. If you hover over node entries returned by\na query, they will also show additional information, if applicable.")
		contextmenu_tooltip = TOOLTIP(tooltip="The context menu. Shows information about what you are looking at.")

		menu_hoverobj = HOVER_OBJECT(1708, 60, 10, 10, menu_tooltip)
		datamenu_hoverobj = HOVER_OBJECT(588, 456, 1130, 90, datamenu_tooltip)
		contextmenu_hoverobj = HOVER_OBJECT(588, 400, 1130, 562, contextmenu_tooltip)

		tooltips = [menu_hoverobj, datamenu_hoverobj, contextmenu_hoverobj]
		# End of display building

		# Drawables
		self.draw_queue.append(bkg)
		self.draw_queue += title_bar
		self.draw_queue += button_framing
		self.draw_queue += buttons
		self.draw_queue.append(self.node_container)

		# Hoverables
		self.hover_queue += buttons
		self.hover_queue += tooltips
		self.hover_queue.append(self.node_container)

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

	def update_node_container(self, stringlist, stringlist_summary):
		self.node_container.populate_content(stringlist, stringlist_summary)
