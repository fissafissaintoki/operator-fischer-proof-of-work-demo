# GlowGlove Live Access & Hardware Bridge Plan

## Zweck

Dieses Dokument beschreibt, wie das `GlowGlove Virtual Test Lab` erreichbar, testbar und spaeter optional mit echter Hardware oder einem lokalen Gadget verbunden werden kann.

Aktuelle Demo-Datei:

```text
pages/glowglove-testlab.html
```

## Zielbild

```text
GitHub / Repo
  -> statische Webroute
  -> Browser-Testseite
  -> optional lokaler Hardware-Bridge-Service
  -> Demo-Events im GlowGlove Test Lab
```

## Stufe 1: Sofort sichtbar im Repo

Die Demo ist bereits als eigenstaendige HTML-Datei vorhanden:

```text
pages/glowglove-testlab.html
```

Direkte GitHub-Datei:

```text
https://github.com/fissafissaintoki/operator-fischer-proof-of-work-demo/blob/main/pages/glowglove-testlab.html
```

Das zeigt den Code und macht das Artefakt auffindbar.

## Stufe 2: Webroute im Prompterator-Server

Gewuenschte Live-Routen:

```text
https://www.prompterator.de/glowglove-testlab
https://www.prompterator.de/virtual-warehouse
```

Dafuer soll `server.py` die beiden statischen HTML-Dateien ausliefern:

```python
SEO_ROUTES = {
    "/ki-prompt-generator": "pages/ki-prompt-generator.html",
    "/ki-use-case-generator": "pages/ki-use-case-generator.html",
    "/operator-fischer-method": "pages/operator-fischer-method.html",
    "/impressum": "pages/impressum.html",
    "/datenschutz": "pages/datenschutz.html",
    "/virtual-warehouse": "pages/virtual-warehouse.html",
    "/glowglove-testlab": "pages/glowglove-testlab.html",
}
```

Damit werden die Seiten ueber die bestehende sichere Allowlist-Logik ausgeliefert. Keine OpenAI-/API-Logik muss geaendert werden.

## Stufe 3: Lokal am Mac testen

### Direkt als Datei oeffnen

```bash
open pages/glowglove-testlab.html
```

### Lokal ueber Prompterator-Server testen

Nach Einbau der Route:

```bash
python3 server.py
open http://localhost:8787/glowglove-testlab
```

## Stufe 4: Hardware-Bridge als spaeteres Modul

Falls ein echter Handschuh, Sensor, Mikrocontroller oder Wearable-Prototyp angebunden werden soll, sollte die Verbindung nicht direkt produktiv laufen, sondern ueber einen lokalen Bridge-Service.

### Empfohlene Architektur

```text
Sensor / Gadget / Handschuh
  -> USB / Bluetooth / Serial / lokale Schnittstelle
  -> lokaler Bridge-Service auf dem Mac
  -> WebSocket / localhost API
  -> GlowGlove Test Lab im Browser
  -> Eventlog / Labelschema / Governance Gate
```

### Beispiel-Eventformat

```json
{
  "device_id": "glowglove-demo-01",
  "event_type": "pick_confirmed",
  "slot": "B-14",
  "sku_demo": "AZ-630",
  "qty": 4,
  "confidence": 0.94,
  "risk_class": "LOW",
  "owner_required": true,
  "timestamp": "2026-05-25T00:00:00Z"
}
```

### Erlaubte Eventklassen

| Event | Bedeutung | Demo-Reaktion |
|---|---|---|
| `navigation_started` | Nutzer wird zum Fach gefuehrt | LED blau / Display GO |
| `slot_reached` | Zielposition erreicht | LED gruen / Slot OK |
| `pick_confirmed` | Pick bestaetigt | RELEASE Event |
| `mispick_detected` | falscher Artikel oder Slot | REVIEW / rote LED |
| `cold_chain_warning` | temperaturkritischer Hinweis | QS REVIEW |
| `training_label_saved` | anonymisiertes Trainingsbeispiel gespeichert | Dataset-Event |

## Public-Safe-Regeln

- Keine echten Kundendaten.
- Keine echten Barcodes.
- Keine personenbezogene Mitarbeiterueberwachung.
- Keine Leistungsbewertung einzelner Personen.
- Keine produktive Freigabe ohne menschlichen Owner.
- Keine Verbindung zu realen Lager-/WMS-/ERP-Systemen ohne eigene Sicherheitspruefung.

## Codex-Patchauftrag

```text
Ziel:
Mache pages/glowglove-testlab.html und pages/virtual-warehouse.html ueber den bestehenden Prompterator-Server erreichbar.

Aenderung:
In server.py die SEO_ROUTES-Map um folgende Routen erweitern:
- /glowglove-testlab -> pages/glowglove-testlab.html
- /virtual-warehouse -> pages/virtual-warehouse.html

Nicht aendern:
- OpenAI-/API-Logik
- Rate-Limits
- Sicherheitsheader
- PDF-/HTML-Dossier-Renderer
- Firewall-Blockliste

Test:
python3 server.py
curl -I http://localhost:8787/glowglove-testlab
curl -I http://localhost:8787/virtual-warehouse

Akzeptanz:
- beide Routen liefern HTTP 200
- keine neuen Dependencies
- keine Secrets
- keine echten Betriebsdaten
```

## Status

`v0.1 · Live Access Plan · Hardware Bridge vorbereitet`
