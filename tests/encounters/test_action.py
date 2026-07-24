import unittest

from encounters.action import Action
from encounters.attack import Attack
from entities.human import Human


class ActionBaseTests(unittest.TestCase):
    def test_apply_is_not_implemented(self):
        alice = Human("Alice")
        bob = Human("Bob")
        action = Action(alice, bob)
        with self.assertRaises(NotImplementedError):
            action.apply()


class AttackTests(unittest.TestCase):
    def test_deals_attack_minus_armor_damage(self):
        alice = Human("Alice", max_hp=100, base_attack=10)
        bob = Human("Bob", max_hp=100, base_armor=4)
        Attack(alice, bob).apply()
        self.assertEqual(bob.hp.current, 94)

    def test_damage_clamped_at_zero_when_armor_exceeds_attack(self):
        alice = Human("Alice", max_hp=100, base_attack=2)
        bob = Human("Bob", max_hp=100, base_armor=10)
        Attack(alice, bob).apply()
        self.assertEqual(bob.hp.current, 100)

    def test_damage_does_not_take_hp_below_zero(self):
        alice = Human("Alice", max_hp=100, base_attack=1000)
        bob = Human("Bob", max_hp=10, base_armor=0)
        Attack(alice, bob).apply()
        self.assertEqual(bob.hp.current, 0)


if __name__ == "__main__":
    unittest.main()
