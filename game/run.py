import random

from battle import Battle, Enemy, ITEMS


BUILDINGS = [
    {"name": "Lynn Hall", "tier": 0, "sprite": "bat"},
    {"name": "Horner", "tier": 1, "sprite": "snake"},
    {"name": "KP", "tier": 2, "sprite": "spider_2"},
    {"name": "CC", "tier": 3, "sprite": "fly"},
]

GUARD_MOVES = [
    {"name": "Scratch", "damage": (5, 9), "weight": 55},
    {"name": "Lunge", "damage": (10, 14), "weight": 25, "heavy": True},
    {"name": "Hover", "weight": 10, "status": "prowl", "target": "self", "message": "its agility is up"},
    {"name": "Snarl", "weight": 10, "status": "intimidated", "target": "player", "message": "Luna is intimidated"},
]

BOSS_MOVES = [
    {"name": "Claw", "damage": (8, 12), "weight": 50},
    {"name": "Maul", "damage": (15, 22), "weight": 25, "heavy": True},
    {"name": "Hover", "weight": 10, "status": "prowl", "target": "self", "message": "its agility is up"},
    {"name": "Snarl", "weight": 15, "status": "intimidated", "target": "player", "message": "Luna is intimidated"},
]

FINAL_BOSS_MOVES = [
    {"name": "Rend", "damage": (12, 18), "weight": 50},
    {"name": "Devour", "damage": (20, 28), "weight": 25, "heavy": True},
    {"name": "Hover", "weight": 10, "status": "prowl", "target": "self", "message": "its agility is up"},
    {"name": "Snarl", "weight": 15, "status": "intimidated", "target": "player", "message": "Luna is intimidated"},
]


class Run:
    """Pure run logic: seeded human location, buildings, and persistent state."""

    MAX_HP = 100
    MAX_FOCUS = 30
    START_FOCUS = 16
    START_HP = 100
    START_AGILITY = 3
    START_INVENTORY = {"wet_food": 4, "catnip": 3, "milk": 2}
    HEAL_BETWEEN = 20

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
        return Enemy("Campus Guardian", 130, 6, FINAL_BOSS_MOVES, "rat")

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
        self.focus = self.MAX_FOCUS
        self.last_reward = self.rng.choice(list(ITEMS))
        self.inventory[self.last_reward] = self.inventory.get(self.last_reward, 0) + 1