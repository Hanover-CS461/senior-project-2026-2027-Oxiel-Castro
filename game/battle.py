"""Pure battle logic.

The combat state machine: player and enemy stats, status effects, intent
selection, turn order, and win/loss resolution. It imports nothing from
pygame, so the rules can be unit-tested and the view can render them however
it likes.
"""

import random

from config import (
    DAMAGE_PER_TIER,
    PLAYER_MAX_FOCUS,
    PLAYER_MAX_HP,
    PLAYER_START_AGILITY,
    PLAYER_START_FOCUS,
    PLAYER_START_HP,
    START_INVENTORY,
)


class Status:
    """A temporary modifier on a combatant with duration, magnitude, and triggers."""

    def __init__(self, definition):
        self.name = definition["name"]
        self.duration = definition["duration"]
        self.modifiers = dict(definition["modifiers"])
        self.caps = dict(definition.get("caps", {}))
        self.triggers = set(definition.get("triggers", ()))
        self.dot = definition.get("dot", 0)


# Status definitions. "modifiers" change a stat while active (agility adds,
# *_mult multiplies damage), "caps" clamp how far stacking can push each stat,
# "triggers" name the events that decrement the duration, and "dot" is
# damage-over-time applied at the end of each round.
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
        "duration": 5,
        "modifiers": {},
        "caps": {},
        "triggers": ("round_end",),
    },
    "poisoned": {
        "name": "Poisoned",
        "duration": 3,
        "modifiers": {},
        "caps": {},
        "triggers": ("round_end",),
        "dot": 4,
    },
    "webbed": {
        "name": "Webbed",
        "duration": 3,
        "modifiers": {"agility": -2},
        "caps": {"agility": -2},
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
                combined = min(combined, cap) if value > 0 else max(combined, cap)
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


def damage_move(name, low, high, weight, heavy=False, tier=1):
    """Build a damage move; heavy moves are flagged so the UI can highlight them.

    Each tier above the first adds DAMAGE_PER_TIER to both the low and high
    ends of the damage range, so difficulty scales attack the same way it
    scales enemy health.
    """
    bonus = (tier - 1) * DAMAGE_PER_TIER
    move = {"name": name, "damage": (low + bonus, high + bonus), "weight": weight}
    if heavy:
        move["heavy"] = True
    return move


def status_move(name, status, target, message, weight):
    """Build a status move that buffs the user or debuffs the player."""
    return {
        "name": name,
        "weight": weight,
        "status": status,
        "target": target,
        "message": message,
    }


ENEMY_MOVES = {
    "fly": [
        damage_move("Buzz", 5, 8, 55),
        damage_move("Sting", 11, 15, 25, heavy=True),
        status_move("Hover", "prowl", "self", "its agility is up.", 10),
        status_move("Irritate", "intimidated", "player", "Luna is intimidated.", 10),
    ],
}

ITEMS = {
    "wet_food": {"name": "Wet Food", "heal": 35, "desc": "Restores 35 HP."},
    "catnip": {
        "name": "Catnip",
        "focus": 12,
        "status": "riled",
        "desc": "Restores 12 focus and makes Luna Riled: 1.5x damage for two hits.",
    },
    "milk": {
        "name": "Milk",
        "heal": 25,
        "status": "puffed",
        "desc": "Restores 25 HP and makes Luna Puffed: halves the next hit.",
    },
}

# Player attack menu. Each attack owns a distinct role: Scratch is the
# efficient baseline, Steal trades damage for a chance at an item, Claw
# Flurry spreads damage across several hits, and Pounce spends a turn
# charging for one large, undodgeable blow.
PLAYER_ATTACKS = {
    "scratch": {
        "name": "Scratch",
        "verb": "scratches",
        "cost": 2,
        "damage": (13, 16),
        "desc": "A reliable swipe for 13-16 damage.",
    },
    "steal": {
        "name": "Steal",
        "verb": "steals from",
        "cost": 3,
        "damage": (8, 11),
        "steal": True,
        "desc": "An 8-11 damage swipe with a chance to snatch an item.",
    },
    "flurry": {
        "name": "Claw Flurry",
        "verb": "slashes",
        "cost": 4,
        "damage": (5, 7),
        "hits": 3,
        "desc": "Three rapid 5-7 damage hits; each can be dodged.",
    },
    "pounce": {
        "name": "Pounce",
        "verb": "pounces on",
        "cost": 6,
        "damage": (34, 42),
        "charge": True,
        "undodgeable": True,
        "desc": "Charge for a turn, then land an undodgeable 34-42 hit.",
    },
}


class Enemy:
    """A single enemy with stats, a move pool, and a chosen intent."""

    def __init__(self, name, hp, agility, moves, sprite="fly", loot=None):
        """Create an enemy with stats, moves, a sprite key, and stealable loot."""
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.agility = agility
        self.statuses = {}
        self.moves = moves
        self.sprite = sprite
        self.loot = list(loot) if loot is not None else list(ITEMS)
        self.intent = None

    def choose_intent(self):
        """Weighted-random pick of the enemy's next move."""
        self.intent = random.choices(
            self.moves, weights=[m["weight"] for m in self.moves]
        )[0]


class Battle:
    """Pure battle logic, no pygame dependency."""

    ATTACKS = PLAYER_ATTACKS
    ATTACK_COST = PLAYER_ATTACKS["scratch"]["cost"]
    REST_GAIN = 12
    REST_HEAL = 5
    MAX_FOCUS = PLAYER_MAX_FOCUS
    DODGE_BASE = 0.05
    DODGE_PER_AGILITY = 0.01
    STEAL_BASE = 0.10
    STEAL_PER_AGILITY = 0.05
    STEAL_CAP = 0.45
    INSTINCTS = {
        "night_vision": {
            "name": "Night Vision",
            "cost": 2,
            "desc": "Reveals the enemy's chosen move for 5 rounds.",
        },
        "lick_wounds": {
            "name": "Lick Wounds",
            "cost": 3,
            "desc": "Restores 30 HP.",
        },
        "yowl": {
            "name": "Yowl",
            "cost": 4,
            "desc": "Intimidates the enemy so it takes 1.5x damage for two hits.",
        },
        "nine_lives": {
            "name": "Nine Lives",
            "cost": 5,
            "desc": "One-time save from death this battle.",
        },
    }
    LICK_HEAL = 30

    def __init__(
        self,
        player_hp=PLAYER_START_HP,
        player_hp_max=PLAYER_MAX_HP,
        focus=PLAYER_START_FOCUS,
        agility=PLAYER_START_AGILITY,
        inventory=None,
        enemy=None,
    ):
        """Start a battle, optionally with a given player state and enemy."""
        self.player_hp = player_hp
        self.player_hp_max = player_hp_max
        self.focus = focus
        self.agility = agility
        self.enemy = (
            enemy if enemy is not None else Enemy("Fly", 80, 5, ENEMY_MOVES["fly"])
        )
        self.enemy.choose_intent()
        self.over = False
        self.won = False
        self.phase = "player"
        self.message = f"A wild {self.enemy.name} appears!"
        self._queued_attack = False
        self.nine_lives = False
        self.pounce_charged = False
        self.hit_damages = []
        self.statuses = {}
        self.inventory = (
            dict(inventory) if inventory is not None else dict(START_INVENTORY)
        )

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
        """Return True if Luna has enough focus for the default attack."""
        return self.can_use_attack("scratch")

    def attack_cost(self, key):
        """Return an attack's focus cost; a charged Pounce releases for free."""
        if key == "pounce" and self.pounce_charged:
            return 0
        return self.ATTACKS[key]["cost"]

    def can_use_attack(self, key):
        """Return True if Luna has enough focus for the named attack."""
        return self.focus >= self.attack_cost(key)

    def can_use_any_attack(self):
        """Return True if Luna can afford at least one attack."""
        return any(self.can_use_attack(key) for key in self.ATTACKS)

    def steal_chance(self):
        """Return the agility-scaled chance to steal an item."""
        agility = effective_agility(self.agility, self.statuses)
        return min(self.STEAL_CAP, self.STEAL_BASE + self.STEAL_PER_AGILITY * agility)

    def charge_pounce(self):
        """Spend the turn charging Pounce; the free release comes next turn."""
        if self.pounce_charged:
            return False
        if not self.can_use_attack("pounce"):
            self.message = "Not enough focus to charge Pounce!"
            return False
        self.focus -= self.attack_cost("pounce")
        self.pounce_charged = True
        self.message = "Luna crouches low, ready to pounce!"
        self.phase = "enemy"
        return True

    def attack(self):
        """Start the round with Luna's attack; the faster combatant acts first."""
        if not self.can_attack():
            self.message = "Not enough focus to attack!"
            return None

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

    def plan_attack(self, key="scratch"):
        """Commit to an attack and return the round's ordered steps.

        The caller animates each step and applies it with resolve_step,
        choosing to do so at the moment of contact for damage. Returns None
        if the attack is unavailable: Pounce must be charged first, and every
        attack must be affordable.
        """
        if key == "pounce" and not self.pounce_charged:
            self.message = "Pounce needs a turn to charge!"
            return None
        if not self.can_use_attack(key):
            self.message = "Not enough focus to attack!"
            return None

        move = dict(self.ATTACKS[key])
        move["cost"] = self.attack_cost(key)
        self.message = ""
        if key == "pounce":
            self.pounce_charged = False

        self.phase = "enemy"
        luna = {"actor": "luna", "move": move}
        enemy = self.enemy_step()
        if self._player_acts_first():
            self._say("Luna strikes first!")
            return [luna, enemy]
        self._say(f"The {self.enemy.name} moves faster and strikes first!")
        return [enemy, luna]

    def plan_enemy_only(self):
        """Return the round's steps after a non-attack action."""
        self.phase = "enemy"
        return [self.enemy_step()]

    def enemy_step(self):
        """Describe the enemy's upcoming move for this round."""
        move = self.enemy.intent
        return {"actor": "enemy", "move": move, "damage": "damage" in move}

    def resolve_step(self, step):
        """Apply a step's effect; call at contact for damage steps."""
        if step["actor"] == "luna":
            return self._luna_attack(step.get("move"))
        self._execute_intent()
        return 0

    def finish_round(self):
        """End the round: damage over time, status ticks, and next intent."""
        if self.over:
            return
        self._apply_round_end()
        tick_statuses(self.statuses, "round_end")
        tick_statuses(self.enemy.statuses, "round_end")
        if not self.over:
            self.phase = "player"
            self.enemy.choose_intent()

    def rest(self):
        """Skip the turn to regain focus and HP, then give the turn to the enemy."""
        gained = min(self.REST_GAIN, self.MAX_FOCUS - self.focus)
        self.focus += gained
        healed = min(self.REST_HEAL, self.player_hp_max - self.player_hp)
        self.player_hp += healed
        self.message = f"You rest and regain {gained} focus and {healed} HP."
        self.phase = "enemy"

    def can_use_instinct(self, name):
        """Return True if Luna has enough focus for the named instinct."""
        return self.focus >= self.INSTINCTS[name]["cost"]

    def use_instinct(self, name):
        """Use a named instinct; give the turn to the enemy if it resolves."""
        if not self.can_use_instinct(name):
            self.message = f"Not enough focus for {self.INSTINCTS[name]['name']}!"
            return None

        self.message = ""
        self.focus -= self.INSTINCTS[name]["cost"]
        getattr(self, f"_instinct_{name}")()
        self.phase = "enemy"
        return self.INSTINCTS[name]["cost"]

    def _instinct_night_vision(self):
        """Reveal the enemy's intent for three rounds."""
        apply_status(self.statuses, "night_vision")
        self._say("Luna's eyes sharpen, reading the enemy's intent!")

    def _instinct_lick_wounds(self):
        """Lick wounds to recover HP, capped at max."""
        healed = min(self.LICK_HEAL, self.player_hp_max - self.player_hp)
        self.player_hp += healed
        self._say(f"Luna licks her wounds and recovers {healed} HP!")

    def _instinct_yowl(self):
        """Intimidate the enemy so it takes 1.5x damage for two hits."""
        apply_status(self.enemy.statuses, "intimidated")
        self._say(f"Luna yowls, intimidating the {self.enemy.name}!")

    def _instinct_nine_lives(self):
        """Grant Luna a one-time save from death this battle."""
        self.nine_lives = True
        self._say("Luna steels herself with her Nine Lives!")

    def defend(self):
        """Puff up to halve the next incoming hit, then give the turn to the enemy."""
        apply_status(self.statuses, "puffed")
        self.message = "Luna puffs up, halving the next attack!"
        self.phase = "enemy"

    def can_use_item(self, name):
        """Return True if Luna has at least one of the named item left."""
        return self.inventory.get(name, 0) > 0

    def use_item(self, name):
        """Use an item from the inventory, then give the turn to the enemy."""
        if not self.can_use_item(name):
            self.message = f"No {ITEMS[name]['name']} left!"
            return None

        item = ITEMS[name]
        self.inventory[name] -= 1
        self.message = ""

        if "heal" in item:
            healed = min(item["heal"], self.player_hp_max - self.player_hp)
            self.player_hp += healed
            self._say(f"Luna eats {item['name'].lower()} and recovers {healed} HP!")
        if "focus" in item:
            gained = min(item["focus"], self.MAX_FOCUS - self.focus)
            self.focus += gained
            self._say(f"Luna munches catnip and regains {gained} focus!")
        if "status" in item:
            apply_status(self.statuses, item["status"])
            self._say(f"Luna feels {STATUSES[item['status']]['name'].lower()}!")
        self.phase = "enemy"
        return name

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
            self._apply_round_end()
            tick_statuses(self.statuses, "round_end")
            tick_statuses(self.enemy.statuses, "round_end")
            if not self.over:
                self.enemy.choose_intent()

    def _apply_round_end(self):
        """Deal any damage-over-time (e.g. Poisoned) at the end of a round."""
        damage = sum(status.dot for status in self.statuses.values())
        if damage <= 0:
            return
        self.player_hp = max(0, self.player_hp - damage)
        self._say(f"Poison deals {damage} damage to Luna!")
        if self.player_hp == 0:
            self.over = True
            self.won = False

    def _execute_intent(self):
        """Carry out the enemy's chosen move for the round."""
        move = self.enemy.intent
        if "status" in move:
            target = (
                self.statuses if move["target"] == "player" else self.enemy.statuses
            )
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

    def _luna_attack(self, move=None):
        """Resolve an attack move: pay its cost, roll each hit, then steal.

        Multi-hit moves roll dodge per hit but tick hit statuses once per
        action, so Riled boosts the whole flurry instead of expiring early.
        """
        move = self.ATTACKS["scratch"] if move is None else move
        self.focus -= move["cost"]
        self.hit_damages = []
        total = 0
        for _ in range(move.get("hits", 1)):
            if not move.get("undodgeable") and random.random() < self.dodge_chance(
                effective_agility(self.enemy.agility, self.enemy.statuses)
            ):
                self._say(
                    f"The {self.enemy.name} dodges Luna's {move['name'].lower()}!"
                )
                continue
            damage = random.randint(*move["damage"])
            outgoing = damage_multipliers(self.statuses)[0]
            incoming = damage_multipliers(self.enemy.statuses)[1]
            damage = int(damage * outgoing * incoming)
            self.enemy.hp = max(0, self.enemy.hp - damage)
            total += damage
            self.hit_damages.append(damage)
            self._say(f"Luna {move['verb']} the {self.enemy.name} for {damage} damage!")
            if self.enemy.hp == 0:
                self.over = True
                self.won = True
                break
        if total > 0:
            tick_statuses(self.statuses, "dealt_hit")
            tick_statuses(self.enemy.statuses, "took_hit")
        tick_statuses(self.enemy.statuses, "was_attacked")
        if move.get("steal"):
            self._try_steal()
        return total

    def _try_steal(self):
        """Snatch a random carried item on a successful agility roll."""
        if not self.enemy.loot:
            return
        if random.random() >= self.steal_chance():
            self._say("Luna finds nothing worth taking.")
            return
        item = random.choice(self.enemy.loot)
        self.enemy.loot.remove(item)
        self.inventory[item] = self.inventory.get(item, 0) + 1
        self._say(f"Luna snatches a {ITEMS[item]['name']}!")

    def _enemy_attack(self, move):
        """Resolve the enemy's damage move, unless Luna dodges or Nine Lives saves her."""
        if random.random() < self.dodge_chance(
            effective_agility(self.agility, self.statuses)
        ):
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
            self._say(
                f"The {self.enemy.name}'s {move['name']} hits you for {damage} damage!"
            )
            if self.player_hp == 0:
                self.over = True
                self.won = False
        tick_statuses(self.statuses, "was_attacked")
        tick_statuses(self.statuses, "took_hit")
