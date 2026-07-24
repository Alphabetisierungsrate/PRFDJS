"""HexMap: one map made of connected hexes, of arbitrary shape.

Each map is its own instance — there is no single global grid. A map is any
set of `Hex` coordinates, subject to one hard rule: every hex must be
reachable from every other by stepping between adjacent in-map hexes. That
still allows all kinds of shapes — a solid blob, a ring with a hole in the
middle, a single line — but rejects a set that splits into disconnected
islands.

Distance comes in two flavors: `Hex.distance` is the straight-line hex
distance ignoring shape, while `HexMap.distance` is the number of steps
along the shortest in-map path, which routes *around* holes.
"""

from collections import deque

from maps.hex import Hex


class HexMap:
    def __init__(self, hexes):
        hexes = frozenset(hexes)
        if not hexes:
            raise ValueError("a map must have at least one hex")
        if not self._is_connected(hexes):
            raise ValueError("every hex in a map must be reachable from every other")
        self.hexes = hexes

    @staticmethod
    def _is_connected(hexes):
        start = next(iter(hexes))
        seen = {start}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in current.neighbors():
                if neighbor in hexes and neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        return len(seen) == len(hexes)

    def __contains__(self, cell):
        return cell in self.hexes

    def __len__(self):
        return len(self.hexes)

    def __iter__(self):
        return iter(self.hexes)

    def __repr__(self):
        return f"HexMap({len(self.hexes)} hexes)"

    def neighbors(self, cell):
        """The in-map hexes adjacent to `cell` (raises if `cell` isn't on the map)."""
        if cell not in self.hexes:
            raise ValueError(f"{cell!r} is not on this map")
        return [n for n in cell.neighbors() if n in self.hexes]

    def shortest_path(self, start, goal):
        """Shortest in-map path from `start` to `goal` as an inclusive list of
        hexes, stepping only through in-map hexes and routing around holes.

        Both endpoints must be on the map. Returns `None` if `goal` is
        unreachable — which can't happen for two on-map hexes (a map is
        connected by construction), but keeps the method total.
        """
        for endpoint in (start, goal):
            if endpoint not in self.hexes:
                raise ValueError(f"{endpoint!r} is not on this map")

        came_from = {start: None}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            if current == goal:
                break
            for neighbor in self.neighbors(current):
                if neighbor not in came_from:
                    came_from[neighbor] = current
                    queue.append(neighbor)

        if goal not in came_from:
            return None

        path = []
        node = goal
        while node is not None:
            path.append(node)
            node = came_from[node]
        path.reverse()
        return path

    def distance(self, start, goal):
        """Steps along the shortest in-map path (routes around holes), or None."""
        path = self.shortest_path(start, goal)
        return None if path is None else len(path) - 1

    @classmethod
    def hexagon(cls, radius, center=None):
        """Build a solid hexagon-shaped map of the given radius around `center`.

        radius 0 is a single hex; radius 1 is 7 hexes; etc.
        """
        if radius < 0:
            raise ValueError("radius must be >= 0")
        if center is None:
            center = Hex(0, 0)
        cells = []
        for dq in range(-radius, radius + 1):
            for dr in range(-radius, radius + 1):
                if max(abs(dq), abs(dr), abs(-dq - dr)) <= radius:
                    cells.append(Hex(center.q + dq, center.r + dr))
        return cls(cells)
