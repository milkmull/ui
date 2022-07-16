from ..ui import get_size

def center_elements_y(elements, marginy=0):
    y = 0
    for e in elements:
        e.midtop = (0, y)
        y += e.rect.height + marginy
        
    r = e[0].rect.uinionall({e.rect for e in elements})
    
    w, h = get_size()
    rx, ry = r.topleft
    r.center = (w // 2, h // 2)
    for e in elements:
        e.rect.move_ip(r.x - rx, r.y - ry)