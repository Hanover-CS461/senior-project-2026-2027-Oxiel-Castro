import random


class Enemy:
    """A single enemy with stats, a random attack, and an agility rating."""

    def __init__(self, name, hp, min_damage, max_damage, agility):
        """Create an enemy with name, hit points, damage range, and agility."""
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.agility = agility
        self.defense_multiplier = 1.0
        self.defense_turns = 0

    def attack(self):
        """Return a random amount of damage."""
        return random.randint(self.min_damage, self.max_damage)


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
        self.enemy = Enemy("Fly", 80, 6, 9, 5)
        self.over = False
        self.won = False
        self.phase = "player"
        self.message = "A wild Fly appears!"
        self._queued_attack = False
        self.luna_attacked = False
        self.attack_bonus = 0
        self.attack_bonus_turns = 0
        self.night_vision = False
        self.nine_lives = False

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
        """Reveal the enemy's intent (placeholder: no visible effect yet)."""
        self.night_vision = True
        self._say("Luna's eyes sharpen, reading the Fly's next move!")

    def _instinct_prowl(self):
        """Raise Luna's attack for the next two attacks."""
        self.attack_bonus = 2
        self.attack_bonus_turns = 2
        self._say("Luna prowls; her attack is up for two turns!")

    def _instinct_yowl(self):
        """Lower the enemy's defense so attacks deal 1.5x for two turns."""
        self.enemy.defense_multiplier = 1.5
        self.enemy.defense_turns = 2
        self._say("Luna yowls, intimidating the Fly!")

    def _instinct_nine_lives(self):
        """Grant Luna a one-time save from death this battle."""
        self.nine_lives = True
        self._say("Luna steels herself with her Nine Lives!")

    def _tick_statuses(self):
        """Count down active instinct durations and clear expired effects."""
        if self.attack_bonus_turns > 0:
            self.attack_bonus_turns -= 1
            if self.attack_bonus_turns == 0:
                self.attack_bonus = 0
        if self.enemy.defense_turns > 0:
            self.enemy.defense_turns -= 1
            if self.enemy.defense_turns == 0:
                self.enemy.defense_multiplier = 1.0

    def enemy_turn(self):
        """Enemy attacks; Luna's queued attack resolves after if she survives."""
        self._enemy_attack()
        if self.over:
            return
        if self._queued_attack:
            self._queued_attack = False
            self._luna_attack()
        if not self.over:
            self.phase = "player"

    def _player_acts_first(self):
        """Decide who acts first: higher agility wins, ties are random."""
        if self.agility > self.enemy.agility:
            return True
        if self.enemy.agility > self.agility:
            return False
        return random.choice([True, False])

    def _luna_attack(self):
        """Resolve Luna's attack: spend focus, then damage unless dodged."""
        self.focus -= self.ATTACK_COST
        self.luna_attacked = True
        if random.random() < self.dodge_chance(self.enemy.agility):
            self._say(f"The {self.enemy.name} dodges Luna's attack!")
            self._tick_statuses()
            return 0
        damage = random.randint(*self.ATTACK_DAMAGE)
        if self.attack_bonus > 0:
            damage += self.attack_bonus
        if self.enemy.defense_multiplier > 1.0:
            damage = int(damage * self.enemy.defense_multiplier)
        self._tick_statuses()
        self.enemy.hp = max(0, self.enemy.hp - damage)
        self._say(f"Luna attacks the {self.enemy.name} for {damage} damage!")
        if self.enemy.hp == 0:
            self.over = True
            self.won = True
        return damage

    def _enemy_attack(self):
        """Resolve the enemy's attack, unless Luna dodges or Nine Lives saves her."""
        if random.random() < self.dodge_chance(self.agility):
            self._say(f"Luna dodges the {self.enemy.name}'s attack!")
            return
        damage = self.enemy.attack()
        if self.player_hp - damage <= 0 and self.nine_lives:
            self.nine_lives = False
            self.player_hp = 1
            self._say("Nine Lives saves Luna from certain death!")
            return
        self.player_hp = max(0, self.player_hp - damage)
        self._say(f"The {self.enemy.name} attacks you for {damage} damage!")
        if self.player_hp == 0:
            self.over = True
            self.won = False