#!/usr/bin/env python3
"""
Tests fuer die Bezahlschranke (shopify_credits.py und ihre Einbindung in server.py).

Es werden keine echten API-Aufrufe gemacht: urllib wird durch Attrappen ersetzt, die Shopify
(Token-Endpunkt, Bestellsuche, Zaehler mit compareDigest) und die KI-Anbieter nachbilden. Shopify wird
ueber den Opener des Moduls (credits._OPENER, folgt keiner Weiterleitung) aufgerufen, die KI-Anbieter
ueber urllib.request.urlopen.
Ausfuehren (vom Repo-Root):

    python3 -m unittest discover -s tests -p "test_*.py" -v

Wichtig: Diese Tests belegen die Logik gegen eine Nachbildung von Shopify. Sie ersetzen keinen
Probelauf mit einer echten Testbestellung.
"""

import http.client
import http.server
import io
import json
import os
import re
import subprocess
import sys
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from contextlib import nullcontext
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import server  # noqa: E402
import shopify_credits as credits  # noqa: E402
from test_synthesis import (  # noqa: E402
    SECRET_ANTHROPIC,
    SECRET_OPENAI,
    FakeNetwork,
    FakeResponse,
    http_error,
)

SHOP = "test-shop.myshopify.com"
VERSION = "2026-07"
CODE = "XPAV284CT"
ORDER_ID = "gid://shopify/Order/1001"
STATIC_TOKEN = "dummy-shopify-secret-token-111"
CLIENT_ID = "dummy-client-id-222"
CLIENT_SECRET = "dummy-shopify-client-secret-333"
ISSUED_TOKEN = "dummy-issued-secret-token-444"
SECRETS = (STATIC_TOKEN, CLIENT_SECRET, ISSUED_TOKEN, SECRET_OPENAI, SECRET_ANTHROPIC)


class RawResponse:
    def __init__(self, body: bytes):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class BrokenBodyResponse(RawResponse):
    """Verbindung bricht mitten in der Antwort ab (urllib wirft dann IncompleteRead, kein OSError)."""

    def __init__(self, error):
        super().__init__(b"")
        self._error = error

    def read(self):
        raise self._error


def http_error_body(code, payload):
    return urllib.error.HTTPError("https://example.invalid", code, "boom", {}, io.BytesIO(json.dumps(payload).encode("utf-8")))


class FakeShopify:
    """Bildet die benoetigten Teile von Shopify nach: Token-Endpunkt und GraphQL-Admin-API.

    Der Zaehler (Metafeld) verhaelt sich wie bei Shopify mit compareDigest: Schreiben klappt nur,
    wenn der mitgesendete Digest zum gespeicherten Wert passt; compareDigest=None heisst
    "darf noch nicht existieren".
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.orders = {}
        self.calls = []
        self.valid_tokens = {STATIC_TOKEN}
        self.token_requests = 0
        self.next_token = ISSUED_TOKEN
        self.token_lifetime = 86399
        self.ignore_filter = False
        self.graphql_errors = None
        self.fail = {}
        self.before_write = None
        self.set_errors = None
        self.digest_seq = 0
        self.fail_after = {}  # wie fail, aber NACH der Verarbeitung: die Aenderung ist angekommen, die Antwort geht verloren
        self.more_items = False  # Bestellung hat mehr Positionen, als die Abfrage liefert
        self.omit_page_info = False

    def _digest(self):
        self.digest_seq += 1
        return f"digest-{self.digest_seq}"

    def add_order(self, code=CODE, order_id=ORDER_ID, status="PAID", cancelled=False, test=False,
                  items=(("PT-LAUF", 5),), used=None):
        order = {"id": order_id, "code": code, "status": status, "cancelled": cancelled, "test": test,
                 "items": list(items), "metafield": None}
        if used is not None:
            order["metafield"] = {"value": str(used), "digest": self._digest()}
        self.orders[order_id] = order
        return order

    def used(self, order_id=ORDER_ID):
        mf = self.orders[order_id]["metafield"]
        return None if mf is None else mf["value"]

    def ops(self):
        return [c["op"] for c in self.calls]

    def calls_for(self, op):
        return [c for c in self.calls if c["op"] == op]

    def __call__(self, req, timeout=None):
        url = req.full_url
        if url == f"https://{SHOP}/admin/oauth/access_token":
            return self._token(req)
        if url == f"https://{SHOP}/admin/api/{VERSION}/graphql.json":
            return self._graphql(req)
        raise AssertionError(f"unerwartete URL: {url}")

    @staticmethod
    def _maybe_fail(hook):
        if hook is None:
            return None
        result = hook() if callable(hook) else hook
        if isinstance(result, BaseException):
            raise result
        return result

    def _token(self, req):
        headers = {k.lower(): v for k, v in req.header_items()}
        form = {k: v[0] for k, v in urllib.parse.parse_qs(req.data.decode("utf-8")).items()}
        with self.lock:
            self.token_requests += 1
            self.calls.append({"op": "token", "headers": headers, "form": form})
        early = self._maybe_fail(self.fail.get("token"))
        if early is not None:
            return early
        assert headers.get("content-type") == "application/x-www-form-urlencoded"
        if (form.get("grant_type"), form.get("client_id"), form.get("client_secret")) != ("client_credentials", CLIENT_ID, CLIENT_SECRET):
            raise http_error_body(400, {"error": "invalid_client"})
        with self.lock:
            self.valid_tokens.add(self.next_token)
        return FakeResponse({"access_token": self.next_token, "scope": "read_orders,write_orders", "expires_in": self.token_lifetime})

    def _graphql(self, req):
        headers = {k.lower(): v for k, v in req.header_items()}
        body = json.loads(req.data.decode("utf-8"))
        op = re.search(r"(?:query|mutation)\s+(\w+)", body["query"]).group(1)
        with self.lock:
            self.calls.append({"op": op, "headers": headers, "vars": body["variables"]})
        early = self._maybe_fail(self.fail.get(op))
        if early is not None:
            return early
        if headers.get("x-shopify-access-token") not in self.valid_tokens:
            raise http_error(401)
        if self.graphql_errors is not None:
            return FakeResponse({"errors": self.graphql_errors})
        response = FakeResponse(getattr(self, "_op_" + op)(body["variables"]))
        late = self._maybe_fail(self.fail_after.get(op))
        return late if late is not None else response

    def _node(self, order):
        mf = order["metafield"]
        return {
            "id": order["id"],
            "confirmationNumber": order["code"],
            "displayFinancialStatus": order["status"],
            "cancelledAt": "2026-10-01T10:00:00Z" if order["cancelled"] else None,
            "test": order["test"],
            "lineItems": {
                **({} if self.omit_page_info else {"pageInfo": {"hasNextPage": self.more_items}}),
                "nodes": [{"sku": sku, "currentQuantity": qty} for sku, qty in order["items"]],
            },
            "metafield": None if mf is None else {"value": mf["value"], "compareDigest": mf["digest"]},
        }

    def _op_PromptoratorOrderByConfirmation(self, variables):
        match = re.fullmatch(r"confirmation_number:([A-Z0-9]+)", variables["search"])
        assert match, f"unzulaessige Suchsyntax gesendet: {variables['search']!r}"
        with self.lock:
            if self.ignore_filter:
                found = list(self.orders.values())
            else:
                found = [o for o in self.orders.values() if o["code"] == match.group(1)]
            return {"data": {"orders": {"nodes": [self._node(o) for o in found[:2]]}}}

    def _op_PromptoratorRunsUsed(self, variables):
        with self.lock:
            order = self.orders.get(variables["id"])
            if order is None:
                return {"data": {"order": None}}
            mf = order["metafield"]
            return {"data": {"order": {"id": order["id"], "metafield": None if mf is None else {"value": mf["value"], "compareDigest": mf["digest"]}}}}

    def _op_PromptoratorSetRunsUsed(self, variables):
        entry = variables["metafields"][0]
        assert entry["namespace"] == "prompterator" and entry["key"] == "runs_used"
        assert entry["type"] == "number_integer" and re.fullmatch(r"\d+", entry["value"])
        assert "compareDigest" in entry, "compareDigest muss immer mitgesendet werden (auch als null)"
        with self.lock:
            order = self.orders[entry["ownerId"]]
            if self.before_write:
                self.before_write(order)
            if self.set_errors is not None:
                return {"data": {"metafieldsSet": {"metafields": [], "userErrors": self.set_errors}}}
            existing = order["metafield"]
            digest = entry["compareDigest"]
            stale = (existing is not None) if digest is None else (existing is None or existing["digest"] != digest)
            if stale:
                return {"data": {"metafieldsSet": {"metafields": [], "userErrors": [
                    {"field": ["metafields", "0"], "message": "stale", "code": "STALE_OBJECT"}]}}}
            order["metafield"] = {"value": entry["value"], "digest": self._digest()}
            return {"data": {"metafieldsSet": {"metafields": [
                {"key": "runs_used", "value": entry["value"], "compareDigest": order["metafield"]["digest"]}], "userErrors": []}}}


class CreditsCase(unittest.TestCase):
    """Gemeinsame Einrichtung: Bezahlschranke EIN, Shopify-Attrappe, Logausgabe eingefangen."""

    use_static_token = True

    def setUp(self):
        self.shop = FakeShopify()
        self.out = io.StringIO()
        patches = [
            mock.patch("sys.stdout", self.out),
            mock.patch.object(credits, "PAYMENT_REQUIRED", True),
            mock.patch.object(credits, "SHOPIFY_SHOP_DOMAIN", SHOP),
            mock.patch.object(credits, "SHOPIFY_ADMIN_TOKEN", STATIC_TOKEN if self.use_static_token else ""),
            mock.patch.object(credits, "SHOPIFY_CLIENT_ID", "" if self.use_static_token else CLIENT_ID),
            mock.patch.object(credits, "SHOPIFY_CLIENT_SECRET", "" if self.use_static_token else CLIENT_SECRET),
            mock.patch.object(credits, "SHOPIFY_API_VERSION", VERSION),
            mock.patch.object(credits, "RUN_SKUS", {"pt-lauf": 1, "pt-10er": 10}),
            mock.patch.object(credits, "SHOPIFY_ACCEPT_TEST_ORDERS", False),
            mock.patch.object(credits, "SHOPIFY_BUY_URL", "https://shop.example/products/prompterator"),
            mock.patch.object(credits._OPENER, "open", self.shop),
            mock.patch.object(credits, "RELEASE_RETRY_DELAY_SECONDS", 0),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        credits._drop_token()
        if not self.use_static_token:
            self.shop.valid_tokens = set()
        self.shop.add_order()

    def assertNoSecretsLogged(self):
        logged = self.out.getvalue()
        for secret in SECRETS + (CODE,):
            self.assertNotIn(secret, logged)


class NormalizeCode(unittest.TestCase):
    def test_accepts_the_usual_spellings(self):
        for raw in ("XPAV284CT", "xpav284ct", " xpav-284 ct ", "#XPAV284CT", "XPAV 284CT"):
            self.assertEqual(credits.normalize_code(raw), "XPAV284CT", raw)

    def test_missing_code(self):
        for raw in (None, "", "   ", "#", 123, ["XPAV284CT"], {"a": 1}):
            with self.assertRaises(credits.InvalidCode) as ctx:
                credits.normalize_code(raw)
            self.assertEqual(ctx.exception.reason, "zugangscode_fehlt", repr(raw))

    def test_rejects_anything_that_could_change_the_search(self):
        for raw in ("AB*", "ABC:DEF123", 'ABC"123456', "ABC123456'", "ABC\\123456", "ABC123456;", "ÄÖÜ123456",
                    "ABC", "A" * 17, "A" * 65, "ABC_123456", "ABC.123456"):
            with self.assertRaises(credits.InvalidCode, msg=raw) as ctx:
                credits.normalize_code(raw)
            self.assertEqual(ctx.exception.reason, "zugangscode_ungueltig", raw)

    def test_whitespace_is_removed_so_operators_cannot_survive(self):
        # "OR" wird Teil des Codes statt Suchoperator; Shopify findet dann schlicht nichts.
        self.assertEqual(credits.normalize_code("XPAV284CT OR 1"), "XPAV284CTOR1")


class ConfigHelpers(unittest.TestCase):
    def test_shop_domain_only_accepts_myshopify_hosts(self):
        ok = credits._normalize_shop_domain
        self.assertEqual(ok("my-shop"), "my-shop.myshopify.com")
        self.assertEqual(ok("My-Shop.myshopify.com"), "my-shop.myshopify.com")
        for bad in ("", "evil.com", "my-shop.myshopify.com.evil.com", "https://my-shop.myshopify.com",
                    "my-shop.myshopify.com/path", "-bad.myshopify.com", "a b.myshopify.com", "my-shop.myshopify.de"):
            self.assertEqual(ok(bad), "", bad)

    def test_run_skus_parsing_is_all_or_nothing(self):
        parse = credits._parse_run_skus
        self.assertEqual(parse("PT-LAUF=1"), {"pt-lauf": 1})
        self.assertEqual(parse("PT-LAUF=1, PT-10ER=10"), {"pt-lauf": 1, "pt-10er": 10})
        for bad in ("", "A", "=5", "A=0", "A=x", "A=-1", "A=1,B=oops", "A=100001", "A=1.5", "A=\u0663", "A=\u00b2", "A=\uff11"):
            self.assertEqual(parse(bad), {}, bad)  # auch Ziffern anderer Schriften gelten nicht

    def test_integer_settings_fall_back_to_the_default_instead_of_crashing(self):
        """Ein Tippfehler in einer optionalen Einstellung darf den Start nicht verhindern (auch nicht bei ausgeschalteter Schranke)."""
        for raw, expected in (("", 15), ("abc", 15), ("0", 15), ("-5", 15), ("601", 15), ("1.5", 15), ("\u0663", 15),
                              ("\u00b2", 15), ("1e3", 15), ("30", 30), (" 30 ", 30), ("1", 1), ("600", 600)):
            with mock.patch.dict(credits.os.environ, {"DUMMY_INT": raw}):
                self.assertEqual(credits._env_int("DUMMY_INT", 15), expected, repr(raw))
        with mock.patch.dict(credits.os.environ, clear=False):
            credits.os.environ.pop("DUMMY_INT", None)
            self.assertEqual(credits._env_int("DUMMY_INT", 15), 15)

    def test_timeout_default_is_sane(self):
        self.assertEqual(credits.SHOPIFY_TIMEOUT_SECONDS, 15)

    def test_buy_url_accepts_only_https(self):
        for url, expected in (("https://shop.example/p", "https://shop.example/p"), ("HTTPS://shop.example/p", "https://shop.example/p"),
                              ("Https://shop.example/p", "https://shop.example/p"), ("http://shop.example/p", None),
                              ("javascript:alert(1)", None), ("data:text/html,x", None), ("", None),
                              ("https://shop.example/a b", None), ("https://", None)):
            with mock.patch.object(credits, "SHOPIFY_BUY_URL", url):
                self.assertEqual(credits.buy_url(), expected, url)

    def test_off_by_default_and_reports_nothing(self):
        with mock.patch.object(credits, "PAYMENT_REQUIRED", False), \
                mock.patch.object(credits, "SHOPIFY_BUY_URL", "https://shop.example/p"):
            self.assertEqual(credits.public_info(), {"payment_required": False, "payment_ready": False, "buy_url": None})
            self.assertEqual(credits.startup_report(), [])
            self.assertFalse(credits.is_ready())

    def test_default_environment_leaves_the_gate_off(self):
        # Reiner Modulstand ohne Patches: Wer nichts setzt, bekommt das bisherige Verhalten.
        self.assertFalse(credits.PAYMENT_REQUIRED)

    def test_payment_switch_is_fail_closed_in_a_fresh_process(self):
        """Die echte Import-Konfiguration pruefen, nicht bloss ein bereits geparstes Flag patchen."""
        code = """
