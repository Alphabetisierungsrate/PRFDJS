"""Encounter: a tick-driven fight, for now strictly 1 vs 1.

An Encounter does not own time — it reads a shared `world.Clock` (passed
in at construction). The clock advances the same way for everyone;
`advance()` on it moves time forward by exactly one tick, never jumping
ahead to "the next interesting moment". That separation is deliberate: it
means a still-free entity can have an action started for it at any tick,
independent of what the other entity is doing (including mid-wind-up of
its own action), and every encounter's log comes out in strict tick order
by construction. Because the clock is global rather than per-encounter,
several fights can run against the same tick line at once, and different
callers reading/acting against it never have to coordinate — which is what
will make concurrent encounters and eventual multiplayer tractable.

Driving a fight: advance the clock, then call `resolve_due()` on the
encounter to apply any actions that have now come due. `start_action()`
can be called for either entity whenever it's ready, independent of the
other. An action already in flight resolves at its scheduled tick even if
its actor has since died in the same resolution pass (`resolve_due()`
processes `a` then `b`) — ticks don't rewind, so two attacks due on the
same tick both land, allowing a genuine mutual-kill draw.

For now, an encounter has exactly two participants (`a`, `b`) and the only
action either can take is `Attack`.
"""

from collections import namedtuple

LogEntry = namedtuple("LogEntry", ["tick", "event", "entity", "action"])


class Encounter:
    def __init__(self, a, b, clock):
        self.a = a
        self.b = b
        self.clock = clock
        self._busy_until = {a: clock.current_tick, b: clock.current_tick}
        self._pending_action = {a: None, b: None}
        self.log = []

    def __repr__(self):
        return f"Encounter(a={self.a!r}, b={self.b!r}, tick={self.current_tick})"

    @property
    def current_tick(self):
        """The shared clock's current tick (this encounter does not own it)."""
        return self.clock.current_tick

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
        return self._busy_until[entity] <= self.current_tick

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
        self._busy_until[entity] = self.current_tick + action.duration
        self.log.append(LogEntry(self.current_tick, "start", entity, action))

    def resolve_due(self):
        """Apply and clear any pending action that has come due by the current tick.

        Call this after advancing the shared clock. Returns the list of
        actions resolved at the current tick.
        """
        resolved = []
        for entity in (self.a, self.b):
            action = self._pending_action[entity]
            if action is not None and self._busy_until[entity] <= self.current_tick:
                action.apply()
                self._pending_action[entity] = None
                self.log.append(LogEntry(self.current_tick, "resolve", entity, action))
                resolved.append(action)
        return resolved
