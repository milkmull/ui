from ..base.position import Position
from .scroll_bar import Scroll_Bar
from ..utils.container import Container

class ObjectFitError(Exception):
    def __init__(self, object_size, rect_size):
        super().__init__(f'Could not fit object of size {object_size} to rect of size {rect_size}')

class Window_Base:
    def __init__(
        self,
        
        inf_width=False,
        inf_height=True,
        
        left_scroll=False,
        top_scroll=False,

        scroll_bar_kwargs={},
        **kwargs
    ):
    
        self.last_offset = (0, 0)
        self.bounding_box = Position(pos=self.pos, size=self.size)
        self.add_child(self.bounding_box, left_anchor='left', top_anchor='top')

        self.inf_width = inf_width
        self.inf_height = inf_height
        
        self.x_scroll_bar = None
        self.y_scroll_bar = None
        
        if inf_width:
            self.x_scroll_bar = Scroll_Bar(size=(1, 0), dir=0, scroll_parent=self, **scroll_bar_kwargs)
            self.x_scroll_bar.set_size(self.rect.width)
            if not top_scroll:
                self.add_child(self.x_scroll_bar, top_anchor='bottom', centerx_anchor='centerx')
            else:
                self.add_child(self.x_scroll_bar, bottom_anchor='top', centerx_anchor='centerx')
        
        if inf_height:
            self.y_scroll_bar = Scroll_Bar(size=(0, 1), dir=1, scroll_parent=self, **scroll_bar_kwargs)
            self.y_scroll_bar.set_size(self.rect.height)
            if not left_scroll:
                self.add_child(self.y_scroll_bar, left_anchor='right', centery_anchor='centery')
            else:
                self.add_child(self.y_scroll_bar, right_anchor='left', centery_anchor='centery')
            
        self.elements = []
            
        self.orientation_cache = {
            'dir': 0, 
            'marginx': 0,
            'marginy': 0,
            'centerx_aligned': False,
            'centery_aligned': False
        }
        
    @property
    def visible_elements(self):
        return [e for e in self.elements if self.rect.colliderect(e.rect)]
        
    def compare_elements(self, elements):
        return all({e0 == e1 for e0, e1 in zip(self.elements, elements)})
        
    def sort_elements(self, key):
        elements = sorted(self.elements, key=key)
        self.join_elements(elements, use_last=True)
        
    def swap_elements(self, elements):
        for i in range(min({len(elements), len(self.elements)})):
            e0 = self.elements[i]
            e1 = elements[i]
            e1.copy_position(e0)
            self.elements[i] = e1
        self.redraw()
    
    def clear(self):
        if self.elements:
            self.join_elements([], use_last=True)

    def bind(self, element):
        element.turn_off()
        element.set_parent(self.bounding_box, current_offset=True)
        
    def add_element(self, element):
        self.join_elements(self.elements + [element], use_last=True)
        
    def join_elements(
        self,
        elements, 
        
        dir=1,
        marginx=0,
        marginy=0,
        margin=None,
        centerx_aligned=False,
        centery_aligned=False,
        
        use_last=False,

    ):
  
        if use_last:
            dir = self.orientation_cache['dir']
            marginx = self.orientation_cache['marginx']
            marginy = self.orientation_cache['marginy']
            centerx_aligned = self.orientation_cache['centerx_aligned']
            centery_aligned = self.orientation_cache['centery_aligned']
            
        elif margin is not None:
            marginx = marginy = margin

        x = marginx
        y = marginy
        
        max_width, max_height = self.rect.size
        
        block = Container()
        current_line = Container()
        
        for e in elements:
        
            if not dir:
            
                if not self.inf_height and y + e.rect.height + marginy > max_height:
                    raise ObjectFitError(e.rect.size, self.size)
                
                if not self.inf_width:
                    if x + e.rect.width + marginx > max_width:
                        if not current_line:
                            raise ObjectFitError(e.rect.size, self.size)
                        
                        x = marginx
                        y += current_line.rect.height + marginy
                        
                        if not self.inf_height:
                            if y + e.rect.height + marginy > max_height:
                                raise ObjectFitError(e.rect.size, self.size)
                            if x + e.rect.width + marginx > max_width:
                                raise ObjectFitError(e.rect.size, self.size)
                                
                        block.add(current_line)
                        current_line = Container()
        
            else:
                
                if not self.inf_width and x + e.rect.width + marginx > max_width:
                    raise ObjectFitError(e.rect.size, self.size)
                
                if not self.inf_height:
                    if y + e.rect.height + marginy > max_height:
                        if not current_line:
                            raise ObjectFitError(e.rect.size, self.size)
                        
                        x += current_line.rect.width + marginx
                        y = marginy
                        
                        if not self.inf_width:
                            if y + e.rect.height + marginy > max_height:
                                raise ObjectFitError(e.rect.size, self.size)
                            if x + e.rect.width + marginx > max_width:
                                raise ObjectFitError(e.rect.size, self.size)
                                
                        block.add(current_line)
                        current_line = Container()

            e.rect.topleft = (x, y)
            current_line.add(e)

            if not dir:
                x += e.rect.width + marginx
            else:
                y += e.rect.height + marginy
                
        if current_line:
            block.add(current_line)
        block._rect = block.rect.inflate(2 * marginx, 2 * marginy)
   
        if centerx_aligned and not self.inf_width:
            for line in (block.swap() if dir else block):
                dx = (self.rect.width - (line.rect.width + (2 * marginx))) // 2
                line.move(dx, 0)
 
        if centery_aligned and not self.inf_height:
            for line in (block if dir else block.swap()):
                dy = (self.rect.height - (line.rect.height + (2 * marginy))) // 2
                line.move(0, dy)

        block.pos = self.rect.topleft
        self.bounding_box.rect = self.rect.copy()
        self.bounding_box.clear_children()
        for e in elements:
            self.bind(e)

        self.elements = elements.copy()
        self.set_total_size(self.rect.union(block.rect).size)
        
        self.orientation_cache = {
            'dir': dir, 
            'marginx': marginx,
            'marginy': marginy,
            'centerx_aligned': centerx_aligned,
            'centery_aligned': centery_aligned
        }
        
    def join_elements_custom(
        self, 
        elements,
        offsets
    ):
        self.bounding_box.rect = self.rect.copy()
        self.bounding_box.clear_children()
        for e, (x, y) in zip(elements, offsets):
            e.rect.topleft = (self.rect.x + x, self.rect.y + y)
            self.bind(e)
            
        self.elements = elements.copy()
        self.set_total_size(self.rect.unionall([e.rect for e in elements]).size)

    def set_total_size(self, size):
        rx = 0
        ry = 0
        
        if self.inf_width:
            self.x_scroll_bar.set_size_ratio(self.rect.width / size[0])
            self.x_scroll_bar.update_full()
            rx = self.x_scroll_bar.scroll_ratio
        if self.inf_height:
            self.y_scroll_bar.set_size_ratio(self.rect.height / size[1])
            self.y_scroll_bar.update_full()
            ry = self.y_scroll_bar.scroll_ratio
            
        self.bounding_box.rect.size = size
        self.set_window(rx, ry)

    def set_window(self, rx, ry):
        self.bounding_box.rect.topleft = (
            self.rect.left - (self.bounding_box.rect.width * rx),
            self.rect.top - (self.bounding_box.rect.height * ry)
        )
        self.last_offset = (rx, ry)
        self.bounding_box.set_stuck(True)
        
    def update_window(self):
        rx = 0
        ry = 0
        
        if self.inf_width:
            rx = self.x_scroll_bar.scroll_ratio
        if self.inf_height:
            ry = self.y_scroll_bar.scroll_ratio
        if self.last_offset != (rx, ry):
            self.set_window(rx, ry)

    def update(self):
        super().update()
        self.update_window()

        
    