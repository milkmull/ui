from ..base.text_element import Text_Element
from ..standard.button import Button
from ..standard.image import Image
from ..window.live_window import Live_Window
from ..utils.image import get_arrow, transform

class Dropdown(Text_Element):
    default_kwargs = {
    
    }
    
    default_arrow_kwargs = {
        
    }
    
    default_button_kwargs = {
        'border_radius': 0,
        'hover_color': (100, 100, 100),
    }
    
    default_window_kwargs = {

    }   
    
    @staticmethod
    def to_dict(selection):
        return {k: None for k in selection}
        
    @staticmethod
    def find_default(selection, data=None):
        if data is None:
            data = selection
        key = list(selection)[0]
        value = data[key]
        if not value:
            return key
        return Dropdown.find_default(value)
        
    @staticmethod
    def find_all_text(data):
        all = []
        for k, v in data.items():
            all.append(k)
            if v is not None:
                all += Dropdown.find_all_text(v)
        return all

    def __init__(
        self,
        
        selection,
        selected=None,
        
        max_buttons=20,
        
        arrow_kwargs={},
        button_kwargs={},
        window_kwargs = {},
        
        **kwargs
        
    ):
    
        if not isinstance(selection, dict):
            selection = Dropdown.to_dict(selection)
        if selected is None:
            selected = Dropdown.find_default(selection)
        super().__init__(text=selected, **(Dropdown.default_kwargs | kwargs))
        if self.auto_fit:
            self.size = self.get_max_size(self.find_all_text(selection))
            self.auto_fit = False
        
        self.button_kwargs = button_kwargs
        self.window_kwargs = window_kwargs
        
        self.selection = selection
        self.max_buttons = max_buttons
        self.windows = {}
        
        if 'size' not in arrow_kwargs:
            arrow_kwargs['size'] = (self.height - 10, self.height - 10)
        down_arrow = get_arrow('v', **(Dropdown.default_arrow_kwargs | arrow_kwargs))
        self.right_arrow = transform('rotate', down_arrow, 90)
        
        self.down_button = Button.Image_Button(
            image=down_arrow,
            **(Dropdown.default_button_kwargs | button_kwargs)
        )
        self.down_button.add_event(func=self.flip, tag='left_click')
        self.add_child(self.down_button, right_anchor='right', centery_anchor='centery')
        
    @property
    def is_open(self):
        return self.windows 
        
    @is_open.setter
    def is_open(self, is_open):
        pass
        
    def set_value(self, val):
        self.set_text(val)
        if self.is_open:
            self.close()

    def flip(self):
        if self.is_open:
            self.close()
        else:
            self.open()
        
    def open(self):
        super().open()
        self.down_button.transform('flip', False, True)
        self.new_window(self.selection)
        
    def close(self):
        super().close()
        self.down_button.transform('flip', False, True)
        for w in self.windows:
            self.remove_child(w)
        self.windows.clear()
        
    def new_window(self, data, last=None, level=0):  
        found = False
        
        for w, info in self.windows.copy().items():
            if info['level'] >= level:
                self.remove_child(w)
                self.windows.pop(w)
                if info['parent']:
                    info['parent'].freeze_animation(None)
                if info['parent'] is last:
                    found = True
        
        if found:
            return
                   
        buttons = []
        w = max({self.get_max_size(data)[0], self.padded_rect.width})
        for k, v in data.items():
            b = Button.Text_Button(
                size=(w, self.rect.height),
                text=k,
                **(Dropdown.default_button_kwargs | self.button_kwargs)
            )
                
            if v is None:
                b.add_event(func=self.set_value, args=[k], tag='left_click')
            else:
                b.add_event(func=self.new_window, args=[v], kwargs={'last': b, 'level': level + 1}, tag='left_click')
                
                i = Image(image=self.right_arrow)
                i.set_enabled(False)
                i.rect.midright = b.rect.midright
                i.rect.x -= 5
                b.add_child(i, current_offset=True)
                
            buttons.append(b)
            
        h = sum([b.rect.height for b in buttons[:self.max_buttons]])
        window = Live_Window(size=(w, h), inf_height=True, **(Dropdown.default_window_kwargs | self.window_kwargs))
        
        self.windows[window] = {
            'parent': last,
            'level': level,
        }

        if last is not None:
            window.rect.topleft = last.rect.topright
            window.rect.x += 2
            last.freeze_animation('hover')
        else:
            window.rect.midtop = self.rect.midbottom
            window.rect.y += self.pad['bottom']
        self.add_child(window, current_offset=True)
        window.join_objects(buttons, centerx_aligned=True)
        
    def events(self, events):
        super().events(events)
        
        mbd = events.get('mbd')
        if mbd:
            if mbd.button == 1 or mbd.button == 3:
                if self.is_open:
                    self.close()   
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
