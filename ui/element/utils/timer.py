
class Timer:
    def __init__(
        self,
        start_time=0,
        stop_time=None,
        time_step=1
    ):
        self.start_time = start_time
        self.stop_time = stop_time
        self.time_step = time_step
        self.time = start_time
        
    def step(self, step=None):
        if step is None:
            step = self.time_step
        self.time += step
        if self.stop_time is not None:
            if self.time >= self.stop_time:
                self.reset()
                return True
        
    def set(self, time):
        self.time = time
        
    def reset(self):
        self.time = self.start_time