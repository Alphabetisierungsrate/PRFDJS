"""Hex: a single hexagonal cell's coordinate.

Uses axial coordinates `(q, r)`; the third cube coordinate `s = -q - r` is
derived on demand and only needed for distance. The six neighbor directions
below are the same in axial space whether the eventual rendering is
pointy-top or flat-top — orientation changes only how a hex is *drawn* and
which side you call "north", not the coordinate math or adjacency — so
nothing here commits to one. (When rendering is added, the plan is
pointy-top.)

`Hex` is a frozen dataclass, so it's immutable and hashable and can be used
directly as a set element / dict key (which `HexMap` relies on).
"""

from dataclasses import dataclass

# Axial deltas to the six adjacent hexes, in a consistent rotational order.
_DIRECTIONS = ((1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1))


@dataclass(frozen=True)
class Hex:
    q: int
    r: int

    @property
    def s(self):
        return -self.q - self.r

    def neighbor(self, direction):
        """The adjacent hex in one of the six directions (0..5)."""
        dq, dr = _DIRECTIONS[direction]
        return Hex(self.q + dq, self.r + dr)

    def neighbors(self):
        """All six adjacent hexes (as bare coordinates, map membership aside)."""
        return [Hex(self.q + dq, self.r + dr) for dq, dr in _DIRECTIONS]

    def distance(self, other):
        """Straight-line hex distance, ignoring any map's shape or holes."""
        return (
            abs(self.q - other.q)
            + abs(self.r - other.r)
            + abs(self.s - other.s)
        ) // 2

    def __repr__(self):
        return f"Hex(q={self.q}, r={self.r})"
