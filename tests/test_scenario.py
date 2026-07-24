"""End-to-end scenario: a human takes a slime-slaying quest, fights the slime
in a tick-driven encounter, completes the quest, and loots its drop.

This is the first integration test that wires the packages together
(entities + quests + encounters + items + the global clock). For now the
encounter "just happens" right after the quest is accepted; later there
will be other actions in between.
"""

import unittest

from encounters.attack import Attack
from encounters.encounter import Encounter
from entities.human import Human
from entities.slime import Slime
from items.slime_core import SlimeCore
from quests.quest import Quest, QuestStatus
from quests.quest_board import QuestBoard
from world.clock import Clock


def run_encounter(encounter, clock, max_ticks=1000):
    """Drive a 1v1 to completion: each entity attacks the other whenever ready.

    Time comes from the shared `clock`; the encounter only reads it. Actions
    are started for whoever is free, then the clock advances one tick and the
    encounter resolves whatever came due.
    """
    while not encounter.is_over:
        for entity in (encounter.a, encounter.b):
            if encounter.is_ready(entity):
                encounter.start_action(entity, Attack(entity, encounter.opponent_of(entity)))
        clock.advance()
        encounter.resolve_due()
        if clock.current_tick > max_ticks:
            raise AssertionError("encounter did not resolve within max_ticks")


class SlimeSlayingScenarioTests(unittest.TestCase):
    def test_human_slays_slime_completes_quest_and_loots_core(self):
        clock = Clock()

        guildmaster = Human("Guildmaster")
        hero = Human("Hero", max_hp=30, base_attack=10, base_armor=5, has_inventory=True)
        slime = Slime("Ooze", max_hp=8, base_attack=2, base_armor=0, drops=[SlimeCore()])

        # The board posts a "slay a slime" quest; the hero accepts it there.
        board = QuestBoard("Town Square")
        quest = Quest(
            "Slay a slime",
            provider=guildmaster,
            conditions=[lambda: slime.hp.current <= 0],
        )
        board.post(quest)
        board.accept(quest, hero)

        self.assertIn(quest, hero.quests)
        self.assertIs(quest.status, QuestStatus.TAKEN)
        self.assertFalse(quest.is_successful())

        # The encounter happens.
        encounter = Encounter(hero, slime, clock)
        run_encounter(encounter, clock)

        self.assertIs(encounter.winner, hero)
        self.assertLessEqual(slime.hp.current, 0)
        self.assertGreater(hero.hp.current, 0)

        # The slaying satisfies the quest; mark it completed.
        self.assertTrue(quest.is_successful())
        quest.complete()
        self.assertIs(quest.status, QuestStatus.COMPLETED)

        # The slime's drop is looted into the hero's inventory.
        looted = hero.loot(slime)
        self.assertEqual(len(looted), 1)
        self.assertIsInstance(looted[0], SlimeCore)
        self.assertIn(looted[0], hero.inventory)
        self.assertEqual(slime.drops, [])


if __name__ == "__main__":
    unittest.main()
