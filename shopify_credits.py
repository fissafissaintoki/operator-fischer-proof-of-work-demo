#!/usr/bin/env python3
"""Bezahlschranke ueber Shopify (Standard: aus).

Eine bezahlte Shopify-Bestellung wird zu einem Guthaben an Laeufen:

  1. Kaeufer bezahlt im Shop ein Produkt, dessen SKU in SHOPIFY_RUN_SKUS steht.
  2. Kaeufer traegt die Bestaetigungsnummer der Bestellung als Zugangscode ein.
  3. Der Server fragt die Bestellung per Admin-API ab (Shopify bleibt die einzige Quelle der
     Wahrheit), zaehlt die gekauften Laeufe und bucht je Lauf einen Zaehler an der Bestellung hoch
     (Metafeld prompterator.runs_used, per compareDigest gegen gleichzeitige Zugriffe abgesichert).

Es gibt keine eigene Datenbank. Der Zaehler ueberlebt Neustarts, weil er in Shopify liegt.

Regeln:
  - Alles hier ist nur aktiv, wenn PAYMENT_REQUIRED=true gesetzt ist.
  - Token, Client-Secret und Zugangscodes werden nie geloggt, nie an den Browser gegeben und nie in
    Fehlertexte geschrieben. Geloggt werden nur Statuscodes und Fehlercodes.
  - Im Zweifel wird nichts freigeschaltet (fail closed): Shopify nicht erreichbar, Zaehler
    unlesbar, Konfiguration unvollstaendig oder mehrdeutige Treffer fuehren zu einer Ablehnung.
  - Ein Treffer zaehlt nur, wenn die Bestaetigungsnummer der gefundenen Bestellung exakt dem Code
    entspricht. Eine von Shopify stillschweigend ignorierte Suchbedingung kann so keinen fremden
    Treffer freischalten.
"""

import hmac
import http.client
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

METAFIELD_NAMESPACE = "prompterator"
METAFIELD_KEY = "runs_used"
PAID_STATUSES = {"PAID", "PARTIALLY_REFUNDED"}
CAS_ATTEMPTS = 4
RELEASE_ATTEMPTS = 2
RELEASE_RETRY_DELAY_SECONDS = 1.0
TOKEN_REFRESH_MARGIN_SECONDS = 300
MAX_CODE_INPUT_CHARS = 64

# Shopify gibt ohne Sonderfreigabe (read_all_orders) nur Bestellungen der letzten 60 Tage heraus.
# Aeltere Codes werden dann als "nicht gefunden" behandelt. Das steht in README und Uebergabe.


def _env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, "true" if default else "false").strip().lower() == "true"


def _env_int(name: str, default: int, minimum: int = 1, maximum: int = 600) -> int:
    """Ganzzahl aus der Umgebung. Ungueltige Werte ergeben den Standardwert: Ein Tippfehler in einer
    optionalen Einstellung darf den Start des Servers nicht verhindern, auch nicht bei ausgeschalteter
    Schranke."""
    raw = os.environ.get(name, "").strip()
    if raw.isascii() and raw.isdecimal() and minimum <= int(raw) <= maximum:
        return int(raw)
    return default


def _normalize_shop_domain(raw: str) -> str:
    """Akzeptiert 'shop' oder 'shop.myshopify.com'. Alles andere wird verworfen, damit das Token
    nie an einen fremden Host gesendet wird."""
    value = (raw or "").strip().lower()
    if value and "." not in value:
        value += ".myshopify.com"
    if re.fullmatch(r"[a-z0-9][a-z0-9-]{0,60}\.myshopify\.com", value):
        return value
    return ""


def _parse_run_skus(raw: str) -> dict:
    """'SKU=Laeufe,SKU2=Laeufe2' -> {'sku': n}. Ungueltige Angaben ergeben ein leeres Mapping."""
    result = {}
    for part in (raw or "").split(","):
        part = part.strip()
        if not part:
            continue
        sku, sep, runs = part.partition("=")
        sku = sku.strip().casefold()
        runs = runs.strip()
        if not sep or not sku or not (runs.isascii() and runs.isdecimal()) or not 1 <= int(runs) <= 100000:
            return {}
        result[sku] = int(runs)
    return result


