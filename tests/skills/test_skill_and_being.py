import random
import unittest

from entities.being import Being
from skills.skill import Skill


class SkillAndBeingTests(unittest.TestCase):
    def test_being_acquires_individual_polynomial_per_skill(self):
        random.seed(1)
        strength = Skill("strength", degree=2, max_sum=100, max_level=10)
        alice = Being("Alice", species="human")
        bob = Being("Bob", species="human")

        alice.acquire_skill(strength)
        bob.acquire_skill(strength)

        self.assertNotEqual(
            alice._skills[strength]["coeffs"], bob._skills[strength]["coeffs"]
        )

        alice_sum = sum(alice.skill_value(strength, level) for level in range(1, 11))
        bob_sum = sum(bob.skill_value(strength, level) for level in range(1, 11))
        self.assertAlmostEqual(alice_sum, 100)
        self.assertAlmostEqual(bob_sum, 100)

    def test_acquire_skill_is_idempotent(self):
        random.seed(1)
        strength = Skill("strength", degree=2, max_sum=100, max_level=10)
        alice = Being("Alice", species="human")

        first = alice.acquire_skill(strength)
        second = alice.acquire_skill(strength)
        self.assertEqual(first, second)

    def test_skill_value_at_out_of_range_level_raises(self):
        random.seed(1)
        strength = Skill("strength", degree=2, max_sum=100, max_level=10)
        alice = Being("Alice", species="human")
        alice.acquire_skill(strength)

        with self.assertRaises(ValueError):
            alice.skill_value(strength, 11)

    def test_per_being_max_sum_and_max_level_override(self):
        random.seed(1)
        strength = Skill("strength", degree=2, max_sum=100, max_level=10)
        giant = Being("Giant", species="giant")
        giant.acquire_skill(strength, max_sum=500, max_level=20)

        giant_sum = sum(giant.skill_value(strength, level) for level in range(1, 21))
        self.assertAlmostEqual(giant_sum, 500)
        with self.assertRaises(ValueError):
            giant.skill_value(strength, 21)

    def test_skill_value_before_acquiring_raises(self):
        strength = Skill("strength", degree=2, max_sum=100, max_level=10)
        alice = Being("Alice", species="human")
        with self.assertRaises(ValueError):
            alice.skill_value(strength, 1)


if __name__ == "__main__":
    unittest.main()
