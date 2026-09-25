---
title: Sprite Sheets
---

# Sprite Sheets — Loading and Cropping Frames

A *sprite sheet* is a single image file that contains many smaller pictures (frames) arranged in a grid. Games crop out one frame at a time and draw the frames in sequence to create animation.

The *Luna* project uses a sheet called `Luna.png`. Each frame on the sheet is located by a rectangle `(x, y, width, height)`, where `(x, y)` is the top-left corner of the frame in pixels.

## Cropping a frame with subsurface

Pygame's [`Surface.subsurface()`](https://www.pygame.org/docs/ref/surface.html#pygame.Surface.subsurface) creates a new surface from a rectangle of an existing one:

```python
import pygame

sheet = pygame.image.load("Luna.png").convert_alpha()
frame = sheet.subsurface((2, 7, 29, 22))  # x, y, width, height
```

[`pygame.image.load`](https://www.pygame.org/docs/ref/image.html#pygame.image.load) reads the image file. [`convert_alpha()`](https://www.pygame.org/docs/ref/surface.html#pygame.Surface.convert_alpha) keeps the transparent parts of the image, which sprite art almost always has — skip it and your frames will show a black box behind them.

## Wrapping it in a class

The project wraps loading in a small class so the sheet is read from disk exactly once:

```python
class SpriteSheet:
    """Loads a sprite sheet and crops frames from it."""

    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def frame(self, rect):
        return self.sheet.subsurface(rect)
```

## Cropping many frames at once

Real games store the crop rectangles as a list, one entry per frame. These are the walk frames from the project:

```python
LUNA_FRAMES = [
    (2, 7, 29, 22),
    (33, 9, 32, 20),
    (67, 11, 31, 18),
    (101, 12, 30, 19),
]
```

The function below loads the sheet, crops every rectangle in the list, and returns the frames as a list of surfaces:

```python
def load_frames(path, frame_rects, size=None, scale=None):
    sheet = SpriteSheet(path)
    frames = []
    for x, y, w, h in frame_rects:
        frame = sheet.frame((x, y, w, h))
        if size is not None:
            frame = pygame.transform.scale(frame, size)
        elif scale is not None:
            frame = pygame.transform.scale(frame, (w * scale, h * scale))
        frames.append(frame)
    return frames
```

## Scaling frames

Sprite sheets are usually drawn small (the Luna walk frames are about 30 pixels wide), so you scale them up. [`pygame.transform.scale()`](https://www.pygame.org/docs/ref/transform.html#pygame.transform.scale) resizes a surface to a new width and height. The function offers two ways:

```python
frames = load_frames("Luna.png", LUNA_FRAMES, size=(132, 96))  # exact size
frames = load_frames("Luna.png", LUNA_FRAMES, scale=5)         # 5x original
```

`size` sets an absolute size; `scale` multiplies each frame's own dimensions, which keeps proportions correct automatically.

## Putting a frame on screen

Now draw the first walk frame onto the window:

```python
import pygame

# SpriteSheet class and load_frames from above go here...
frames = load_frames("Luna.png", LUNA_FRAMES, scale=5)

screen = pygame.display.set_mode((800, 600))
screen.blit(frames[0], (60, 300))
pygame.display.flip()
```

[`Surface.blit()`](https://www.pygame.org/docs/ref/surface.html#pygame.Surface.blit) copies the frame surface onto the window at the position you give it. `screen.fill(...)` paints over the previous frame first, or you would see every frame drawn on top of each other.

You can now load and crop any frame from a sheet. Next: make the frames move.

[Next: Animation — moving, flipping, and attacks](animation.md) · [Previous: index](index.md)