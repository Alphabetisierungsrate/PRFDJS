import unittest

from entities.being import Being
from entities.goblin import Goblin
from entities.human import Human
from entities.slime import Slime
from entities.species_stats import SPECIES_BASE_STATS


class BeingStatsTests(unittest.TestCase):
    def test_defaults(self):
        alice = Human("Alice")
        self.assertEqual(alice.level, 1)
        self.assertEqual(alice.experience, 0)
        self.assertEqual(alice.hp.current, alice.hp.max_value)
        self.assertEqual(alice.mana.current, alice.mana.max_value)

    def test_unregistered_species_falls_back_to_flat_defaults(self):
        dragon = Being("Smaug", species="dragon")
        self.assertEqual(dragon.hp.max_value, 10)
        self.assertEqual(dragon.mana.max_value, 10)
        self.assertEqual(dragon.base_attack, 0)
        self.assertEqual(dragon.base_armor, 0)
        self.assertEqual(dragon.base_magic, 0)

    def test_subtypes_pick_up_their_species_base_stats(self):
        alice = Human("Alice")
        grix = Goblin("Grix")
        ooze = Slime("Ooze")

        for being, species in ((alice, "human"), (grix, "goblin"), (ooze, "slime")):
            expected = SPECIES_BASE_STATS[species]
            self.assertEqual(being.hp.max_value, expected["max_hp"])
            self.assertEqual(being.mana.max_value, expected["max_mana"])
            self.assertEqual(being.base_attack, expected["base_attack"])
            self.assertEqual(being.base_armor, expected["base_armor"])
            self.assertEqual(being.base_magic, expected["base_magic"])

    def test_instance_override_wins_over_species_default(self):
        grix = Goblin("Grix", max_hp=999, base_attack=999)
        self.assertEqual(grix.hp.max_value, 999)
        self.assertEqual(grix.base_attack, 999)
        # Untouched stats still come from the goblin species defaults.
        self.assertEqual(grix.base_armor, SPECIES_BASE_STATS["goblin"]["base_armor"])

    def test_starts_at_full_hp_and_mana(self):
        alice = Being("Alice", species="human", max_hp=30, max_mana=15)
        self.assertEqual(alice.hp.current, 30)
        self.assertEqual(alice.mana.current, 15)

    def test_heal_does_not_exceed_max_hp(self):
        alice = Being("Alice", species="human", max_hp=30)
        alice.hp.add(-20)
        self.assertEqual(alice.hp.current, 10)
        alice.heal(100)
        self.assertEqual(alice.hp.current, 30)

    def test_restore_mana_does_not_exceed_max_mana(self):
        alice = Being("Alice", species="human", max_mana=15)
        alice.mana.add(-10)
        self.assertEqual(alice.mana.current, 5)
        alice.restore_mana(100)
        self.assertEqual(alice.mana.current, 15)

    def test_base_stats_are_mutable(self):
        goblin = Goblin("Grix")
        goblin.base_attack = 7
        goblin.base_armor = 3
        goblin.base_magic = 1
        self.assertEqual((goblin.base_attack, goblin.base_armor, goblin.base_magic), (7, 3, 1))

    def test_level_must_be_at_least_1(self):
        with self.assertRaises(ValueError):
            Being("Alice", species="human", level=0)

    def test_subtype_forwards_stat_overrides(self):
        grix = Goblin("Grix", max_hp=25, base_attack=5, level=3)
        self.assertEqual(grix.hp.max_value, 25)
        self.assertEqual(grix.hp.current, 25)
        self.assertEqual(grix.base_attack, 5)
        self.assertEqual(grix.level, 3)
        self.assertEqual(grix.species, "goblin")


if __name__ == "__main__":
    unittest.main()
