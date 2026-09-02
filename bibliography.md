# Luna turned based RPG
  ## Languages
  - https://www.youtube.com/watch?v=HxifSbwH4T0&t=185s
    - Is a secondary educational source comparing **Godot vs Pygame** as game development frameworks.
    - It's a development resource since it helps me decide between Godot and Pygame for building Luna.
    - The video covers each framework's strengths and weaknesses — setup, learning curve, scene/UI tools, and how well each fits a 2D turn-based game.
    - The comparison helps me justify my choice of Pygame for Luna (I already know Python, and since Luna is turn-based it never stresses Pygame's limits) and understand what the Godot alternative would involve.
  ## Library
  - https://www.pygame.org/docs/
    - Is a primary educational source — the official Pygame documentation — which teaches how to use the Pygame library in Python.
    - It's a development resource since I plan on using Python and Pygame in my project.
    - The docs cover setting up a window, the game/draw loop, handling input (keyboard/mouse), and drawing shapes and text. It includes reference pages and examples to help people apply the concepts in their own games.
    - The features discussed help with building the UI, menus, and clickable map that my turn-based game needs, while keeping the game logic separate and testable.
  ## Platform
  - Desktop app (Python + Pygame), cross-platform across Windows, macOS, and Linux.
    - The game runs locally on my laptop — no browser or server required.
    - Pygame is cross-platform, so the same code runs on any OS without changes.
    - The demo targets my own machine, so no distribution or packaging is needed for the semester demo.
  ## Similar Projects
  - https://store.steampowered.com/app/646570/Slay_the_Spire/
    - Is a turn-based roguelike deck-builder by MegaCrit (2019) and the direct inspiration for Luna's run structure.
    - It's a similar existing solution since it shares Luna's core loop: seeded, procedural runs that escalate in difficulty and end in a boss fight.
    - Unlike Luna, its combat builds a deck of cards each run rather than using a fixed JRPG-style menu, and its setting is an abstract spire instead of a real campus.
    - From it Luna takes the run structure, seeded replayability, and escalating bosses, while the Focus/Rest tension plays a role similar to its energy economy and rest sites.
  - https://www.pokemon.com/
    - Is a turn-based JRPG series by Game Freak (1996–present) and the inspiration for Luna's menu-combat layer.
    - It's a similar existing solution since it uses menu commands, turn order, status effects, and consumable items in battle, just like Luna.
    - Unlike Luna, its progression is linear and permanent (building a team across sessions) rather than per-run, and it lacks a resource-replenishment risk like Rest (its per-move PP limits constrain *which* moves you use, not *when* you refuel).
    - From it Luna takes the menu-combat layer and adds the Focus/Rest resource economy on top.
  - https://store.steampowered.com/app/593280/Cat_Quest/
    - Is a cat-protagonist action RPG by The Gentlebros (2017), the closest match to Luna on surface appeal.
    - It's a similar existing solution since it's an RPG starring a cat, proving the cat-fantasy angle Luna uses.
    - Unlike Luna, it's a real-time action RPG in an open world rather than turn-based with a roguelike run structure.
    - From it Luna takes the cat protagonist and RPG systems, while staying turn-based to avoid competing with its mechanics directly.
  - https://store.steampowered.com/app/1332010/Stray/
    - Is a 3D adventure/puzzle platformer by BlueTwelve Studio (2022) starring a lone cat, and the closest match to Luna in tone.
    - It's a similar existing solution since it shares Luna's premise of a cat navigating a world on its own with a mission.
    - Unlike Luna, it has no combat at all and is a linear 3D adventure rather than a turn-based roguelike.
    - From it Luna keeps the "cat with a mission" fantasy but replaces exploration-and-puzzle play with turn-based battle and replayable runs.
  ## Pygame Tutorials
  - https://www.youtube.com/@DaFluffyPotato
    - Is a secondary educational source by DaFluffyPotato, a channel focused on teaching Pygame game development in Python.
    - It's a development resource since I plan on using Python and Pygame in my project.
    - The channel's tutorials cover building games with Pygame step by step — handling game loops, sprites, drawing, and structuring game code — with practical examples that apply directly to my project.
    - The content helps with writing clean, organized Pygame code for the menus, UI, and combat screens in my turn-based game.
  - https://www.youtube.com/watch?v=8OMghdHP-zs&t=5s
    - Is a secondary educational source by Clear Code — "Master Python by making 5 games [the new ultimate introduction to pygame]" — a long-form tutorial that builds five complete games in Python and Pygame.
    - It's a development resource since it teaches Pygame through full projects rather than isolated snippets, which matches how I plan to build Luna.
    - The video covers game loops, movement and delta time, input handling, sprites, collisions, menus, and a full battle system. The fifth game is a Pokémon-inspired turn-based battle game with menus, a battle system, and battle visuals — the closest structural match to Luna's combat screens.
    - The battle-game segment (menus + battle system, starting around 09:09:20) maps directly to my turn-based combat and shows how to organize the code behind it.