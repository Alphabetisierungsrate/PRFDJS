import unittest

from maps.hex import Hex
from maps.hex_map import HexMap


class HexMapConstructionTests(unittest.TestCase):
    def test_empty_map_is_rejected(self):
        with self.assertRaises(ValueError):
            HexMap([])

    def test_single_hex_is_valid(self):
        m = HexMap([Hex(0, 0)])
        self.assertEqual(len(m), 1)

    def test_line_shape_is_connected(self):
        line = HexMap([Hex(0, 0), Hex(1, 0), Hex(2, 0), Hex(3, 0)])
        self.assertEqual(len(line), 4)

    def test_ring_with_hole_in_the_middle_is_connected(self):
        # Radius-1 hexagon with the center removed: a 6-hex ring, still valid.
        ring = HexMap(h for h in HexMap.hexagon(1) if h != Hex(0, 0))
        self.assertEqual(len(ring), 6)
        self.assertNotIn(Hex(0, 0), ring)

    def test_disconnected_islands_are_rejected(self):
        with self.assertRaises(ValueError):
            HexMap([Hex(0, 0), Hex(5, 0)])

    def test_hexagon_sizes(self):
        self.assertEqual(len(HexMap.hexagon(0)), 1)
        self.assertEqual(len(HexMap.hexagon(1)), 7)
        self.assertEqual(len(HexMap.hexagon(2)), 19)


class HexMapQueryTests(unittest.TestCase):
    def setUp(self):
        self.map = HexMap.hexagon(1)

    def test_contains(self):
        self.assertIn(Hex(0, 0), self.map)
        self.assertNotIn(Hex(5, 5), self.map)

    def test_center_has_six_in_map_neighbors(self):
        self.assertEqual(len(self.map.neighbors(Hex(0, 0))), 6)

    def test_edge_hex_has_fewer_in_map_neighbors(self):
        # An outer hex of a radius-1 hexagon touches the center plus two
        # other outer hexes that are in the map; its other neighbors are off-map.
        self.assertEqual(len(self.map.neighbors(Hex(1, 0))), 3)

    def test_neighbors_rejects_off_map_hex(self):
        with self.assertRaises(ValueError):
            self.map.neighbors(Hex(9, 9))


class HexMapPathTests(unittest.TestCase):
    def test_shortest_path_on_a_line(self):
        line = HexMap([Hex(0, 0), Hex(1, 0), Hex(2, 0)])
        path = line.shortest_path(Hex(0, 0), Hex(2, 0))
        self.assertEqual(path, [Hex(0, 0), Hex(1, 0), Hex(2, 0)])
        self.assertEqual(line.distance(Hex(0, 0), Hex(2, 0)), 2)

    def test_path_routes_around_a_hole(self):
        # In a ring (center removed) the straight-line distance across is 2,
        # but with the middle gone the real path around the ring is 3 steps.
        ring = HexMap(h for h in HexMap.hexagon(1) if h != Hex(0, 0))
        a, b = Hex(1, 0), Hex(-1, 0)
        self.assertEqual(a.distance(b), 2)
        self.assertEqual(ring.distance(a, b), 3)

    def test_path_to_self(self):
        m = HexMap.hexagon(1)
        self.assertEqual(m.shortest_path(Hex(0, 0), Hex(0, 0)), [Hex(0, 0)])
        self.assertEqual(m.distance(Hex(0, 0), Hex(0, 0)), 0)

    def test_shortest_path_rejects_off_map_endpoint(self):
        m = HexMap.hexagon(1)
        with self.assertRaises(ValueError):
            m.shortest_path(Hex(0, 0), Hex(9, 9))


if __name__ == "__main__":
    unittest.main()
