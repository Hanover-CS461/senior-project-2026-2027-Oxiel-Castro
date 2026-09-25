"""Automated tests for the pure battle logic in game/battle.py.

Run from the repo root with:  python3 -m unittest discover -s tests
No pygame required -- battle.py only imports the random module.
"""

import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "game"))

from battle import (
    Battle,
    ENEMY_MOVES,
    STATUSES,
    Enemy,
    apply_status,
    damage_multipliers,
    effective_agility,
    tick_statuses,
)

BUZZ = {"name": "Buzz", "damage": (5, 8), "weight": 55}
STING = {"name": "Sting", "damage": (11, 15), "weight": 25, "heavy": True}
HOVER = {"name": "Hover", "weight": 10, "status": "prowl", "target": "self", "message": "its agility is up"}
IRRITATE = {"name": "Irritate", "weight": 10, "status": "intimidated", "target": "player", "message": "Luna is intimidated"}


class StatusFrameworkTest(TestCase):
    """Unit tests for the status system: apply, cap, tick, and multipliers."""

    def test_all_statuses_defined(self):
        for key in ("prowl", "riled", "intimidated", "puffed", "night_vision"):
            self.assertIn(key, STATUSES)
            self.assertIn("name", STATUSES[key])
            self.assertIn("duration", STATUSES[key])

    def test_apply_status_fresh(self):
        statuses = {}
        apply_status(statuses, "prowl")
        self.assertIn("prowl", statuses)
        self.assertEqual(statuses["prowl"].duration, 2)
        self.assertEqual(statuses["prowl"].modifiers["agility"], 0.5)

    def test_apply_status_refreshes_duration(self):
        statuses = {}
        apply_status(statuses, "prowl")
        statuses["prowl"].duration = 1
        apply_status(statuses, "prowl")
        self.assertEqual(statuses["prowl"].duration, 2)

    def test_prowl_stacking_capped(self):
        statuses = {}
        for _ in range(4):
            apply_status(statuses, "prowl")
        self.assertEqual(statuses["prowl"].modifiers["agility"], 1.5)

    def test_riled_stacking_capped(self):
        statuses = {}
        for _ in range(3):
            apply_status(statuses, "riled")
        self.assertEqual(statuses["riled"].modifiers["outgoing_mult"], 2.0)

    def test_intimidated_stacking_capped(self):
        statuses = {}
        for _ in range(3):
            apply_status(statuses, "intimidated")
        self.assertEqual(statuses["intimidated"].modifiers["incoming_mult"], 2.0)

    def test_puffed_stacking_capped(self):
        statuses = {}
        for _ in range(3):
            apply_status(statuses, "puffed")
        self.assertEqual(statuses["puffed"].modifiers["incoming_mult"], 0.5)

    def test_effective_agility_with_bonus(self):
        statuses = {}
        apply_status(statuses, "prowl")
        self.assertEqual(effective_agility(3, statuses), 3.5)
        self.assertEqual(effective_agility(3, {}), 3.0)

    def test_damage_multipliers(self):
        riled = {}
        apply_status(riled, "riled")
        self.assertEqual(damage_multipliers(riled), (1.5, 1.0))
        debuffed = {}
        apply_status(debuffed, "intimidated")
        self.assertEqual(damage_multipliers(debuffed), (1.0, 1.5))
        puffed = {}
        apply_status(puffed, "puffed")
        self.assertEqual(damage_multipliers(puffed), (1.0, 0.5))

    def test_tick_only_matching_trigger(self):
        statuses = {}
        apply_status(statuses, "night_vision")
        tick_statuses(statuses, "was_attacked")
        self.assertEqual(statuses["night_vision"].duration, 3)
        tick_statuses(statuses, "round_end")
        self.assertEqual(statuses["night_vision"].duration, 2)

    def test_tick_removes_expired(self):
        statuses = {}
        apply_status(statuses, "puffed")
        statuses["puffed"].duration = 1
        tick_statuses(statuses, "took_hit")
        self.assertNotIn("puffed", statuses)


