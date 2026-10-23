import unittest
from checkout import checkout

class TotalTest(unittest.TestCase):
    def test_total(self):
        self.assertEqual(checkout([{"unit_cents":125,"quantity":2}]),{"total_cents":250})
