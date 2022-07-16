from ...math.bezier import Bezier

class Animation:
    def __init__(
        self,
        element,
        sequence,
        tag=''
    ):
    
        self.element = element
        self.sequence = sequence
        self.index = 0
        self.tag = tag
        
        self.dir = 1
        self.t = 0
        self.current_frame = 0

        self.attr = None
        self.start_value = None
        self.end_value = None
        
        self.frames = 1
        self.delay = 0
        
        self.method = 'linear'
        self.strict = False

        self.start_next()
        
    @property
    def step_size(self):
        return 1 / self.frames
        
    @property
    def equation(self):
        return getattr(Bezier, self.method)
        
    @property
    def reverse(self):
        return self.dir == -1
        
    @property
    def finished(self):
        if self.dir == -1:
            return self.index == 0 and self.current_frame <= 0
        return self.index == len(self.sequence) - 1 and self.current_frame >= self.frames + self.delay
            
    @property
    def finished_sequence(self):
        if self.dir == -1:
            return self.current_frame <= 0
        return self.current_frame >= self.frames + self.delay
        
    def start(self, reverse=False):
        f = self.finished
        self.dir = 1 if not reverse else -1
        if f and self.index == 0:
            self.start_next()
        
    def start_next(self):
        s = self.sequence[self.index]
        
        attr = s['attr']
        
        end = s['end']
        if isinstance(end, int):
            end = [end]

        if 'start' in s:
            start = s['start']
        elif 'temp_start' in s:
            start = s['temp_start']
        else:
            start = getattr(self.element, attr)
            s['temp_start'] = start
        if isinstance(start, int):
            start = [start]
        elif start is None:
            start = [0 for _ in end]

        frames = s.get('frames', 1)
        delay = s.get('delay', 0)
        method = s.get('method', 'linear')
        strict = s.get('strict', False)
        
        self.attr = attr
        self.start_value = start
        self.end_value = end
        self.frames = frames
        self.delay = delay
        self.method = method
        self.strict = strict
        
        self.current_frame = 0 if not self.reverse else frames
        
    def step(self):
        if not self.finished:
            self.current_frame += self.dir
            
            if self.current_frame > self.delay:
                self.t += (self.dir * self.step_size)
                
                cv = []
                for s, e in zip(self.start_value, self.end_value):
                    v = s + ((e - s) * self.equation(self.t))
                    if self.strict:
                        v = int(round(v))
                    cv.append(v)
                self.set_value(cv)

            if self.finished_sequence:
                self.end()
            
    def set_value(self, value):
        if len(value) == 1:
            value = value[0]
        else:
            value = tuple(value)
        setattr(self.element, self.attr, value)
            
    def end(self):
        self.set_value(self.end_value if not self.reverse else self.start_value)
        if not self.finished:
            self.t = 0 if not self.reverse else 1
            self.index += self.dir
            self.start_next()
        else:
            self.t = 1 if not self.reverse else 0
            if self.reverse:
                for s in self.sequence:
                    t = s.pop('temp_start', None)            
        