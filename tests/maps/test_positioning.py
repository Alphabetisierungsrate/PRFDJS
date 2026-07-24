import unittest

from entities.human import Human
from maps.hex import Hex
from maps.hex_map import HexMap
from maps.positioning import Positioning
from world.clock import Clock


class PlacementTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.map = HexMap.hexagon(1)
        self.positioning = Positioning(self.map, self.clock)
        self.alice = Human("Alice")
        self.bob = Human("Bob")

    def test_place_and_query(self):
        self.positioning.place(self.alice, Hex(0, 0))
        self.assertEqual(self.positioning.position_of(self.alice), Hex(0, 0))
        self.assertIs(self.positioning.occupant_at(Hex(0, 0)), self.alice)
        self.assertTrue(self.positioning.is_occupied(Hex(0, 0)))
        self.assertTrue(self.positioning.is_placed(self.alice))

    def test_place_off_map_raises(self):
        with self.assertRaises(ValueError):
            self.positioning.place(self.alice, Hex(9, 9))

    def test_place_on_occupied_hex_raises(self):
        self.positioning.place(self.alice, Hex(0, 0))
        with self.assertRaises(ValueError):
            self.positioning.place(self.bob, Hex(0, 0))

    def test_place_already_placed_entity_raises(self):
        self.positioning.place(self.alice, Hex(0, 0))
        with self.assertRaises(ValueError):
            self.positioning.place(self.alice, Hex(1, 0))

    def test_remove_frees_the_hex(self):
        self.positioning.place(self.alice, Hex(0, 0))
        self.positioning.remove(self.alice)
        self.assertFalse(self.positioning.is_occupied(Hex(0, 0)))
        self.assertFalse(self.positioning.is_placed(self.alice))
        self.assertIsNone(self.positioning.position_of(self.alice))


class MovementTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.map = HexMap.hexagon(2)
        self.positioning = Positioning(self.map, self.clock, ticks_per_hex=3)
        self.alice = Human("Alice")
        self.bob = Human("Bob")
        self.positioning.place(self.alice, Hex(0, 0))

    def test_step_takes_ticks_per_hex_to_resolve(self):
        self.positioning.start_move(self.alice, Hex(1, 0))
        self.assertTrue(self.positioning.is_moving(self.alice))

        for _ in range(self.positioning.ticks_per_hex - 1):
            self.clock.advance()
            self.assertEqual(self.positioning.resolve_due(), [])
        # Still at origin, destination still reserved (not settled).
        self.assertEqual(self.positioning.position_of(self.alice), Hex(0, 0))
        self.assertIsNone(self.positioning.occupant_at(Hex(1, 0)))
        self.assertTrue(self.positioning.is_occupied(Hex(1, 0)))

        self.clock.advance()
        arrived = self.positioning.resolve_due()
        self.assertEqual(arrived, [(self.alice, Hex(1, 0))])
        self.assertEqual(self.positioning.position_of(self.alice), Hex(1, 0))
        self.assertIs(self.positioning.occupant_at(Hex(1, 0)), self.alice)
        self.assertFalse(self.positioning.is_occupied(Hex(0, 0)))
        self.assertFalse(self.positioning.is_moving(self.alice))

    def test_move_to_non_adjacent_hex_raises(self):
        with self.assertRaises(ValueError):
            self.positioning.start_move(self.alice, Hex(2, 0))

    def test_move_off_map_raises(self):
        self.positioning.remove(self.alice)
        self.positioning.place(self.alice, Hex(2, 0))  # edge of the radius-2 map
        with self.assertRaises(ValueError):
            self.positioning.start_move(self.alice, Hex(3, 0))

    def test_cannot_move_into_an_occupied_hex(self):
        self.positioning.place(self.bob, Hex(1, 0))
        with self.assertRaises(ValueError):
            self.positioning.start_move(self.alice, Hex(1, 0))

    def test_reserved_destination_blocks_others(self):
        self.positioning.place(self.bob, Hex(0, -1))
        # Alice reserves (1, -1); Bob then can't move into or be blocked by it.
        self.positioning.start_move(self.alice, Hex(1, -1))
        with self.assertRaises(ValueError):
            self.positioning.start_move(self.bob, Hex(1, -1))

    def test_moving_entity_cannot_start_a_second_move(self):
        self.positioning.start_move(self.alice, Hex(1, 0))
        with self.assertRaises(ValueError):
            self.positioning.start_move(self.alice, Hex(0, 1))

    def test_walking_a_multi_hex_path(self):
        goal = Hex(2, 0)
        max_ticks = 100
        while self.positioning.position_of(self.alice) != goal:
            if not self.positioning.is_moving(self.alice):
                route = self.positioning.path_to(self.alice, goal)
                self.positioning.start_move(self.alice, route[1])
            self.clock.advance()
            self.positioning.resolve_due()
            self.assertLess(self.clock.current_tick, max_ticks)

        self.assertEqual(self.positioning.position_of(self.alice), goal)
        # 2 hexes * 3 ticks each.
        self.assertEqual(self.clock.current_tick, 6)

    def test_path_to_returns_route(self):
        route = self.positioning.path_to(self.alice, Hex(2, 0))
        self.assertEqual(route[0], Hex(0, 0))
        self.assertEqual(route[-1], Hex(2, 0))


if __name__ == "__main__":
    unittest.main()
