import unittest

from world.clock import Clock


class ClockTests(unittest.TestCase):
    def test_starts_at_zero_by_default(self):
        self.assertEqual(Clock().current_tick, 0)

    def test_custom_start(self):
        self.assertEqual(Clock(start=5).current_tick, 5)

    def test_advance_moves_forward_by_exactly_one(self):
        clock = Clock()
        self.assertEqual(clock.advance(), 1)
        self.assertEqual(clock.advance(), 2)
        self.assertEqual(clock.current_tick, 2)


if __name__ == "__main__":
    unittest.main()
