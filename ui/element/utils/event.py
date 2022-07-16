
class Event:
    def __init__(
        self,
        
        func=None,
        args=None,
        kwargs=None,
        
        tag=''
    ):
        self.func = func
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.return_value = None
        
        self.tag = tag
        
    def __call__(self):
        if self.func is not None:
            self.return_value = self.func(*self.args, **self.kwargs)
        
    def set_args(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    def set_func(self, func, args=[], kwargs={}):    
        self.func = func
        self.set_args(*args, **kwargs)

    def peek_return(self):
        return self.return_value

    def get_return(self):
        r = self.return_value
        self.return_value = None
        return r
        
    