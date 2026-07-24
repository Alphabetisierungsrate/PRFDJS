"""Positioning: where entities stand on a map, and their movement over time.

A `HexMap` is pure geometry (an immutable shape); `Positioning` is the
mutable layer on top of one map that tracks which entity occupies which hex
and moves them around. Keeping the two separate means a map's shape can be
reused while occupancy is its own state.

Rules for now (no hex types yet — every hex costs the same):
- At most one entity per hex.
- Movement is hex-by-hex to an adjacent hex, and each step takes
  `ticks_per_hex` ticks. Time comes from the shared `world.Clock` (this
  layer only reads it): call `start_move()` to begin a step, advance the
  clock, then `resolve_due()` to apply any arrivals — the same drive loop
  as `Encounter`.
- While a step is in flight the entity still occupies its origin hex, and
  its destination hex is *reserved* so nothing else can move into or be
  placed on it. On arrival the origin frees and the entity occupies the
  destination.

Multi-hex travel is just repeated single steps: `path_to()` gives the route
(via the map's BFS), and a driver starts the next step whenever the entity
is idle (see the movement tests for the canonical loop).
"""


class Positioning:
    def __init__(self, hex_map, clock, ticks_per_hex=1):
        if ticks_per_hex < 1:
            raise ValueError("ticks_per_hex must be >= 1")
        self.map = hex_map
        self.clock = clock
        self.ticks_per_hex = ticks_per_hex
        self._position = {}   # entity -> its settled origin hex
        self._occupant = {}   # hex -> the entity settled there
        self._reserved = {}   # hex -> entity whose in-flight move is heading there
        self._moving = {}     # entity -> (destination hex, arrival tick)

    def __repr__(self):
        return f"Positioning(map={self.map!r}, placed={len(self._position)})"

    # --- queries ---------------------------------------------------------

    def position_of(self, entity):
        """The hex `entity` currently occupies (its origin while mid-move), or None."""
        return self._position.get(entity)

    def occupant_at(self, cell):
        """The entity settled on `cell`, or None (a reserved-but-empty hex is None)."""
        return self._occupant.get(cell)

    def is_occupied(self, cell):
        """Whether `cell` is unavailable — settled-occupied or reserved for a move."""
        return cell in self._occupant or cell in self._reserved

    def is_placed(self, entity):
        return entity in self._position

    def is_moving(self, entity):
        return entity in self._moving

    # --- placement -------------------------------------------------------

    def place(self, entity, cell):
        """Put `entity` on `cell` (raises if off-map, occupied, or already placed)."""
        if cell not in self.map:
            raise ValueError(f"{cell!r} is not on this map")
        if self.is_placed(entity):
            raise ValueError(f"{entity!r} is already placed")
        if self.is_occupied(cell):
            raise ValueError(f"{cell!r} is already occupied")
        self._occupant[cell] = entity
        self._position[entity] = cell

    def remove(self, entity):
        """Take `entity` off the map, cancelling any in-flight move."""
        if not self.is_placed(entity):
            raise ValueError(f"{entity!r} is not on this map")
        if self.is_moving(entity):
            destination, _ = self._moving.pop(entity)
            del self._reserved[destination]
        cell = self._position.pop(entity)
        del self._occupant[cell]

    # --- movement --------------------------------------------------------

    def start_move(self, entity, destination):
        """Begin moving `entity` one hex to the adjacent `destination`.

        Reserves `destination` and marks `entity` in-transit until the step
        resolves `ticks_per_hex` ticks from now. Returns the arrival tick.
        """
        if not self.is_placed(entity):
            raise ValueError(f"{entity!r} is not on this map")
        if self.is_moving(entity):
            raise ValueError(f"{entity!r} is already moving")

        origin = self._position[entity]
        if destination not in self.map:
            raise ValueError(f"{destination!r} is not on this map")
        if destination not in origin.neighbors():
            raise ValueError(f"{destination!r} is not adjacent to {origin!r}")
        if self.is_occupied(destination):
            raise ValueError(f"{destination!r} is already occupied")

        arrival_tick = self.clock.current_tick + self.ticks_per_hex
        self._reserved[destination] = entity
        self._moving[entity] = (destination, arrival_tick)
        return arrival_tick

    def resolve_due(self):
        """Apply any moves whose arrival tick has been reached.

        Call after advancing the shared clock. Returns a list of
        (entity, destination) pairs for the moves that completed.
        """
        arrived = []
        for entity, (destination, arrival_tick) in list(self._moving.items()):
            if arrival_tick <= self.clock.current_tick:
                origin = self._position[entity]
                del self._occupant[origin]
                del self._reserved[destination]
                self._occupant[destination] = entity
                self._position[entity] = destination
                del self._moving[entity]
                arrived.append((entity, destination))
        return arrived

    def path_to(self, entity, destination):
        """The route `entity` would take to `destination` (map BFS, routes around holes)."""
        if not self.is_placed(entity):
            raise ValueError(f"{entity!r} is not on this map")
        return self.map.shortest_path(self._position[entity], destination)