PAYMENT_REQUIRED = _env_bool("PAYMENT_REQUIRED")
SHOPIFY_SHOP_DOMAIN = _normalize_shop_domain(os.environ.get("SHOPIFY_SHOP_DOMAIN", ""))
SHOPIFY_ADMIN_TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN", "").strip()
SHOPIFY_CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID", "").strip()
SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET", "").strip()
SHOPIFY_API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2026-07").strip()
RUN_SKUS = _parse_run_skus(os.environ.get("SHOPIFY_RUN_SKUS", ""))
SHOPIFY_BUY_URL = os.environ.get("SHOPIFY_BUY_URL", "").strip()
SHOPIFY_ACCEPT_TEST_ORDERS = _env_bool("SHOPIFY_ACCEPT_TEST_ORDERS")
SHOPIFY_TIMEOUT_SECONDS = _env_int("SHOPIFY_TIMEOUT_SECONDS", 15)


# ---------------------------------------------------------------------------
# Fehler. Die Texte sind fuer Kaeufer gedacht und enthalten nie interne Details.
# ---------------------------------------------------------------------------

MSG_MISSING = "Bitte den Zugangscode aus deiner Bestellbestätigung eingeben."
MSG_INVALID = "Dieser Zugangscode wurde nicht gefunden. Bitte die Bestätigungsnummer deiner Bestellung prüfen."
MSG_AMBIGUOUS = "Dieser Zugangscode ist nicht eindeutig. Bitte melde dich beim Betreiber."
MSG_UNPAID = "Die Zahlung zu dieser Bestellung ist noch nicht eingegangen."
MSG_CANCELLED = "Diese Bestellung wurde storniert oder erstattet."
MSG_TEST = "Dieser Code stammt aus einer Testbestellung."
MSG_NO_RUNS_IN_ORDER = "In dieser Bestellung sind keine Läufe enthalten."
MSG_EXHAUSTED = "Alle Läufe dieser Bestellung sind verbraucht."
MSG_UNAVAILABLE = "Die Bezahlprüfung ist gerade nicht erreichbar. Es wurde nichts abgebucht. Bitte später erneut versuchen."
MSG_NOT_READY = "Der Verkauf ist noch nicht freigeschaltet."
MSG_TOO_MANY_ITEMS = "Diese Bestellung ist zu umfangreich für die automatische Prüfung. Bitte melde dich beim Betreiber."
MSG_UNCLEAR = "Der Buchungsstand ist unklar: Die Abbuchung ist möglicherweise angekommen. Bitte prüfe den Stand mit „Prüfen“ oder melde dich beim Betreiber."


class CreditsError(Exception):
    http_status = 402

    def __init__(self, message: str, reason: str):
        super().__init__(message)
        self.message = message
        self.reason = reason


class InvalidCode(CreditsError):
    """Code fehlt, hat ein falsches Format oder gehoert zu keiner (eindeutigen) Bestellung."""


class OrderNotPaid(CreditsError):
    """Bestellung ist nicht bezahlt, storniert, erstattet oder eine Testbestellung."""


class NoRunsLeft(CreditsError):
    """Bestellung enthaelt keine Laeufe oder alle Laeufe sind verbraucht."""

    def __init__(self, message: str, reason: str, balance: "Balance"):
        super().__init__(message, reason)
        self.balance = balance


class CreditsUnavailable(CreditsError):
    """Shopify nicht erreichbar, Konfiguration unvollstaendig oder Zaehler nicht schreibbar.

    maybe_applied: True, wenn ein Schreibzugriff trotz Fehlermeldung angekommen sein koennte (Zeitueberschreitung,
    abgebrochene Verbindung, Serverfehler). Nur beim Schreiben aussagekraeftig; reserve_run und release_run
    pruefen dann nach, bevor sie "nichts abgebucht" sagen."""

    http_status = 503

    def __init__(self, message: str, reason: str, maybe_applied: bool = False):
        super().__init__(message, reason)
        self.maybe_applied = maybe_applied


