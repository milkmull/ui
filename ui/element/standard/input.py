import pygame as pg

import pyperclip

from ...math.line import distance

from ..utils.timer import Timer
from ..base.text import Text
from ..base.text_element import Text_Element

class Input(Text_Element):
    VALID_CHARS = set(range(32, 127)) | {9, 10}

    BLINK_TIMER_MAX = 20
    
    default_kwargs = {
        'size': (200, 20),
        'pad': 2,
        'inf_width': True,
        'fill_color': (255, 255, 255),
        'text_color': (0, 0, 0),
        'cursor': pg.SYSTEM_CURSOR_IBEAM
    }

    @classmethod
    def copy(cls, text):
        pyperclip.copy(text.strip())
    
    @classmethod
    def paste(cls): 
        return pyperclip.paste()
        
    @classmethod
    def num_input(cls, **kwargs):
        return cls(text_check=lambda text: f"{text.lstrip('-+')}0".isnumeric(), **kwargs)

    def __init__(
        self,
        default=None,
        
        highlight_color=(0, 100, 255),
        highlight_text_color=(0, 0, 0),
        cursor_color=(0, 0, 0),

        text_check=lambda text: True,
        max_length=None,

        **kwargs
    ):
        super().__init__(**(Input.default_kwargs | kwargs))
        
        if default is None:
            default = self.text
        self.default = default

        self.selecting = False
        self.held_key = None
        
        self.index = len(self.text)
        self.end_index = self.index
        
        self.highlight_color = highlight_color
        self.highlight_text_color = highlight_text_color
        self.cursor_color = cursor_color
        
        self.text_check = text_check
        self.max_length = max_length
        
        self.key_timer = Timer()
        self.blink_timer = Timer(
            start_time=-Input.BLINK_TIMER_MAX,
            stop_time=Input.BLINK_TIMER_MAX
        )
                
    @property
    def selected(self):
        return self.index != self.end_index
        
    @property
    def selected_characters(self):
        i = self.index
        j = self.end_index
        if i > j:
            i, j = j, i
        return self.characters[i:j]
        
    @property
    def selected_text(self):
        return ''.join([c.character for c in self.selected_characters])
        
    def open(self):
        super().open()
        self.blink_timer.reset()
        
    def close(self):
        super().close()
        self.selecting = False
        if not self.text:
            self.set_text(self.default)
                        
    def set_index(self, index):
        if index < 0:
            index = 0 
        elif index > len(self.text):
            index = len(self.text)
        self.index = index
        if not self.selecting:
            self.end_index = index
        self.blink_timer.reset()
            
    def shift_index_x(self, dir):
        if self.index == self.end_index:
            self.set_index(self.index + dir)
        elif dir == 1:
            self.set_index(max({self.index, self.end_index}))
        elif dir == -1:
            self.set_index(min({self.index, self.end_index}))
            
    def shift_index_y(self, dir):
        c = self.characters[self.index]
        p = (c.rect.x, c.rect.centery - (dir * c.size))
        self.set_index(self.get_closest_index(p))

    def get_closest_index(self, p):
        i = min(
            range(len(self.characters) - 1),
            key=lambda i: distance(self.characters[i].rect.center, p),
            default=0
        )
        r = self.characters[i].rect
        if p[0] - r.centerx >= 0:
            i += 1
        return i
        
    def set_text(self, text):
        if (
            not text 
            or 
            (self.text_check(text) and all({ord(c) in Input.VALID_CHARS for c in text}))
            and 
            (self.max_length is None or len(text) < self.max_length)
        ):
            super().set_text(text)

    def add_text(self, text):
        self.set_text(self.text[:self.index] + text + self.text[self.index:])
        self.set_index(self.index + len(text))
        
    def backspace(self):
        if self.selected:
            self.remove_selected()
        elif self.index > 0:
            self.set_text(self.text[:self.index - 1] + self.text[self.index:])
            self.set_index(self.index - 1)
        
    def delete(self):
        if self.selected:
            self.remove_selected()
        else:
            self.set_text(self.text[:self.index] + self.text[self.index + 1:])
        
    def remove_selected(self):
        i = self.index
        j = self.end_index
        if i > j:
            i, j = j, i
        self.set_text(self.text[:i] + self.text[j:])
        if self.index > self.end_index:
            self.set_index(self.end_index)
        else:
            self.end_index = self.index
        
    def cut(self):
        Input.copy(self.get_selected_text())
        self.remove_selected()
        
    def highlight_section(self, dividers):
        start = end = self.index
        while start > 0 and self.text[start - 1] not in dividers:
            start -= 1
        while end < len(self.text) and self.text[end] not in dividers:
            end += 1
        self.set_index(end)
        self.end_index = start

    def left_click(self):
        super().left_click()

        if self.clicks == 1:
            if not self.is_open:
                self.open()
            self.set_index(self.get_closest_index(pg.mouse.get_pos()))
            self.selecting = True
        elif self.is_open:
            if self.clicks == 2:
                self.highlight_section(' \n')
            elif self.clicks == 3:
                self.highlight_section('\n')
                
    def events(self, events):  
        super().events(events)
        
        if events.get('mbd'):
            self.close()

        if events.get('mbu'):
            if events['mbu'].button == 1:
                self.selecting = False

        if self.is_open:

            kd = events.get(
                'kd',
                self.held_key if self.key_timer.time > 15 else None
            )
            if kd:
                
                if kd.key != getattr(self.held_key, 'key', None):
                    self.held_key = kd
                    self.key_timer.reset()

                if events['ctrl']:
                    if kd.key == pg.K_a:
                        self.highlight_section('')
                    elif kd.key == pg.K_c:
                        Input.copy(self.selected_text)
                    elif kd.key == pg.K_x:
                        self.cut()
                    elif kd.key == pg.K_v:
                        self.remove_selected()
                        self.add_text(Input.paste())
                                
                elif kd.key == pg.K_RIGHT:
                    self.shift_index_x(1)
                elif kd.key == pg.K_LEFT:
                    self.shift_index_x(-1)
                elif kd.key == pg.K_UP:
                    self.shift_index_y(1)
                elif kd.key == pg.K_DOWN:
                    self.shift_index_y(-1)
                    
                elif kd.key == pg.K_HOME:
                    self.set_index(0)
                elif kd.key == pg.K_END:
                    self.set_index(len(self.text))
            
                elif kd.key == pg.K_BACKSPACE:
                    self.backspace()
                elif kd.key == pg.K_DELETE:
                    self.delete()

                elif kd.key == pg.K_RETURN:
                    self.add_text('\n')
                elif kd.key == pg.K_TAB:
                    self.add_text('    ')

                elif kd.unicode:
                    if self.selected:
                        self.remove_selected()
                    self.add_text(kd.unicode)
                    
            ku = events.get('ku')
            if ku and self.held_key:
                self.held_key = None
                    
            if self.selecting:
                self.set_index(self.get_closest_index(pg.mouse.get_pos()))

        super().events(events)
        
    def update(self):
        super().update()
        self.key_timer.step()
        if self.is_open:
            self.blink_timer.step()
        
    def draw(self, surf):
        super().draw(surf)

        if self.is_open:
            
            surf.set_clip(self.rect)
            
            for c in self.selected_characters:
                pg.draw.rect(surf, self.highlight_color, c.rect)
                Text.render_to(surf,
                    c.rect,
                    c.character,
                    font=self.font,
                    size=c.size,
                    fgcolor=self.highlight_text_color
                )

            if self.blink_timer.time < 0:
                r = self.characters[self.index].rect
                pg.draw.line(surf, self.cursor_color, r.topleft, r.bottomleft, width=2)
            
            surf.set_clip(None)
            
            
        
        
        
        
        
        
        
        