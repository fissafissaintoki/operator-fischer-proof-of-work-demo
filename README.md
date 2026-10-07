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
| POST    | `/api/generate`        | ChatGPT- und Claude-Entwurf, Zusammenfuehrung durch Claude (siehe Synthese) |
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

- Backend: Python `http.server`, OpenAI-API und Anthropic-API (Synthese), ReportLab (PDF).
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
