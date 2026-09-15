---
marp: true
theme: gaia
paginate: true
transition: fade 0.3s
---

<!--
  This is your Marp slide deck.
  In VS Code: install "Marp for VS Code" (marp-team.marp-vscode),
  then enable the preview with the Marp icon in the toolbar.
  The front-matter above (`marp: true`) is what activates Marp.

  Slides are separated by `---`.
  Put any images in ./assets and reference them like:
  ![alt text](assets/your-image.png)
-->

# Luna: A Turn-Based Cat RPG

My senior project at Hanover

---

## The Story

<!-- Replace this with your own text -->

- Luna's human has gone missing somewhere on campus
- Each run, the human's location is seeded randomly in a building
- Turn-based JRPG-style combat with a Focus/Rest resource economy

---

## Core Gameplay

<!-- Add screenshots from ./assets here -->

- Menu combat: Attack, Items, Defend, Instincts
- Agility drives turn order and dodge
- Rest to regain focus, but skip your turn

---

## Technical Approach

- Python + Pygame, pure battle logic (state machine)
- Pygame handles input and drawing only

---

## Demo

<!-- Demo goes here -->
- Run the game

---

## Questions?

<!-- End of deck -->