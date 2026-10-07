# Prompterator

**Operator-Fischer Proof of Work · AI Operations**

Prompterator verwandelt Rohinput in strukturierte Use-Case-Artefakte. Das
Projekt ist ein technischer Proof of Work und demonstriert eine
deterministische Pipeline fuer wiederverwendbare KI-Artefakte.

---

## Status

Dies ist ein **MVP / Proof of Work**, kein produktionsreifes SaaS.

- Keine final geprueften Datenschutzhinweise.
- Keine geprueften Auftragsverarbeitungsvertraege.
- Keine DSGVO-Konformitaetsgarantie.
- Bitte keine personenbezogenen, sensiblen oder vertraulichen Daten eingeben.

Vor produktiver oder breiter oeffentlicher Nutzung muessen Impressum,
Datenschutzhinweise, Anbieter- und Auftragsverarbeitungsfragen,
Drittlandtransfers sowie Speicher- und Logging-Prozesse final rechtlich
geprueft werden.

---

## Was Prompterator macht

```
Rohinput
   ↓
Problemklasse erkennen
   ↓
Modus / Strukturierung
   ↓
Artefakt erzeugen
   ↓
Qualitaetspruefung
   ↓
Governance-Markierung
   ↓
Wiederverwendung als Dossier
```

Ausgaben:

- **Strukturierter Markdown-Output** im Browser
- **Direkt nutzbares Artefakt** (separat anzeigbar)
- **Masterprompt** (wiederverwendbare Arbeitsanweisung, separat anzeigbar)
- **Executive PDF-Dossier** (ReportLab, Download)
- **HTML-Dossier** (High-End-Layout, Browser-Preview unter `/dossier-preview`)
- **Virtual Warehouse Playground** (spielbare HTML-Demo unter `pages/virtual-warehouse.html`)
- **GlowGlove Virtual Test Lab** (Wearable-Picking-Demo unter `pages/glowglove-testlab.html`)
- **ARC2 Cognitive Lab** (lokales JSON-/Grid-Labor unter `pages/arc2-cognitive-lab.html`)

---

## Synthese: ChatGPT und Claude

`/api/generate` laesst zwei Modelle unabhaengig voneinander entwerfen und
fuehrt die Entwuerfe anschliessend zusammen. Ein Lauf besteht aus drei
Modellaufrufen:

```
Rohinput
   ├─ ChatGPT-Entwurf (OpenAI)     ┐ parallel, ohne
   └─ Claude-Entwurf  (Anthropic)  ┘ Kenntnis voneinander
              ↓
   Zusammenfuehrung durch Claude: je Abschnitt die staerkere Fassung.
   Widersprueche werden nicht stillschweigend aufgeloest, sondern als
   [ANNAHME] / [HYPOTHESE] markiert und unter "Abweichungen" aufgelistet.
```

Antwort von `POST /api/generate` (Request: `raw_input`, optional `artifact_type`
aus `matrix`, `sop`, `post`, `research`, `profile`, `codex`):

| Feld            | Inhalt |
|-----------------|--------|
| `result`        | finales Ergebnis (bei Ausfall der Zusammenfuehrung der ChatGPT-Entwurf) |
| `differences`   | Abweichungen und Widersprueche zwischen den Entwuerfen (leer ohne Synthese) |
| `mode`          | `synthese`, `entwuerfe` (Zusammenfuehrung ausgefallen), `chatgpt` oder `claude` (nur ein Anbieter) |
| `participants`  | je `chatgpt`, `claude`, `synthese`: `ok`, `fehler`, `nicht_aktiv` oder `uebersprungen` |
| `models`        | verwendete Modelle |
| `drafts`        | die einzelnen Entwuerfe |

Ehrliche Degradierung: Faellt ein Anbieter aus oder ist nicht konfiguriert, wird
das im Ergebnis ausgewiesen. Eine unvollstaendige Paarung wird nie als gelungene
Synthese gemeldet. Sind beide Anbieter aus, antwortet der Server mit 503 bzw. 502.

