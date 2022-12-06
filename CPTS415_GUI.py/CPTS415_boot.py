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
from CPTS415_setup import setup
from CPTS415_teardown import teardown
from CPTS415_ui import *

# You have to call this before pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
CLOCK = pygame.time.Clock() # For framerate-based update cycles.
# Use a fixed screen size - don't want to have to code dynamic scaling objects.
DISPLAY = pygame.display.set_mode((1728, 972))
# A list of every drawable object in the GUI instance, in the form [(object, priority)]. Objects with a higher priority will be
# drawn on top of objects of a lower priority. Equal priority objects will be drawn in an arbitrary order.
DRAW_QUEUE = []
# Indicate to the drawing queue whether we will need to re-sort the drawing queue priority before drawing objects to the screen.
DRAW_QUEUE_MARKDIRTY = False
# A list of every hoverable object in the GUI instance, in the form [(object, priority)]. Objects with a higher priority will be
# drawn on top of objects of a lower priority. Equal priority objects will be drawn in an arbitrary order.
HOVER_QUEUE = []
# Indicate whether we will need to re-sort the hovering queue priority before drawing objects to the screen.
HOVER_QUEUE_MARKDIRTY = False 
# Global controller for GUI loop. Set to false to exit GUI drawing and enter teardown.
RUNNING = True
# A list of queued operations to execute. Used to delay the execution of halting actions so that the GUI
# can draw indicators that they are running - there shouldn't ever be more than one object in this at a time, as
# the queue is executed and flushed each draw cycle.
OP_QUEUE = []
# Indicates whether we should spend this cycle handling a queued operation. If so, UI interaction is paused (properly, not evaluated)
# and the operation is executed.
OP_QUEUE_FLUSH = False
# The location of the mouse. Used so we don't have to keep polling it.
MOUSE_POSITION = (0,0)

# UI hooks
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
	print("mouseclick at " + str(MOUSE_POSITION[0]), " ", str(MOUSE_POSITION[1]), "\n")

KEYBINDS = {pygame.K_ESCAPE: escape, pygame.K_DOWN: down, pygame.K_UP: up, pygame.K_LEFT: left, pygame.K_RIGHT: right}

# Basic UI polling functionality for GUI rendering loops. Allows for the capture of keyboard and mouse events,
# mouse position detection, and special keyboard characters for GUI escape.
def ui_poll():
	global MOUSE_POSITION
	MOUSE_POSITION = pygame.mouse.get_pos()
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key in KEYBINDS:
				KEYBINDS[event.key]()
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouseclick()
		elif event.type == pygame.QUIT:
			global RUNNING
			RUNNING = False

if __name__ == "__main__":
	# Initial system setup.
	setup()

	while RUNNING:
		if OP_QUEUE_FLUSH:
			OP_QUEUE[0]
			OP_QUEUE_FLUSH = False
			OP_QUEUE.clear()
		else:
			ui_poll()


		# Tick our framerate forward one frame (1/120th of a second, by default)
		CLOCK.tick(120)
		# Flip the blitted display - aka, render it onscreen.
		pygame.display.flip()

	teardown()