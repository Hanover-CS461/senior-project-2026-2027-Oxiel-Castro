import random

from battle import Battle, Enemy, ITEMS, damage_move, status_move
from config import (
    PLAYER_MAX_FOCUS,
    PLAYER_MAX_HP,
    PLAYER_START_AGILITY,
    PLAYER_START_FOCUS,
    PLAYER_START_HP,
    START_INVENTORY,
)


DIFFICULTY_TIER = 1

BUILDINGS = [
    {"name": "Lynn Hall", "tier": DIFFICULTY_TIER, "sprite": "bat"},
    {"name": "Horner", "tier": DIFFICULTY_TIER, "sprite": "snake"},
    {"name": "KP", "tier": DIFFICULTY_TIER, "sprite": "spider_2"},
    {"name": "CC", "tier": DIFFICULTY_TIER, "sprite": "fly"},
]

GUARD_MOVES = [
    damage_move("Scratch", 5, 9, 55),
    damage_move("Lunge", 10, 14, 25, heavy=True),
    status_move("Hover", "prowl", "self", "its agility is up", 10),
    status_move("Snarl", "intimidated", "player", "Luna is intimidated", 10),
]

BOSS_MOVES = [
    damage_move("Claw", 8, 12, 50),
    damage_move("Maul", 15, 22, 25, heavy=True),
    status_move("Hover", "prowl", "self", "its agility is up", 10),
    status_move("Snarl", "intimidated", "player", "Luna is intimidated", 15),
]

FINAL_BOSS_MOVES = [
    damage_move("Rend", 10, 15, 50),
    damage_move("Devour", 16, 22, 25, heavy=True),
    status_move("Hover", "prowl", "self", "its agility is up", 10),
    status_move("Snarl", "intimidated", "player", "Luna is intimidated", 15),
]


class Run:
    """Pure run logic: seeded human location, buildings, and persistent state."""

    MAX_HP = PLAYER_MAX_HP
    MAX_FOCUS = PLAYER_MAX_FOCUS
    START_FOCUS = PLAYER_START_FOCUS
    START_HP = PLAYER_START_HP
    START_AGILITY = PLAYER_START_AGILITY
    START_INVENTORY = dict(START_INVENTORY)
    HEAL_BETWEEN = 10
    BETWEEN_FOCUS = 20

    def __init__(self, seed=None):
        """Start a run, seeding the human's building for reproducibility."""
        self.seed = seed if seed is not None else random.randrange(1000000)
        self.rng = random.Random(self.seed)
        self.player_hp = self.START_HP
        self.player_hp_max = self.MAX_HP
        self.focus = self.START_FOCUS
        self.agility = self.START_AGILITY
        self.inventory = dict(self.START_INVENTORY)
        self.human_building = self.rng.choice([b["name"] for b in BUILDINGS])
        self.stage = {}
        self.current_building = None
        self.found_human = False
        self.won = False
        self.lost = False
        self.last_reward = None

    def building_by_name(self, name):
        """Return the building dict for a name."""
        return next(b for b in BUILDINGS if b["name"] == name)

    def is_cleared(self, name):
        """Return True once a building has no battles left."""
        stage = self.stage.get(name, 0)
        if name == self.human_building:
            return stage >= 3
        return stage >= 2

    def available_buildings(self):
        """Return buildings that still have a fight left."""
        return [b["name"] for b in BUILDINGS if not self.is_cleared(b["name"])]

    def _guard(self, name, tier, sprite):
        return Enemy(f"{name} Guard", 55 + tier * 15, 3 + tier, GUARD_MOVES, sprite)

    def _boss(self, name, tier, sprite):
        return Enemy(f"{name} Boss", 90 + tier * 25, 4 + tier, BOSS_MOVES, sprite)

    def _final_boss(self):
        return Enemy("Campus Guardian", 110, 5, FINAL_BOSS_MOVES, "rat")

    def start_battle(self, name):
        """Create the Battle for the current stage of a building."""
        self.current_building = name
        stage = self.stage.get(name, 0)
        tier = self.building_by_name(name)["tier"]
        sprite = self.building_by_name(name)["sprite"]
        if name == self.human_building and stage >= 2:
            enemy = self._final_boss()
        elif stage == 0:
            enemy = self._guard(name, tier, sprite)
        else:
            enemy = self._boss(name, tier, sprite)
        return Battle(
            player_hp=self.player_hp,
            player_hp_max=self.player_hp_max,
            focus=self.focus,
            agility=self.agility,
            inventory=self.inventory,
            enemy=enemy,
        )

    def end_battle(self, battle):
        """Persist battle results, advance the building, and check win/loss."""
        self.player_hp = battle.player_hp
        self.focus = battle.focus
        self.inventory = battle.inventory
        if not battle.won:
            self.lost = True
            return
        name = self.current_building
        self.stage[name] = self.stage.get(name, 0) + 1
        if name == self.human_building and self.stage[name] == 2:
            self.found_human = True
        elif name == self.human_building and self.stage[name] == 3:
            self.won = True
        self.player_hp = min(self.player_hp_max, self.player_hp + self.HEAL_BETWEEN)
        self.focus = max(self.focus, self.BETWEEN_FOCUS)
        self.last_reward = self.rng.choice(list(ITEMS))
        self.inventory[self.last_reward] = self.inventory.get(self.last_reward, 0) + 1