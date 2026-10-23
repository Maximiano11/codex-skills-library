import unittest
from app import health

class Health(unittest.TestCase):
    def test_health(self):
        self.assertEqual(health(),"ok")
