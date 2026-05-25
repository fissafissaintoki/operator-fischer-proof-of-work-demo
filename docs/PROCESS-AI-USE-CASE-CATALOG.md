# Process-AI Use-Case Catalog

## Zweck

Dieser Katalog zeigt, welche operativen Prozessprobleme mit Prompterator, OPS Core und KnowledgeOS in KI-faehige Use Cases uebersetzt werden koennen.

Er ist public-safe formuliert und enthaelt keine vertraulichen Betriebsdaten, keine Kundennamen, keine internen Nummern und keine personenbezogenen Details.

## Kernpositionierung

Operator Fischer uebersetzt reale Prozesslogik in strukturierte KI-Artefakte:

```text
Prozessbeobachtung
  -> Problemklasse
  -> Datenpunkte
  -> Entscheidungslogik
  -> Governance Gate
  -> Artefakt / Dossier / SOP
  -> Wiederverwendung
```

## Use-Case-Cluster

| Cluster | Problemklasse | KI-faehiger Output | Governance-Fokus |
|---|---|---|---|
| Wareneingang | Uneinheitliche Pruefung und Eskalation | Entscheidungsmodell / Pruefmatrix | Qualitaet, Sperrlogik, Freigabe |
| Cold Chain | Temperaturabweichungen und Dokumentationsdruck | Annahme-/Sperr-/Ablehnungslogik | Produktsicherheit, Nachweis, QS |
| Tourenfreigabe | Unsichere oder unklare Freigabeentscheidungen | Decision Engine / Freigabeprotokoll | Verantwortlichkeit, Plausibilitaet |
| Kommissionierung | Fehler, Suchzeiten, unklare Priorisierung | Fehlpickschutz / Priorisierungslogik | Menschliche Kontrolle, Datenqualitaet |
| Lagerleitstand | Fehlende Uebersicht ueber Prozesszustand | Prozessleitstand / Statusmodell | Eskalation, Owner, Transparenz |
| Safety / Arbeitsschutz | Risiken werden nicht systematisch erfasst | Safety-Checkliste / Risiko-Gate | Arbeitssicherheit, Dokumentation |
| Schulung / Wissen | Erfahrungswissen bleibt informell | SOP / Schulungsmodul / Lernfragen | Freigabe, Aktualitaet, Verantwortliche |
| Kundenprozessaufnahme | Kunden beschreiben Probleme unscharf | Intake-Canvas / Use-Case-Steckbrief | Annahmen, Scope, Erwartungsmanagement |
| AI-Agent-Handoff | Coding-/Agentenauftraege sind zu unscharf | Handoff-Prompt / Pruefprotokoll | Secrets, Scope, Rueckrollbarkeit |
| Portfolio / Proof of Work | Kompetenz ist vorhanden, aber nicht sichtbar | Onepager / Dossier / GitHub-Struktur | Public-Safe, Nachweislogik |

## Detail-Use-Cases

### UC-001: Wareneingang Decision Gate

**Problemklasse:** Wareneingangspruefungen werden uneinheitlich entschieden oder dokumentiert.

**Input:** Lieferung, Warengruppe, Soll-/Ist-Zustand, Temperatur, Menge, Zeitfenster, Abweichung, Pruefstatus.

**Output:** Entscheidung `annehmen / sperren / ablehnen / eskalieren` mit Begruendung.

**Artefakt:** Pruefmatrix, SOP, PDF-Dossier, Schulungsmodul.

**Governance:** QS-Freigabe, Dokumentationspflicht, keine automatische Endentscheidung ohne Owner.

---

### UC-002: Cold-Chain Abweichungslogik

**Problemklasse:** Temperaturabweichungen muessen schnell, nachvollziehbar und risikobewusst eingeordnet werden.

**Input:** Produktgruppe, Grenzwert, gemessene Temperatur, Dauer der Abweichung, Transportstatus, Dokumentation.

**Output:** Abweichungsklasse, Risikostufe, Pruefbedarf, Eskalationsweg.

**Artefakt:** Entscheidungsmodell Cold Chain, Risiko-Matrix, Schulungskarte.

**Governance:** Produktsicherheit, fachliche Freigabe, klare Trennung von Annahme und Sperrung.

