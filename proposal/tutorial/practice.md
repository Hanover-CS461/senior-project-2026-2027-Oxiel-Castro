---
title: Practice Exercises
---

# Practice Exercises

Try these on your own. Each one builds on the code from the tutorial. A hint is hidden under each exercise — only peek when you are stuck.

## Exercise 1: Animate the fly

The project has a 7-frame fly sprite with these crop rectangles:

```python
FLY_FRAMES = [
    (7, 105, 17, 13), (39, 107, 17, 14), (71, 109, 17, 13), (105, 114, 15, 13),
    (137, 117, 16, 11), (168, 121, 17, 7), (200, 122, 17, 6),
]
```

Load it with `load_frames("fly.png", FLY_FRAMES, scale=5)` and loop it like the walk animation, but faster — wings should flap noticeably, so use an interval around **70 ms**.

<details>
<summary>Hint</summary>

Reuse the timer pattern, but track the fly's own index and timer:

```python
fly_index = 0
fly_timer = 0

now = pygame.time.get_ticks()
if now - fly_timer > 70:
    fly_timer = now
    fly_index = (fly_index + 1) % len(fly_frames)

screen.blit(fly_frames[fly_index], (400, 100))
```

</details>

## Exercise 2: Make Luna walk left and right

Add a `facing_left` variable. When the left arrow key is held, set `facing_left = True`; the right arrow sets it to `False`. Then flip the drawn frame based on the variable:

```python
keys = pygame.key.get_pressed()
if keys[pygame.K_LEFT]:
    facing_left = True
if keys[pygame.K_RIGHT]:
    facing_left = False
```

When it works, the cat should face and "walk" in the direction you press.

<details>
<summary>Hint</summary>

Flip the *current* frame, not the whole sheet:

```python
surface = frames[frame_index]
if facing_left:
    surface = pygame.transform.flip(surface, True, False)
screen.blit(surface, (60, 300))
```

If nothing happens when you press a key, double-check that `pygame.key.get_pressed()` is called inside the main loop.

</details>

## Exercise 3 (stretch): A bouncing scale effect

Make the character appear to bounce by scaling its height up and down over time with `pygame.transform.scale`. Use a counter that goes up to a maximum and then back down, or a sine curve.

This one is open-ended: there is no single right answer. A smooth, looping effect is success. Try combining it with the flip from Exercise 2.

When you finish, move on to the summary to see the full picture.

[Next: Summary and further reading](summary.md) · [Previous: Animation](animation.md)