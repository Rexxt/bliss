import tools
from random import random
from time import time
from math import sin, pi

class Tab:
    def __init__(self, app, data):
        self.title = 'Welcome'
        self.tab_name = 'welcome'
        self.status_text = 'Bliss ' + app.VERSION

        self.visual_keybinds = [
            ['Ctrl+Q', 'Quit'],
            ['Ctrl+TAB', 'Change tab'],
            ['Ctrl+W', 'Exit tab'],
            ['Ctrl+T', 'Create tab'],
            ['Ctrl+B', 'Open project browser'],
        ]
        self.tips = [
            ['[Ctrl+T]welcome[ENTER]', 'Create a tab to this page'],
            ['[Ctrl+T]editor <file>[ENTER]', 'Create an editor tab']
        ]
        
    def key_down(self, app, event): pass
    def key_up(self, app, event): pass
    def text_input(self, app, event): pass

    def update(self, app, pygame, dt): pass

    def draw(self, app, pygame):
        tools.write_to_screen(app.tab_surface, app.interface_font_bold, 'Welcome to Bliss!', (app.tab_y*(2+sin(time()*(pi/2))), 0), (True, (255,)*3))
        tools.write_to_screen(app.tab_surface, app.interface_font, 'Bliss is a new text editor built from the ground up using PyGame.', (app.tab_y, app.interface_font.get_height()*1), (True, (255,)*3))
        tools.write_to_screen(app.tab_surface, app.interface_font, 'Its main focus is style mixed with productivity.', (app.tab_y, app.interface_font.get_height()*2), (True, (255,)*3))

        tools.write_to_screen(app.tab_surface, app.interface_font_bold, 'Key bindings', (app.tab_y, app.interface_font.get_height()*4), (True, (255,)*3))
        tools.write_to_screen(app.tab_surface, app.interface_font, 'Bliss limits the usage of the mouse for increased productivity.', (app.tab_y, app.interface_font.get_height()*5), (True, (255,)*3))
        for i in range(len(self.visual_keybinds)):
            bind = self.visual_keybinds[i]

            tools.write_to_screen(app.tab_surface, app.interface_font_bold, f'[{bind[0]}]', (app.tab_y, app.interface_font.get_height()*(6+i)), (True, (255,)*3))
            tools.write_to_screen(app.tab_surface, app.interface_font, bind[1], (app.tab_y + 200, app.interface_font.get_height()*(6+i)), (True, (255,)*3))
        
        tools.write_to_screen(app.tab_surface, app.interface_font_bold, 'Tips', (app.tab_y, app.interface_font.get_height()*(7 + len(self.visual_keybinds))), (True, (255,)*3))
        for i in range(len(self.tips)):
            tip = self.tips[i]

            tools.write_to_screen(app.tab_surface, app.interface_font_bold, tip[0], (app.tab_y, app.interface_font.get_height()*(8+len(self.visual_keybinds)+i)), (True, (255,)*3))
            tools.write_to_screen(app.tab_surface, app.interface_font, tip[1], (app.tab_y + 200, app.interface_font.get_height()*(8+len(self.visual_keybinds)+i)), (True, (255,)*3))

