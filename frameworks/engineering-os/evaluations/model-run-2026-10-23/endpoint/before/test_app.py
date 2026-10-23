import unittest

class Baseline(unittest.TestCase):
    def test_import(self):
        from app import Handler
        self.assertTrue(callable(Handler))
