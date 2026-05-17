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
| POST    | `/api/generate`        | OpenAI-Call mit Systemprompt              |
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

---

## Technische Hinweise

- Backend: Python `http.server`, OpenAI-API, ReportLab (PDF).
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