class _Conflict(Exception):
    """Der Zaehler wurde zwischen Lesen und Schreiben von jemand anderem geaendert."""


@dataclass(frozen=True)
class Balance:
    order_id: str
    granted: int
    used: int
    digest: object = None  # compareDigest des Zaehlers beim Lesen (None: noch nicht vorhanden)

    @property
    def remaining(self) -> int:
        return max(0, self.granted - self.used)


def _unavailable(maybe_applied: bool = False) -> CreditsUnavailable:
    return CreditsUnavailable(MSG_UNAVAILABLE, "bezahlung_nicht_erreichbar", maybe_applied)


def _log(message: str) -> None:
    print(f"credits: {message}")


# ---------------------------------------------------------------------------
# Konfiguration und oeffentlicher Status
# ---------------------------------------------------------------------------

def config_problems() -> list:
    """Namen fehlender oder ungueltiger Einstellungen (nie Werte)."""
    problems = []
    if not SHOPIFY_SHOP_DOMAIN:
        problems.append("SHOPIFY_SHOP_DOMAIN fehlt oder ist ungültig")
    if not SHOPIFY_ADMIN_TOKEN and not (SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET):
        problems.append("SHOPIFY_CLIENT_ID und SHOPIFY_CLIENT_SECRET (oder SHOPIFY_ADMIN_TOKEN) fehlen")
    if not RUN_SKUS:
        problems.append("SHOPIFY_RUN_SKUS fehlt oder ist ungültig (Format: SKU=Läufe,SKU2=Läufe2)")
    if not re.fullmatch(r"\d{4}-\d{2}|unstable", SHOPIFY_API_VERSION or ""):
        problems.append("SHOPIFY_API_VERSION ist ungültig")
    return problems


def is_ready() -> bool:
    return PAYMENT_REQUIRED and not config_problems()


def buy_url():
    """Kauflink fuer die Oberflaeche. Nur https, damit kein javascript:- oder data:-Link entsteht."""
    parsed = urllib.parse.urlparse(SHOPIFY_BUY_URL)
    if parsed.scheme == "https" and parsed.netloc and len(SHOPIFY_BUY_URL) <= 300 and not re.search(r"\s", SHOPIFY_BUY_URL):
        return "https" + SHOPIFY_BUY_URL[5:]  # Schema klein geschrieben, damit die Oberflaeche es sicher erkennt
    return None


def public_info() -> dict:
    return {
        "payment_required": PAYMENT_REQUIRED,
        "payment_ready": is_ready(),
        "buy_url": buy_url() if PAYMENT_REQUIRED else None,
    }


def startup_report() -> list:
    """Zeilen fuer das Start-Log. Nennt nur Namen, nie Werte."""
    if not PAYMENT_REQUIRED:
        # Ein Tippfehler ("yes", "1", "True ") darf die Schranke nicht still ausgeschaltet lassen.
        raw = os.environ.get("PAYMENT_REQUIRED", "").strip().lower()
        if raw and raw != "false":
            return ["WARNUNG: PAYMENT_REQUIRED hat keinen gültigen Wert (erlaubt: true oder false). Die Bezahlschranke ist AUS."]
        return []
    problems = config_problems()
    if problems:
        return ["Bezahlschranke ist EIN, aber nicht startklar: " + "; ".join(problems) + " (Generator bleibt gesperrt)"]
    note = ", Testbestellungen erlaubt" if SHOPIFY_ACCEPT_TEST_ORDERS else ""
    return [f"Bezahlschranke ist EIN (Shop {SHOPIFY_SHOP_DOMAIN}, API {SHOPIFY_API_VERSION}{note})"]


# ---------------------------------------------------------------------------
# Zugangscode
# ---------------------------------------------------------------------------

_CODE_RE = re.compile(r"[A-Z0-9]{6,16}")


