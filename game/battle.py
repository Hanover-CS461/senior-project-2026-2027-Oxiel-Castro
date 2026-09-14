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

    def attack(self):
        """Return a random amount of damage."""
        return random.randint(self.min_damage, self.max_damage)


class Battle:
    """Pure battle logic, no pygame dependency."""

    ATTACK_COST = 3
    ATTACK_DAMAGE = (13, 16)
    REST_GAIN = 12
    MAX_FOCUS = 30
    DODGE_BASE = 0.15
    DODGE_PER_AGILITY = 0.01

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

    @staticmethod
    def dodge_chance(agility):
        """Return the dodge chance (0.15-0.25) for the given agility."""
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
            return 0
        damage = random.randint(*self.ATTACK_DAMAGE)
        self.enemy.hp = max(0, self.enemy.hp - damage)
        self._say(f"Luna attacks the {self.enemy.name} for {damage} damage!")
        if self.enemy.hp == 0:
            self.over = True
            self.won = True
        return damage

    def _enemy_attack(self):
        """Resolve the enemy's attack, unless Luna dodges."""
        if random.random() < self.dodge_chance(self.agility):
            self._say(f"Luna dodges the {self.enemy.name}'s attack!")
            return
        damage = self.enemy.attack()
        self.player_hp = max(0, self.player_hp - damage)
        self._say(f"The {self.enemy.name} attacks you for {damage} damage!")
        if self.player_hp == 0:
            self.over = True
            self.won = False