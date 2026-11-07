"""HTTP framing regressions; loopback only and no model/provider calls."""

import http.client
import json
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import server


class QuietHandler(server.Handler):
    def log_message(self, *_args):
        pass


class ResponseFraming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection(*self.httpd.server_address, timeout=3)
        try:
            conn.request(method, path, body=body, headers=headers or {})
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            conn.close()

    def test_early_rejection_has_complete_framed_body(self):
        # The unknown route rejects before consuming the submitted body. Clients
        # must not rely on a clean EOF to determine where its JSON response ends.
        for _ in range(10):
            status, headers, body = self.request(
                "POST", "/api/unknown-framing-test", b'{"unused":true}',
                {"Content-Type": "application/json"},
            )
            self.assertEqual(status, 404)
            self.assertEqual(int(headers["Content-Length"]), len(body))
            self.assertEqual(json.loads(body), {"error": "Nicht gefunden"})

    def test_utf8_error_length_counts_bytes(self):
        status, headers, body = self.request(
            "POST", "/api/generate", b"[]",
            {"Origin": "http://localhost:8787", "Content-Type": "application/json"},
        )
        self.assertEqual(status, 400)
        self.assertEqual(json.loads(body), {"error": "Ungültiges JSON"})
        self.assertEqual(int(headers["Content-Length"]), len(body))
        self.assertGreater(len(body), len(body.decode("utf-8")))


if __name__ == "__main__":
    unittest.main()
