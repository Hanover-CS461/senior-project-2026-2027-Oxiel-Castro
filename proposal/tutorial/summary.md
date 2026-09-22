---
title: Summary
---

# Summary and Further Reading

You have now done everything needed to use sprites in a Pygame game:

- Loaded a sprite sheet with [`pygame.image.load`](https://www.pygame.org/docs/ref/image.html#pygame.image.load) and `.convert_alpha()`
- Cropped frames with [`Surface.subsurface`](https://www.pygame.org/docs/ref/surface.html#pygame.Surface.subsurface)
- Scaled frames with [`pygame.transform.scale`](https://www.pygame.org/docs/ref/transform.html#pygame.transform.scale)
- Animated sprites by cycling frame indices on a [`pygame.time`](https://www.pygame.org/docs/ref/time.html) timer
- Flipped sprites for direction with [`pygame.transform.flip`](https://www.pygame.org/docs/ref/transform.html#pygame.transform.flip)
- Built a one-shot attack animation

In the *Luna* project, all of this lives in `game/sprites.py` (the `SpriteSheet` class and the `load_frames` function), driven by the frame rectangles in `game/config.py` and the animation timers in `game/main.py`. Now that you have worked through the same ideas, you should be able to open those files and read them straight through.

## See also

- [pygame.image.load — pygame documentation](https://www.pygame.org/docs/ref/image.html#pygame.image.load)
- [pygame.Surface.subsurface — pygame documentation](https://www.pygame.org/docs/ref/surface.html#pygame.Surface.subsurface)
- [pygame.Surface.convert_alpha — pygame documentation](https://www.pygame.org/docs/ref/surface.html#pygame.Surface.convert_alpha)
- [pygame.Surface.blit — pygame documentation](https://www.pygame.org/docs/ref/surface.html#pygame.Surface.blit)
- [pygame.transform.scale — pygame documentation](https://www.pygame.org/docs/ref/transform.html#pygame.transform.scale)
- [pygame.transform.flip — pygame documentation](https://www.pygame.org/docs/ref/transform.html#pygame.transform.flip)
- [pygame.time.get_ticks — pygame documentation](https://www.pygame.org/docs/ref/time.html#pygame.time.get_ticks)
- [pygame.time.Clock.tick — pygame documentation](https://www.pygame.org/docs/ref/time.html#pygame.time.Clock.tick)
- [pygame.display.set_mode — pygame documentation](https://www.pygame.org/docs/ref/display.html#pygame.display.set_mode)
- [Pygame front page and full documentation](https://www.pygame.org/docs/)

[Previous: Practice exercises](practice.md) · [index](index.md)