import unittest

from entities.stat import Stat


class StatTests(unittest.TestCase):
    def test_starts_full(self):
        stat = Stat(10)
        self.assertEqual(stat.current, 10)
        self.assertEqual(stat.max_value, 10)

    def test_add_clamps_at_max(self):
        stat = Stat(10)
        stat.add(100)
        self.assertEqual(stat.current, 10)

    def test_add_clamps_at_zero(self):
        stat = Stat(10)
        stat.add(-100)
        self.assertEqual(stat.current, 0)

    def test_add_negative_then_positive_heals_within_bounds(self):
        stat = Stat(10)
        stat.add(-4)
        self.assertEqual(stat.current, 6)
        stat.add(3)
        self.assertEqual(stat.current, 9)

    def test_set_max_clamps_current_down(self):
        stat = Stat(10)
        stat.set_max(5)
        self.assertEqual(stat.max_value, 5)
        self.assertEqual(stat.current, 5)

    def test_set_max_up_does_not_change_current(self):
        stat = Stat(10)
        stat.add(-5)
        stat.set_max(20)
        self.assertEqual(stat.current, 5)
        self.assertEqual(stat.max_value, 20)

    def test_negative_max_value_raises(self):
        with self.assertRaises(ValueError):
            Stat(-1)


if __name__ == "__main__":
    unittest.main()
