import unittest

from encounters.attack import Attack
from encounters.encounter import Encounter
from entities.human import Human


class EncounterTests(unittest.TestCase):
    def setUp(self):
        self.alice = Human("Alice", max_hp=100, base_attack=10, base_armor=0)
        self.bob = Human("Bob", max_hp=100, base_attack=10, base_armor=0)
        self.encounter = Encounter(self.alice, self.bob)

    def test_starts_at_tick_zero_and_both_ready(self):
        self.assertEqual(self.encounter.tick_count, 0)
        self.assertTrue(self.encounter.is_ready(self.alice))
        self.assertTrue(self.encounter.is_ready(self.bob))

    def test_opponent_of(self):
        self.assertIs(self.encounter.opponent_of(self.alice), self.bob)
        self.assertIs(self.encounter.opponent_of(self.bob), self.alice)

    def test_opponent_of_rejects_non_participant(self):
        outsider = Human("Carol")
        with self.assertRaises(ValueError):
            self.encounter.opponent_of(outsider)

    def test_start_action_rejects_non_participant(self):
        outsider = Human("Carol")
        with self.assertRaises(ValueError):
            self.encounter.start_action(outsider, Attack(outsider, self.bob))

    def test_start_action_rejects_actor_mismatch(self):
        with self.assertRaises(ValueError):
            self.encounter.start_action(self.alice, Attack(self.bob, self.alice))

    def test_attack_does_not_resolve_before_its_duration_elapses(self):
        self.encounter.start_action(self.alice, Attack(self.alice, self.bob))
        for _ in range(Attack.duration - 1):
            resolved = self.encounter.tick()
            self.assertEqual(resolved, [])
        self.assertEqual(self.bob.hp.current, 100)
        self.assertFalse(self.encounter.is_ready(self.alice))

    def test_attack_resolves_exactly_on_its_duration_tick(self):
        action = Attack(self.alice, self.bob)
        self.encounter.start_action(self.alice, action)
        for _ in range(Attack.duration - 1):
            self.encounter.tick()
        resolved = self.encounter.tick()
        self.assertEqual(resolved, [action])
        self.assertEqual(self.bob.hp.current, 90)
        self.assertTrue(self.encounter.is_ready(self.alice))

    def test_busy_entity_cannot_start_a_new_action(self):
        self.encounter.start_action(self.alice, Attack(self.alice, self.bob))
        with self.assertRaises(ValueError):
            self.encounter.start_action(self.alice, Attack(self.alice, self.bob))

    def test_entity_can_act_again_immediately_after_resolution(self):
        self.encounter.start_action(self.alice, Attack(self.alice, self.bob))
        for _ in range(Attack.duration):
            self.encounter.tick()
        # Should not raise now that the first attack has resolved.
        self.encounter.start_action(self.alice, Attack(self.alice, self.bob))

    def test_entities_act_independently_of_each_other(self):
        # Bob starts mid-wind-up of Alice's attack, unaffected by it.
        self.encounter.start_action(self.alice, Attack(self.alice, self.bob))
        self.encounter.tick()
        self.encounter.tick()
        self.encounter.start_action(self.bob, Attack(self.bob, self.alice))
        self.assertFalse(self.encounter.is_ready(self.alice))
        self.assertFalse(self.encounter.is_ready(self.bob))

    def test_is_over_and_winner(self):
        self.assertFalse(self.encounter.is_over)
        self.assertIsNone(self.encounter.winner)

        self.bob.hp.add(-self.bob.hp.current)
        self.assertTrue(self.encounter.is_over)
        self.assertIs(self.encounter.winner, self.alice)

    def test_start_action_rejects_once_encounter_is_over(self):
        self.bob.hp.add(-self.bob.hp.current)
        with self.assertRaises(ValueError):
            self.encounter.start_action(self.alice, Attack(self.alice, self.bob))

    def test_in_flight_action_still_resolves_even_if_actor_has_since_died(self):
        # Both throw a lethal hit at each other on the same tick; Alice's
        # resolves first (processing order), killing Bob - but Bob's own
        # already-in-flight attack still lands afterwards, killing Alice too.
        lethal_alice = Human("Alice", max_hp=10, base_attack=15, base_armor=0)
        lethal_bob = Human("Bob", max_hp=10, base_attack=15, base_armor=0)
        encounter = Encounter(lethal_alice, lethal_bob)

        encounter.start_action(lethal_alice, Attack(lethal_alice, lethal_bob))
        encounter.start_action(lethal_bob, Attack(lethal_bob, lethal_alice))
        for _ in range(Attack.duration):
            encounter.tick()

        self.assertEqual(lethal_bob.hp.current, 0)
        self.assertEqual(lethal_alice.hp.current, 0)
        self.assertTrue(encounter.is_over)
        self.assertIsNone(encounter.winner)


if __name__ == "__main__":
    unittest.main()
