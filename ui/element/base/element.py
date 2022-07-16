import pygame as pg

from .style import Style

from ..utils.event import Event
from ..utils.animation import Animation
from ..utils.timer import Timer

class Element(Style):
    CLICK_TIMER_MAX = 8
    HOVER_TIMER_MAX = 15
    
    def __init__(
        self,
        
        clip=False,
        
        cursor=pg.SYSTEM_CURSOR_ARROW,

        listeners = None,
        animations = None,
        
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.hit = False
        self.click = None
        self.is_open = False
        self.clip = clip
        
        self.cursor = cursor

        self.listeners = listeners if listeners is not None else []
        self.animations = animations if animations is not None else []
        self.active_animations = []
        self.frozen_animation_type = None

        self.clicks = 1
        self.click_timer = Timer()
        self.hover_timer = Timer()
        
    @property
    def moving(self):
        return any({a.attr in ('x', 'y', 'pos') for a in self.active_animations})
        
    def add_event(self, func=None, args=None, kwargs=None, include_self=False, tag='update'):
        if func is None:
            return
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        if include_self:
            args.insert(0, self)
        self.listeners.append(Event(func=func, args=args, kwargs=kwargs, tag=tag))
        
    def run_events(self, type):
        for e in self.listeners:
            if e.tag == type:
                e()
                
    def peek_return(self, type):
        for e in self.listeners[::-1]:
            if e.tag == type:
                r = e.peek_return()
                if r is not None:
                    return r
                
    def get_return(self, type):
        for e in self.listeners[::-1]: 
            if e.tag == type:
                r = e.get_return()
                if r is not None:
                    return r
            
    def add_animation(self, sequence, element=None, tag='temp'):
        a = Animation(
            element if element is not None else self, 
            sequence, 
            tag=tag
        )
        if tag == 'temp':
            self.active_animations.append(a)
        else:
            self.animations.append(a)
            
    def run_animations(self, type, reverse=False):
        if type == self.frozen_animation_type:
            return
        for a in self.animations:
            if a.tag == type:
                if a not in self.active_animations:
                    self.active_animations.append(a)
                a.start(reverse=reverse)
                    
    def cancel_aimation(self, tag):
        for a in self.active_animations.copy():
            if a.tag == tag:
                self.active_animations.remove(a)
                
    def freeze_animation(self, type):
        self.frozen_animation_type = type
                
    def update_animations(self):
        for a in self.active_animations.copy():
            a.step()
            if a.finished:
                self.active_animations.remove(a)
            
    def open(self):
        self.is_open = True
        self.run_events('open')
        self.run_animations('open')
        
    def close(self):
        self.is_open = False
        self.run_events('close')
        self.run_animations('open', reverse=True)
        
    def get_hit(self):
        return self.padded_rect.collidepoint(pg.mouse.get_pos())
        
    def left_click(self):
        self.run_events('left_click')

        if self.click_timer.time < Element.CLICK_TIMER_MAX:
            self.clicks += 1
        else:
            self.clicks = 1
        self.click_timer.reset()
        
    def right_click(self):
        self.run_events('right_click')
        
    def events(self, events):
        super().events(events)
        
        self.hit = self.get_hit()
        if self.hit:
            if 'cursor_set' not in events:
                pg.mouse.set_cursor(self.cursor)
                events['cursor_set'] = True
                
            if not self.hover_timer.time:
                self.run_events('hover')
                self.run_animations('hover')
            self.hover_timer.step()

        elif self.hover_timer.time:
            self.run_events('no_hover')
            self.run_animations('hover', reverse=True)
            self.hover_timer.reset()

        mbd = events.get('mbd')
        if mbd and self.hit:
            events.pop('mbd')
            if mbd.button == 1:
                self.left_click()
            elif mbd.button == 3:
                self.right_click()
        self.click = mbd

    def update(self):
        self.update_animations()
        self.run_events('update')
        super().update()
        self.click_timer.step()
        
    def draw(self, surf):
        self.draw_rect(surf)
        if self.clip:
            clip = surf.get_clip()
            surf.set_clip(self.rect)
            super().draw(surf)
            surf.set_clip(clip)
        else:
            super().draw(surf)
        
        