Umgebungsvariablen (alle Schluessel ausschliesslich als Environment Variable,
nie im Repo oder im Frontend):

| Variable                   | Standard            | Bedeutung |
|----------------------------|---------------------|-----------|
| `OPENAI_API_KEY`           | –                   | ChatGPT-Entwurf |
| `OPENAI_MODEL`             | `gpt-4.1-mini`      | ChatGPT-Modell |
| `ANTHROPIC_API_KEY`        | –                   | Claude-Entwurf und Zusammenfuehrung |
| `ANTHROPIC_MODEL`          | `claude-sonnet-5-5` | Claude-Modell |
| `ANTHROPIC_THINKING`       | `between_tools`     | niedrigste Denkstufe von Claude Sonnet 5.5 (Denk-Tokens zaehlen zu `max_tokens`, `disabled` wird dort abgelehnt). Bei anderem Modell ggf. `omit` setzen |
| `SYNTHESIS_ENABLED`        | `true`              | `false` schaltet Claude ab (nur ChatGPT) |
| `MERGE_MAX_OUTPUT_TOKENS`  | `2000`              | Ausgabelimit der Zusammenfuehrung |
| `PROVIDER_TIMEOUT_SECONDS` | `120`               | Zeitlimit je Modellaufruf |

Die Ring-2-Grenzen (Rate-Limit, Input-/Output-Limit, Tages- und Monatslimit,
Origin-Pruefung) gelten unveraendert; ein Lauf zaehlt einmal. Tokens werden je
Monat und Anbieter gezaehlt (nur Zahlen, keine Inhalte), dazu ein Zaehler
`truncated` fuer Antworten, die am Ausgabelimit abgeschnitten wurden. Beides ist
im internen `/api/usage` mit Admin-Token sichtbar und die Grundlage fuer
Preisbildung und das Abstimmen der Limits.

Tests (ohne API-Keys; die Netzwerkaufrufe werden durch Attrappen ersetzt):

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

Die Tests sind nicht gegen die echten Anbieter-APIs gelaufen.

---

## Bezahlschranke (Shopify)

Optional und **standardmaessig aus**. Ohne `PAYMENT_REQUIRED=true` verhaelt sich
alles wie bisher: kein Zugangscode, kein Shopify-Aufruf, `/api/credits`
antwortet 404. Der Schalter versteht nur `true` oder `false`; bei einem anderen
Wert (Tippfehler) warnt der Server beim Start und die Schranke bleibt aus.

```
Kaeufer bezahlt im Shopify-Shop ein Produkt (SKU steht in SHOPIFY_RUN_SKUS)
   ↓
Bestaetigungsnummer der Bestellung = Zugangscode (z. B. XPAV284CT, nicht "#1001")
   ↓
Prompterator: Code eingeben, "Pruefen" zeigt die Restlaeufe
   ↓
Server fragt die Bestellung per Shopify Admin API: bezahlt? nicht storniert? wie viele Laeufe?
   ↓
Der Lauf wird VOR den Modellaufrufen abgebucht und bei Misserfolg zurueckgebucht
```

Regeln im Code (jeweils durch Tests belegt, siehe unten):

- **Bezahlt** heisst `PAID` oder `PARTIALLY_REFUNDED`. Nicht: ausstehend, autorisiert,
  teilbezahlt, storniert, erstattet, ungueltig, abgelaufen. Testbestellungen nur mit
  `SHOPIFY_ACCEPT_TEST_ORDERS=true` (nur fuer einen Probe-Deploy).
- **Laeufe je Bestellung:** Summe aus der verbleibenden Menge (`currentQuantity`, nach
  Erstattungen) mal Laeufe je SKU.
- **Zaehler:** Metafeld `prompterator.runs_used` an der Bestellung in Shopify. Es gibt
  keine eigene Datenbank; der Stand ueberlebt Neustarts und Deploys. Geschrieben wird nur
  mit `compareDigest` (Compare-and-Set): gleichzeitige Anfragen koennen keinen Lauf doppelt
  nutzen oder ueberbuchen. Bei einem Konflikt wird bis zu 4-mal neu gelesen, danach 503
  mit "nichts abgebucht".
