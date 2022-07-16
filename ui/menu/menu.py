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
        args=None,
        kwargs=None,
        
        **kw
    ):
        
        super().__init__(**kw)
        
        self.init = init
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.return_value = None
        
    def set_elements(self):
        self.elements = self.init(self, *self.args, **self.kwargs)
        self.set_funcs()
        
    def set_funcs(self):
        for e in self.elements:
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
        return self.return_value
        
        
        
        
        
        
        
        