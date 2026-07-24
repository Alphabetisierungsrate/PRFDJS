"""Action: something an entity does that takes time to resolve.

An Action bundles the actor and its target with how long it takes (in
ticks) before its effect actually happens. `apply()` is that effect;
`Encounter` calls it once `duration` ticks have passed since the action
started, not before.
"""


class Action:
    duration = 0

    def __init__(self, actor, target):
        self.actor = actor
        self.target = target

    def apply(self):
        raise NotImplementedError

    def __repr__(self):
        return f"{type(self).__name__}(actor={self.actor!r}, target={self.target!r})"
