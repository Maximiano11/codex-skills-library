import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import HTTPServer
from app import Handler, ITEMS

class EndpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path):
        connection = HTTPConnection(*self.server.server_address, timeout=3)
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            return response.status, response.getheader("Content-Type"), response.read()
        finally:
            connection.close()

    def test_items_contract(self):
        status, content_type, body = self.request("/items")
        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(json.loads(body), ITEMS)

    def test_items_uses_constant(self):
        ITEMS.append({"id": 2, "name": "isolated"})
        try:
            self.assertEqual(json.loads(self.request("/items")[2]), ITEMS)
        finally:
            ITEMS.pop()

    def test_health_preserved(self):
        status, _, body = self.request("/health")
        self.assertEqual((status, body), (200, b"ok"))

    def test_unknown_route(self):
        self.assertEqual(self.request("/unknown")[0], 404)

class Baseline(unittest.TestCase):
    def test_import(self):
        from app import Handler
        self.assertTrue(callable(Handler))
