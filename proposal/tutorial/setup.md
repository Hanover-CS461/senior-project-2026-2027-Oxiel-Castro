---
title: Setup
---

# Setup — Your First Pygame Window

Before we can draw sprites, we need a running Pygame program. This part installs Pygame and builds the smallest game loop that can display anything.

## Install Pygame

Open a terminal and install the library:

```bash
pip install pygame
```

Verify that it installed:

```bash
python -c "import pygame; print(pygame.version.ver)"
```

You should see a version number printed. If you get `ModuleNotFoundError`, either the install failed or you are using a different Python than the one pip installed to.

## A window that stays open

Create a file called `main.py` in your tutorial folder and add:

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sprite Tutorial")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.flip()

pygame.quit()
```

Run it with `python main.py`. A blank window should appear and close when you click the X.

What each piece does:

- `pygame.init()` — starts Pygame's subsystems (video, audio, fonts, and so on)
- `set_mode((800, 600))` — creates the window; the tuple is *width* by *height*
- `event.get()` — hands you one event at a time, such as `QUIT` when the window is closed
- `pygame.display.flip()` — draws the frame you prepared to the actual screen

See the [pygame.display documentation](https://www.pygame.org/docs/ref/display.html#pygame.display.set_mode) for the other options `set_mode` accepts.

## A stable frame rate

The window above runs as fast as your computer allows. Games lock the speed with a clock:

```python
clock = pygame.time.Clock()

# inside the loop, at the end:
clock.tick(60)
```

[`clock.tick(60)`](https://www.pygame.org/docs/ref/time.html#pygame.time.Clock.tick) waits just enough time so the loop runs at most 60 times per second. The animation timers in the next parts rely on this steady rhythm, so keep this line at the end of your loop.

You now have a window you can draw into. Next: put a sprite sheet on it.

[Next: Sprite sheets — loading and cropping frames](spritesheet.md) · [Previous: index](index.md)