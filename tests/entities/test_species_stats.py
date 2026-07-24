import unittest

from entities.species_stats import SPECIES_BASE_STATS, base_stats_for


class SpeciesStatsTests(unittest.TestCase):
    def test_returns_registered_species_stats(self):
        self.assertEqual(base_stats_for("goblin"), SPECIES_BASE_STATS["goblin"])

    def test_unregistered_species_returns_empty_dict(self):
        self.assertEqual(base_stats_for("dragon"), {})

    def test_returned_dict_is_a_copy(self):
        stats = base_stats_for("goblin")
        stats["max_hp"] = 99999
        self.assertNotEqual(SPECIES_BASE_STATS["goblin"]["max_hp"], 99999)


if __name__ == "__main__":
    unittest.main()
