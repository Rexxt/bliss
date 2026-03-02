# bliss
# edit code and text - blissfully
# extensible, modulable code editor with an emphasis on productivity and looks
# this project follows the ti* philosophy: small, very extensible, doesn't compromise looks for usability and vice versa

import os
from rich import print
from sys import argv
command_line_arguments = argv[1:]
import pygame
import tools
import json
import time
import shlex

# define tabs
import tabs.welcome as tab_welcome
import tabs.editor as tab_editor

if not os.path.isdir('tifer'):
    print('[red]tifer not installed, exiting[/red]')
    print('To install tifer, run [blue]git clone https://github.com/rexxt/tifer.git[/blue].')
    exit(1)

# from tifer.tifer import FileEditor

pygame.init()

class App:
    VERSION = '0.1.1'

    def __init__(self):
        self.ui_config = json.load(open('UI.json'))

        self.interface_font = pygame.font.SysFont(self.ui_config['interface_font'][0], self.ui_config['interface_font'][1])
        self.interface_font_bold = pygame.font.SysFont(self.ui_config['interface_font'][0], self.ui_config['interface_font'][1], bold=True)
        self.editor_font = pygame.font.SysFont(self.ui_config['editor_font'][0], self.ui_config['editor_font'][1])
        self.editor_font_bold = pygame.font.SysFont(self.ui_config['editor_font'][0], self.ui_config['editor_font'][1], bold=True)

        self.current_tab = 0
        self.open_tabs = []
        self.tabs = {
            'welcome': tab_welcome,
            'editor': tab_editor,
        }
        self.project = ''
        if len(command_line_arguments) > 0:
            self.project = command_line_arguments.pop()
            if os.path.isfile(self.project):
                self.open_tab('editor', self.project)

        pygame.display.set_caption("Bliss - " + ("no project" if self.project == '' else self.project))
        logo = pygame.image.load("icon.png")
        pygame.display.set_icon(logo)

        self.screen = pygame.display.set_mode((640,360), pygame.RESIZABLE)
        self.tab_surface = pygame.Surface((640,360-self.interface_font.get_height()*3), pygame.RESIZABLE)

        self.toasts = [['', None, 0]] # message (str), type ('info', 'error'), display start time
        self.tab_palette = None
    
    def post_toast(self, string, toast_type):
        if type(string) != str:
            raise Exception('expected str as toast string')
        if toast_type not in ('info', 'error'):
            raise Exception('expected valid toast type (info or error)')
        self.toasts.append([string, toast_type, time.time()])

    def key_down(self, event):
        print(event)
        if event.unicode == '\x11':
            self.running = False
        elif event.unicode == '\x17':
            self.tab_palette = None
            self.close_tab(self.current_tab)
        elif event.unicode == '\x14':
            if type(self.tab_palette) == str:
                self.tab_palette = None
            else:
                self.tab_palette = ''
        elif event.key == pygame.K_TAB and pygame.K_LCTRL in self.keys:
            print(self.current_tab)
            self.current_tab += 1
            if self.current_tab >= len(self.open_tabs):
                self.current_tab = 0
        elif self.tab_palette == None:
            self.open_tabs[self.current_tab].key_down(self, event)
        if self.tab_palette != None:
            if event.key == pygame.K_BACKSPACE:
                self.tab_palette = self.tab_palette[:-1]
            elif event.key == pygame.K_RETURN:
                command = shlex.split(self.tab_palette)
                args = command[1:]
                if len(args) == 1:
                    args = args[0]
                elif len(args) == 0:
                    args = None
                command = command[0]
                self.tab_palette = None
                try:
                    self.open_tab(command, args)
                except KeyError as e:
                    self.post_toast(f"No tab named '{command}'.", 'error')
                except Exception as e:
                    self.post_toast(f"Error creating '{command}': {e}", 'error')

    def text_input(self, event):
        print(event)
        if self.tab_palette != None:
            self.tab_palette += event.text
        else:
            self.open_tabs[self.current_tab].text_input(self, event)

    def key_up(self, event):
        print(event)
        self.open_tabs[self.current_tab].key_up(self, event)

    def open_tab(self, name, data=None):
        self.open_tabs.insert(self.current_tab + 1, self.tabs[name].Tab(self, data))
    
    def close_tab(self, id):
        self.open_tabs.pop(id)
        if self.current_tab >= len(self.open_tabs):
            self.current_tab = len(self.open_tabs) - 1
        if len(self.open_tabs) == 0:
            self.open_tab('welcome')
            self.post_toast('Cannot close only tab - returning to Welcome screen.', 'error')
            self.current_tab = 0

    def mainloop(self):
        self.keys = []
        if len(self.open_tabs) < 1:
            self.open_tab('welcome', None)
        self.current_tab = 0
        self.running = True
        last_update = time.time()
        while self.running:
            self.screen.fill(self.ui_config['application_background'])
            dt = time.time() - last_update
            last_update = time.time()
            
            for event in pygame.event.get():
                #print(event)
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN:
                    self.key_down(event)
                    self.keys.append(event.key)
                elif event.type == pygame.KEYUP:
                    self.key_up(event)
                    self.keys.remove(event.key)
                elif event.type == pygame.TEXTINPUT:
                    self.text_input(event)

            self.open_tabs[self.current_tab].update(self, pygame, dt)

            w, h = pygame.display.get_surface().get_size()
            status_bar_pos = tools.Point((0, h-self.interface_font.get_height()*1.5))
            pygame.draw.rect(self.screen, self.ui_config['status_bar_background'], pygame.Rect(status_bar_pos[0], status_bar_pos[1], w, self.interface_font.get_height()*1.5))
            pygame.draw.rect(self.screen, self.ui_config['tab_bar_background'], pygame.Rect(0, 0, w, self.interface_font.get_height()*1.5))
            tools.write_to_screen(self.screen, self.interface_font_bold, self.open_tabs[self.current_tab].status_text, status_bar_pos + tools.Point((self.interface_font.get_height()/4, self.interface_font.get_height()/4)), (True, self.ui_config['status_bar_foreground']))
            tools.write_to_screen(self.screen, self.interface_font, '[' + self.open_tabs[self.current_tab].tab_name + ']', status_bar_pos + tools.Point((self.interface_font.get_height()/4 + w/4*3, self.interface_font.get_height()/4)), (True, self.ui_config['status_bar_foreground']))

            if self.tab_palette != None:
                pygame.draw.rect(self.screen, self.ui_config['status_bar_foreground'], pygame.Rect(status_bar_pos[0], status_bar_pos[1], w, self.interface_font.get_height()*1.5))
                tools.write_to_screen(self.screen, self.interface_font_bold, 'Create tab', status_bar_pos + tools.Point((self.interface_font.get_height()/4, self.interface_font.get_height()/4)), (True, self.ui_config['status_bar_background']))
                tw, th = self.interface_font_bold.size('Create tab ')
                tools.write_to_screen(self.screen, self.interface_font, self.tab_palette + '|', status_bar_pos + tools.Point((self.interface_font.get_height()/4 + tw, self.interface_font.get_height()/4)), (True, self.ui_config['status_bar_background']))

            i = 0
            while i < len(self.toasts):
                if time.time() - self.toasts[i][2] >= 3:
                    self.toasts.pop(i)
                else:
                    i += 1

            open_tab_number = len(self.open_tabs)
            if open_tab_number > 0:
                for i in range(open_tab_number):
                    tab_width = w/open_tab_number
                    tab_pos = tab_width*i
                    colour = self.ui_config['tab_bar_foreground']
                    if self.current_tab == i:
                        colour = self.ui_config['tab_focus_foreground']
                        pygame.draw.rect(self.screen, self.ui_config['tab_focus_background'], pygame.Rect(tab_pos, 0, tab_width, self.interface_font.get_height()*1.5))
                    self.tab_y = self.interface_font.get_height()*1.5
                    tools.write_to_screen(self.screen, self.interface_font, self.open_tabs[i].title, tools.Point((self.interface_font.get_height()/4 + tab_pos, self.interface_font.get_height()/4)), (True, colour))

                self.tab_surface = pygame.transform.scale(self.tab_surface, (w, h-self.interface_font.get_height()*3))

                self.open_tabs[self.current_tab].draw(self, pygame)
                self.screen.blit(self.tab_surface, (0, self.tab_y))
                self.tab_surface.fill(self.ui_config['application_background'])

            for i in range(len(self.toasts)):
                inv_i = len(self.toasts) - i - 1
                tw, th = self.interface_font.size(self.toasts[i][0])
                if time.time() - self.toasts[i][2] < 2.5 :
                    offset = 0
                else:
                    offset = ((time.time() - self.toasts[i][2] - 2.5)*2)**2
                pos = tools.Point((0-offset*(tw+15), h-self.interface_font.get_height()*(1+inv_i)))
                pygame.draw.rect(self.screen, self.ui_config['toasts']['base_background'], pygame.Rect(pos[0], pos[1], tw + 15, self.interface_font.get_height()))
                pygame.draw.rect(self.screen, self.ui_config['toasts'][self.toasts[i][1]][0], pygame.Rect(pos[0], pos[1], 5, self.interface_font.get_height()))
                tools.write_to_screen(self.screen, self.interface_font, self.toasts[i][0], pos + tools.Point((10, 0)), (True, self.ui_config['toasts'][self.toasts[i][1]][1]))
            
            pygame.display.flip()

if __name__ == '__main__':
    app = App()
    app.mainloop()