---
title: Sprites Tutorial
---

# Pygame Sprites: Loading Sprite Sheets and Animating Characters

Welcome to the tutorial for working with sprites in Pygame. This tutorial is built around the code used in the *Luna* senior project, but everything you learn here applies to any Pygame project that uses 2D sprite art.

## Who this is for

This tutorial is aimed at **undergraduate computer science students who know Python and already know Pygame** — you should be comfortable opening a window, running the main loop, and handling events. You do **not** need any prior game-programming or graphics experience, but the focus here is on sprites specifically, not the basics of Pygame.

## Learning objectives

By the end of this tutorial you will be able to:

- Explain what a sprite sheet is and how frames are stored on it
- Load a sprite sheet in Pygame and crop individual frames out of it
- Scale frames to the size your game needs
- Animate a sprite by cycling frames on a timer
- Flip a sprite to face left or right
- Trigger a one-shot animation (such as an attack) from an event

## Prerequisites

Before you start, make sure you have:

- **Pygame installed** — check with `python -c "import pygame; print(pygame.version.ver)"`
- **Sprite art to work with** — either a copy of the `game/assets` folder from this project, or any sprite sheet you want to practice with

If you are following along outside the project, create a fresh folder for the tutorial and place a copy of the sprite images you want to use inside it.

## How to use this tutorial

The tutorial is split into three parts plus a summary. Work through them in order; each one builds on the last.

1. [Sprite sheets — loading and cropping frames](spritesheet.md)
2. [Animation — moving, flipping, and attacks](animation.md)
3. [Practice exercises](practice.md)
4. [Summary and further reading](summary.md)

Start with [Sprite sheets — loading and cropping frames](spritesheet.md).