## About the project

User-Interface library designed to be used with pygame

### Built with
* [pygame](https://www.pygame.org)

## Getting started

### Prerequisites
* python3
* pygame
```python3 -m pip install -U pygame```
* pyperclip
```python3 -m pip install -U pyperclip```

### Installation
1. Clone the repo
``git clone https://github.com/milkmull/ui.git``
2. Install dependencies

### Basic Usage
* To get started, import the ui module and call the init method where the 'size' key word represents the size of the screen in pixels.
* Menu objects dictate a scene
* A menu takes a function as an argument. That function must take the menu as its first argument and must return a list of elements which will be present in your menu.
```python
from ui import ui
from ui.menu.menu import Menu

ui.init(size=(1024, 576))

def get_elements(menu):
    return []
        
m = Menu(get_elements)
m.run()
```

