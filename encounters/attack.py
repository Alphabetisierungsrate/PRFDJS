"""Attack: the first Action - a fixed-duration hit against the target's HP."""

from encounters.action import Action


class Attack(Action):
    duration = 10

    def apply(self):
        damage = max(0, self.actor.base_attack - self.target.base_armor)
        self.target.hp.add(-damage)
