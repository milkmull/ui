import pygame as pg

class Image:
    @staticmethod
    def get_max_aspect(images):
        mw = 0
        mh = 0
        for i in images:
            w, h = i.get_size()
            if w > mw:
                mw = w
            if h > mh:
                mh = h
        return (mw, mh)
        
    def __init__(
        self, 
        
        image=None,
        colorkey=None,
        
        const_size=True,
        auto_fit=False,
        keep_aspect=True,
        
        **kwargs
    ):

        if colorkey:
            image.set_colorkey(colorkey)
        self.original_image = image
        self.image = image.copy() if image else None
        self.colorkey = colorkey
        
        if self.size == (0, 0):
            auto_fit = True
        self.const_size = const_size
        self.auto_fit = auto_fit
        self.keep_aspect = keep_aspect

        self.fit_image()

    @property
    def image_size(self):
        if self.original_image:
            return self.original_image.get_size()
        return self.rect.size
        
    @property
    def image_rect(self):
        r = self.image.get_rect()
        r.center = self.rect.center
        return r
        
    def set_colorkey(self, colorkey=None):
        if colorkey:
            self.original_image.set_colorkey(colorkey)
            self.image.set_colorkey(colorkey)
        self.colorkey = colorkey
        
    def fill(self, color):
        self.original_image.fill(color)
        self.image.fill(color)
        
    def reset_image(self):
        self.image = self.original_image.copy()
        
    def refresh_image(self):
        self.image.blit(self.original_image, (0, 0))
        
    def set_image(self, image, overwrite=True):
        self.image = image
        if overwrite:
            self.original_image = image.copy()
            self.fit_image()
            
    def transform(self, mode, *args, **kwargs):
        self.image = getattr(pg.transform, mode)(self.image, *args, **kwargs)
            
    def get_scaled(self, size):
        return pg.transform.smoothscale(self.original_image, size)
        
    def scale(self, size):
        w, h = size
        if w < 0:
            w = 0
        if h < 0:
            h = 0
        self.set_image(self.get_scaled((w, h)), overwrite=False)
        
    def scale_by_factor(self, factor):
        if factor != 1:
            w, h = self.image_size
            self.scale((w * factor, h * factor))

    def fit_image(self):
        if self.image:
        
            if self.auto_fit:
                self.rect.size = self.image_size

            elif not self.const_size:
                if self.keep_aspect:
                    w, h = self.image_size
                    if w > h:
                        factor = self.rect.width / w
                    else:
                        factor = self.rect.height / h
                    self.scale_by_factor(factor)
                    
                else:
                    self.scale(self.size)
        
    def fit_to_image(self, width=False, height=False):
        w, h = self.image_size
        if not width:
            w = self.rect.width
        if not height:
            h = self.rect.height
        self.size = (w, h)
        
    def draw_image(self, surf):
        surf.blit(self.image, self.image_rect)
        