def normalize_code(raw) -> str:
    """Bestaetigungsnummern sind zufaellige Grossbuchstaben und Ziffern (z. B. XPAV284CT).
    Erlaubt sind Leerzeichen, Bindestriche und ein fuehrendes '#'. Alles andere wird abgelehnt,
    damit nie Suchsyntax von Shopify (Platzhalter, OR, Leerzeichen) in die Abfrage gelangt."""
    if not isinstance(raw, str) or len(raw) > MAX_CODE_INPUT_CHARS:
        raise InvalidCode(MSG_MISSING if not isinstance(raw, str) else MSG_INVALID,
                          "zugangscode_fehlt" if not isinstance(raw, str) else "zugangscode_ungueltig")
    cleaned = re.sub(r"[\s\-]", "", raw).lstrip("#").upper()
    if not cleaned:
        raise InvalidCode(MSG_MISSING, "zugangscode_fehlt")
    if not _CODE_RE.fullmatch(cleaned):
        raise InvalidCode(MSG_INVALID, "zugangscode_ungueltig")
    return cleaned


# ---------------------------------------------------------------------------
# Zugriff auf die Shopify Admin API
# ---------------------------------------------------------------------------

ORDER_QUERY = """
query PromptoratorOrderByConfirmation($search: String!) {
  orders(first: 2, query: $search) {
    nodes {
      id
      confirmationNumber
      displayFinancialStatus
      cancelledAt
      test
      lineItems(first: 25) {
        pageInfo {
          hasNextPage
        }
        nodes {
          sku
          currentQuantity
        }
      }
      metafield(namespace: "prompterator", key: "runs_used") {
        value
        compareDigest
      }
    }
  }
}
"""

USED_QUERY = """
query PromptoratorRunsUsed($id: ID!) {
  order(id: $id) {
    id
    metafield(namespace: "prompterator", key: "runs_used") {
      value
      compareDigest
    }
  }
}
"""

SET_MUTATION = """
mutation PromptoratorSetRunsUsed($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields {
      key
      value
      compareDigest
    }
    userErrors {
      field
      message
      code
    }
  }
}
"""

_token_lock = threading.Lock()
_token_cache = {"value": None, "expires_at": 0.0}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Folgt keiner Weiterleitung: Das Zugriffstoken darf nie an einen anderen Host gehen."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def _graphql_url() -> str:
    return f"https://{SHOPIFY_SHOP_DOMAIN}/admin/api/{SHOPIFY_API_VERSION}/graphql.json"


def _safe_error_token(value, pattern: str = r"[A-Za-z_]{2,40}") -> str:
    return value if isinstance(value, str) and re.fullmatch(pattern, value) else "?"


def _drop_token() -> None:
    with _token_lock:
        _token_cache["value"] = None
        _token_cache["expires_at"] = 0.0


