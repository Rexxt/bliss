import tools
import os
from random import random
from time import time
from math import sin, pi
from tifer.tifer import FileEditor
import pygame as pg

class Tab:
    def __init__(self, app, data):
        self.title = 'Editor'
        self.tab_name = 'editor'
        self.status_text = f'{data}: L1:C1'

        self.file = data

        if self.file is not None:
            if not os.path.isfile(self.file):
                with open(self.file, 'w', encoding='utf-8') as f:
                    f.write('')
            with open(self.file, 'r', encoding='utf-8') as f:
                self.original_file = f.read()
                self.editor = FileEditor(self.original_file)
                self.visual_cursor = self.editor.cursor.copy()
        self.scroll = [0,0]
        self.visual_scroll = self.scroll.copy()
        
    def key_down(self, app, event):
        if event.key == pg.K_RIGHT:
            self.editor.move_xy(1,0)
        elif event.key == pg.K_LEFT:
            self.editor.move_xy(-1,0)
        elif event.key == pg.K_UP:
            self.editor.move_xy(0,-1)
        elif event.key == pg.K_DOWN:
            self.editor.move_xy(0,1)
        elif event.key == pg.K_BACKSPACE:
            self.editor.backspace(1)
        elif event.key == pg.K_RETURN:
            self.editor.write('\n')
        elif event.key == pg.K_TAB:
            self.editor.write('    ')
        elif event.key == pg.K_s and pg.K_LCTRL in app.keys:
            if '\n'.join([''.join(x) for x in self.editor.text]) != self.original_file:
                with open(self.file, 'w') as f:
                    print('\n'.join([''.join(x) for x in self.editor.text]))
                    f.write('\n'.join([''.join(x) for x in self.editor.text]))
                with open(self.file, 'r') as f:
                    self.original_file = f.read()
                app.post_toast('Saved file.', 'info')
            else:
                app.post_toast('Cannot save unmodified file.', 'error')
    def key_up(self, app, event): pass

    def text_input(self, app, event):
        self.editor.write(event.text)

    def update(self, app, pygame, dt):
        #print(self.visual_cursor, self.editor.cursor)
        if self.visual_cursor is not None and self.editor is not None:
            if self.visual_cursor[0] != self.editor.cursor[0]:
                self.visual_cursor[0] += (self.editor.cursor[0] - self.visual_cursor[0])*(dt*20)
                if abs(self.editor.cursor[0] - self.visual_cursor[0]) < 0.05:
                    self.visual_cursor[0] = self.editor.cursor[0]
            
            cl, cc = self.editor.cursor
            tw, th = app.editor_font.size(str(''.join(self.editor.text[cl][:cc])))
            vtw = self.visual_cursor[1]
            
            if vtw != tw:
                self.visual_cursor[1] += (tw - self.visual_cursor[1])*(dt*20)
                if abs(tw - self.visual_cursor[1]) < 0.05:
                    self.visual_cursor[1] = tw


            w, h = app.tab_surface.get_size()
            while app.editor_font.get_height()*(self.editor.cursor[0]-self.scroll[0]) < 0:
                self.scroll[0] -= 1
            while app.editor_font.get_height()*(self.editor.cursor[0]-self.scroll[0]) >= h:
                self.scroll[0] += 1

            if self.visual_scroll != self.scroll:
                self.visual_scroll[0] = (self.visual_scroll[0]+self.scroll[0])/2
                self.visual_scroll[1] = (self.visual_scroll[1]+self.scroll[1])/2
                if abs(self.scroll[0] - self.visual_scroll[0]) < 0.05:
                    self.visual_scroll[0] = self.scroll[0]
                if abs(self.scroll[1] - self.visual_scroll[1]) < 0.05:
                    self.visual_scroll[1] = self.scroll[1]
            
            mod = ''
            if '\n'.join([''.join(x) for x in self.editor.text]) != self.original_file:
                mod = '*'
            self.status_text = f'{self.file} - L{self.editor.cursor[0] + 1}:C{self.editor.cursor[1] + 1} {mod}'

    def draw(self, app, pygame: pg):
        if self.file != None:
            cl, cc = self.editor.cursor
            vcl, vcc = self.visual_cursor
            self.title = str(self.file)
            pad = app.editor_font.size('0  ') [0]
            for l in range(len(self.editor.text)+1):
                pw, ph = app.editor_font.size(str(l) + '  ')
                pad = max(pad, pw)
            spw, sph = app.editor_font_bold.size(' ')
            w, h = app.tab_surface.get_size()
            pygame.draw.rect(app.tab_surface, (app.ui_config['application_background_highlight']), pygame.Rect(0, app.editor_font.get_height()*(vcl-self.visual_scroll[0]), app.tab_surface.get_size()[0], app.editor_font.get_height()))
            for l in range(len(self.editor.text)):
                if app.editor_font.get_height()*(l-self.scroll[0]) < 0:
                    continue
                if app.editor_font.get_height()*(l-self.scroll[0]) >= h:
                    break
                if self.editor.cursor[0] == l:
                    tools.write_to_screen(app.tab_surface, app.editor_font_bold, str(l + 1), (spw/2, app.editor_font.get_height()*(l-self.visual_scroll[0])), (True, (200,)*3))
                else:
                    tools.write_to_screen(app.tab_surface, app.editor_font, str(l + 1), (0, app.editor_font.get_height()*(l-self.visual_scroll[0])), (True, (200,)*3))
                tools.write_to_screen(app.tab_surface, app.editor_font, ''.join(self.editor.text[l]), (pad, app.editor_font.get_height()*(l-self.visual_scroll[0])), (True, (255,)*3))
            tw, th = app.editor_font.size(str(''.join(self.editor.text[cl][:cc])))
            pygame.draw.line(app.tab_surface, (255,)*3, (pad+vcc-self.visual_scroll[1], app.editor_font.get_height()*(vcl-self.visual_scroll[0])), (pad+vcc-self.visual_scroll[1], app.editor_font.get_height()*(vcl+1-self.visual_scroll[0])))