- **Eindeutigkeit:** Ein Treffer zaehlt nur, wenn die Bestaetigungsnummer der gefundenen
  Bestellung exakt dem Code entspricht und genau eine Bestellung passt. Codes bestehen aus
  Buchstaben und Ziffern (6 bis 16 Zeichen; Leerzeichen, Bindestriche und ein fuehrendes `#`
  werden ignoriert), damit keine Suchsyntax in die Shopify-Abfrage gelangt.
- **Keine geratene Laufzahl:** Es werden bis zu 25 Positionen je Bestellung gelesen. Hat eine
  Bestellung mehr (`hasNextPage`), wird sie abgelehnt (`bestellung_zu_gross`) statt
  zu wenige Laeufe zu zaehlen; der Kaeufer wird an den Betreiber verwiesen.
- **Fail closed:** Shopify nicht erreichbar, Zaehler unlesbar oder Konfiguration
  unvollstaendig fuehren zu 503, ohne Modellaufruf und ohne Abbuchung.
- **Unklare Buchung:** Kommt auf das Hochzaehlen keine verwertbare Antwort
  (Zeitueberschreitung, Serverfehler), liest der Server den Zaehler nach. Nur wenn er
  unveraendert ist, steht "nichts abgebucht"; ist er gestiegen, gilt der Lauf als gebucht.
  Laesst sich auch das nicht klaeren, sagt die Antwort es offen (`buchung_unklar`, 503, kein
  Modellaufruf), und die Oberflaeche raet, zuerst mit "Pruefen" den Stand anzusehen.
  Abgelehnte Schreibzugriffe (4xx, Drosselung) werden nicht nachgelesen: sie wurden nicht
  ausgefuehrt.
- **Rueckbuchung:** Scheitert die Erzeugung (auch durch einen Absturz), wird der Lauf
  zurueckgebucht ("Es wurde nichts abgebucht."). Die Gutschrift wird einmal wiederholt, nie
  blind: Ist unklar, ob sie schon angekommen ist, wird nicht noch einmal geschrieben, weil
  sonst doppelt gutgeschrieben wuerde. Misslingt die Gutschrift endgueltig, steht das offen in
  der Antwort und im Zaehler `release_failed`; dann muss der Betreiber den Zaehler in Shopify
  von Hand korrigieren (Metafeld `prompterator.runs_used` an der Bestellung).
- **Token bleibt bei Shopify:** Weiterleitungen werden nicht befolgt; das Zugriffstoken geht
  nie an einen anderen Host.
- **Teilergebnisse:** Sind beide Anbieter konfiguriert, aber es kommt keine vollstaendige
  Synthese zustande, wird der Lauf nicht abgerechnet. Ist nur ein Anbieter konfiguriert,
  wird dessen Ergebnis abgerechnet.
- **Geheimnisse:** Codes, Tokens und Secrets werden nie geloggt, nie an den Browser
  gegeben und nie im Browser gespeichert. Geloggt werden nur Statuscodes und Fehlercodes.

Schnittstellen bei eingeschalteter Schranke:

| Pfad | Verhalten |
|------|-----------|
| `POST /api/generate` | zusaetzliches Feld `access_code`. Ohne gueltigen Code `402` mit `{error, reason}` (`zugangscode_fehlt`, `zugangscode_ungueltig`, `zugangscode_nicht_eindeutig`, `nicht_bezahlt`, `storniert`, `testbestellung`, `keine_laeufe`, `bestellung_zu_gross`); bei Shopify-Problemen `503` (`bezahlung_nicht_erreichbar`, `bezahlung_nicht_eingerichtet`, `buchung_unklar`). Erfolg enthaelt `credits: {granted, used, remaining, charged}` (bei misslungener Gutschrift eines Teilergebnisses zusaetzlich `giveback_failed: true`) |
| `POST /api/credits` | nur Lesen: `{access_code}` → `{valid, granted, used, remaining}`. Eigenes Rate-Limit (`CREDITS_RATE_LIMIT_MAX_REQUESTS`), Origin-Pflicht wie bei `/api/generate`. Bei ausgeschalteter Schranke ein unbekannter Pfad (404, ohne dass Body oder Origin geprueft werden) |
| `GET /api/status` | zusaetzlich `payment_required`, `payment_ready`, `buy_url`. `generate_enabled` ist `false`, solange die Schranke an, aber nicht startklar ist |
| `GET /api/usage` (Admin) | zusaetzlich `payment_required`, `payment_ready` und je Monat `credits\|charged`, `credits\|released`, `credits\|release_failed`, `credits\|degraded` (Laeufe mit Teilausfall, nicht abgerechnet) |

