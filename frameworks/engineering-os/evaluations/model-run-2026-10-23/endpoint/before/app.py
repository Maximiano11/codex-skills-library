from http.server import BaseHTTPRequestHandler

ITEMS = [{"id": 1, "name": "demo"}]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
        else:
            self.send_response(404); self.end_headers()

    def log_message(self, *args):
        pass
