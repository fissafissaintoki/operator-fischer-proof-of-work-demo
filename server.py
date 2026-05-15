#!/usr/bin/env python3
import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PORT = int(os.environ.get("PORT", "8787"))
HOST = os.environ.get("HOST", "0.0.0.0")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

SYSTEM_PROMPT = """
Du arbeitest als Prompterator im Operator-Fischer-Modus.

Arbeitslogik:
Rohinput -> Problemklasse -> Modus -> Artefakt -> Qualitätsprüfung -> Governance -> Wiederverwendung

Regeln:
- Antworte auf Deutsch.
- Trenne Fakten, Annahmen und Hypothesen.
- Mensch bleibt Owner, KI bleibt Werkzeug.
- Erzeuge kein loses Gelaber, sondern eine verwertbare Arbeitsstruktur.
- Gib konkrete nächste Schritte aus.
- Wenn KPI-Werte nicht gemessen sind, markiere sie als Annahmen.
"""

def call_openai(raw_input: str) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY fehlt. Bitte als Environment Variable setzen.")

    payload = {
        "model": MODEL,
        "input": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Rohinput:
{raw_input}

Aufgabe:
1. Klassifiziere die Problemklasse.
2. Wähle den passenden Modus.
3. Erzeuge einen Artefakt-Blueprint.
4. Ergänze Qualitätsprüfung und Governance-Gates.
5. Gib einen direkt nutzbaren Masterprompt aus.

Ausgabeformat:
## Problemklasse
## Modus
## Artefakt-Blueprint
## Qualitätsprüfung
## Governance
## Masterprompt
## Nächste Schritte
"""
            }
        ]
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=180) as response:
        data = json.loads(response.read().decode("utf-8"))

    chunks = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in ("output_text", "text"):
                chunks.append(content.get("text", ""))

    if chunks:
        return "\n".join(chunks).strip()

    return json.dumps(data, indent=2, ensure_ascii=False)


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: str, content_type: str = "text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_OPTIONS(self):
        self._send(204, "")

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html = Path("index.html").read_text(encoding="utf-8")
            self._send(200, html, "text/html; charset=utf-8")

        elif self.path == "/health":
            self._send(200, json.dumps({
                "status": "ok",
                "model": MODEL,
                "openai_key_set": bool(OPENAI_API_KEY)
            }), "application/json; charset=utf-8")

        else:
            self._send(404, "Not found")

    def do_POST(self):
        if self.path != "/api/generate":
            self._send(404, "Not found")
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(body)
            raw_input = payload.get("raw_input", "").strip()

            if not raw_input:
                self._send(400, json.dumps({"error": "raw_input fehlt"}), "application/json; charset=utf-8")
                return

            result = call_openai(raw_input)
            self._send(200, json.dumps({"result": result}, ensure_ascii=False), "application/json; charset=utf-8")

        except Exception as exc:
            self._send(500, json.dumps({"error": str(exc)}, ensure_ascii=False), "application/json; charset=utf-8")


if __name__ == "__main__":
    print(f"Prompterator API läuft auf http://{HOST}:{PORT}")
    print("Healthcheck:", f"http://{HOST}:{PORT}/health")
    HTTPServer((HOST, PORT), Handler).serve_forever()