class EnemyAITest(TestCase):
    """Tests for the enemy move pool, intent selection, and intent execution."""

    def test_choose_intent_returns_valid_move(self):
        enemy = Enemy("Fly", 80, 5, ENEMY_MOVES["fly"])
        for _ in range(50):
            enemy.choose_intent()
            self.assertIn(enemy.intent, ENEMY_MOVES["fly"])

    def test_battle_starts_with_intent(self):
        battle = Battle()
        self.assertIn(battle.enemy.intent, ENEMY_MOVES["fly"])

    def test_damage_intent_hits_player(self):
        battle = Battle()
        battle.enemy.intent = BUZZ
        before = battle.player_hp
        with patch("random.random", return_value=1.0), patch("random.randint", return_value=6):
            battle.enemy_turn()
        self.assertEqual(before - battle.player_hp, 6)

    def test_player_status_intent_applies_debuff(self):
        battle = Battle()
        battle.enemy.intent = IRRITATE
        battle.enemy_turn()
        self.assertIn("intimidated", battle.statuses)
        self.assertEqual(battle.statuses["intimidated"].duration, 2)

    def test_self_status_intent_applies_buff_to_enemy(self):
        battle = Battle()
        battle.enemy.intent = HOVER
        battle.enemy_turn()
        self.assertIn("prowl", battle.enemy.statuses)
        self.assertEqual(battle.enemy.statuses["prowl"].modifiers["agility"], 0.5)

    def test_enemy_buff_ticks_when_attacked(self):
        battle = Battle()
        battle.enemy.intent = HOVER
        battle.enemy_turn()
        self.assertIn("prowl", battle.enemy.statuses)
        battle.enemy.agility = 1
        battle.enemy.intent = BUZZ
        with patch("random.random", return_value=1.0):
            battle.attack()
        self.assertEqual(battle.enemy.statuses["prowl"].duration, 1)
        battle.enemy.intent = BUZZ
        with patch("random.random", return_value=1.0):
            battle.attack()
        self.assertNotIn("prowl", battle.enemy.statuses)

    def test_intent_rechosen_each_round(self):
        battle = Battle()
        battle.enemy.intent = BUZZ
        battle.enemy_turn()
        self.assertIn(battle.enemy.intent, ENEMY_MOVES["fly"])


