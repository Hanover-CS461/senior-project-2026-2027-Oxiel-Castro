---
---

# Luna: A Turn-Based Cat RPG at Hanover College

**Working/story title:** *Luna — a Hanover College Mystery* (a cat searching campus for her missing human)
**Genre:** Turn-based battle game (Slay-the-Spire-style run structure, JRPG-style menu combat)
**Platform:** Desktop app (Python + Pygame)

---

## 1. Project Description

*Luna* is a turn-based battle game in which the player controls Luna, a black shorthair cat with a thief's look — curious and quick on her feet. Her human has gone missing somewhere on **Hanover College's campus**, and each run Luna searches a clickable map of campus buildings for clues and fights the creatures standing in her way. The human's location is **seeded randomly each run**, giving the game replayability while keeping demos reproducible on demand.

**Main features:**

- **JRPG-style menu combat** — Attack, Items, Defend, Instincts, and Steal, with turn order and dodge both driven by a single Agility stat.
- **"Act, or refuel?" economy** — a limited Focus resource spent on strong actions; a Rest action (skip the turn to recharge) is the core risk/reward knob.
- **Cat-flavored Instincts** — special abilities such as Yowl, Night Vision, Prowl, and the once-per-run Nine Lives.
- **Status effects** — Riled, Soaked/Intimidated, and Puffed, each with explicit stacking rules and duration math.
- **Seeded, replayable runs** — clickable campus map, escalating building-by-building battles, a boss per building, and a final boss when the human is found.
- **Out-of-combat Investigation** — finding items and clues between battles (kept separate from in-combat Steal).

Sections 2–5 detail the fiction, core design idea, core systems, and run structure.

---

## 2. Fiction & Hook

Luna is a black shorthair cat with a thief's look — curious and quick on her feet. Her human has gone missing somewhere on **Hanover College's campus**. Each run, Luna searches the campus (a clickable map of buildings) for clues and fights the creatures standing in her way. The human's location is **seeded randomly each run**, which gives the game replayability and lets us reproduce a good demo on demand.

Why this works for a senior project: it's a real, named place the whole seminar recognizes, and the premise gives every mechanic a home.

---

## 3. Core Design Idea

> **"Act, or refuel?"**

Luna's resources (focus) are limited. Every turn, the player chooses between spending focus to do something strong, or burning the turn to recharge. Momentum versus survival — that tension is the game. Manage it well and you win; mismanage it and you lose.

---

## 4. Core Systems

### Luna's stats
- **Agility** — a single stat with two outputs:
  - **Turn order:** higher agility acts first (compared against enemy speed).
  - **Dodge:** a *modest* chance (15–25%) to avoid an attack. Kept low to avoid frustrating dice swings.
- **HP** — health; reaching 0 loses (or triggers Nine Lives once per run).
- **Focus** (MP) — resource spent on Instincts and strong actions; the heart of the tension.

### Battle actions (the menu)
- **Attack** — a small list of attack moves (e.g., Scratch, Pounce, Swipe) with different damage/accuracy.
- **Items** — use consumables.
- **Defend** — "Puffed up": gain block for the next turn.
- **Instincts** — cat-flavored special abilities (see below).
- **Steal** — agility-based chance to snag an enemy's item from that enemy's loot table.

### Focus & refueling
- **Rest** action: gain a large chunk of focus but **skip the turn**. Enemy pressure (they attack every turn) is what makes Rest cost HP — the balance knob.
- **Catnip** is the item-based alternative to refueling, competing with healing items for inventory.

### Status effects
- **Riled** — strength up (catnip-amped).
- **Soaked / Intimidated** — defense down.
- **Puffed** — block / damage reduction.
- Each has clear stacking rules and duration math.

### Instincts (the "magic" slot)
- **Yowl** — intimidate: enemy defense down.
- **Night Vision** — reveal enemy intent / weakness.
- **Prowl** — dodge up.
- **Nine Lives** — once per run, cheat death.

### Items
- **Wet food** — heal.
- **Catnip** — refuel / temporary Riled buff.
- **Milk** — heal + small buff.

### Out-of-combat
- **Investigate** — Luna's curiosity: find items/clues between battles. (Kept separate from Steal: Investigate = out of combat, Steal = in combat.)

---

## 5. Run Structure

1. Clickable **campus map** → choose a building.
2. Each building = a sequence of battles/clues, escalating difficulty.
3. Boss per building; final boss when the human is found.
4. Run ends when the human is found (or Luna is defeated).

**Seeded runs:** the human's location is randomized per run → replayability + reproducible demos.

---

## 6. Similar Existing Solutions

Luna sits at the intersection of several well-known games; the table below summarizes how they compare, and the prose notes what Luna borrows and what it changes.

| Solution | Combat model | Progression | What Luna takes | What Luna changes |
|---|---|---|---|---|
| Slay the Spire [1] | Turn-based card deck | Seeded roguelike runs | Run structure, seeded runs, escalating boss fights | Menu combat instead of deck-building; a real, named campus setting instead of abstract floors |
| Pokémon [2] | Turn-based menu | Linear JRPG | Menu commands, turn order, status effects, in-battle items | Roguelike runs instead of permanent progression; adds the Focus/Rest resource economy |
| Cat Quest [3] | Real-time action | Open world | Cat protagonist and RPG systems | Turn-based and roguelike instead of an action RPG |
| Stray [4] | None (adventure/puzzle) | Linear narrative | Cat protagonist, "search the world" premise | Adds combat and replayable runs |

