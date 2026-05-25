# Claude / Codex Orchestration Handoff

## Zweck

Dieses Dokument beschreibt, wie OPS Core Claude und Codex arbeitsteilig fuer den Prompterator- und Virtual-Warehouse-Build orchestriert.

Der menschliche Owner bleibt Entscheider. Claude und Codex sind Werkzeuge mit getrennten Rollen.

## Rollenmodell

| Rolle | Aufgabe | Grenze |
|---|---|---|
| Operator Fischer | Ziel, Freigabe, Priorisierung, finale Verantwortung | Entscheidet, was veroeffentlicht wird |
| OPS Core | Routing, Governance, Qualitaet, Handoff-Struktur | Keine autonome Entscheidung |
| Claude | Konzept, UX-Review, Sprach-/Strukturkritik, Risikoanalyse | Aendert nicht direkt am Repo |
| Codex | Implementierung, Refactoring, Tests, Repo-Diff | Keine Secrets, keine destruktiven Befehle |
| Verifier | Pruefung auf Scope, Public-Safe, Risiko und Wiederverwendung | Keine Wahrheitgarantie |

## Standardfluss

```text
Operator-Ziel
  -> OPS Core klassifiziert Problemklasse
  -> Claude prueft Konzept, UX und Kommunikationslogik
  -> Codex setzt begrenzten Repo-Diff um
  -> OPS Core prueft Governance Gate
  -> Owner gibt frei
```

## Claude-Auftrag fuer Virtual Warehouse

```text
Du bist UX-/Produkt-Reviewer fuer ein public-safe Process-AI Portfolio-Demo.
Pruefe die Datei pages/virtual-warehouse.html.
Ziel: virtuelles Lager zum Rumspielen, das Prozesslogik, Governance und Operator-Fischer-Kompetenz sichtbar macht.

Pruefe:
- Ist die Demo sofort verstaendlich?
- Wirkt sie professionell genug fuer KI-Beratung / Everlast-Kontext?
- Sind die Begriffe fuer Nicht-Logistiker verstaendlich?
- Wo braucht es weniger Text und mehr Wirkung?
- Welche 3 UI-Verbesserungen haetten den groessten Portfolio-Effekt?

Grenzen:
- Keine vertraulichen Betriebsdaten.
- Keine echten Kundendaten.
- Keine personenbezogene Leistungskontrolle.
- Keine offiziellen Everlast-Claims.

Rueckgabeformat:
1. Kurzurteil
2. Staerken
3. Schwachstellen
4. Top-3 Verbesserungen
5. Konkrete Text-/UX-Vorschlaege
```

## Codex-Auftrag fuer Virtual Warehouse

```text
Du arbeitest im Repository fissafissaintoki/operator-fischer-proof-of-work-demo.

Ziel:
Die Datei pages/virtual-warehouse.html als public-safe interaktive Demo verbessern und optional sauber im Server als Route /virtual-warehouse einhaengen.

Arbeitsprinzip:
1. Repo-Zustand pruefen.
2. server.py und README.md lesen.
3. Keine Secrets lesen oder ausgeben.
4. Keine bestehende Prompterator-Logik brechen.
5. Kleine, nachvollziehbare Aenderungen.
6. Wenn Route hinzugefuegt wird: nur statische HTML-Auslieferung analog SEO_ROUTES.
7. Rueckgabe als Diff-Zusammenfassung und Testplan.

Akzeptanzkriterien:
- /virtual-warehouse liefert pages/virtual-warehouse.html aus.
- README verlinkt die Demo.
- Keine API-/OpenAI-Logik veraendert.
- Keine neuen externen Abhaengigkeiten.
- Keine echten Betriebsdaten.
- Mobile Ansicht bleibt nutzbar.

Rueckgabeformat:
Status:
Geaenderte Dateien:
Risiko-Klasse:
Tests:
Offene Punkte:
```

## Governance Gate

Jede Aenderung wird bewertet mit:

```text
Problemklasse:
Risiko-Klasse:
Public-Safe:
Betroffene Dateien:
Rollback:
Owner-Freigabe erforderlich:
Ergebnis: RELEASE / REVIEW / REWORK / HOLD / BLOCK
```

## Spezifische Regeln fuer diese Demo

- Die Demo ist ein Portfolio-/Proof-of-Work-Artefakt, keine produktive Lagersteuerung.
- Keine realen Betriebsdaten.
- Keine personenbezogene Mitarbeiterbewertung.
- Keine automatische Freigabe ohne menschlichen Owner.
- Keine Marken- oder Kundennamen ohne Freigabe.

## Status

`v0.1 · OPS Core Claude/Codex Orchestration Handoff`
