import unittest

from group import Group
from human import Human
from quest import Quest, QuestStatus


class QuestAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.provider = Human("Elder")
        self.alice = Human("Alice")
        self.bob = Human("Bob")
        self.carol = Human("Carol")

    def test_single_acceptor_quest_rejects_a_second_acceptor(self):
        q = Quest("Clear the well", provider=self.provider)
        q.accept(self.alice)
        with self.assertRaises(ValueError):
            q.accept(self.bob)

    def test_entity_cannot_accept_twice(self):
        q = Quest("Clear the well", provider=self.provider)
        q.accept(self.alice)
        with self.assertRaises(ValueError):
            q.accept(self.alice)

    def test_multi_acceptor_quest_enforces_max(self):
        q = Quest("Bounty: rats", provider=self.provider, allow_multiple=True, max_acceptors=2)
        q.accept(self.alice)
        q.accept(self.bob)
        with self.assertRaises(ValueError):
            q.accept(self.carol)

    def test_group_accept_after_individual_moves_acceptance_over(self):
        q = Quest("Slay the goblin king", provider=self.provider, allow_multiple=True, max_acceptors=3)
        q.accept(self.alice)
        group = Group([self.alice, self.bob])
        q.accept(group)

        self.assertIs(q.accepted_by(self.alice), group)
        self.assertIs(q.accepted_by(self.bob), group)
        self.assertEqual(len(q._acceptors), 1)

    def test_individual_accept_while_covered_by_group_is_rejected(self):
        q = Quest("Slay the goblin king", provider=self.provider, allow_multiple=True, max_acceptors=3)
        group = Group([self.alice, self.bob])
        q.accept(group)
        with self.assertRaises(ValueError):
            q.accept(self.bob)

    def test_leave_group_keeps_quest_individually_when_slot_free(self):
        q = Quest("Escort", provider=self.provider, allow_multiple=True, max_acceptors=2)
        group = Group([self.alice, self.bob])
        q.accept(group)

        q.leave_group(group, self.bob)
        self.assertIs(q.accepted_by(self.bob), self.bob)
        self.assertIn(q, self.bob.quests)

    def test_leave_group_grants_quest_even_without_prior_individual_acceptance(self):
        # bob never held this quest individually - the group formed and
        # accepted it together - yet leaving should still hand it to him.
        q = Quest("Escort", provider=self.provider, allow_multiple=True, max_acceptors=2)
        group = Group([self.alice, self.bob])
        q.accept(group)
        q.leave_group(group, self.bob)
        self.assertIs(q.accepted_by(self.bob), self.bob)

    def test_leave_group_loses_quest_when_no_slot_free(self):
        q = Quest("Two-person escort", provider=self.provider, allow_multiple=True, max_acceptors=2)
        group = Group([self.alice, self.bob])
        q.accept(group)
        q.accept(self.carol)

        q.leave_group(group, self.alice)
        self.assertIsNone(q.accepted_by(self.alice))
        self.assertNotIn(q, self.alice.quests)

    def test_beings_quests_field_tracks_holdings(self):
        q = Quest("Deliver the letter", provider=self.provider)
        self.assertNotIn(q, self.alice.quests)
        q.accept(self.alice)
        self.assertIn(q, self.alice.quests)


class QuestStatusTests(unittest.TestCase):
    def setUp(self):
        self.provider = Human("Elder")
        self.alice = Human("Alice")
        self.bob = Human("Bob")

    def test_starts_open(self):
        q = Quest("Slay the goblin", provider=self.provider)
        self.assertIs(q.status, QuestStatus.OPEN)

    def test_single_acceptor_quest_becomes_taken_once_accepted(self):
        q = Quest("Slay the goblin", provider=self.provider)
        q.accept(self.alice)
        self.assertIs(q.status, QuestStatus.TAKEN)

    def test_multi_acceptor_quest_stays_open_until_full(self):
        q = Quest("Bounty: rats", provider=self.provider, allow_multiple=True, max_acceptors=2)
        q.accept(self.alice)
        self.assertIs(q.status, QuestStatus.OPEN)
        q.accept(self.bob)
        self.assertIs(q.status, QuestStatus.TAKEN)

    def test_complete_is_terminal(self):
        q = Quest("Slay the goblin", provider=self.provider)
        q.accept(self.alice)
        q.complete()
        self.assertIs(q.status, QuestStatus.COMPLETED)
        self.assertTrue(q.is_resolved)
        with self.assertRaises(ValueError):
            q.accept(self.bob)
        with self.assertRaises(ValueError):
            q.fail()

    def test_fail_after_acceptance(self):
        q = Quest("Deliver goods", provider=self.provider)
        q.accept(self.alice)
        q.fail()
        self.assertIs(q.status, QuestStatus.FAILED)

    def test_expire_requires_no_acceptors(self):
        q = Quest("Never taken", provider=self.provider)
        q.expire()
        self.assertIs(q.status, QuestStatus.EXPIRED)

        q2 = Quest("Taken then abandoned", provider=self.provider)
        q2.accept(self.alice)
        with self.assertRaises(ValueError):
            q2.expire()


if __name__ == "__main__":
    unittest.main()
