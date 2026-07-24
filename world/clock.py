"""Clock: the global, ever-advancing measure of in-game time.

Time is not owned by any one encounter or system — a single `Clock` is the
shared source of truth that everything reads from and that advances the
same way for everyone. `advance()` moves it forward by exactly one tick;
it never jumps ahead to "the next interesting moment". Encounters (and, in
future, anything else that cares about timing) just read `current_tick`
and schedule against it, so two systems reading/acting against the clock
at the same moment stay consistent without having to coordinate — which is
what makes concurrent fights and eventual multiplayer tractable.
"""


class Clock:
    def __init__(self, start=0):
        self.current_tick = start

    def advance(self):
        """Move time forward by exactly one tick; return the new current tick."""
        self.current_tick += 1
        return self.current_tick

    def __repr__(self):
        return f"Clock(tick={self.current_tick})"