class BattleFlowTest(TestCase):
    """Tests for the full battle: actions, instincts, and win/lose conditions."""

    def test_init_state(self):
        battle = Battle()
        self.assertEqual(battle.player_hp, 100)
        self.assertEqual(battle.enemy.hp, 80)
        self.assertEqual(battle.focus, 16)
        self.assertEqual(battle.phase, "player")
        self.assertFalse(battle.over)

    def test_attack_spends_focus_and_deals_damage(self):
        battle = Battle()
        battle.enemy.agility = 1
        with patch("random.random", return_value=1.0), patch("random.randint", return_value=13):
            damage = battle.attack()
        self.assertEqual(damage, 13)
        self.assertEqual(battle.enemy.hp, 67)
        self.assertEqual(battle.focus, 16 - Battle.ATTACK_COST)

    def test_attack_can_be_dodged(self):
        battle = Battle()
        battle.enemy.agility = 1
        with patch("random.random", return_value=0.0):
            damage = battle.attack()
        self.assertEqual(damage, 0)
        self.assertEqual(battle.enemy.hp, 80)

    def test_attack_queued_when_enemy_faster(self):
        battle = Battle()
        with patch("random.random", return_value=1.0), patch("random.randint", return_value=13):
            self.assertIsNone(battle.attack())
        self.assertTrue(battle._queued_attack)
        self.assertEqual(battle.phase, "enemy")
        battle.enemy.intent = BUZZ
        with patch("random.random", return_value=1.0), patch("random.randint", return_value=13):
            battle.enemy_turn()
        self.assertEqual(battle.enemy.hp, 67)

    def test_attack_insufficient_focus(self):
        battle = Battle()
        battle.focus = 2
        self.assertIsNone(battle.attack())
        self.assertEqual(battle.message, "Not enough focus to attack!")

    def test_player_acts_first_by_agility(self):
        battle = Battle()
        battle.enemy.agility = 1
        self.assertTrue(battle._player_acts_first())
        battle.enemy.agility = 10
        self.assertFalse(battle._player_acts_first())

    def test_rest_regains_focus(self):
        battle = Battle()
        battle.rest()
        self.assertEqual(battle.focus, 28)
        self.assertEqual(battle.phase, "enemy")

    def test_rest_capped_at_max(self):
        battle = Battle()
        battle.focus = Battle.MAX_FOCUS - 5
        battle.rest()
        self.assertEqual(battle.focus, Battle.MAX_FOCUS)

    def test_defend_applies_puffed(self):
        battle = Battle()
        battle.defend()
        self.assertIn("puffed", battle.statuses)
        self.assertEqual(battle.phase, "enemy")

    def test_night_vision_instinct(self):
        battle = Battle()
        battle.use_instinct("night_vision")
        self.assertIn("night_vision", battle.statuses)
        self.assertEqual(battle.statuses["night_vision"].duration, 3)

    def test_night_vision_ticks_each_round(self):
        battle = Battle()
        battle.use_instinct("night_vision")
        battle.enemy.intent = BUZZ
        battle.enemy_turn()
        self.assertEqual(battle.statuses["night_vision"].duration, 2)

    def test_prowl_instinct_boosts_agility(self):
        battle = Battle()
        battle.use_instinct("prowl")
        self.assertEqual(effective_agility(battle.agility, battle.statuses), 3.5)

    def test_yowl_instinct_intimidates_enemy(self):
        battle = Battle()
        battle.use_instinct("yowl")
        self.assertIn("intimidated", battle.enemy.statuses)
        self.assertEqual(damage_multipliers(battle.enemy.statuses), (1.0, 1.5))

    def test_nine_lives_instinct(self):
        battle = Battle()
        battle.use_instinct("nine_lives")
        self.assertTrue(battle.nine_lives)

    def test_instinct_insufficient_focus(self):
        battle = Battle()
        battle.focus = 1
        self.assertIsNone(battle.use_instinct("yowl"))
        self.assertNotIn("intimidated", battle.enemy.statuses)

    def test_victory_when_enemy_defeated(self):
        battle = Battle()
        battle.enemy.agility = 1
        battle.enemy.hp = 10
        with patch("random.random", return_value=1.0), patch("random.randint", return_value=13):
            battle.attack()
        self.assertTrue(battle.over)
        self.assertTrue(battle.won)

    def test_defeat_when_player_defeated(self):
        battle = Battle()
        battle.player_hp = 5
        battle.enemy.intent = STING
        with patch("random.random", return_value=1.0), patch("random.randint", return_value=15):
            battle.enemy_turn()
        self.assertTrue(battle.over)
        self.assertFalse(battle.won)

    def test_nine_lives_saves_from_death(self):
        battle = Battle()
        battle.player_hp = 10
        battle.nine_lives = True
        battle.enemy.intent = STING
        with patch("random.random", return_value=1.0), patch("random.randint", return_value=15):
            battle.enemy_turn()
        self.assertFalse(battle.over)
        self.assertEqual(battle.player_hp, 1)
        self.assertFalse(battle.nine_lives)

    def test_nine_lives_used_up(self):
        battle = Battle()
        battle.player_hp = 10
        battle.nine_lives = True
        battle.enemy.intent = STING
        with patch("random.random", return_value=1.0), patch("random.randint", return_value=15):
            battle.enemy_turn()
        battle.enemy.intent = STING
        with patch("random.random", return_value=1.0), patch("random.randint", return_value=15):
            battle.enemy_turn()
        self.assertTrue(battle.over)
        self.assertFalse(battle.won)


if __name__ == "__main__":
    import unittest

    unittest.main()