Umgebungsvariablen (Secrets nur im Render-Environment, nie im Repo und nie im Chat):

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `PAYMENT_REQUIRED` | `false` | `true` schaltet die Schranke ein |
| `SHOPIFY_SHOP_DOMAIN` | – | `<shop>.myshopify.com`; andere Hosts werden verworfen, damit das Token nirgends sonst hingeht |
| `SHOPIFY_CLIENT_ID`, `SHOPIFY_CLIENT_SECRET` | – | Dev-Dashboard-App: Token ueber den Client-Credentials-Grant (gilt 24 Stunden, wird vor Ablauf erneuert) |
| `SHOPIFY_ADMIN_TOKEN` | – | Alternative: festes Admin-Token einer aelteren Custom App (hat Vorrang) |
| `SHOPIFY_API_VERSION` | `2026-07` | Admin-API-Version |
| `SHOPIFY_RUN_SKUS` | – | `SKU=Laeufe,SKU2=Laeufe2`, z. B. `PT-LAUF=1,PT-10ER=10`; ein Tippfehler macht die ganze Angabe ungueltig |
| `SHOPIFY_BUY_URL` | – | https-Link zum Produkt (Kauflink in der Oberflaeche) |
| `SHOPIFY_ACCEPT_TEST_ORDERS` | `false` | nur fuer einen Probe-Deploy |
| `SHOPIFY_TIMEOUT_SECONDS` | `15` | Zeitlimit je Shopify-Aufruf |
| `CREDITS_RATE_LIMIT_MAX_REQUESTS` | `6` | Pruefungen je Minute und IP |

Einrichtung:

1. **Shopify-Tarif.** Der Shop laeuft derzeit im Testzeitraum (`trial`); fuer echte
   Verkaeufe ist laut Shopify ein bezahlter Tarif noetig. Das sind Fixkosten, die der
   Betreiber bewusst entscheidet.
2. **App im Dev Dashboard** anlegen (neue Custom Apps im Shop-Admin gibt es nicht mehr).
   Laut Shopify-Doku muessen App und Shop zur selben Organisation gehoeren, sonst lehnt
   Shopify die Token-Anfrage ab (`shop_not_permitted`). Scopes: `read_orders` und
   `write_orders` (das Schreiben des Metafelds verlangt das Zugriffsniveau der Bestellung).
   App im Shop installieren.
3. **Produkt** mit der SKU anlegen (digital, ohne Versand). Im Produkttext nennen:
   "Zugangscode = Bestaetigungsnummer deiner Bestellung".
4. **Render-Environment** setzen (Tabelle oben) und die Ring-2-Grenzen fuer den Verkauf
   anheben (`RATE_LIMIT_MAX_REQUESTS`, `DAILY_REQUEST_LIMIT`, `MONTHLY_REQUEST_LIMIT`; sie
   gelten auch fuer Zahlende).
5. **Probelauf** mit einer Testbestellung auf einem Probe-Deploy
   (`SHOPIFY_ACCEPT_TEST_ORDERS=true`): kaufen, Code pruefen, Lauf erzeugen, den Zaehler in
   Shopify ansehen, die Rueckbuchung bei einem erzwungenen Fehler pruefen. Danach
   `SHOPIFY_ACCEPT_TEST_ORDERS` wieder entfernen.
6. **Rueckweg:** `PAYMENT_REQUIRED=false` (oder Variable loeschen) und neu starten.

