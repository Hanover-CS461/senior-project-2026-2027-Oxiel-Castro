---
title: Sprites Tutorial
---

# Pygame Sprites: Loading Sprite Sheets and Animating Characters

Welcome to the tutorial for working with sprites in Pygame. This tutorial is built around the code used in the *Luna* senior project, but everything you learn here applies to any Pygame project that uses 2D sprite art.

## Who this is for

This tutorial is aimed at **undergraduate computer science students who know Python but have never used Pygame**. You should be comfortable with functions, lists, tuples, loops, and simple classes. You do **not** need any prior game-programming or graphics experience.

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

- **Python 3.8 or newer** — check with `python --version`
- **pip** available — check with `pip --version`
- **pygame** installed — `pip install pygame`
- **Sprite art to work with** — either a copy of the `game/assets` folder from this project, or any sprite sheet you want to practice with

If you are following along outside the project, create a fresh folder for the tutorial and place a copy of the sprite images you want to use inside it.

## How to use this tutorial

The tutorial is split into four parts plus a summary. Work through them in order; each one builds on the last.

1. [Setup — your first Pygame window](setup.md)
2. [Sprite sheets — loading and cropping frames](spritesheet.md)
3. [Animation — moving, flipping, and attacks](animation.md)
4. [Practice exercises](practice.md)
5. [Summary and further reading](summary.md)

Start with [Setup — your first Pygame window](setup.md).