import unittest

from entities.human import Human
from entities.inventory import Inventory
from entities.slime import Slime
from items.slime_core import SlimeCore


class InventoryTests(unittest.TestCase):
    def test_add_contains_len_iter(self):
        inv = Inventory()
        core = SlimeCore()
        inv.add(core)
        self.assertIn(core, inv)
        self.assertEqual(len(inv), 1)
        self.assertEqual(list(inv), [core])

    def test_remove(self):
        core = SlimeCore()
        inv = Inventory([core])
        inv.remove(core)
        self.assertNotIn(core, inv)


class BeingInventoryTests(unittest.TestCase):
    def test_inventory_is_opt_in(self):
        with_inv = Human("Alice", has_inventory=True)
        without_inv = Human("Bob")
        self.assertIsInstance(with_inv.inventory, Inventory)
        self.assertIsNone(without_inv.inventory)

    def test_pick_up_requires_inventory(self):
        bob = Human("Bob")
        with self.assertRaises(ValueError):
            bob.pick_up(SlimeCore())

    def test_pick_up_adds_to_inventory(self):
        alice = Human("Alice", has_inventory=True)
        core = SlimeCore()
        alice.pick_up(core)
        self.assertIn(core, alice.inventory)

    def test_loot_moves_drops_into_inventory_and_empties_them(self):
        alice = Human("Alice", has_inventory=True)
        core = SlimeCore()
        slime = Slime("Ooze", drops=[core])

        looted = alice.loot(slime)
        self.assertEqual(looted, [core])
        self.assertIn(core, alice.inventory)
        self.assertEqual(slime.drops, [])

    def test_loot_requires_an_inventory(self):
        # A slime without an inventory can still carry drops but can't loot.
        looter = Slime("Blob")
        victim = Slime("Ooze", drops=[SlimeCore()])
        self.assertIsNone(looter.inventory)
        with self.assertRaises(ValueError):
            looter.loot(victim)


if __name__ == "__main__":
    unittest.main()
