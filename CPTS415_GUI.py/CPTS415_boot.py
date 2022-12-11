# Matthew R. Jones - SID 11566314
# CptS_415 Final Project Graphical Interface Code
# *_boot.py

# *_boot.py is responsible for the initial setup and teardown of the project GUI, as well as serving as
# the highest layer for GLOBAL program values, human interface and graphical object action queues, and
# establishing the pygame-based running GUI instance.

# Most users will require running 'pip install pygame' in their python environment to get this library.
# https://www.pygame.org/wiki/GettingStarted  for new users.
import pygame
import os
from CPTS415_dbase import *
from CPTS415_gui_elements import *
import sys

# You have to call this before pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
#sysfonts = pygame.font.get_fonts()
font_24 = pygame.font.Font(None, 24)
CLOCK = pygame.time.Clock() # For framerate-based update cycles.
# Use a fixed screen size - don't want to have to code dynamic scaling objects.
DISPLAY = pygame.display.set_mode((1728, 972))
### Global Control Values ###

# Global controller for GUI loop. Set to false to exit GUI drawing and enter teardown.
RUNNING = True

### UI hooks and UI control functions. ###

def escape():
	global RUNNING
	RUNNING = False

def down():
	pass

def up():
	pass

def left():
	pass

def right():
	pass

def mouseclick():
	# Find the highest priority object in the hover_queue...
	iref = None
	for item in gui.hover_queue:
		if item.mouse_is_in() and (iref is None or iref.priority < item.priority):
			iref = item
	iref.on_click()

KEYBINDS = {pygame.K_ESCAPE: escape, pygame.K_DOWN: down, pygame.K_UP: up, pygame.K_LEFT: left, pygame.K_RIGHT: right}

# Basic UI polling functionality for GUI rendering loops. Allows for the capture of keyboard and mouse events,
# mouse position detection, and special keyboard characters for GUI escape.
def ui_poll():
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key in KEYBINDS:
				KEYBINDS[event.key]()
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouseclick()
		elif event.type == pygame.QUIT:
			global RUNNING
			RUNNING = False

### Program Execution ###


if __name__ == "__main__":

	if len(sys.argv) <= 1: print("Needed argument is 'truncate' or 'delete' or 'create' for database mode.")
	if sys.argv[1] == 'create' or sys.argv[1] == 'truncate':
		if len(sys.argv) <= 2: 
			print("Number of files to ingest are required.")
			print("python CPTS415_boot.py <Truncat|Create> <Number of files to ingest>")
			exit()

	if sys.argv[1] == 'create' or sys.argv[1] == 'truncate':
		database = Dbase(delete_mode=sys.argv[1], population_path_count=sys.argv[2])
	else:
		database = Dbase(delete_mode=sys.argv[1])

	
	# Ugly, given that this means GUI is a controller of the database calls (normally we would want to seperate these planes entirely)
	# but the tradeoff is that people can directly program call-response functionality from Arango through the GUI, which means they don't
	# have to touch any of the GUI code directly.
	gui = GUI(DISPLAY, database)

	while RUNNING:
		ui_poll()
		gui.draw()
		gui.hover()		

		# Tick our framerate forward one frame (1/120th of a second, by default)
		CLOCK.tick(120)
		# Flip the blitted display - aka, render it onscreen.
		pygame.display.flip()

	pygame.quit()
	#teardown goes here