Bekannte Grenzen (bewusst nicht schoengeredet):

- Ohne den Scope `read_all_orders` (Freigabe durch Shopify noetig) liefert Shopify nur
  Bestellungen der letzten 60 Tage. Zugangscodes laufen deshalb praktisch 60 Tage nach dem
  Kauf ab; das muss im Produkttext und in den AGB stehen.
- Ob die Bestaetigungsnummer auf der Danke-Seite und in der Bestellbestaetigung steht, muss
  an einer Testbestellung geprueft werden; sonst die Benachrichtigungsvorlage anpassen.
- Wer einen Code weitergibt, teilt die Laeufe. Erstattungen und Chargebacks werden nur
  erkannt, solange Shopify die Bestellung als erstattet fuehrt; bereits verbrauchte Laeufe
  werden nicht ausgeglichen.
- Die Abbuchung ist so zuverlaessig wie die Shopify-Admin-API. Faellt Shopify aus, steht
  der Verkauf still (bewusst).
- Eine Buchung, die erst nach dem Nachlesen bei Shopify ankommt (sehr langsame Antwort nach
  Zeitueberschreitung), kostet den Kaeufer einen Lauf, ohne dass der Server es merkt. Das ist
  selten; der Betreiber kann den Zaehler in Shopify korrigieren. Dafuer braucht der Betreiber
  eine Support-Adresse, an die sich Kaeufer mit ihrem Zugangscode wenden koennen.
- Bricht die Verbindung des Kaeufers waehrend eines Laufs ab (oder dauert er laenger als vier
  Minuten), bleibt der Lauf abgebucht. Die Oberflaeche weist darauf hin und raet, den Stand zu
  pruefen.
- Laeufe mit Teilausfall werden nicht abgerechnet (`credits|degraded` zaehlt sie). Faellt ein
  Anbieter dauerhaft aus, ist der Dienst faktisch kostenlos und kostet den Betreiber die
  Modellaufrufe.
- Eine Bestellung mit 100-%-Rabatt zaehlt als bezahlt, sobald Shopify sie so fuehrt.
- Kosten: Ein Lauf sind drei Modellaufrufe. Ein Preis ist nicht festgelegt; er soll aus
  einem gemessenen Probelauf kommen (`/api/usage`: Tokenzaehler je Anbieter und
  `credits|charged`). Ist die Schranke aus, zahlt der Betreiber jeden Lauf selbst.
- Rechtliches (Impressum, Datenschutz inkl. Shopify, AGB, Widerruf bei digitalen
  Leistungen, Preisangaben) ist nicht geprueft.

Tests: `tests/test_credits.py` (ohne Netzwerk, gegen eine Nachbildung von Shopify). Sie
belegen die Logik, ersetzen aber keinen Probelauf mit einer echten Testbestellung. Echte
Zahlungen sowie OpenAI, Anthropic und Shopify wurden dabei nicht angesprochen.

---

## Governance-Grundsatz

> Mensch bleibt Owner. KI bleibt Werkzeug.

Owner, Pruefer und Freigebender sind unterschiedliche Rollen, auch wenn sie in
einer Person zusammenfallen. Fachliche Pruefung kann nicht durch das System
ersetzt werden.

---

## Endpoints

| Methode | Pfad                   | Funktion                                  |
|---------|------------------------|-------------------------------------------|
| GET     | `/`                    | Hauptseite (Prompterator UI)              |
| GET     | `/dossier-preview`     | Statische HTML-Dossier-Vorschau           |
| GET     | `/health`              | Health-Check                              |
| GET     | `/api/status`          | Oeffentlicher Status (welche Anbieter aktiv sind), ohne Geheimnisse |
| POST    | `/api/generate`        | ChatGPT- und Claude-Entwurf, Zusammenfuehrung durch Claude (siehe Synthese); mit eingeschalteter Bezahlschranke zusaetzlich `access_code` |
| POST    | `/api/credits`         | Zugangscode pruefen und Restlaeufe lesen (nur mit eingeschalteter Bezahlschranke, sonst 404) |
| POST    | `/api/pdf`             | Executive PDF-Dossier (ReportLab)         |
| POST    | `/api/dossier-html`    | Dynamisches HTML-Dossier (parallel zu PDF)|