**Slay the Spire [1]** is the direct inspiration for Luna's run structure: procedurally generated runs, escalating floors, and a boss at the end. The key difference is the combat layer — Slay the Spire builds a deck of cards each run, while Luna keeps a fixed JRPG-style menu and instead centers its variety on the Focus/Rest tension (which plays a role similar to Slay the Spire's energy economy and rest sites). Luna also swaps Slay the Spire's abstract spire for a real, recognizable campus, which gives each run a narrative goal beyond climbing.

**Pokémon [2]** is the inspiration for the menu-combat layer: moves with different damage/accuracy, turn order, status effects, and consumable items in battle. Luna differs in that progression is per-run rather than permanent — there is no growing a team across sessions. Pokémon also lacks a resource-replenishment risk like Rest; its closest analogue (per-move PP limits) constrains *which* moves you use, not *when* you refuel.

**Cat Quest [3]** shares the most with Luna on surface appeal: a cat protagonist in an RPG. But Cat Quest is a real-time action RPG in an open world, whereas Luna is turn-based with a roguelike run structure. Cat Quest demonstrates that the cat-fantasy angle is proven, without competing directly with Luna's mechanics.

**Stray [4]** proves the premise — a lone cat navigating a world on its own — resonates with players, and is the closest match in tone. Mechanically it is the furthest from Luna: a 3D adventure/puzzle platformer with no combat at all. Luna keeps the "cat with a mission" fantasy but replaces exploration-and-puzzle play with turn-based battle.

On the development side, the Pygame documentation [5] and Pygame tutorial content [6] were used to inform the technical approach below, and a framework comparison between Godot and Pygame [7] was considered when choosing the stack.

---

## 7. Technical Approach (proposed stack)

**Python + Pygame [5]**, with battle logic written as a **pure state machine** (Pygame handles only input and drawing, not game logic).

Rationale:
- A turn-based game *is* a state machine: menu → submenu → resolve → next turn.
- Python is already familiar territory, so the plan skips the multi-week stack-learning phase entirely.
- Game logic stays pure and testable (plain Python classes/functions, no framework).
- A turn-based game never stresses Pygame's limits — 2D drawing, menus, and click handling are exactly its comfort zone [5].
- Deliverable runs with a single command (`python main.py`) — easy to demo and easy to explain.
- The main alternative, Godot, was considered and set aside: its built-in scene/UI tools would help, but the learning curve and the switch away from Python outweigh the benefit for a turn-based game [7].

---

## 8. Semester Plan (~10 weeks)

**Build order principle: combat fun first, then systems, then map, then polish — so a playable demo always exists.**

- **Weeks 1–2:** Scaffold the Pygame project (window, draw loop, input handling). Then build **one battle** — Attack, one enemy, one damage formula, focus + Rest. *If this isn't fun, everything changes here.*
- **Weeks 3–5:** Full combat system — all statuses, instincts, enemy AI with intent telegraphing, turn order + agility + dodge.
- **Weeks 6–7:** Items + inventory UI + the focus/item/heal economy balance.
- **Weeks 8–9:** Clickable campus map + run structure + seeded human location, then enemies per building + first boss.
- **Week 10:** Playtesting, balance, bug fixes, demo video, presentation prep.

### Cut list (cut first if time runs out)
Save/serialization · full art pass (flat geometric cats only if time) · Steal · Nine Lives · bosses beyond the first · walkable movement · sound

---

## 9. Open Questions / Next Decisions
- Exact status effect numbers and formulas (balance pass).
- Which enemies live in which buildings.
- Whether Steal stays a must-have or moves to the stretch list.

---

## References

[1] MegaCrit, *Slay the Spire*. Seattle, WA, USA: MegaCrit, 2019. [Online]. Available: https://store.steampowered.com/app/646570/Slay_the_Spire/ [Accessed Sep. 1, 2026].

[2] Game Freak, *Pokémon*. Kyoto, Japan: Nintendo, 1996. [Online]. Available: https://www.pokemon.com/ [Accessed Sep. 1, 2026].

[3] The Gentlebros, *Cat Quest*. Auckland, New Zealand: The Gentlebros, 2017. [Online]. Available: https://store.steampowered.com/app/593280/Cat_Quest/ [Accessed Sep. 1, 2026].

[4] BlueTwelve Studio, *Stray*. Montpellier, France: Annapurna Interactive, 2022. [Online]. Available: https://store.steampowered.com/app/1332010/Stray/ [Accessed Sep. 1, 2026].

[5] Pygame developers, "Pygame Front Page — pygame v2.6.0 documentation," pygame.org, 2023. [Online]. Available: https://www.pygame.org/docs/ [Accessed Sep. 1, 2026].

[6] DaFluffyPotato, "Pygame tutorials," YouTube. [Online]. Available: https://www.youtube.com/@DaFluffyPotato [Accessed Sep. 1, 2026].

[7] "Godot vs Pygame: Which Game Development Framework Is Better," YouTube. [Online]. Available: https://www.youtube.com/watch?v=HxifSbwH4T0 [Accessed Sep. 1, 2026].
