import unittest

from maps.hex import Hex


class HexTests(unittest.TestCase):
    def test_s_is_derived_from_q_and_r(self):
        self.assertEqual(Hex(2, -1).s, -1)
        self.assertEqual(Hex(0, 0).s, 0)

    def test_has_six_distinct_neighbors(self):
        neighbors = Hex(0, 0).neighbors()
        self.assertEqual(len(neighbors), 6)
        self.assertEqual(len(set(neighbors)), 6)

    def test_each_neighbor_is_distance_one_away(self):
        origin = Hex(0, 0)
        for neighbor in origin.neighbors():
            self.assertEqual(origin.distance(neighbor), 1)

    def test_distance(self):
        self.assertEqual(Hex(0, 0).distance(Hex(0, 0)), 0)
        self.assertEqual(Hex(0, 0).distance(Hex(2, -1)), 2)
        self.assertEqual(Hex(0, 0).distance(Hex(3, -1)), 3)

    def test_is_hashable_and_value_equal(self):
        self.assertEqual(Hex(1, 2), Hex(1, 2))
        self.assertEqual(len({Hex(1, 2), Hex(1, 2)}), 1)

    def test_neighbor_by_direction(self):
        self.assertIn(Hex(0, 0).neighbor(0), Hex(0, 0).neighbors())


if __name__ == "__main__":
    unittest.main()