def _request_client_credentials_token():
    """Holt ein Token ueber den Client-Credentials-Grant (Dev-Dashboard-App im eigenen Shop).
    Das Token gilt 24 Stunden; ein erneuter Aufruf liefert ein neues."""
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": SHOPIFY_CLIENT_ID,
        "client_secret": SHOPIFY_CLIENT_SECRET,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"https://{SHOPIFY_SHOP_DOMAIN}/admin/oauth/access_token",
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
    )
    try:
        with _OPENER.open(req, timeout=SHOPIFY_TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = "?"
        try:
            detail = _safe_error_token(json.loads(exc.read().decode("utf-8")).get("error"))
        except Exception:
            pass
        _log(f"Token-Anfrage an Shopify fehlgeschlagen: HTTP {exc.code} ({detail})")
        raise _unavailable()
    except (urllib.error.URLError, OSError, ValueError, http.client.HTTPException) as exc:
        _log(f"Token-Anfrage an Shopify fehlgeschlagen: {type(exc).__name__}")
        raise _unavailable()
    token = payload.get("access_token") if isinstance(payload, dict) else None
    if not isinstance(token, str) or not token:
        _log("Token-Antwort von Shopify ohne access_token")
        raise _unavailable()
    expires_in = payload.get("expires_in")
    expires_in = expires_in if isinstance(expires_in, int) and expires_in > 0 else 3600
    return token, expires_in


def _access_token() -> str:
    if SHOPIFY_ADMIN_TOKEN:
        return SHOPIFY_ADMIN_TOKEN
    with _token_lock:
        if _token_cache["value"] and _token_cache["expires_at"] - time.time() > TOKEN_REFRESH_MARGIN_SECONDS:
            return _token_cache["value"]
        token, expires_in = _request_client_credentials_token()
        _token_cache["value"] = token
        _token_cache["expires_at"] = time.time() + expires_in
        return token


def _graphql(query: str, variables: dict) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    for attempt in (1, 2):
        token = _access_token()
        req = urllib.request.Request(
            _graphql_url(),
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Shopify-Access-Token": token,
            },
        )
        try:
            with _OPENER.open(req, timeout=SHOPIFY_TIMEOUT_SECONDS) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 401 and attempt == 1 and not SHOPIFY_ADMIN_TOKEN:
                _drop_token()  # abgelaufenes Token: einmal neu holen
                continue
            _log(f"Shopify HTTP {exc.code}")
            # 4xx und Weiterleitungen wurden nicht ausgefuehrt; bei 5xx ist offen, ob eine Buchung ankam.
            raise _unavailable(maybe_applied=exc.code >= 500)
        except (urllib.error.URLError, OSError, http.client.HTTPException) as exc:
            _log(f"Shopify nicht erreichbar: {type(exc).__name__}")
            raise _unavailable(maybe_applied=True)
        try:
            body = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            _log("Shopify-Antwort ist kein JSON")
            raise _unavailable(maybe_applied=True)
        if not isinstance(body, dict):
            raise _unavailable(maybe_applied=True)
        errors = body.get("errors")
        if errors:
            codes = set()
            for item in errors if isinstance(errors, list) else []:
                extensions = item.get("extensions") if isinstance(item, dict) else None
                codes.add(_safe_error_token((extensions or {}).get("code"), r"[A-Z_]{2,40}"))
            _log("Shopify GraphQL-Fehler: " + (",".join(sorted(codes)) or "?"))
            # Gedrosselt oder ohne Berechtigung heisst: nicht ausgefuehrt. Alles andere ist unklar.
            raise _unavailable(maybe_applied=not (codes and codes <= {"THROTTLED", "ACCESS_DENIED"}))
        data = body.get("data")
        if not isinstance(data, dict):
            raise _unavailable(maybe_applied=True)
        return data
    raise _unavailable()


# ---------------------------------------------------------------------------
# Bestellung -> Guthaben
# ---------------------------------------------------------------------------

def _read_counter(metafield):
    """(verbraucht, digest) aus dem Zaehler-Metafeld. Ein unlesbarer Zaehler ist ein Fehler."""
    if not metafield:
        return 0, None
    try:
        used = int(str(metafield.get("value")).strip())
    except (TypeError, ValueError):
        _log("Zaehler an der Bestellung ist nicht lesbar")
        raise _unavailable()
    return max(0, used), metafield.get("compareDigest")


def _granted_runs(order: dict) -> int:
    total = 0
    items = ((order.get("lineItems") or {}).get("nodes")) or []
    for item in items:
        if not isinstance(item, dict):
            continue
        runs = RUN_SKUS.get(str(item.get("sku") or "").strip().casefold())
        quantity = item.get("currentQuantity")
        if runs and isinstance(quantity, int) and quantity > 0:
            total += quantity * runs
    return total