import json
import server
import shopify_credits as credits
print(json.dumps({"status": server.public_status(), "problems": credits.config_problems(),
                  "report": credits.startup_report()}))
"""
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("SHOPIFY_", "OPENAI_", "ANTHROPIC_", "PAYMENT_"))}
        env.update({"OPENAI_API_KEY": SECRET_OPENAI, "ANTHROPIC_API_KEY": SECRET_ANTHROPIC,
                    "GENERATE_ENABLED": "true", "SYNTHESIS_ENABLED": "true",
                    "SHOPIFY_SHOP_DOMAIN": SHOP, "SHOPIFY_ADMIN_TOKEN": STATIC_TOKEN,
                    "SHOPIFY_RUN_SKUS": "PT-LAUF=1"})
        cases = [(None, False, False), ("", False, False), ("  ", False, False),
                 ("false", False, False), (" FALSE ", False, False),
                 ("true", True, True), (" True ", True, True)]
        cases += [(typo, True, False) for typo in ("yes", "1", "ja", "on", "tru", "ture")]
        for raw, required, ready in cases:
            with self.subTest(raw=raw):
                child_env = dict(env)
                if raw is not None:
                    child_env["PAYMENT_REQUIRED"] = raw
                result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=child_env,
                                        capture_output=True, text=True, check=True, timeout=15)
                data = json.loads(result.stdout)
                self.assertEqual(data["status"]["payment_required"], required)
                self.assertEqual(data["status"]["payment_ready"], ready)
                self.assertEqual(data["status"]["generate_enabled"], not required or ready)
                if required and not ready:
                    self.assertTrue(any("PAYMENT_REQUIRED" in p for p in data["problems"]))
                    self.assertIn("Generator bleibt gesperrt", " ".join(data["report"]))
                else:
                    self.assertEqual(data["problems"], [])

    def test_readiness_needs_every_part(self):
        base = dict(PAYMENT_REQUIRED=True, SHOPIFY_SHOP_DOMAIN=SHOP, SHOPIFY_ADMIN_TOKEN=STATIC_TOKEN,
                    SHOPIFY_CLIENT_ID="", SHOPIFY_CLIENT_SECRET="", RUN_SKUS={"a": 1}, SHOPIFY_API_VERSION=VERSION)

        def ready(**override):
            values = {**base, **override}
            with mock.patch.multiple(credits, **values):
                return credits.is_ready()

        self.assertTrue(ready())
        self.assertTrue(ready(SHOPIFY_ADMIN_TOKEN="", SHOPIFY_CLIENT_ID=CLIENT_ID, SHOPIFY_CLIENT_SECRET=CLIENT_SECRET))
        self.assertFalse(ready(SHOPIFY_SHOP_DOMAIN=""))
        self.assertFalse(ready(SHOPIFY_ADMIN_TOKEN=""))
        self.assertFalse(ready(SHOPIFY_ADMIN_TOKEN="", SHOPIFY_CLIENT_ID=CLIENT_ID))
        self.assertFalse(ready(RUN_SKUS={}))
        self.assertFalse(ready(SHOPIFY_API_VERSION="latest; drop"))
        self.assertFalse(ready(PAYMENT_REQUIRED=False))

    def test_startup_report_names_problems_but_never_values(self):
        with mock.patch.multiple(credits, PAYMENT_REQUIRED=True, SHOPIFY_SHOP_DOMAIN="", SHOPIFY_ADMIN_TOKEN=STATIC_TOKEN,
                                 SHOPIFY_CLIENT_ID="", SHOPIFY_CLIENT_SECRET=CLIENT_SECRET, RUN_SKUS={}):
            text = " ".join(credits.startup_report())
        self.assertIn("SHOPIFY_SHOP_DOMAIN", text)
        self.assertIn("SHOPIFY_RUN_SKUS", text)
        self.assertNotIn(STATIC_TOKEN, text)
        self.assertNotIn(CLIENT_SECRET, text)


class RedirectSafety(unittest.TestCase):
    """Das Zugriffstoken darf nie an einen anderen Host gehen, auch nicht ueber eine Weiterleitung."""

    def test_opener_refuses_to_follow_redirects_and_never_forwards_the_token(self):
        seen = {"second": []}

        class Second(http.server.BaseHTTPRequestHandler):
            def do_GET(self):  # urllib macht aus POST + 302 ein GET und behaelt die uebrigen Header
                seen["second"].append(dict(self.headers))
                self.send_response(200)
                self.end_headers()

            do_POST = do_GET

            def log_message(self, *args):
                pass

        second = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Second)

        class First(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                self.send_response(302)
                self.send_header("Location", f"http://127.0.0.1:{second.server_address[1]}/stolen")
                self.end_headers()

            def log_message(self, *args):
                pass

        first = http.server.ThreadingHTTPServer(("127.0.0.1", 0), First)
        threads = [threading.Thread(target=s.serve_forever, daemon=True) for s in (first, second)]
        [t.start() for t in threads]
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{first.server_address[1]}/", data=b"{}", method="POST",
                                         headers={"X-Shopify-Access-Token": STATIC_TOKEN})
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                credits._OPENER.open(req, timeout=5)
            self.assertEqual(ctx.exception.code, 302)
        finally:
            for s in (first, second):
                s.shutdown()
                s.server_close()
        self.assertEqual(seen["second"], [])
        self.assertTrue(any(isinstance(h, credits._NoRedirect) for h in credits._OPENER.handlers))

    def test_redirect_responses_count_as_unavailable_without_a_second_request(self):
        shop = FakeShopify()
        shop.fail["PromptoratorOrderByConfirmation"] = urllib.error.HTTPError("https://x.invalid", 307, "Temporary Redirect", {}, io.BytesIO(b""))
        out = io.StringIO()
        with mock.patch("sys.stdout", out), mock.patch.multiple(
                credits, PAYMENT_REQUIRED=True, SHOPIFY_SHOP_DOMAIN=SHOP, SHOPIFY_ADMIN_TOKEN=STATIC_TOKEN, SHOPIFY_CLIENT_ID="",
                SHOPIFY_CLIENT_SECRET="", SHOPIFY_API_VERSION=VERSION, RUN_SKUS={"pt-lauf": 1}), \
                mock.patch.object(credits._OPENER, "open", shop):
            shop.add_order()
            with self.assertRaises(credits.CreditsUnavailable) as ctx:
                credits.reserve_run(CODE)
        self.assertFalse(ctx.exception.maybe_applied)  # eine Weiterleitung bedeutet: nicht ausgefuehrt
        self.assertEqual(len(shop.calls), 1)
        self.assertNotIn(STATIC_TOKEN, out.getvalue())


class LookupAndStatus(CreditsCase):
    def test_paid_order_gives_balance(self):
        balance = credits.check_balance(CODE)
        self.assertEqual((balance.granted, balance.used, balance.remaining), (5, 0, 5))
        self.assertEqual(balance.order_id, ORDER_ID)

    def test_request_shape(self):
        credits.check_balance(" xpav-284ct ")
        call = self.shop.calls[0]
        self.assertEqual(call["op"], "PromptoratorOrderByConfirmation")
        self.assertEqual(call["vars"], {"search": "confirmation_number:XPAV284CT"})
        self.assertEqual(call["headers"]["x-shopify-access-token"], STATIC_TOKEN)
        self.assertEqual(call["headers"]["content-type"], "application/json")

    def test_unknown_code(self):
        with self.assertRaises(credits.InvalidCode) as ctx:
            credits.check_balance("ZZZZ99999")
        self.assertEqual(ctx.exception.reason, "zugangscode_ungueltig")

    def test_shopify_ignoring_the_filter_cannot_unlock_foreign_orders(self):
        """Gibt Shopify die Suchbedingung nicht weiter, kommen beliebige Bestellungen zurueck.
        Ohne exakten Vergleich der Bestaetigungsnummer wuerde jeder Code irgendeine Bestellung oeffnen."""
        self.shop.orders.clear()
        self.shop.add_order(code="AAAA11111", order_id="gid://shopify/Order/1")
        self.shop.add_order(code="BBBB22222", order_id="gid://shopify/Order/2")
        self.shop.ignore_filter = True
        with self.assertRaises(credits.InvalidCode) as ctx:
            credits.reserve_run("CCCC33333")
        self.assertEqual(ctx.exception.reason, "zugangscode_ungueltig")
        self.assertEqual(self.shop.ops(), ["PromptoratorOrderByConfirmation"])  # nichts geschrieben

    def test_ignored_filter_still_finds_the_right_order_only(self):
        self.shop.add_order(code="AAAA11111", order_id="gid://shopify/Order/1", items=(("PT-LAUF", 99),))
        self.shop.ignore_filter = True
        balance = credits.check_balance(CODE)
        self.assertEqual((balance.order_id, balance.granted), (ORDER_ID, 5))

    def test_ambiguous_confirmation_number_is_refused(self):
        self.shop.add_order(order_id="gid://shopify/Order/2002")  # gleiche Nummer, andere Bestellung
        with self.assertRaises(credits.InvalidCode) as ctx:
            credits.reserve_run(CODE)
        self.assertEqual(ctx.exception.reason, "zugangscode_nicht_eindeutig")
        self.assertEqual(self.shop.ops(), ["PromptoratorOrderByConfirmation"])

    def test_unpaid_and_cancelled_orders(self):
        cases = [("PENDING", False, "nicht_bezahlt"), ("AUTHORIZED", False, "nicht_bezahlt"),
                 ("PARTIALLY_PAID", False, "nicht_bezahlt"), ("REFUNDED", False, "storniert"),
                 ("VOIDED", False, "storniert"), ("EXPIRED", False, "storniert"), ("PAID", True, "storniert")]
        for status, cancelled, reason in cases:
            self.shop.orders[ORDER_ID]["status"] = status
            self.shop.orders[ORDER_ID]["cancelled"] = cancelled
            with self.assertRaises(credits.OrderNotPaid, msg=f"{status}/{cancelled}") as ctx:
                credits.reserve_run(CODE)
            self.assertEqual(ctx.exception.reason, reason, f"{status}/{cancelled}")
        self.assertNotIn("PromptoratorSetRunsUsed", self.shop.ops())

    def test_partially_refunded_uses_the_remaining_quantity(self):
        self.shop.orders[ORDER_ID]["status"] = "PARTIALLY_REFUNDED"
        self.shop.orders[ORDER_ID]["items"] = [("PT-LAUF", 3)]  # currentQuantity nach Erstattung
        self.assertEqual(credits.check_balance(CODE).granted, 3)

    def test_test_orders_are_refused_unless_allowed(self):
        self.shop.orders[ORDER_ID]["test"] = True
        with self.assertRaises(credits.OrderNotPaid) as ctx:
            credits.reserve_run(CODE)
        self.assertEqual(ctx.exception.reason, "testbestellung")
        with mock.patch.object(credits, "SHOPIFY_ACCEPT_TEST_ORDERS", True):
            self.assertEqual(credits.reserve_run(CODE).used, 1)

    def test_runs_come_from_the_configured_skus_only(self):
        self.shop.orders[ORDER_ID]["items"] = [("pt-10er", 2), ("PT-LAUF", 1), ("ANDERES-PRODUKT", 7), (None, 3)]
        self.assertEqual(credits.check_balance(CODE).granted, 21)

    def test_order_without_runs(self):
        self.shop.orders[ORDER_ID]["items"] = [("ANDERES-PRODUKT", 2)]
        with self.assertRaises(credits.NoRunsLeft) as ctx:
            credits.check_balance(CODE)
        self.assertEqual(ctx.exception.message, credits.MSG_NO_RUNS_IN_ORDER)
        with self.assertRaises(credits.NoRunsLeft):
            credits.reserve_run(CODE)
        self.assertNotIn("PromptoratorSetRunsUsed", self.shop.ops())

    def test_fully_refunded_line_item_gives_no_runs(self):
        self.shop.orders[ORDER_ID]["status"] = "PARTIALLY_REFUNDED"
        self.shop.orders[ORDER_ID]["items"] = [("PT-LAUF", 0)]
        with self.assertRaises(credits.NoRunsLeft):
            credits.reserve_run(CODE)

    def test_exhausted_order_still_reports_its_balance(self):
        self.shop.orders[ORDER_ID]["metafield"] = {"value": "5", "digest": "d"}
        balance = credits.check_balance(CODE)
        self.assertEqual((balance.granted, balance.used, balance.remaining), (5, 5, 0))

    def test_order_with_more_line_items_than_were_fetched_is_refused(self):
        self.shop.more_items = True
        for call in (credits.check_balance, credits.reserve_run):
            with self.assertRaises(credits.InvalidCode) as ctx:
                call(CODE)
            self.assertEqual(ctx.exception.reason, "bestellung_zu_gross")
            self.assertEqual(ctx.exception.message, credits.MSG_TOO_MANY_ITEMS)
        self.assertNotIn("PromptoratorSetRunsUsed", self.shop.ops())

    def test_response_without_page_info_fails_closed(self):
        self.shop.omit_page_info = True
        for call in (credits.check_balance, credits.reserve_run):
            with self.assertRaises(credits.CreditsUnavailable):
                call(CODE)
        self.assertNotIn("PromptoratorSetRunsUsed", self.shop.ops())

    def test_query_stays_small_and_asks_whether_more_line_items_exist(self):
        self.assertIn("orders(first: 2", credits.ORDER_QUERY)
        self.assertIn("lineItems(first: 25)", credits.ORDER_QUERY)
        self.assertIn("hasNextPage", credits.ORDER_QUERY)

    def test_readiness_is_checked_before_the_code_format(self):
        with mock.patch.object(credits, "RUN_SKUS", {}):
            for call in (credits.check_balance, credits.reserve_run):
                for raw in (None, "", "kaputt*", CODE):
                    with self.assertRaises(credits.CreditsUnavailable, msg=repr(raw)) as ctx:
                        call(raw)
                    self.assertEqual(ctx.exception.reason, "bezahlung_nicht_eingerichtet")
        self.assertEqual(self.shop.calls, [])

    def test_not_ready_configuration_fails_closed_without_network(self):
        with mock.patch.object(credits, "RUN_SKUS", {}):
            for call in (credits.check_balance, credits.reserve_run):
                with self.assertRaises(credits.CreditsUnavailable) as ctx:
                    call(CODE)
                self.assertEqual(ctx.exception.reason, "bezahlung_nicht_eingerichtet")
        self.assertEqual(self.shop.calls, [])


class Counter(CreditsCase):
    def test_reserve_counts_up_and_persists_in_shopify(self):
        first = credits.reserve_run(CODE)
        self.assertEqual((first.granted, first.used), (5, 1))
        self.assertEqual(self.shop.used(), "1")
        second = credits.reserve_run(CODE)
        self.assertEqual(second.used, 2)
        self.assertEqual(self.shop.used(), "2")
        writes = self.shop.calls_for("PromptoratorSetRunsUsed")
        self.assertIsNone(writes[0]["vars"]["metafields"][0]["compareDigest"])  # erstes Mal: abgesichertes Anlegen
        self.assertIsNotNone(writes[1]["vars"]["metafields"][0]["compareDigest"])
        self.assertEqual(writes[0]["vars"]["metafields"][0]["ownerId"], ORDER_ID)

    def test_counter_survives_a_restart(self):
        credits.reserve_run(CODE)
        credits._drop_token()  # neuer Prozess: kein Speicher ausser Shopify
        self.assertEqual(credits.check_balance(CODE).used, 1)

    def test_last_run_is_the_last_run(self):
        for _ in range(5):
            credits.reserve_run(CODE)
        with self.assertRaises(credits.NoRunsLeft) as ctx:
            credits.reserve_run(CODE)
        self.assertEqual(ctx.exception.message, credits.MSG_EXHAUSTED)
        self.assertEqual(self.shop.used(), "5")
        self.assertEqual(len(self.shop.calls_for("PromptoratorSetRunsUsed")), 5)

    def test_release_gives_the_run_back(self):
        credits.reserve_run(CODE)
        credits.reserve_run(CODE)
        self.assertEqual(credits.release_run(ORDER_ID), 1)
        self.assertEqual(self.shop.used(), "1")
        self.assertEqual(credits.check_balance(CODE).remaining, 4)

    def test_release_never_goes_below_zero(self):
        credits.reserve_run(CODE)
        self.assertEqual(credits.release_run(ORDER_ID), 0)
        self.assertEqual(credits.release_run(ORDER_ID), 0)
        self.assertEqual(self.shop.used(), "0")

    def test_release_with_bad_or_unknown_id(self):
        self.assertIsNone(credits.release_run("gid://shopify/Order/999"))
        for bad in (None, "", "1001", "gid://shopify/Product/1", "gid://shopify/Order/1; drop"):
            self.assertIsNone(credits.release_run(bad), repr(bad))

    def test_release_reports_failure_instead_of_pretending(self):
        credits.reserve_run(CODE)
        self.shop.fail["PromptoratorRunsUsed"] = http_error(500)
        self.assertIsNone(credits.release_run(ORDER_ID))
        self.assertEqual(self.shop.used(), "1")

    def test_conflicting_writer_is_retried_and_nothing_is_lost(self):
        """Ein zweiter Prozess zaehlt zwischen unserem Lesen und Schreiben hoch."""
        credits.reserve_run(CODE)  # Stand: 1
        fired = []

        def other_writer(order):
            if not fired:
                fired.append(True)
                order["metafield"] = {"value": "2", "digest": self.shop._digest()}

        self.shop.before_write = other_writer
        result = credits.reserve_run(CODE)
        self.assertEqual(result.used, 3)  # der fremde Lauf (2) und unserer (3) sind beide verbucht
        self.assertEqual(self.shop.used(), "3")
        self.assertEqual(self.shop.ops()[-4:], ["PromptoratorOrderByConfirmation", "PromptoratorSetRunsUsed",
                                                "PromptoratorOrderByConfirmation", "PromptoratorSetRunsUsed"])

    def test_first_use_race_does_not_double_create(self):
        fired = []

        def other_creator(order):
            if not fired:
                fired.append(True)
                order["metafield"] = {"value": "1", "digest": self.shop._digest()}

        self.shop.before_write = other_creator
        self.assertEqual(credits.reserve_run(CODE).used, 2)
        self.assertEqual(self.shop.used(), "2")

    def test_permanent_conflict_gives_up_without_overwriting(self):
        def always_changing(order):
            current = int(order["metafield"]["value"]) if order["metafield"] else 0
            order["metafield"] = {"value": str(current + 1), "digest": self.shop._digest()}

        self.shop.before_write = always_changing
        with self.assertRaises(credits.CreditsUnavailable):
            credits.reserve_run(CODE)
        self.assertEqual(len(self.shop.calls_for("PromptoratorSetRunsUsed")), credits.CAS_ATTEMPTS)
        # Der Zaehler enthaelt nur die Schreibvorgaenge des "anderen" Prozesses, keinen eigenen.
        self.assertEqual(self.shop.used(), str(credits.CAS_ATTEMPTS))

    def test_parallel_requests_never_oversell(self):
        outcomes = []
        gate = threading.Barrier(12)

        def worker():
            gate.wait()
            try:
                credits.reserve_run(CODE)
                outcomes.append("ok")
            except credits.NoRunsLeft:
                outcomes.append("leer")
            except credits.CreditsUnavailable:
                outcomes.append("unavailable")

        threads = [threading.Thread(target=worker) for _ in range(12)]
        [t.start() for t in threads]
        [t.join(timeout=20) for t in threads]
        self.assertEqual(outcomes.count("ok"), 5)
        self.assertEqual(outcomes.count("leer"), 7)
        self.assertEqual(self.shop.used(), "5")

    def test_compare_digest_alone_prevents_overselling_even_without_the_process_lock(self):
        """Zweite Instanz oder Neustart ueberlappend: die Prozess-Sperre hilft dann nicht, der Digest schon."""
        outcomes = []
        gate = threading.Barrier(12)

        def worker():
            gate.wait()
            try:
                credits.reserve_run(CODE)
                outcomes.append("ok")
            except credits.NoRunsLeft:
                outcomes.append("leer")
            except credits.CreditsUnavailable:
                outcomes.append("unavailable")

        with mock.patch.object(credits, "_stripe", lambda key: nullcontext()):
            threads = [threading.Thread(target=worker) for _ in range(12)]
            [t.start() for t in threads]
            [t.join(timeout=20) for t in threads]
        self.assertEqual(len(outcomes), 12)
        self.assertLessEqual(outcomes.count("ok"), 5)
        self.assertEqual(self.shop.used(), str(outcomes.count("ok")))  # kein verlorenes Hochzaehlen

    def test_unreadable_counter_fails_closed(self):
        self.shop.orders[ORDER_ID]["metafield"] = {"value": "abc", "digest": "d"}
        with self.assertRaises(credits.CreditsUnavailable):
            credits.reserve_run(CODE)
        self.assertNotIn("PromptoratorSetRunsUsed", self.shop.ops())

    def test_negative_counter_is_treated_as_zero(self):
        self.shop.orders[ORDER_ID]["metafield"] = {"value": "-3", "digest": "d"}
        self.assertEqual(credits.check_balance(CODE).remaining, 5)

    def test_unexpected_user_errors_fail_closed(self):
        self.shop.set_errors = [{"field": ["metafields", "0"], "message": "x", "code": "INVALID_VALUE"}]
        with self.assertRaises(credits.CreditsUnavailable):
            credits.reserve_run(CODE)
        self.assertIsNone(self.shop.orders[ORDER_ID]["metafield"])
        self.assertIn("INVALID_VALUE", self.out.getvalue())
        self.assertNoSecretsLogged()


class ShopifyFailures(CreditsCase):
    def test_every_kind_of_outage_becomes_unavailable_and_never_unlocks(self):
        failures = [
            http_error(500), http_error(502), http_error(429), http_error(401), http_error(403),
            urllib.error.URLError("boom"), TimeoutError(), ConnectionResetError(), OSError("x"),
            RawResponse(b"<html>Bad gateway</html>"), RawResponse(b"[]"), RawResponse(b'{"data": null}'),
            RawResponse(b"\xff\xfe"), FakeResponse({"unexpected": True}),
            BrokenBodyResponse(http.client.IncompleteRead(b"partial")),
            BrokenBodyResponse(http.client.BadStatusLine("x")),
            http.client.RemoteDisconnected("closed"),
        ]
        for failure in failures:
            self.shop.fail["PromptoratorOrderByConfirmation"] = failure
            for call in (credits.check_balance, credits.reserve_run):
                with self.assertRaises(credits.CreditsUnavailable, msg=repr(failure)) as ctx:
                    call(CODE)
                self.assertEqual(ctx.exception.reason, "bezahlung_nicht_erreichbar")
                self.assertEqual(ctx.exception.http_status, 503)
                for secret in SECRETS + (CODE,):
                    self.assertNotIn(secret, ctx.exception.message)
        self.assertNotIn("PromptoratorSetRunsUsed", self.shop.ops())
        self.assertNoSecretsLogged()

    def test_graphql_errors_are_unavailable_and_log_only_the_code(self):
        for code in ("THROTTLED", "ACCESS_DENIED", "INTERNAL_SERVER_ERROR"):
            self.shop.graphql_errors = [{"message": f"secret detail {CODE}", "extensions": {"code": code}}]
            with self.assertRaises(credits.CreditsUnavailable):
                credits.reserve_run(CODE)
            self.assertIn(code, self.out.getvalue())
        self.shop.graphql_errors = [{"message": "no code"}, "weird"]
        with self.assertRaises(credits.CreditsUnavailable):
            credits.reserve_run(CODE)
        self.assertNoSecretsLogged()
        self.assertNotIn("secret detail", self.out.getvalue())

    def test_static_token_is_not_retried_on_401(self):
        self.shop.valid_tokens = set()
        with self.assertRaises(credits.CreditsUnavailable):
            credits.check_balance(CODE)
        self.assertEqual(len(self.shop.calls), 1)
        self.assertEqual(self.shop.token_requests, 0)

    def test_write_failure_after_reading_does_not_count_a_run(self):
        self.shop.fail["PromptoratorSetRunsUsed"] = http_error(500)
        with self.assertRaises(credits.CreditsUnavailable):
            credits.reserve_run(CODE)
        self.assertIsNone(self.shop.orders[ORDER_ID]["metafield"])


class UnclearBookings(CreditsCase):
    """Ein gemeinsamer Zaehler kann nach verlorener Antwort keine einzelne Buchung beweisen."""

    def test_applied_write_with_lost_response_stays_unclear(self):
        self.shop.fail_after["PromptoratorSetRunsUsed"] = TimeoutError()
        with self.assertRaises(credits.CreditsUnavailable) as ctx:
            credits.reserve_run(CODE)
        self.assertEqual(ctx.exception.reason, "buchung_unklar")
        self.assertEqual(self.shop.used(), "1")
        self.assertEqual(len(self.shop.calls_for("PromptoratorSetRunsUsed")), 1)  # nicht ein zweites Mal gebucht
        self.assertNotIn("PromptoratorRunsUsed", self.shop.ops())

    def test_write_without_a_reliable_response_never_claims_nothing_was_booked(self):
        failures = [TimeoutError(), http_error(500), http_error(502), urllib.error.URLError("boom"),
                    ConnectionResetError(), RawResponse(b"<html>Bad gateway</html>"), FakeResponse({"data": None}),
                    BrokenBodyResponse(http.client.IncompleteRead(b"partial")),
                    FakeResponse({"errors": [{"message": "x", "extensions": {"code": "INTERNAL_SERVER_ERROR"}}]})]
        for failure in failures:
            self.shop.orders[ORDER_ID]["metafield"] = None
            self.shop.calls.clear()
            self.shop.fail["PromptoratorSetRunsUsed"] = failure
            with self.assertRaises(credits.CreditsUnavailable, msg=repr(failure)) as ctx:
                credits.reserve_run(CODE)
            self.assertEqual(ctx.exception.reason, "buchung_unklar", repr(failure))
            self.assertNotIn("nichts abgebucht", ctx.exception.message)
            self.assertTrue(ctx.exception.maybe_applied)
            self.assertNotIn("PromptoratorRunsUsed", self.shop.ops(), repr(failure))
            self.assertIsNone(self.shop.orders[ORDER_ID]["metafield"])

    def test_another_process_booking_cannot_be_claimed_after_our_timeout(self):
        """A liest 0; nur B schreibt 0->1; As fehlgeschlagener Write darf keinen Lauf freigeben."""
        def other_process_then_timeout():
            # B hatte denselben alten Stand und schreibt mit dessen Digest. As eigentlicher Write
            # wird durch den Timeout vor der Verarbeitung ersetzt.
            variables = self.shop.calls_for("PromptoratorSetRunsUsed")[-1]["vars"]
            self.shop._op_PromptoratorSetRunsUsed(variables)
            return TimeoutError()

        self.shop.fail["PromptoratorSetRunsUsed"] = other_process_then_timeout
        with self.assertRaises(credits.CreditsUnavailable) as ctx:
            credits.reserve_run(CODE)
        self.assertEqual(ctx.exception.reason, "buchung_unklar")
        self.assertEqual(self.shop.used(), "1")  # nur die fremde Buchung
        self.assertEqual(len(self.shop.calls_for("PromptoratorSetRunsUsed")), 1)
        self.assertNoSecretsLogged()

    def test_write_can_arrive_after_the_unclear_response(self):
        """Ein zunaechst unveraenderter Stand ist kein Beweis, dass der Write nie mehr ankommt."""
        self.shop.fail["PromptoratorSetRunsUsed"] = TimeoutError()
        with self.assertRaises(credits.CreditsUnavailable) as ctx:
            credits.reserve_run(CODE)
        delayed_variables = self.shop.calls_for("PromptoratorSetRunsUsed")[-1]["vars"]
        self.assertIsNone(self.shop.used())
        self.assertEqual(ctx.exception.reason, "buchung_unklar")
        self.assertNotIn("nichts abgebucht", ctx.exception.message)
        self.shop._op_PromptoratorSetRunsUsed(delayed_variables)  # der urspruengliche Write kommt spaeter an
        self.assertEqual(self.shop.used(), "1")

    def test_rejected_writes_are_not_rechecked(self):
        """4xx, Drosselung und fachliche Ablehnung bedeuten: nicht ausgefuehrt. Da gibt es nichts nachzulesen."""
        rejected = [http_error(401), http_error(403), http_error(404), http_error(429),
                    FakeResponse({"errors": [{"message": "x", "extensions": {"code": "THROTTLED"}}]}),
                    FakeResponse({"errors": [{"message": "x", "extensions": {"code": "ACCESS_DENIED"}}]})]
        for failure in rejected:
            self.shop.calls.clear()
            self.shop.fail["PromptoratorSetRunsUsed"] = failure
            with self.assertRaises(credits.CreditsUnavailable, msg=repr(failure)) as ctx:
                credits.reserve_run(CODE)
            self.assertIn("nichts abgebucht", ctx.exception.message)
            self.assertNotIn("PromptoratorRunsUsed", self.shop.ops(), repr(failure))
        self.shop.fail.clear()
        self.shop.set_errors = [{"field": ["metafields", "0"], "message": "x", "code": "INVALID_VALUE"}]
        self.shop.calls.clear()
        with self.assertRaises(credits.CreditsUnavailable):
            credits.reserve_run(CODE)
        self.assertNotIn("PromptoratorRunsUsed", self.shop.ops())

    def test_a_later_request_observes_the_previously_unclear_booking(self):
        self.shop.fail_after["PromptoratorSetRunsUsed"] = TimeoutError()
        with self.assertRaises(credits.CreditsUnavailable):
            credits.reserve_run(CODE)  # Stand: 1 (angekommen), kein freigegebener Modellaufruf
        self.shop.fail_after.clear()
        self.assertEqual(credits.reserve_run(CODE).used, 2)
        self.assertEqual(self.shop.used(), "2")


class ReleaseHardening(CreditsCase):
    """Nur sicher nicht ausgefuehrte Gutschriften duerfen wiederholt werden."""

    def setUp(self):
        super().setUp()
        credits.reserve_run(CODE)
        credits.reserve_run(CODE)  # Stand: 2
        self.shop.calls.clear()

    def test_release_retries_once_after_a_failed_read(self):
        outcomes = iter([urllib.error.URLError("boom")])
        self.shop.fail["PromptoratorRunsUsed"] = lambda: next(outcomes, None)
        self.assertEqual(credits.release_run(ORDER_ID), 1)
        self.assertEqual(self.shop.used(), "1")
        self.assertEqual(len(self.shop.calls_for("PromptoratorRunsUsed")), 2)

    def test_release_gives_up_after_the_configured_attempts(self):
        self.shop.fail["PromptoratorRunsUsed"] = http_error(500)
        self.assertIsNone(credits.release_run(ORDER_ID))
        self.assertEqual(len(self.shop.calls_for("PromptoratorRunsUsed")), credits.RELEASE_ATTEMPTS)
        self.assertEqual(self.shop.used(), "2")
        self.assertIn("Gutschrift", self.out.getvalue())
        self.assertNoSecretsLogged()

    def test_release_waits_between_attempts(self):
        self.shop.fail["PromptoratorRunsUsed"] = http_error(500)
        with mock.patch.object(credits, "RELEASE_RETRY_DELAY_SECONDS", 0.25), mock.patch.object(credits.time, "sleep") as sleep:
            credits.release_run(ORDER_ID)
        sleep.assert_called_once_with(0.25)

    def test_release_timeout_is_not_retried_even_if_the_write_arrives_late(self):
        outcomes = iter([TimeoutError()])
        self.shop.fail["PromptoratorSetRunsUsed"] = lambda: next(outcomes, None)
        self.assertIsNone(credits.release_run(ORDER_ID))
        self.assertEqual(self.shop.used(), "2")
        self.assertEqual(len(self.shop.calls_for("PromptoratorSetRunsUsed")), 1)
        delayed_variables = self.shop.calls_for("PromptoratorSetRunsUsed")[0]["vars"]
        self.shop._op_PromptoratorSetRunsUsed(delayed_variables)
        self.assertEqual(self.shop.used(), "1")

    def test_rejected_release_write_can_be_retried(self):
        outcomes = iter([http_error(429)])
        self.shop.fail["PromptoratorSetRunsUsed"] = lambda: next(outcomes, None)
        self.assertEqual(credits.release_run(ORDER_ID), 1)
        self.assertEqual(self.shop.used(), "1")
        self.assertEqual(len(self.shop.calls_for("PromptoratorSetRunsUsed")), 2)

    def test_release_with_lost_response_is_not_applied_twice(self):
        self.shop.fail_after["PromptoratorSetRunsUsed"] = TimeoutError()
        self.assertIsNone(credits.release_run(ORDER_ID))
        self.assertEqual(self.shop.used(), "1")
        self.assertEqual(len(self.shop.calls_for("PromptoratorSetRunsUsed")), 1)

    def test_new_booking_cannot_hide_a_release_and_cause_a_second_refund(self):
        """A schreibt 2->1, B reserviert 1->2, As Antwort geht verloren: niemals erneut 2->1."""
        fired = []

        def another_reservation_before_lost_response():
            if fired:
                return None
            fired.append(True)
            mf = self.shop.orders[ORDER_ID]["metafield"]
            self.assertEqual(mf["value"], "1")  # Rueckbuchung ist bereits angekommen
            entry = dict(self.shop.calls_for("PromptoratorSetRunsUsed")[-1]["vars"]["metafields"][0])
            entry.update(value="2", compareDigest=mf["digest"])
            result = self.shop._op_PromptoratorSetRunsUsed({"metafields": [entry]})
            self.assertEqual(result["data"]["metafieldsSet"]["userErrors"], [])
            return TimeoutError()

        self.shop.fail_after["PromptoratorSetRunsUsed"] = another_reservation_before_lost_response
        self.assertIsNone(credits.release_run(ORDER_ID))
        self.assertEqual(len(self.shop.calls_for("PromptoratorSetRunsUsed")), 1)
        self.assertEqual(self.shop.used(), "2")  # 2 - genau eine Rueckbuchung + neue Reservierung
        self.assertEqual(len(self.shop.calls_for("PromptoratorRunsUsed")), 1)

    def test_release_never_raises_on_odd_responses(self):
        odd = [
            FakeResponse({"data": {"order": {"id": ORDER_ID, "metafield": "kaputt"}}}),
            FakeResponse({"data": {"order": {"id": ORDER_ID, "metafield": 7}}}),
            FakeResponse({"data": {"order": {"id": ORDER_ID, "metafield": {"value": None}}}}),
            FakeResponse({"data": {"order": []}}),
            FakeResponse({"data": []}),
        ]
        for response in odd:
            self.shop.fail["PromptoratorRunsUsed"] = response
            self.assertIsNone(credits.release_run(ORDER_ID), repr(response))
        self.assertEqual(self.shop.used(), "2")

    def test_release_after_an_unexpected_write_response_does_not_retry(self):
        self.shop.fail_after["PromptoratorSetRunsUsed"] = FakeResponse({"data": {"metafieldsSet": ["x"]}})
        self.assertIsNone(credits.release_run(ORDER_ID))
        self.assertEqual(len(self.shop.calls_for("PromptoratorSetRunsUsed")), 1)
        self.assertEqual(self.shop.used(), "1")
        self.assertIn("unerwarteter Fehler", self.out.getvalue())


class ClientCredentialsToken(CreditsCase):
    use_static_token = False

    def test_token_is_requested_with_client_credentials_and_cached(self):
        credits.check_balance(CODE)
        credits.check_balance(CODE)
        self.assertEqual(self.shop.token_requests, 1)
        token_call = self.shop.calls_for("token")[0]
        self.assertEqual(token_call["form"], {"grant_type": "client_credentials", "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET})
        for call in self.shop.calls_for("PromptoratorOrderByConfirmation"):
            self.assertEqual(call["headers"]["x-shopify-access-token"], ISSUED_TOKEN)
        self.assertNoSecretsLogged()

    def test_token_is_renewed_before_it_expires(self):
        now = [1_000_000.0]
        with mock.patch.object(credits.time, "time", lambda: now[0]):
            credits.check_balance(CODE)
            self.shop.next_token = "dummy-issued-secret-token-555"
            now[0] += 86399 - 600  # noch mehr als 5 Minuten Restlaufzeit
            credits.check_balance(CODE)
            self.assertEqual(self.shop.token_requests, 1)
            now[0] += 400  # unter der Sicherheitsmarge
            credits.check_balance(CODE)
        self.assertEqual(self.shop.token_requests, 2)
        self.assertEqual(self.shop.calls_for("PromptoratorOrderByConfirmation")[-1]["headers"]["x-shopify-access-token"],
                         "dummy-issued-secret-token-555")

    def test_revoked_token_is_replaced_once(self):
        credits.check_balance(CODE)
        self.shop.valid_tokens.clear()  # Shopify hat das Token verworfen
        self.shop.next_token = "dummy-issued-secret-token-666"
        self.assertEqual(credits.check_balance(CODE).granted, 5)
        self.assertEqual(self.shop.token_requests, 2)

    def test_token_failures_are_unavailable_and_logged_without_secrets(self):
        self.shop.fail["token"] = http_error_body(400, {"error": "shop_not_permitted", "error_description": f"leak {CLIENT_SECRET}"})
        with self.assertRaises(credits.CreditsUnavailable):
            credits.check_balance(CODE)
        self.assertIn("shop_not_permitted", self.out.getvalue())
        self.assertNoSecretsLogged()
        for failure in (urllib.error.URLError("x"), TimeoutError(), RawResponse(b"nope"), FakeResponse({}),
                        FakeResponse({"access_token": ""}), FakeResponse({"access_token": 5}),
                        BrokenBodyResponse(http.client.IncompleteRead(b"partial"))):
            self.shop.fail["token"] = failure
            with self.assertRaises(credits.CreditsUnavailable, msg=repr(failure)):
                credits.check_balance(CODE)
        self.assertNoSecretsLogged()

    def test_wrong_credentials_are_rejected_by_shopify(self):
        with mock.patch.object(credits, "SHOPIFY_CLIENT_SECRET", "dummy-wrong-secret-000"):
            with self.assertRaises(credits.CreditsUnavailable):
                credits.check_balance(CODE)
        self.assertNotIn("dummy-wrong-secret-000", self.out.getvalue())

    def test_missing_expiry_falls_back_to_a_short_lifetime(self):
        self.shop.fail["token"] = lambda: FakeResponse({"access_token": ISSUED_TOKEN})
        self.shop.valid_tokens.add(ISSUED_TOKEN)
        now = [5_000.0]
        with mock.patch.object(credits.time, "time", lambda: now[0]):
            credits.check_balance(CODE)
            now[0] += 3600 - 100
            credits.check_balance(CODE)
        self.assertEqual(self.shop.token_requests, 2)


class HttpCredits(unittest.TestCase):
    """Einbindung in den HTTP-Server: Reihenfolge der Pruefungen, Abbuchung, Rueckbuchung, Ehrlichkeit."""

    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        cls.origin = f"http://127.0.0.1:{cls.port}"
        server.ALLOWED_ORIGINS.add(cls.origin)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        server.ALLOWED_ORIGINS.discard(cls.origin)

    def setUp(self):
        self.shop = FakeShopify()
        self.net = FakeNetwork()
        self.out = io.StringIO()
        patches = [
            mock.patch("sys.stdout", self.out),
            mock.patch.object(server, "OPENAI_API_KEY", SECRET_OPENAI),
            mock.patch.object(server, "ANTHROPIC_API_KEY", SECRET_ANTHROPIC),
            mock.patch.object(server, "SYNTHESIS_ENABLED", True),
            mock.patch.object(credits, "PAYMENT_REQUIRED", True),
            mock.patch.object(credits, "SHOPIFY_SHOP_DOMAIN", SHOP),
            mock.patch.object(credits, "SHOPIFY_ADMIN_TOKEN", STATIC_TOKEN),
            mock.patch.object(credits, "SHOPIFY_CLIENT_ID", ""),
            mock.patch.object(credits, "SHOPIFY_CLIENT_SECRET", ""),
            mock.patch.object(credits, "SHOPIFY_API_VERSION", VERSION),
            mock.patch.object(credits, "RUN_SKUS", {"pt-lauf": 1}),
            mock.patch.object(credits, "SHOPIFY_ACCEPT_TEST_ORDERS", False),
            mock.patch.object(credits, "SHOPIFY_BUY_URL", "https://shop.example/products/prompterator"),
            mock.patch.object(server.urllib.request, "urlopen", self.net),
            mock.patch.object(credits._OPENER, "open", self.shop),
            mock.patch.object(credits, "RELEASE_RETRY_DELAY_SECONDS", 0),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        for store in (server.request_log, server.pdf_request_log, server.credits_request_log, server.daily_usage,
                      server.monthly_usage, server.blocked_usage, server.token_usage):
            store.clear()
        self.shop.add_order()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        data = json.dumps(body) if body is not None else None
        hdrs = {"Content-Type": "application/json"} if body is not None else {}
        hdrs.update(headers or {})
        conn.request(method, path, body=data, headers=hdrs)
        resp = conn.getresponse()
        raw = resp.read().decode("utf-8")
        conn.close()
        try:
            parsed = json.loads(raw)
        except ValueError:
            parsed = raw
        return resp.status, parsed

    def generate(self, code=CODE, raw="Wir verlieren Zeit im Wareneingang.", **extra):
        body = {"raw_input": raw, **extra}
        if code is not None:
            body["access_code"] = code
        return self.request("POST", "/api/generate", body, {"Origin": self.origin})

    def check(self, body, origin=True):
        return self.request("POST", "/api/credits", body, {"Origin": self.origin} if origin else {})

    def event(self, kind):
        return server.token_usage.get(f"{server.month_key()}|credits|{kind}", 0)

    def assertNoModelCalls(self):
        self.assertEqual(self.net.calls, [])

    # ---- Schranke aus: bisheriges Verhalten bleibt unveraendert ----

    def test_gate_off_behaves_exactly_as_before(self):
        with mock.patch.object(credits, "PAYMENT_REQUIRED", False):
            status, data = self.generate(code="egal")  # Feld wird ignoriert
            self.assertEqual(status, 200)
            self.assertNotIn("credits", data)
            self.assertEqual(self.shop.calls, [])
            status, data = self.generate(code=None)
            self.assertEqual(status, 200)
            self.assertEqual(self.check({"access_code": CODE})[0], 404)
            _, info = self.request("GET", "/api/status")
        self.assertEqual((info["payment_required"], info["payment_ready"], info["buy_url"]), (False, False, None))
        self.assertTrue(info["generate_enabled"])

    def test_credits_path_does_not_exist_when_the_gate_is_off(self):
        """Ausgeschaltet ist /api/credits ein unbekannter Pfad: dieselbe Antwort wie bei jedem anderen,
        ohne dass Body, Origin oder Content-Type geprueft werden."""
        _, reference = self.request("POST", "/api/gibt-es-nicht", {"x": 1}, {"Origin": self.origin})
        with mock.patch.object(credits, "PAYMENT_REQUIRED", False):
            attempts = [
                ({"access_code": CODE}, {"Origin": self.origin}),
                ({"access_code": CODE}, {}),
                ({"access_code": CODE}, {"Origin": "https://evil.example"}),
                ({"access_code": CODE}, {"Origin": self.origin, "Content-Type": "text/plain"}),
                ("kein-objekt", {"Origin": self.origin}),
            ]
            for body, headers in attempts:
                self.assertEqual(self.request("POST", "/api/credits", body, headers), (404, reference), repr(headers))
        self.assertEqual(self.shop.calls, [])
        self.assertEqual(server.credits_request_log, {})  # nicht einmal der Zaehler wurde beruehrt

    # ---- Status ----

    def test_status_when_on_and_ready(self):
        _, info = self.request("GET", "/api/status")
        self.assertEqual((info["payment_required"], info["payment_ready"], info["generate_enabled"]), (True, True, True))
        self.assertEqual(info["buy_url"], "https://shop.example/products/prompterator")
        blob = json.dumps(info)
        for secret in SECRETS + (SHOP,):
            self.assertNotIn(secret, blob)

    def test_status_when_on_but_not_ready_locks_the_generator(self):
        with mock.patch.object(credits, "RUN_SKUS", {}):
            _, info = self.request("GET", "/api/status")
            self.assertEqual((info["payment_required"], info["payment_ready"], info["generate_enabled"]), (True, False, False))
            status, data = self.generate()
        self.assertEqual(status, 503)
        self.assertEqual(data["reason"], "bezahlung_nicht_eingerichtet")
        self.assertNoModelCalls()
        self.assertEqual(self.shop.calls, [])

    def test_invalid_payment_switch_locks_status_and_generation_even_with_valid_credentials(self):
        with mock.patch.object(credits, "_PAYMENT_REQUIRED_VALUE", "ture"):
            _, info = self.request("GET", "/api/status")
            self.assertEqual((info["payment_required"], info["payment_ready"], info["generate_enabled"]),
                             (True, False, False))
            status, data = self.generate(code=None)
        self.assertEqual((status, data["reason"]), (503, "bezahlung_nicht_eingerichtet"))
        self.assertNoModelCalls()
        self.assertEqual(self.shop.calls, [])

    # ---- Ohne gueltigen Code keine Kosten ----

    def test_missing_and_invalid_codes_cost_nothing(self):
        for code, reason in ((None, "zugangscode_fehlt"), ("", "zugangscode_fehlt"), ("ZZZZ99999", "zugangscode_ungueltig"),
                             ("kaputt*", "zugangscode_ungueltig")):
            server.request_log.clear()
            status, data = self.generate(code=code)
            self.assertEqual(status, 402, code)
            self.assertEqual(data["reason"], reason, code)
        self.assertNoModelCalls()
        self.assertNotIn("PromptoratorSetRunsUsed", self.shop.ops())
        self.assertEqual(server.daily_usage[server.day_key()], 0)

    def test_unpaid_order_costs_nothing(self):
        self.shop.orders[ORDER_ID]["status"] = "PENDING"
        status, data = self.generate()
        self.assertEqual((status, data["reason"]), (402, "nicht_bezahlt"))
        self.assertNoModelCalls()

    def test_invalid_requests_do_not_consume_a_run(self):
        for body in ({"raw_input": "", "access_code": CODE}, {"raw_input": "x" * (server.MAX_INPUT_CHARS + 1), "access_code": CODE},
                     {"raw_input": "x", "access_code": CODE, "artifact_type": "nope"}, {"raw_input": "x", "access_code": CODE, "evil": 1}):
            server.request_log.clear()
            status, _ = self.request("POST", "/api/generate", body, {"Origin": self.origin})
            self.assertIn(status, (400, 413))
        self.assertEqual(self.shop.calls, [])

    def test_ring2_limits_are_checked_before_any_booking(self):
        server.daily_usage[server.day_key()] = server.DAILY_REQUEST_LIMIT
        self.assertEqual(self.generate()[0], 429)
        self.assertEqual(self.shop.calls, [])
        self.assertNoModelCalls()

    def test_rate_limit_applies_before_shopify_is_asked(self):
        for _ in range(server.RATE_LIMIT_MAX_REQUESTS):
            self.assertEqual(self.generate(code="ZZZZ99999")[0], 402)
        lookups = len(self.shop.calls)
        self.assertEqual(self.generate(code="ZZZZ99999")[0], 429)
        self.assertEqual(len(self.shop.calls), lookups)

    def test_origin_is_still_required(self):
        status, _ = self.request("POST", "/api/generate", {"raw_input": "x", "access_code": CODE})
        self.assertEqual(status, 403)
        self.assertEqual(self.shop.calls, [])

    # ---- Bezahlter Lauf ----

    def test_paid_run_is_booked_and_reported(self):
        status, data = self.generate()
        self.assertEqual(status, 200)
        self.assertEqual(data["mode"], "synthese")
        self.assertEqual(data["credits"], {"granted": 5, "used": 1, "remaining": 4, "charged": True})
        self.assertEqual(self.shop.used(), "1")
        self.assertEqual(len(self.net.calls), 3)
        self.assertEqual(self.event("charged"), 1)
        self.assertEqual(server.daily_usage[server.day_key()], 1)

    def test_runs_are_used_up_then_refused_without_model_calls(self):
        self.shop.orders[ORDER_ID]["items"] = [("PT-LAUF", 2)]
        for expected in (1, 2):
            server.request_log.clear()
            status, data = self.generate()
            self.assertEqual((status, data["credits"]["used"], data["credits"]["remaining"]), (200, expected, 2 - expected))
        calls_before = len(self.net.calls)
        server.request_log.clear()
        status, data = self.generate()
        self.assertEqual((status, data["reason"]), (402, "keine_laeufe"))
        self.assertEqual(len(self.net.calls), calls_before)
        self.assertEqual(self.shop.used(), "2")

    def test_code_is_never_echoed_or_logged(self):
        status, data = self.generate(code=" xpav-284ct ")
        self.assertEqual(status, 200)
        self.assertNotIn(CODE, json.dumps(data))
        self.generate(code="ZZZZ99999")
        self.shop.fail["PromptoratorOrderByConfirmation"] = http_error(500)
        server.request_log.clear()
        self.generate()
        logged = self.out.getvalue()
        for secret in SECRETS + (CODE, "ZZZZ99999"):
            self.assertNotIn(secret, logged)

    # ---- Rueckbuchung ----

    def test_total_failure_returns_the_run(self):
        self.net.openai = lambda body: http_error(500)
        self.net.draft = lambda body: http_error(500)
        status, data = self.generate()
        self.assertEqual(status, 502)
        self.assertEqual(self.shop.used(), "0")
        self.assertNotIn("Gutschrift", data["error"])
        self.assertIn("nichts abgebucht", data["error"])
        self.assertEqual(self.event("released"), 1)
        self.assertEqual(self.event("charged"), 0)
        self.assertEqual(server.daily_usage[server.day_key()], 0)

    def test_unconfigured_generator_never_touches_shopify(self):
        with mock.patch.object(server, "OPENAI_API_KEY", None), mock.patch.object(server, "ANTHROPIC_API_KEY", None):
            status, _ = self.generate()
        self.assertEqual(status, 503)
        self.assertEqual(self.shop.calls, [])

    def test_unexpected_crash_returns_the_run_and_says_so(self):
        with mock.patch.object(server, "generate_artifact", side_effect=RuntimeError("kaputt")):
            status, data = self.generate()
        self.assertEqual(status, 500)
        self.assertEqual(self.shop.used(), "0")
        self.assertIn("nichts abgebucht", data["error"])
        self.assertNotIn("kaputt", json.dumps(data))
        self.assertEqual(self.event("released"), 1)

    def test_unexpected_crash_with_failed_giveback_is_stated_openly(self):
        self.shop.fail["PromptoratorRunsUsed"] = http_error(500)
        with mock.patch.object(server, "generate_artifact", side_effect=RuntimeError("kaputt")):
            status, data = self.generate()
        self.assertEqual(status, 500)
        self.assertIn("Gutschrift", data["error"])
        self.assertNotIn("nichts abgebucht", data["error"])
        self.assertEqual(self.shop.used(), "1")
        self.assertEqual(self.event("release_failed"), 1)

    def test_unexpected_crash_with_the_gate_off_is_unchanged(self):
        with mock.patch.object(credits, "PAYMENT_REQUIRED", False), \
                mock.patch.object(server, "generate_artifact", side_effect=RuntimeError("kaputt")):
            status, data = self.generate(code=None)
        self.assertEqual((status, data), (500, {"error": "Interner Serverfehler. Bitte später erneut versuchen."}))
        self.assertEqual(self.shop.calls, [])

    def test_unclear_booking_is_reported_openly_and_no_model_is_called(self):
        self.shop.fail_after["PromptoratorSetRunsUsed"] = TimeoutError()  # Buchung kam an, Antwort ging verloren
        status, data = self.generate()
        self.assertEqual((status, data["reason"]), (503, "buchung_unklar"))
        self.assertNotIn("nichts abgebucht", data["error"])
        self.assertIn("Prüfen", data["error"])
        self.assertNoModelCalls()

    def test_foreign_booking_after_our_failed_write_cannot_trigger_model_calls(self):
        def other_process_then_timeout():
            variables = self.shop.calls_for("PromptoratorSetRunsUsed")[-1]["vars"]
            self.shop._op_PromptoratorSetRunsUsed(variables)  # B bucht, A erhaelt nur den Timeout
            return TimeoutError()

        self.shop.fail["PromptoratorSetRunsUsed"] = other_process_then_timeout
        status, data = self.generate()
        self.assertEqual((status, data["reason"]), (503, "buchung_unklar"))
        self.assertNotIn("nichts abgebucht", data["error"])
        self.assertEqual(self.shop.used(), "1")  # genau die Buchung des anderen Prozesses
        self.assertNoModelCalls()
        self.assertEqual(self.event("charged"), 0)

    def test_failed_giveback_is_stated_openly(self):
        self.net.openai = lambda body: http_error(500)
        self.net.draft = lambda body: http_error(500)
        self.shop.fail["PromptoratorRunsUsed"] = http_error(500)
        status, data = self.generate()
        self.assertEqual(status, 502)
        self.assertIn("Gutschrift", data["error"])
        self.assertEqual(self.shop.used(), "1")
        self.assertEqual(self.event("release_failed"), 1)

    def test_partial_result_is_not_charged_when_both_providers_are_expected(self):
        cases = {
            "claude faellt aus": dict(draft=lambda body: http_error(500)),
            "chatgpt faellt aus": dict(openai=lambda body: http_error(500)),
            "zusammenfuehrung faellt aus": dict(merge=lambda body: http_error(500)),
        }
        for name, overrides in cases.items():
            with self.subTest(name):
                server.request_log.clear()
                self.shop.orders[ORDER_ID]["metafield"] = None
                self.net = FakeNetwork(**overrides)
                with mock.patch.object(server.urllib.request, "urlopen", self.net):
                    status, data = self.generate()
                self.assertEqual(status, 200)
                self.assertNotEqual(data["mode"], "synthese")
                self.assertEqual(data["credits"], {"granted": 5, "used": 0, "remaining": 5, "charged": False})
                self.assertEqual(self.shop.used(), "0")
        self.assertEqual(self.event("released"), 3)
        self.assertEqual(self.event("degraded"), 3)  # sichtbar fuer den Betreiber: Teilausfaelle sind Gratis-Laeufe

    def test_single_provider_setup_is_charged_for_its_result(self):
        with mock.patch.object(server, "ANTHROPIC_API_KEY", None):
            status, data = self.generate()
        self.assertEqual(status, 200)
        self.assertEqual(data["mode"], "chatgpt")
        self.assertEqual(data["credits"]["charged"], True)
        self.assertEqual(self.shop.used(), "1")

    def test_partial_result_whose_giveback_fails_stays_charged_and_says_so(self):
        self.net.draft = lambda body: http_error(500)
        self.shop.fail["PromptoratorRunsUsed"] = http_error(500)
        status, data = self.generate()
        self.assertEqual(status, 200)
        self.assertEqual(data["credits"]["charged"], True)
        self.assertEqual(data["credits"].get("giveback_failed"), True)
        self.assertEqual(self.event("release_failed"), 1)

    def test_unclear_giveback_is_reported_without_a_second_refund(self):
        self.net.draft = lambda body: http_error(500)

        def lose_only_the_refund_response():
            entry = self.shop.calls_for("PromptoratorSetRunsUsed")[-1]["vars"]["metafields"][0]
            return TimeoutError() if entry["value"] == "0" else None

        self.shop.fail_after["PromptoratorSetRunsUsed"] = lose_only_the_refund_response
        status, data = self.generate()
        self.assertEqual(status, 200)
        self.assertTrue(data["credits"].get("giveback_failed"))
        self.assertEqual(self.event("release_failed"), 1)
        self.assertEqual(self.event("released"), 0)  # kein Erfolg behauptet, obwohl sie tatsaechlich ankam
        self.assertEqual(len(self.shop.calls_for("PromptoratorSetRunsUsed")), 2)  # Reservierung + ein Refund
        self.assertEqual(self.shop.used(), "0")

    # ---- Shopify nicht erreichbar ----

    def test_shopify_outage_blocks_generation_and_costs_nothing(self):
        self.shop.fail["PromptoratorOrderByConfirmation"] = http_error(500)
        status, data = self.generate()
        self.assertEqual((status, data["reason"]), (503, "bezahlung_nicht_erreichbar"))
        self.assertIn("nichts abgebucht", data["error"])
        self.assertNoModelCalls()

    # ---- /api/credits ----

    def test_credits_endpoint_reports_balance(self):
        status, data = self.check({"access_code": CODE})
        self.assertEqual(status, 200)
        self.assertEqual(data, {"valid": True, "granted": 5, "used": 0, "remaining": 5})
        self.generate()
        server.credits_request_log.clear()
        self.assertEqual(self.check({"access_code": CODE})[1]["remaining"], 4)
        self.assertEqual(self.shop.calls_for("PromptoratorSetRunsUsed")[0]["vars"]["metafields"][0]["value"], "1")

    def test_credits_endpoint_rejects_bad_input(self):
        self.assertEqual(self.check({"access_code": "ZZZZ99999"})[0], 402)
        self.assertEqual(self.check({"access_code": ""})[1]["reason"], "zugangscode_fehlt")
        self.assertEqual(self.check({})[1]["reason"], "zugangscode_fehlt")
        self.assertEqual(self.check({"access_code": CODE, "x": 1})[0], 400)
        self.assertEqual(self.check({"access_code": CODE}, origin=False)[0], 403)
        self.assertNotIn("PromptoratorSetRunsUsed", self.shop.ops())

    def test_credits_endpoint_is_rate_limited_before_shopify_is_asked(self):
        for _ in range(server.CREDITS_RATE_LIMIT_MAX_REQUESTS):
            self.assertEqual(self.check({"access_code": "ZZZZ99999"})[0], 402)
        lookups = len(self.shop.calls)
        self.assertEqual(self.check({"access_code": "ZZZZ99999"})[0], 429)
        self.assertEqual(len(self.shop.calls), lookups)

    def test_credits_endpoint_unavailable_when_shopify_is_down(self):
        self.shop.fail["PromptoratorOrderByConfirmation"] = http_error(500)
        status, data = self.check({"access_code": CODE})
        self.assertEqual((status, data["reason"]), (503, "bezahlung_nicht_erreichbar"))

    # ---- Messwerte ----

    def test_usage_shows_charged_and_released_runs(self):
        self.generate()
        self.net.draft = lambda body: http_error(500)
        server.request_log.clear()
        self.generate()
        usage = server.usage_snapshot()
        month = server.month_key()
        self.assertEqual(usage["token_usage"][f"{month}|credits|charged"], 1)
        self.assertEqual(usage["token_usage"][f"{month}|credits|released"], 1)
        self.assertEqual((usage["payment_required"], usage["payment_ready"]), (True, True))
        self.assertNotIn(STATIC_TOKEN, json.dumps(usage))


class UiWiring(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_access_code_field_and_buy_link_exist(self):
        self.assertIn('id="accessCode"', self.html)
        self.assertIn('autocomplete="off"', self.html)
        self.assertIn('id="buyLink"', self.html)
        self.assertIn("/api/credits", self.html)
        self.assertIn("access_code", self.html)

    def test_ui_drops_stale_checks_and_is_honest_after_aborted_runs(self):
        for needle in ("function dropCheck", "AbortController", "buchung_unklar", "PAY_CHECK_HINT", "function setText"):
            self.assertIn(needle, self.html, needle)

    def test_buy_link_cannot_be_abused(self):
        self.assertRegex(self.html, r'rel="noopener noreferrer"')
        self.assertIn('indexOf("https://")===0', self.html)

    def test_ui_still_uses_no_innerhtml(self):
        # Kommentare duerfen das Wort nennen; verboten ist jede Benutzung, die Text als HTML einliest.
        self.assertNotRegex(self.html, r"\.innerHTML|innerHTML\s*=|insertAdjacentHTML|document\.write|outerHTML")


if __name__ == "__main__":
    unittest.main(verbosity=2)
