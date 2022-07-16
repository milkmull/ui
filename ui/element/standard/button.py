import pygame as pg

from ..base.text_element import Text_Element
from ..base.image_element import Image_Element

class Button_Base:
    def __init__(
        self,
        hover_color=None,
        
        func=None,
        include_self=False,
        args=None,
        kwargs=None,
        
        **kw
    ):
        if hover_color:
            self.add_animation([{'attr': 'fill_color', 'end': hover_color}], tag='hover')
        if func:
            self.add_event(func, include_self=include_self, args=args, kwargs=kwargs)
   
class Button:

    class Text_Button(Text_Element, Button_Base):
        default_kwargs = {
            'inf_width': True,
            'inf_height': True,
            'cursor': pg.SYSTEM_CURSOR_HAND,
            'key_color': (0, 0, 0)
        }
        
        def __init__(self, **kwargs):
            Text_Element.__init__(self, **(Button.Text_Button.default_kwargs | kwargs))
            Button_Base.__init__(self, **kwargs)
    
    class Image_Button(Image_Element, Button_Base):
        default_kwargs = {
            'const_size': False,
            'cursor': pg.SYSTEM_CURSOR_HAND,
            'key_color': (0, 0, 0)
        }
        
        def __init__(self, **kwargs):
            Image_Element.__init__(self, **(Button.Image_Button.default_kwargs | kwargs))
            Button_Base.__init__(self, **kwargs)