def _load_balance(code: str) -> Balance:
    data = _graphql(ORDER_QUERY, {"search": f"confirmation_number:{code}"})
    nodes = ((data.get("orders") or {}).get("nodes")) or []
    matches = [
        node for node in nodes
        if isinstance(node, dict)
        and isinstance(node.get("confirmationNumber"), str)
        and hmac.compare_digest(node["confirmationNumber"].strip().upper().encode("utf-8"), code.encode("utf-8"))
    ]
    if not matches:
        raise InvalidCode(MSG_INVALID, "zugangscode_ungueltig")
    if len(matches) > 1:
        _log("Bestaetigungsnummer ist nicht eindeutig")
        raise InvalidCode(MSG_AMBIGUOUS, "zugangscode_nicht_eindeutig")
    order = matches[0]

    if order.get("cancelledAt"):
        raise OrderNotPaid(MSG_CANCELLED, "storniert")
    status = order.get("displayFinancialStatus")
    if status not in PAID_STATUSES:
        if status in ("REFUNDED", "VOIDED", "EXPIRED"):
            raise OrderNotPaid(MSG_CANCELLED, "storniert")
        raise OrderNotPaid(MSG_UNPAID, "nicht_bezahlt")
    if order.get("test") and not SHOPIFY_ACCEPT_TEST_ORDERS:
        raise OrderNotPaid(MSG_TEST, "testbestellung")
    order_id = order.get("id")
    if not isinstance(order_id, str) or not re.fullmatch(r"gid://shopify/Order/\d+", order_id):
        raise _unavailable()

    # Alle Positionen muessen gesehen worden sein, sonst waere die Laufzahl geraten.
    page_info = (order.get("lineItems") or {}).get("pageInfo")
    has_next = page_info.get("hasNextPage") if isinstance(page_info, dict) else None
    if has_next is True:
        raise InvalidCode(MSG_TOO_MANY_ITEMS, "bestellung_zu_gross")
    if has_next is not False:
        raise _unavailable()

    used, digest = _read_counter(order.get("metafield"))
    return Balance(order_id=order_id, granted=_granted_runs(order), used=used, digest=digest)


def _write_used(order_id: str, new_value: int, digest) -> None:
    """Schreibt den Zaehler nur, wenn er seit dem Lesen unveraendert ist (compareDigest).
    digest=None bedeutet: der Zaehler darf noch nicht existieren (abgesichertes Anlegen)."""
    data = _graphql(SET_MUTATION, {"metafields": [{
        "ownerId": order_id,
        "namespace": METAFIELD_NAMESPACE,
        "key": METAFIELD_KEY,
        "type": "number_integer",
        "value": str(new_value),
        "compareDigest": digest,
    }]})
    result = data.get("metafieldsSet") or {}
    errors = result.get("userErrors") or []
    if errors:
        codes = {_safe_error_token(e.get("code"), r"[A-Z_]{2,40}") if isinstance(e, dict) else "?" for e in errors}
        if codes & {"STALE_OBJECT", "INVALID_COMPARE_DIGEST", "TAKEN"}:
            raise _Conflict()
        _log("Zaehler konnte nicht geschrieben werden: " + ",".join(sorted(codes)))
        raise _unavailable()
    if not result.get("metafields"):
        raise _unavailable(maybe_applied=True)


_LOCK_STRIPES = tuple(threading.Lock() for _ in range(64))


def _stripe(key: str) -> threading.Lock:
    return _LOCK_STRIPES[hash(key) % len(_LOCK_STRIPES)]


def _require_ready() -> None:
    if not is_ready():
        raise CreditsUnavailable(MSG_NOT_READY, "bezahlung_nicht_eingerichtet")


def check_balance(raw_code) -> Balance:
    """Nur lesen: ist der Code gueltig, und wie viele Laeufe sind uebrig? Sind alle Laeufe verbraucht,
    kommt der Stand mit remaining=0 zurueck. Enthaelt die Bestellung gar keine Laeufe, ist das ein Fehler."""
    _require_ready()
    code = normalize_code(raw_code)
    balance = _load_balance(code)
    if balance.granted <= 0:
        raise NoRunsLeft(MSG_NO_RUNS_IN_ORDER, "keine_laeufe", balance)
    return balance


def _read_used(order_id: str) -> int:
    """Liest nur den Zaehler, um nach einer ungeklaerten Schreibantwort festzustellen, was angekommen ist.
    Scheitert schon das Lesen, bleibt der Buchungsstand unklar (CreditsUnavailable, maybe_applied=True)."""
    try:
        data = _graphql(USED_QUERY, {"id": order_id})
        order = data.get("order")
        if not isinstance(order, dict):
            raise _unavailable()
        return _read_counter(order.get("metafield"))[0]
    except CreditsUnavailable:
        _log("Buchungsstand konnte nicht nachgelesen werden")
        raise CreditsUnavailable(MSG_UNCLEAR, "buchung_unklar", maybe_applied=True)


