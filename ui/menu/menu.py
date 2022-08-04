import pygame as pg

from .base import Base_Loop

class Menu(Base_Loop):
    @classmethod
    def build_and_run(cls, *args, **kwargs):
        m = cls(*args, **kwargs)
        return m.run()

    def __init__(
        self,
        
        init,
        init_args=None,
        init_kwargs=None,
        
        overlay=False,
        
        **kwargs
    ):
        
        super().__init__(**kwargs)
        
        self.init = init
        self.args = init_args if init_args is not None else []
        self.kwargs = init_kwargs if init_kwargs is not None else {}
        self.return_value = None
        
        self.background = None
        if overlay:
            surf = self.window.copy()
            over = pg.Surface(surf.get_size()).convert_alpha()
            over.fill((0, 0, 0, 180))
            surf.blit(over, (0, 0))
            self.background = surf

        self.elements = []
        self.elements_dict = {}
        
    @property
    def body(self):
        return self.window.get_rect()
        
    @property
    def all_elements(self):
        elements = set()
        for e in self.elements:
            elements.add(e)
            if hasattr(e, 'all_children'):
                elements |= e.all_children
        return elements
        
    def set_elements(self):
        self.elements = self.init(self, *self.args, **self.kwargs)
        self.set_funcs()
        
    def set_funcs(self):
        for e in self.all_elements:
            if e.tag == 'exit':
                e.add_event(tag='left_click', func=self.exit)
            elif e.tag == 'return':
                e.add_event(
                    tag='left_click',
                    func=lambda e=e: self.set_return(e.get_return('left_click'))
                )
            elif e.tag == 'refresh':
                e.add_event(tag='left_click', func=self.set_elements)

    def set_return(self, value):
        self.return_value = value
        
    def get_return(self):
        r = self.return_value
        self.return_value = None
        return r
        
    def quit(self):
        self.close()
        super().quit()
        
    def close(self):
        for e in self.all_elements:
            e.kill()
        
    def draw(self):
        self.window.fill(self.fill_color)
        if self.background:
            self.window.blit(self.background, (0, 0))
        for e in sorted(self.elements, key=lambda e: e.layer):
            if e.visible:
                e.draw(self.window)
        pg.display.flip()
        
    def run(self):
        self.set_elements()
        self.running = True
        while self.running:
            self.clock.tick(Base_Loop.FPS)
            self.events()
            if not self.running or self.return_value is not None:
                break
            self.update()
            self.draw()
        self.close()
        return self.return_value
        
        
        
        
        
        
        
        