---

### UC-003: Tourenfreigabe Decision Engine

**Problemklasse:** Tourenfreigaben brauchen Plausibilitaet, Verantwortlichkeit und dokumentierte Entscheidung.

**Input:** Tourstatus, Fahrzeug-/Ladezustand, Zeitfenster, Risikohinweise, Abweichungen, Freigabeanforderung.

**Output:** Freigabe, Rueckfrage, Sperre oder Eskalation mit Begruendung.

**Artefakt:** Freigabeprotokoll, Prozessmodell, Proof-of-Work-Portfolioseite.

**Governance:** Menschliche Freigabe bleibt Pflicht; KI darf nur strukturieren und pruefen.

---

### UC-004: Lagerleitstand Statusmodell

**Problemklasse:** Prozesszustand im Lager ist verteilt, implizit oder nicht schnell genug entscheidbar.

**Input:** Wareneingang, Kommissionierung, Warenausgang, Rueckstaende, Personalstatus, Stoerungen, Prioritaeten.

**Output:** Statusboard mit Ampellogik, Engpasshinweisen und naechstem Entscheidungspunkt.

**Artefakt:** Leitstand-Canvas, Statusmodell, Management-Dashboard-Blueprint.

**Governance:** Keine falsche Automationsautoritaet; Statusmodell muss fachlich validiert werden.

---

### UC-005: Fehlpickschutz / Kommissionierlogik

**Problemklasse:** Kommissionierfehler, Suchzeiten oder Medienbrueche verursachen Aufwand.

**Input:** Artikel, Lagerplatz, MHD/FIFO, Menge, Auftrag, Pickstatus, Plausibilitaetsregeln.

**Output:** Pruefhinweis, Fehlpickwarnung, Priorisierung oder Rueckfrage.

**Artefakt:** Pruefregel-Canvas, SOP, Trainingsdaten-Sammelplan.

**Governance:** Keine personenbezogene Leistungsueberwachung; Fokus auf Prozessqualitaet.

---

### UC-006: Trainingsdaten-Sammelplan fuer operative KI

**Problemklasse:** KI-Projekte scheitern oft, weil keine sauberen Beispiele, Labels oder Prozessdaten vorliegen.

**Input:** Prozessereignisse, Entscheidungsfaelle, Fehlerklassen, Freigabeentscheidungen, Bild-/Statusdaten ohne Personenbezug.

**Output:** Datenkatalog, Labelschema, Erfassungsregel, Pruefplan.

**Artefakt:** Trainingsdaten-Blueprint, Governance-Hinweis, Public-Safe-Dokumentation.

**Governance:** Datenschutz, Zweckbindung, Anonymisierung, kein sensibles Betriebsdatenleck.

---

### UC-007: Safety / Arbeitsschutz Gate

**Problemklasse:** Sicherheitsrisiken werden nicht systematisch vor Ausfuehrung oder Prozessumstellung geprueft.

**Input:** Arbeitsbereich, Taetigkeit, Hilfsmittel, Risiken, Schutzmassnahmen, Verantwortliche.

**Output:** Risiko-Klasse, Pruefpflicht, Freigabe oder Block.

**Artefakt:** Safety-Checkliste, Governance Gate, Schulungsseite.

**Governance:** Arbeitssicherheit, Dokumentationspflicht, keine Ersetzung fachlicher Sicherheitsbewertung.

---

### UC-008: Kundenprozess-Intake fuer KI-Beratung

**Problemklasse:** Kunden beschreiben KI-Wuensche oft als Toolwunsch statt als Prozessproblem.

**Input:** Rohbeschreibung, Ziel, Schmerzpunkt, bestehender Prozess, Datenlage, Stakeholder, Risiken.

**Output:** Use-Case-Steckbrief mit Problemklasse, Zielbild, Datenbedarf, Risiken und naechstem Schritt.

**Artefakt:** Intake-Canvas, Beratungsdossier, Scope-Dokument.

**Governance:** Erwartungsmanagement, Annahmen markieren, keine unbelegten ROI-Versprechen.

---

### UC-009: SOP-Generator fuer Prozesswissen

