
class Base_Element:
    ID = 0
    @classmethod
    def new_id(cls):
        id = cls.ID
        cls.ID += 1
        return id
        
    def __init__(
        self,
        tag='',
        layer=None,
        
        events=None,
        update=None,
        draw=None,

        **kwargs
    ):
        
        self._id = Base_Element.new_id()
        self.tag = tag
        self.layer = layer if layer is not None else 0
        
        if events:
            self.events = events
        if update:
            self.update = update
        if draw:
            self.draw = draw

        self.enabled = True
        self.refresh = True
        self.visible = True

        self.leftover_kwargs = kwargs
        
    def __hash__(self):
        return self._id
        
    @property
    def id(self):
        return self._id
        
    def dump_leftover(self):
        leftover = self.leftover_kwargs.copy()
        self.leftover_kwargs.clear()
        return leftover
        
    def set_leftover_attr(self):
        for name, value in self.leftover_kwargs.items():
            setattr(self, name, value)
            
    def set_tag(self, tag):
        self.tag = tag
        
    def get_tag(self):
        return self.tag
        
    def set_layer(self, layer):
        self.layer = layer
        
    def set_scene(self, scene):
        self.scene = scene

    def set_enabled(self, enabled):
        self.enabled = enabled
        
    def set_refresh(self, refresh):
        self.refresh = refresh
        
    def set_visible(self, visible):
        self.visible = visible
        
    def turn_off(self):
        self.refresh = False
        self.enabled = False
        self.visible = False
        
    def turn_on(self):
        self.refresh = True
        self.enabled = True
        self.visible = True
        
    def set_on_off(self, on_off):
        self.refresh = on_off
        self.enabled = on_off
        self.visible = on_off
        
    def kill(self):
        pass

    def events(self, events):
        pass

    def update(self):
        pass
        
    def draw(self, surf):
        pass

