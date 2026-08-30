# Luna — a Hanover College Mystery

**Working title:** *Luna* (cat searching campus for her missing human)
**Genre:** Turn-based battle game (Slay-the-Spire-style run structure, JRPG-style menu combat)
**Platform:** Web app (browser)

---

## 1. Fiction & Hook

Luna is a black shorthair cat with a thief's look — curious and quick on her feet. Her human has gone missing somewhere on **Hanover College's campus**. Each run, Luna searches the campus (a clickable map of buildings) for clues and fights the creatures standing in her way. The human's location is **seeded randomly each run**, which gives the game replayability and lets us reproduce a good demo on demand.

Why this works for a senior project: it's a real, named place the whole seminar recognizes, and the premise gives every mechanic a home.

---

## 2. Design Thesis (the spine)

> **"Act, or refuel?"**

Luna's resources (focus) are limited. Every turn, the player chooses between spending focus to do something strong, or burning the turn to recharge. Momentum versus survival — that tension is the game. Manage it well and you win; mismanage it and you lose.

---

## 3. Core Systems

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

## 4. Run Structure

1. Clickable **campus map** → choose a building.
2. Each building = a sequence of battles/clues, escalating difficulty.
3. Boss per building; final boss when the human is found.
4. Run ends when the human is found (or Luna is defeated).

**Seeded runs:** the human's location is randomized per run → replayability + reproducible demos.

---

## 5. Technical Approach (proposed stack)

**React + TypeScript**, with battle logic written as a **pure state machine** (no game engine).

Rationale:
- A turn-based game *is* a state machine: menu → submenu → resolve → next turn.
- React renders whatever the current state is; game logic stays pure and testable.
- Reads cleanly as a "web app" for a senior project, and avoids fighting a realtime game engine (Phaser) that doesn't fit turn-based menus.

*Note: with little prior web-dev experience, the first several weeks are dedicated to learning the stack. That learning curve is expected and budgeted for below.*

---

## 6. Semester Plan (~15 weeks)

**Build order principle: combat fun first, then systems, then map, then polish — so a playable demo always exists.**

- **Weeks 1–4:** Learn React + TypeScript; scaffold the project. Then build **one battle** — Attack, one enemy, one damage formula, focus + Rest. *If this isn't fun, everything changes here.*
- **Weeks 5–7:** Full combat system — all statuses, all instincts, enemy AI with intent telegraphing, turn order + agility + dodge.
- **Weeks 8–9:** Items + inventory UI + the focus/item/heal economy balance.
- **Weeks 10–11:** Clickable campus map + run structure + seeded human location.
- **Week 12:** Enemies per building + first boss.
- **Weeks 13–14:** Save/serialization, seed polish, UI + art pass (flat geometric cats).
- **Weeks 14–15:** Playtesting, balance, bug fixes, demo video, presentation prep.

### Cut list (cut first if time runs out)
Steal · Nine Lives · bosses beyond the first · walkable movement · sound

---

## 7. Open Questions / Next Decisions
- Final stack confirmation after the learning-curve estimate.
- Exact status effect numbers and formulas (balance pass).
- Which enemies live in which buildings.
- Whether Steal stays a must-have or moves to the stretch list.