def reserve_run(raw_code) -> Balance:
    """Bucht einen Lauf ab, bevor die KI aufgerufen wird. Gibt den Stand nach der Buchung zurueck.
    Schlaegt die Erzeugung fehl, muss release_run aufgerufen werden.

    Kommt auf den Schreibzugriff keine verwertbare Antwort (Zeitueberschreitung, Serverfehler), wird der
    Zaehler nachgelesen: Nur wenn er nicht gestiegen ist, heisst es ehrlich "nichts abgebucht". Ist er
    gestiegen, gilt der Lauf als gebucht. Laesst sich auch das nicht klaeren, sagt die Meldung das offen."""
    _require_ready()
    code = normalize_code(raw_code)
    with _stripe(code):
        for _ in range(CAS_ATTEMPTS):
            balance = _load_balance(code)
            if balance.granted <= 0:
                raise NoRunsLeft(MSG_NO_RUNS_IN_ORDER, "keine_laeufe", balance)
            if balance.used >= balance.granted:
                raise NoRunsLeft(MSG_EXHAUSTED, "keine_laeufe", balance)
            try:
                _write_used(balance.order_id, balance.used + 1, balance.digest)
            except _Conflict:
                continue
            except CreditsUnavailable as exc:
                if not exc.maybe_applied:
                    raise
                if _read_used(balance.order_id) <= balance.used:
                    raise _unavailable()  # Zaehler unveraendert: die Buchung ist nicht angekommen
                # Zaehler gestiegen: Die Buchung ist angekommen, nur die Antwort ging verloren.
            return Balance(order_id=balance.order_id, granted=balance.granted, used=balance.used + 1)
    _log("Zaehler wegen gleichzeitiger Zugriffe nicht schreibbar")
    raise _unavailable()


class _Unsure(Exception):
    """Ob eine Gutschrift angekommen ist, laesst sich nicht klaeren. Dann wird nicht wiederholt, weil
    sonst doppelt gutgeschrieben werden koennte."""


def _release_attempt(order_id: str) -> int:
    with _stripe(order_id):
        for _ in range(CAS_ATTEMPTS):
            data = _graphql(USED_QUERY, {"id": order_id})
            order = data.get("order")
            if not isinstance(order, dict):
                raise _unavailable()
            used, digest = _read_counter(order.get("metafield"))
            if used <= 0:
                return 0
            try:
                _write_used(order_id, used - 1, digest)
            except _Conflict:
                continue
            except CreditsUnavailable as exc:
                if not exc.maybe_applied:
                    raise
                try:
                    now = _read_used(order_id)
                except CreditsUnavailable:
                    raise _Unsure()
                if now < used:
                    return now  # angekommen, nur die Antwort ging verloren
                raise  # nicht angekommen: ein weiterer Versuch ist sicher
            return used - 1
    raise _unavailable()


def release_run(order_id: str):
    """Macht eine Buchung rueckgaengig. Gibt den neuen Zaehlerstand zurueck, bei Misserfolg None.
    Wirft nie: Der Aufrufer steckt in einem Fehlerpfad und muss dem Kaeufer trotzdem antworten.
    Ein gescheiterter Versuch wird einmal wiederholt, ausser es ist unklar, ob die Gutschrift schon
    angekommen ist. Ein endgueltiger Misserfolg geht zulasten des Kaeufers; der Aufrufer sagt ihm das."""
    if not isinstance(order_id, str) or not re.fullmatch(r"gid://shopify/Order/\d+", order_id):
        return None
    for attempt in range(RELEASE_ATTEMPTS):
        try:
            return _release_attempt(order_id)
        except CreditsUnavailable:
            pass  # sicher nichts geschrieben: wiederholbar
        except _Unsure:
            break
        except Exception as exc:  # unerwartete Antwortform o. ae.: nicht blind wiederholen
            _log(f"Gutschrift: unerwarteter Fehler ({type(exc).__name__})")
            break
        if attempt + 1 < RELEASE_ATTEMPTS:
            time.sleep(RELEASE_RETRY_DELAY_SECONDS)
    _log("Gutschrift eines Laufs fehlgeschlagen")
    return None
