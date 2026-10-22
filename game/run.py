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


DEFAULT_TIER = 1

# Player-selectable difficulties, mapped to the enemy tier they apply.
DIFFICULTY_TIERS = {"Easy": 1, "Medium": 2, "Hard": 3}

BUILDINGS = [
    {"name": "Lynn Hall", "sprite": "bat"},
    {"name": "Horner", "sprite": "snake"},
    {"name": "KP", "sprite": "spider_2"},
    {"name": "CC", "sprite": "fly"},
]

# Agility is held constant across difficulties so higher tiers don't also
# dodge more or steal the first turn. Enemy HP and damage carry the difficulty.
GUARD_AGILITY = 4
BOSS_AGILITY = 5
FINAL_BOSS_AGILITY = 5

# Enemy HP: one base per role, all sharing HP_PER_TIER per difficulty step,
# so guard < boss < final at every tier and the final boss is always the peak.
GUARD_HP = 50
BOSS_HP = 100
FINAL_BOSS_HP = 150
HP_PER_TIER = 35

# Per-building enemy identity, keyed by the building's sprite. Each entry
# gives the display name and base damage of a light and heavy attack, plus a
# signature status move. Damage scales with difficulty via moves_for().
ARCHETYPE_MOVES = {
    "bat": {
        "light": ("Screech", 5, 9),
        "heavy": ("Dive", 11, 16),
        "status": ("Flutter", "prowl", "self", "it flutters, agility up"),
    },
    "snake": {
        "light": ("Bite", 6, 10),
        "heavy": ("Constrict", 12, 17),
        "status": ("Venom Spit", "poisoned", "player", "Luna is poisoned"),
    },
    "spider_2": {
        "light": ("Nip", 4, 8),
        "heavy": ("Venom Bite", 10, 15),
        "status": ("Sling Web", "webbed", "player", "Luna is webbed"),
    },
    "fly": {
        "light": ("Buzz", 5, 8),
        "heavy": ("Sting", 11, 15),
        "status": ("Irritate", "intimidated", "player", "Luna is intimidated"),
    },
}


def moves_for(sprite, tier, boss=False):
    """Build an enemy's move pool from its archetype, scaling damage by tier."""
    spec = ARCHETYPE_MOVES[sprite]
    light_name, light_low, light_high = spec["light"]
    heavy_name, heavy_low, heavy_high = spec["heavy"]
    status_name, status, target, message = spec["status"]
    moves = [
        damage_move(light_name, light_low, light_high, 50, tier=tier),
        damage_move(heavy_name, heavy_low, heavy_high, 30, heavy=True, tier=tier),
        status_move(status_name, status, target, message, 20),
    ]
    if boss and status != "intimidated":
        moves.append(
            status_move("Snarl", "intimidated", "player", "Luna is intimidated", 20)
        )
    return moves


def final_boss_moves(tier):
    """Moves for the Campus Guardian, with damage scaled by difficulty tier."""
    return [
        damage_move("Rend", 10, 15, 50, tier=tier),
        damage_move("Devour", 16, 22, 25, heavy=True, tier=tier),
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

    def __init__(self, seed=None, tier=DEFAULT_TIER):
        """Start a run, seeding the human's building for reproducibility."""
        self.seed = seed if seed is not None else random.randrange(1000000)
        self.rng = random.Random(self.seed)
        self.tier = tier
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
        return Enemy(
            f"{name} Guard",
            GUARD_HP + (tier - 1) * HP_PER_TIER,
            GUARD_AGILITY,
            moves_for(sprite, tier),
            sprite,
        )

    def _boss(self, name, tier, sprite):
        return Enemy(
            f"{name} Boss",
            BOSS_HP + (tier - 1) * HP_PER_TIER,
            BOSS_AGILITY,
            moves_for(sprite, tier, boss=True),
            sprite,
        )

    def _final_boss(self, tier):
        return Enemy(
            "Campus Guardian",
            FINAL_BOSS_HP + (tier - 1) * HP_PER_TIER,
            FINAL_BOSS_AGILITY,
            final_boss_moves(tier),
            "rat",
        )

    def start_battle(self, name):
        """Create the Battle for the current stage of a building."""
        self.current_building = name
        stage = self.stage.get(name, 0)
        sprite = self.building_by_name(name)["sprite"]
        if name == self.human_building and stage >= 2:
            enemy = self._final_boss(self.tier)
        elif stage == 0:
            enemy = self._guard(name, self.tier, sprite)
        else:
            enemy = self._boss(name, self.tier, sprite)
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