Beide Render-Pfade (PDF und HTML) lesen aus demselben Use-Case-Modell, damit
inhaltliche Verbesserungen automatisch in beiden Pfaden wirken.

---

## Architekturpfade

Siehe:

- `docs/PHILLIP-ARTEFAKT-LOGIC-INTEGRATION.md` —
  Schichtenmodell und Agentenlogik.
- `docs/PDF-HTML-CSS-DOSSIER-TEMPLATE-BRIEF.md` —
  Beziehung zwischen PDF- und HTML-Pfad.
- `pages/virtual-warehouse.html` —
  spielbare Virtual-Warehouse-Demo fuer Prozesslogik, Lagerstatus, Governance und Decision Gates.
- `pages/glowglove-testlab.html` —
  spielbare Wearable-Picking-Demo fuer GlowGlove-Logik, LED-Feedback, Pickbestaetigung und Trainingsdaten.
- `pages/arc2-cognitive-lab.html` —
  lokales ARC2-/Grid-Labor fuer JSON-Tasks, Visualisierung, Hypothesen und Primitive Checks.

---

## OPS Core / KnowledgeOS Architecture Layer

Prompterator ist nicht nur eine App, sondern ein dokumentiertes Arbeits-,
Governance- und Artefaktsystem. OPS Core beschreibt den operativen Runtime-,
Routing- und Governance-Layer. KnowledgeOS beschreibt den kuratierten Skill-,
Artefakt-, Notiz- und Wiederverwendungslayer.

Siehe:

- `docs/OPS-CORE-KNOWLEDGEOS-GITHUB-BUILD.md` —
  Architekturrahmen fuer OPS Core, KnowledgeOS und Prompterator als Proof of Work.
- `docs/GOVERNANCE-GATE.md` —
  Pruef- und Freigabelayer mit Risiko-Klassen, Public-Safe-Pruefung und Command Safety Gate.
- `docs/PROCESS-AI-USE-CASE-CATALOG.md` —
  public-safe Use-Case-Katalog fuer Prozess-KI, Logistik, Governance und Beratungs-Intake.
- `docs/KIBERATUNG-STYLE-USE-CASE-ONEPAGER.md` —
  kiberatung.de-orientierter Onepager mit GitHub-Link, Skill-Match und Beratungsnutzen.
- `docs/CLAUDE-CODEX-ORCHESTRATION.md` —
  Handoff fuer Claude/Codex-Orchestrierung unter OPS Core.
- `docs/CODEX-HANDOFF-WAREHOUSE-DRIVE-SIMULATOR.md` —
  Handoff fuer einen spielbaren Warehouse Drive Simulator auf Basis abstrahierter Lager-Video-Merkmale.
- `knowledgeos/SKILL-REGISTRY.md` —
  wiederverwendbare Skill-Cluster, Artefaktmuster und Operator-Faehigkeiten.
- `docs/CODING-AGENT-HANDOFF.md` —
  sichere Uebergabevorlage fuer Codex, Claude, GitHub-Agenten und andere Coding-Assistenten.

---

## Technische Hinweise

- Backend: Python `http.server`, OpenAI-API und Anthropic-API (Synthese), ReportLab (PDF),
  optional Shopify Admin API (Bezahlschranke, `shopify_credits.py`).
- Frontend: Single-File `index.html`, kein Framework, kein Build-Step.
- Deploy: Render (Procfile vorhanden).
- Keine externen Agenten- oder Orchestrierungs-Bibliotheken
  (kein LangChain, kein CrewAI, kein AutoGen).

---

## Was bewusst nicht behauptet wird

- Keine DSGVO-Konformitaet, solange rechtliche Pruefung nicht erfolgt ist.
- Keine geschaeftliche Belastbarkeit der erzeugten Artefakte ohne Fachpruefung.
- Kein autonomes Agentensystem.
- Kein Replacement fuer menschliche Entscheidung.
