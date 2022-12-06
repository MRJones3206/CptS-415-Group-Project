# Matthew R. Jones - SID 11566314
# CptS_415 Final Project Graphical Interface Code
# *_ui.py

# *_ui.py is responsible for the handling of UI control messages, keyboard and mouse event capture,
# and anything of that nature. If other group members choose to request keybinding, that would also
# go here.
import pygame
#from CPTS415_boot import update_RUNNING

# A container for all of the function operations that ui reports we should execute.
FLAGS = {}
# Declare the functionality of the keybind function pointers.
def escape():
	FLAGS["boot"] = [""]

def down():
	pass

def up():
	pass

def left():
	pass

def right():
	pass

def mouseclick():
	mousepos = pygame.mouse.get_pos()
	print("mouseclick at " + str(mousepos[0]), " ", str(mousepos[1]), "\n")

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
			RUNNING = False