**Problemklasse:** Erfahrungswissen ist im Kopf einzelner Personen und nicht sauber dokumentiert.

**Input:** Prozessbeschreibung, Rollen, Schritte, Fehlerquellen, Pruefpunkte, Eskalationen.

**Output:** SOP mit Ziel, Scope, Ablauf, Rollen, Pruefung und Governance.

**Artefakt:** SOP-Dokument, Schulungsmodul, Checkliste.

**Governance:** Fachliche Freigabe, Versionskontrolle, keine unvalidierten Prozessanweisungen.

---

### UC-010: Coding-Agent Handoff Safety

**Problemklasse:** KI-generierte Coding- oder Terminalaufgaben koennen zu breit, riskant oder unklar sein.

**Input:** Ziel, Repo, betroffene Dateien, Nicht-Ziele, Sicherheitsgrenzen, erwarteter Output.

**Output:** Agenten-Handoff mit Scope, Pruefpflichten, Risiko-Klasse und Rueckgabeformat.

**Artefakt:** `docs/CODING-AGENT-HANDOFF.md`, Command Safety Gate, Review-Protokoll.

**Governance:** Keine Secrets, keine destruktiven Befehle, keine unklaren Installationen.

## Bewertungsmatrix

| Use Case | Umsetzbarkeit | Portfolio-Wert | Everlast-Relevanz | Risiko |
|---|---|---|---|---|
| Wareneingang Decision Gate | hoch | hoch | mittel | mittel |
| Cold-Chain Abweichungslogik | hoch | hoch | mittel | mittel |
| Tourenfreigabe Decision Engine | hoch | sehr hoch | mittel | mittel |
| Lagerleitstand Statusmodell | mittel | sehr hoch | hoch | mittel |
| Fehlpickschutz / Kommissionierlogik | mittel | hoch | hoch | mittel |
| Trainingsdaten-Sammelplan | hoch | sehr hoch | sehr hoch | hoch |
| Safety / Arbeitsschutz Gate | hoch | hoch | mittel | hoch |
| Kundenprozess-Intake | sehr hoch | sehr hoch | sehr hoch | niedrig-mittel |
| SOP-Generator | sehr hoch | hoch | hoch | niedrig-mittel |
| Coding-Agent Handoff Safety | hoch | hoch | hoch | hoch |

## Priorisierte Proof-of-Work-Sequenz

1. **Kundenprozess-Intake fuer KI-Beratung**  
   Direkt anschlussfaehig fuer Everlast, weil es Kundenprobleme in KI-Use-Cases uebersetzt.

2. **Trainingsdaten-Sammelplan fuer operative KI**  
   Zeigt Verstaendnis fuer die Vorarbeit, die KI-Projekte praktisch brauchen.

3. **Lagerleitstand Statusmodell**  
   Zeigt operative Prozesskompetenz und Systemdenken.

4. **Tourenfreigabe Decision Engine**  
   Bereits als Proof-of-Work naheliegend und portfoliofaehig.

5. **Coding-Agent Handoff Safety**  
   Zeigt KI-Governance und sichere Multi-Agent-Orchestrierung.

## Wiederverwendungsformate

| Format | Zweck |
|---|---|
| Markdown | Repo-Dokumentation, schnelle Iteration |
| HTML-Dossier | Browser-Vorschau, Praesentation, visuelles Portfolio |
| PDF-Dossier | Versand, Bewerbung, Management-Dokument |
| SOP | Schulung und Prozessstandardisierung |
| Handoff | Uebergabe an Coding- oder Review-Agenten |
| Skill-Eintrag | Wiederverwendung in KnowledgeOS |

## Governance-Grundsatz

> Mensch bleibt Owner. KI bleibt Werkzeug.

Alle Use Cases sind als Entscheidungsunterstuetzung, Strukturierung oder Artefaktgenerierung zu verstehen. Sie ersetzen keine fachliche, rechtliche, datenschutzrechtliche, sicherheitstechnische oder managementseitige Freigabe.

## Status

Build-Status: `v0.1 public-safe process-ai use-case catalog`

Dieser Katalog ist ein additiver Portfolio- und Architekturbaustein. Er veraendert keine bestehende Prompterator-Logik und keine Renderpfade.
