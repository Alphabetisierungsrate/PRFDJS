"""Encounter: a tick-driven fight, for now strictly 1 vs 1.

Ticks are a shared, ever-advancing measure of time: `tick()` moves the
clock forward by exactly one, whether or not anyone is acting - it never
jumps ahead to "the next interesting moment". That's deliberate: it means
a still-free entity can have an action started for it at any tick,
independent of what the other entity is doing (including mid-wind-up of
its own action), and every encounter's log comes out in strict tick order
by construction. It's also what will let this scale to multiplayer later:
two people reading/acting against the current tick of two different
encounters (or the same one) never have to coordinate around each other -
the clock just keeps advancing the same way for everyone.

An action already in flight resolves at its scheduled tick even if its
actor has since died - ticks don't rewind the past; a killing blow already
thrown lands regardless of what happens to its thrower afterwards.

For now, an encounter has exactly two participants (`a`, `b`) and the only
action either can take is `Attack`.
"""

from collections import namedtuple

LogEntry = namedtuple("LogEntry", ["tick", "event", "entity", "action"])


class Encounter:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.tick_count = 0
        self._busy_until = {a: 0, b: 0}
        self._pending_action = {a: None, b: None}
        self.log = []

    def __repr__(self):
        return f"Encounter(a={self.a!r}, b={self.b!r}, tick={self.tick_count})"

    def opponent_of(self, entity):
        if entity is self.a:
            return self.b
        if entity is self.b:
            return self.a
        raise ValueError(f"{entity!r} is not part of this encounter")

    @property
    def is_over(self):
        return self.a.hp.current <= 0 or self.b.hp.current <= 0

    @property
    def winner(self):
        """The surviving entity, or None if the fight isn't over (or ended in a draw)."""
        a_alive = self.a.hp.current > 0
        b_alive = self.b.hp.current > 0
        if a_alive and not b_alive:
            return self.a
        if b_alive and not a_alive:
            return self.b
        return None

    def is_ready(self, entity):
        """Whether `entity` has no action in flight and can start a new one now."""
        return self._busy_until[entity] <= self.tick_count

    def start_action(self, entity, action):
        """Start `action` for `entity` right now, if `entity` is free to act."""
        if entity not in (self.a, self.b):
            raise ValueError(f"{entity!r} is not part of this encounter")
        if action.actor is not entity:
            raise ValueError("action.actor must be the entity starting it")
        if self.is_over:
            raise ValueError("encounter is already over")
        if not self.is_ready(entity):
            raise ValueError(f"{entity!r} is still busy until tick {self._busy_until[entity]}")

        self._pending_action[entity] = action
        self._busy_until[entity] = self.tick_count + action.duration
        self.log.append(LogEntry(self.tick_count, "start", entity, action))

    def tick(self):
        """Advance the encounter's clock by exactly one tick.

        Resolves (applies and clears) any pending action whose duration has
        now elapsed. Returns the list of actions resolved on this tick.
        """
        self.tick_count += 1
        resolved = []
        for entity in (self.a, self.b):
            action = self._pending_action[entity]
            if action is not None and self._busy_until[entity] <= self.tick_count:
                action.apply()
                self._pending_action[entity] = None
                self.log.append(LogEntry(self.tick_count, "resolve", entity, action))
                resolved.append(action)
        return resolved
