"""Automated tests for the pure run logic in game/run.py.

Run with:  python3 -m unittest discover -s tests
"""

import sys
from pathlib import Path
from unittest import TestCase

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "game"))

from battle import Battle
from run import BUILDINGS, DIFFICULTY_TIERS, Run


class RunTest(TestCase):
    """Tests for the seeded run: buildings, persistence, and win/loss."""

    def test_seed_reproducible(self):
        run1 = Run(seed=42)
        run2 = Run(seed=42)
        self.assertEqual(run1.human_building, run2.human_building)

    def test_human_in_one_building(self):
        run = Run(seed=1234)
        self.assertIn(run.human_building, [b["name"] for b in BUILDINGS])

    def test_all_buildings_available_at_start(self):
        run = Run(seed=5)
        self.assertEqual(set(run.available_buildings()), {b["name"] for b in BUILDINGS})

    def test_battle_starts_with_run_state(self):
        run = Run(seed=7)
        battle = run.start_battle(run.available_buildings()[0])
        self.assertEqual(battle.player_hp, Run.START_HP)
        self.assertEqual(battle.focus, Run.START_FOCUS)
        self.assertEqual(battle.inventory, Run.START_INVENTORY)

    def test_win_persists_state_and_heals(self):
        run = Run(seed=9)
        name = run.available_buildings()[0]
        battle = run.start_battle(name)
        battle.won = True
        battle.player_hp = 40
        run.end_battle(battle)
        self.assertEqual(run.player_hp, 40 + Run.HEAL_BETWEEN)
        self.assertEqual(run.focus, Run.BETWEEN_FOCUS)
        self.assertEqual(run.stage[name], 1)
        self.assertFalse(run.lost)

    def test_heal_capped_at_max_hp(self):
        run = Run(seed=9)
        name = run.available_buildings()[0]
        battle = run.start_battle(name)
        battle.won = True
        battle.player_hp = 99
        run.end_battle(battle)
        self.assertEqual(run.player_hp, Run.MAX_HP)

    def test_loss_ends_run(self):
        run = Run(seed=11)
        name = run.available_buildings()[0]
        battle = run.start_battle(name)
        battle.won = False
        run.end_battle(battle)
        self.assertTrue(run.lost)
        self.assertFalse(run.won)

    def test_guard_then_boss_then_cleared(self):
        run = Run(seed=13)
        name = run.available_buildings()[0]
        for _ in range(2):
            battle = run.start_battle(name)
            battle.won = True
            run.end_battle(battle)
        self.assertTrue(run.is_cleared(name))
        self.assertNotIn(name, run.available_buildings())

    def test_escalating_enemies(self):
        run = Run(seed=15)
        names = run.available_buildings()
        guard_battle = run.start_battle(names[0])
        guard_hp = guard_battle.enemy.max_hp
        run.current_building = names[0]
        run.stage[names[0]] = 1
        boss_battle = run.start_battle(names[0])
        self.assertGreater(boss_battle.enemy.max_hp, guard_hp)

    def test_human_building_final_boss_wins(self):
        run = Run(seed=17)
        human = run.human_building
        run.stage[human] = 2
        battle = run.start_battle(human)
        self.assertEqual(battle.enemy.name, "Campus Guardian")
        battle.won = True
        run.end_battle(battle)
        self.assertTrue(run.won)
        self.assertTrue(run.is_cleared(human))

    def test_difficulty_tiers_map_easy_medium_hard(self):
        self.assertEqual(DIFFICULTY_TIERS, {"Easy": 1, "Medium": 2, "Hard": 3})

    def test_higher_difficulty_scales_guard(self):
        name = Run(seed=21).available_buildings()[0]
        easy = Run(seed=21, tier=DIFFICULTY_TIERS["Easy"]).start_battle(name)
        hard = Run(seed=21, tier=DIFFICULTY_TIERS["Hard"]).start_battle(name)
        self.assertGreater(hard.enemy.max_hp, easy.enemy.max_hp)
        self.assertGreater(hard.enemy.agility, easy.enemy.agility)

    def test_higher_difficulty_scales_final_boss(self):
        easy = Run(seed=23, tier=DIFFICULTY_TIERS["Easy"])
        hard = Run(seed=23, tier=DIFFICULTY_TIERS["Hard"])
        for run in (easy, hard):
            run.stage[run.human_building] = 2
        easy_boss = easy.start_battle(easy.human_building)
        hard_boss = hard.start_battle(hard.human_building)
        self.assertEqual(easy_boss.enemy.name, "Campus Guardian")
        self.assertGreater(hard_boss.enemy.max_hp, easy_boss.enemy.max_hp)

    def test_default_tier_matches_easy(self):
        default = Run(seed=25).tier
        self.assertEqual(default, DIFFICULTY_TIERS["Easy"])


if __name__ == "__main__":
    import unittest

    unittest.main()