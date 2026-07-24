import unittest

from items.item import Item
from items.slime_core import SlimeCore


class ItemTests(unittest.TestCase):
    def test_item_has_name(self):
        self.assertEqual(Item("gold").name, "gold")

    def test_slime_core_is_an_item_named_slime_core(self):
        core = SlimeCore()
        self.assertIsInstance(core, Item)
        self.assertEqual(core.name, "slime core")


if __name__ == "__main__":
    unittest.main()
