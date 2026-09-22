---
title: Animation
---

# Animation — Moving, Flipping, and Attacks

Animation is just drawing one frame, waiting a few milliseconds, then drawing the next. The tricky part is timing it off a clock so every computer animates at the same speed.

## The frame counter and timer

Keep two variables: which frame is showing, and when we last changed it.

```python
frame_index = 0
timer = 0
```

Each tick of the loop, if enough time has passed, advance to the next frame and wrap around to the start:

```python
while running:
    now = pygame.time.get_ticks()        # milliseconds since the program started
    if now - timer > 150:                # change frame every 150 ms
        timer = now
        frame_index = (frame_index + 1) % len(frames)  # wrap around to 0

    screen.fill((120, 200, 120))
    screen.blit(frames[frame_index], (60, 300))
    pygame.display.flip()
```

[`pygame.time.get_ticks()`](https://www.pygame.org/docs/ref/time.html#pygame.time.get_ticks) returns the number of milliseconds since Pygame started, so `now - timer` is how long it has been since the last frame change. The expression `(frame_index + 1) % len(frames)` cycles 0 → 1 → 2 → 3 → 0 forever. At 150 ms per frame you get roughly seven frames per second — a gentle walk.

Why use a *timer* instead of advancing one frame per loop iteration? Because the loop speed depends on the machine. On a fast computer you would fly through the frames; on a slow one the walk would crawl. Timing by milliseconds keeps the speed identical everywhere.

## Flipping the sprite for direction

If the character can face left and right, flip the surface with [`pygame.transform.flip()`](https://www.pygame.org/docs/ref/transform.html#pygame.transform.flip). The two flags mean *flip horizontally* and *flip vertically*:

```python
facing_left = False
frame_surface = frames[frame_index]

if facing_left:
    frame_surface = pygame.transform.flip(frame_surface, True, False)

screen.blit(frame_surface, (60, 300))
```

Flip the *current* frame each draw, not the whole sheet. Flipping the sheet once per draw is wasteful, and you would be stuck facing one direction.

## One-shot animations (an attack)

An attack uses the same timer idea but plays a fixed number of frames once instead of looping. The project keeps a flag and a separate index:

```python
attack_anim = False
attack_index = 0
attack_timer = 0

# when the player clicks Attack:
attack_anim = True
attack_index = 0
attack_timer = pygame.time.get_ticks()
```

Then, each frame, if the animation is active, advance it and turn it off when it runs out of frames:

```python
now = pygame.time.get_ticks()
if attack_anim:
    if now - attack_timer > 80:
        attack_timer = now
        attack_index += 1
        if attack_index >= len(attack_frames):
            attack_anim = False
            attack_index = 0

if attack_anim:
    luna = attack_frames[attack_index]
else:
    luna = frames[frame_index]
```

While the attack is playing, the attack frames are drawn; once it finishes, the idle walk resumes. This is exactly the pattern used in `game/main.py` in the `_update_animations` and `handle_click` methods.

You now have everything needed to animate the game's characters. Put it to work in the exercises.

[Next: Practice exercises](practice.md) · [Previous: Sprite sheets](spritesheet.md)