import random


class Status:
    """A temporary modifier on a combatant with duration, magnitude, and triggers."""

    def __init__(self, definition):
        self.name = definition["name"]
        self.duration = definition["duration"]
        self.modifiers = dict(definition["modifiers"])
        self.caps = dict(definition.get("caps", {}))
        self.triggers = set(definition.get("triggers", ()))


STATUSES = {
    "prowl": {
        "name": "Prowl",
        "duration": 2,
        "modifiers": {"agility": 0.5},
        "caps": {"agility": 1.5},
        "triggers": ("was_attacked",),
    },
    "riled": {
        "name": "Riled",
        "duration": 2,
        "modifiers": {"outgoing_mult": 1.5},
        "caps": {"outgoing_mult": 2.0},
        "triggers": ("dealt_hit",),
    },
    "intimidated": {
        "name": "Intimidated",
        "duration": 2,
        "modifiers": {"incoming_mult": 1.5},
        "caps": {"incoming_mult": 2.0},
        "triggers": ("took_hit",),
    },
    "puffed": {
        "name": "Puffed",
        "duration": 1,
        "modifiers": {"incoming_mult": 0.5},
        "caps": {"incoming_mult": 0.5},
        "triggers": ("took_hit",),
    },
    "night_vision": {
        "name": "Night Vision",
        "duration": 3,
        "modifiers": {},
        "caps": {},
        "triggers": ("round_end",),
    },
}


def apply_status(statuses, key):
    """Apply a status to a combatant, refreshing duration and capping magnitude."""
    definition = STATUSES[key]
    existing = statuses.get(key)
    if existing is None:
        statuses[key] = Status(definition)
        return
    existing.duration = max(existing.duration, definition["duration"])
    for stat, value in definition["modifiers"].items():
        cap = definition["caps"].get(stat)
        if stat.endswith("_mult"):
            combined = existing.modifiers[stat] * value
            if cap is not None:
                combined = max(combined, cap) if value < 1.0 else min(combined, cap)
        else:
            combined = existing.modifiers[stat] + value
            if cap is not None:
                combined = min(combined, cap)
        existing.modifiers[stat] = combined


def effective_agility(base, statuses):
    """Return a combatant's base agility plus agility granted by active statuses."""
    return base + sum(s.modifiers.get("agility", 0.0) for s in statuses.values())


def damage_multipliers(statuses):
    """Return the (outgoing, incoming) damage multipliers for a combatant."""
    outgoing = 1.0
    incoming = 1.0
    for status in statuses.values():
        outgoing *= status.modifiers.get("outgoing_mult", 1.0)
        incoming *= status.modifiers.get("incoming_mult", 1.0)
    return outgoing, incoming


def tick_statuses(statuses, trigger):
    """Decrement statuses triggered by an event; remove them when they expire."""
    for key in [k for k, s in statuses.items() if trigger in s.triggers]:
        statuses[key].duration -= 1
        if statuses[key].duration <= 0:
            del statuses[key]


ENEMY_MOVES = {
    "fly": [
        {"name": "Buzz", "damage": (5, 8), "weight": 55},
        {"name": "Sting", "damage": (11, 15), "weight": 25, "heavy": True},
        {"name": "Hover", "weight": 10, "status": "prowl", "target": "self", "message": "its agility is up"},
        {"name": "Irritate", "weight": 10, "status": "intimidated", "target": "player", "message": "Luna is intimidated"},
    ],
}


class Enemy:
    """A single enemy with stats, a move pool, and a chosen intent."""

    def __init__(self, name, hp, agility, moves):
        """Create an enemy with name, hit points, agility, and a move pool."""
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.agility = agility
        self.statuses = {}
        self.moves = moves
        self.intent = None

    def choose_intent(self):
        """Weighted-random pick of the enemy's next move."""
        self.intent = random.choices(self.moves, weights=[m["weight"] for m in self.moves])[0]


class Battle:
    """Pure battle logic, no pygame dependency."""

    ATTACK_COST = 3
    ATTACK_DAMAGE = (13, 16)
    REST_GAIN = 12
    MAX_FOCUS = 30
    DODGE_BASE = 0.05
    DODGE_PER_AGILITY = 0.01
    INSTINCTS = {
        "night_vision": {"name": "Night Vision", "cost": 2},
        "prowl": {"name": "Prowl", "cost": 3},
        "yowl": {"name": "Yowl", "cost": 4},
        "nine_lives": {"name": "Nine Lives", "cost": 5},
    }

    def __init__(self):
        """Start a new battle against the Fly."""
        self.player_hp = 100
        self.player_hp_max = 100
        self.focus = 16
        self.agility = 3
        self.enemy = Enemy("Fly", 80, 5, ENEMY_MOVES["fly"])
        self.enemy.choose_intent()
        self.over = False
        self.won = False
        self.phase = "player"
        self.message = "A wild Fly appears!"
        self._queued_attack = False
        self.luna_attacked = False
        self.nine_lives = False
        self.statuses = {}

    @staticmethod
    def dodge_chance(agility):
        """Return the dodge chance (0.05-0.15) for the given agility."""
        return Battle.DODGE_BASE + Battle.DODGE_PER_AGILITY * agility

    def _say(self, text):
        """Append a sentence to the current battle narration."""
        if self.message:
            self.message += f" {text}"
        else:
            self.message = text

    def can_attack(self):
        """Return True if Luna has enough focus to attack."""
        return self.focus >= self.ATTACK_COST

    def attack(self):
        """Start the round with Luna's attack; the faster combatant acts first."""
        if not self.can_attack():
            self.message = "Not enough focus to attack!"
            return None

        self.luna_attacked = False
        self.message = ""
        if self._player_acts_first():
            damage = self._luna_attack()
            if not self.over:
                self.phase = "enemy"
            return damage

        self._queued_attack = True
        self._say(f"The {self.enemy.name} moves faster and strikes first!")
        self.phase = "enemy"
        return None

    def rest(self):
        """Skip the turn to regain focus, then give the turn to the enemy."""
        self.luna_attacked = False
        gained = min(self.REST_GAIN, self.MAX_FOCUS - self.focus)
        self.focus += gained
        self.message = f"You rest and regain {gained} focus."
        self.phase = "enemy"

    def can_use_instinct(self, name):
        """Return True if Luna has enough focus for the named instinct."""
        return self.focus >= self.INSTINCTS[name]["cost"]

    def use_instinct(self, name):
        """Use a named instinct; give the turn to the enemy if it resolves."""
        if not self.can_use_instinct(name):
            self.message = f"Not enough focus for {self.INSTINCTS[name]['name']}!"
            return None

        self.luna_attacked = False
        self.message = ""
        self.focus -= self.INSTINCTS[name]["cost"]
        getattr(self, f"_instinct_{name}")()
        self.phase = "enemy"
        return self.INSTINCTS[name]["cost"]

    def _instinct_night_vision(self):
        """Reveal the enemy's intent for three rounds."""
        apply_status(self.statuses, "night_vision")
        self._say("Luna's eyes sharpen, reading the enemy's intent!")

    def _instinct_prowl(self):
        """Raise Luna's agility for two attacks, improving dodge and turn order."""
        apply_status(self.statuses, "prowl")
        self._say("Luna prowls; her agility is up!")

    def _instinct_yowl(self):
        """Intimidate the enemy so it takes 1.5x damage for two hits."""
        apply_status(self.enemy.statuses, "intimidated")
        self._say("Luna yowls, intimidating the Fly!")

    def _instinct_nine_lives(self):
        """Grant Luna a one-time save from death this battle."""
        self.nine_lives = True
        self._say("Luna steels herself with her Nine Lives!")

    def defend(self):
        """Puff up to halve the next incoming hit, then give the turn to the enemy."""
        self.luna_attacked = False
        apply_status(self.statuses, "puffed")
        self.message = "Luna puffs up, halving the next attack!"
        self.phase = "enemy"

    def enemy_turn(self):
        """Enemy executes its intent; Luna's queued attack resolves after."""
        self._execute_intent()
        if self.over:
            return
        if self._queued_attack:
            self._queued_attack = False
            self._luna_attack()
        if not self.over:
            self.phase = "player"
            tick_statuses(self.statuses, "round_end")
            tick_statuses(self.enemy.statuses, "round_end")
            self.enemy.choose_intent()

    def _execute_intent(self):
        """Carry out the enemy's chosen move for the round."""
        move = self.enemy.intent
        if "status" in move:
            target = self.statuses if move["target"] == "player" else self.enemy.statuses
            apply_status(target, move["status"])
            detail = move.get("message", "")
            self._say(f"The {self.enemy.name} uses {move['name']}! {detail}".strip())
        else:
            self._enemy_attack(move)

    def _player_acts_first(self):
        """Decide who acts first: higher agility wins, ties are random."""
        luna = effective_agility(self.agility, self.statuses)
        enemy = effective_agility(self.enemy.agility, self.enemy.statuses)
        if luna > enemy:
            return True
        if enemy > luna:
            return False
        return random.choice([True, False])

    def _luna_attack(self):
        """Resolve Luna's attack: spend focus, then damage unless dodged."""
        self.focus -= self.ATTACK_COST
        self.luna_attacked = True
        if random.random() < self.dodge_chance(effective_agility(self.enemy.agility, self.enemy.statuses)):
            self._say(f"The {self.enemy.name} dodges Luna's attack!")
            tick_statuses(self.enemy.statuses, "was_attacked")
            return 0
        damage = random.randint(*self.ATTACK_DAMAGE)
        outgoing = damage_multipliers(self.statuses)[0]
        incoming = damage_multipliers(self.enemy.statuses)[1]
        damage = int(damage * outgoing * incoming)
        self.enemy.hp = max(0, self.enemy.hp - damage)
        self._say(f"Luna attacks the {self.enemy.name} for {damage} damage!")
        tick_statuses(self.statuses, "dealt_hit")
        tick_statuses(self.enemy.statuses, "took_hit")
        tick_statuses(self.enemy.statuses, "was_attacked")
        if self.enemy.hp == 0:
            self.over = True
            self.won = True
        return damage

    def _enemy_attack(self, move):
        """Resolve the enemy's damage move, unless Luna dodges or Nine Lives saves her."""
        if random.random() < self.dodge_chance(effective_agility(self.agility, self.statuses)):
            self._say(f"Luna dodges the {self.enemy.name}'s attack!")
            tick_statuses(self.statuses, "was_attacked")
            return
        outgoing = damage_multipliers(self.enemy.statuses)[0]
        incoming = damage_multipliers(self.statuses)[1]
        damage = int(random.randint(*move["damage"]) * outgoing * incoming)
        if self.player_hp - damage <= 0 and self.nine_lives:
            self.nine_lives = False
            self.player_hp = 1
            self._say("Nine Lives saves Luna from certain death!")
        else:
            self.player_hp = max(0, self.player_hp - damage)
            self._say(f"The {self.enemy.name}'s {move['name']} hits you for {damage} damage!")
            if self.player_hp == 0:
                self.over = True
                self.won = False
        tick_statuses(self.statuses, "was_attacked")
        tick_statuses(self.statuses, "took_hit")