# Prompterator

**Live:** https://www.prompterator.de  
**Projekt:** AI-Operations-Proof-of-Work von Peter Fischer / Operator Fischer  
**Repository:** `fissafissaintoki/operator-fischer-proof-of-work-demo`

---

## Executive Summary

Prompterator ist ein eigenes Proof-of-Work-Projekt zur KI-gestützten Workflow-Orchestrierung.

Die Webapp zeigt, wie roher Input in strukturierte Use Cases, Arbeitsartefakte, Entscheidungslogiken, Qualitätsprüfungen und wiederverwendbare Prompts überführt werden kann.

Der Fokus liegt nicht auf KI als Spielerei, sondern auf kontrollierter Umsetzung:

```text
Rohinput -> Problemklasse -> Modus -> Artefakt -> Qualitätsprüfung -> Governance -> Wiederverwendung
```

Prompterator verbindet operative Prozesslogik mit einer praktisch umgesetzten Webapp, API-Anbindung, Deployment, GitHub-Versionierung, Sicherheitslogik, Rollback und dokumentierter KI-Systemkompetenz.

---

## Was dieses Projekt demonstriert

| Bereich | Nachweis |
|---|---|
| KI-Workflow-Orchestrierung | strukturierte Transformation von Rohinput in verwertbare Artefakte |
| AI Operations | Webapp, Backend, API, Deployment, Monitoring-/Notfalllogik |
| Governance-first KI-Nutzung | Qualitätsprüfung, Sicherheitsgrenzen, Kostenkontrolle, Rollback |
| Coding-Agent-Steuerung | Claude-/Codex-Workflow-Prompts, Workspace-Prüfung, Git-Logik |
| Autodidaktische KI-Systemkompetenz | eigenständiger Aufbau von Workflows, Artefakten und Betriebslogik |
| Prozessintelligenz | Übertragung operativer Logistik- und Prozesslogik auf KI-Systeme |

---

## Kernnutzen

Prompterator unterstützt dabei, unklare Anforderungen in eine arbeitsfähige Struktur zu bringen:

- Problemklasse erkennen
- Fakten, Annahmen und Hypothesen trennen
- passenden Arbeitsmodus bestimmen
- Artefakt-Blueprint erzeugen
- direkt nutzbares Arbeitsartefakt liefern
- Qualitätsprüfung ergänzen
- Governance-Gates definieren
- wiederverwendbaren Masterprompt erstellen
- nächste Schritte ableiten

---

## Technischer Aufbau

```text
Nutzer
  ↓
Prompterator Web-Interface
  ↓
Python Backend / server.py
  ↓
/api/generate
  ↓
OpenAI API
  ↓
strukturierter Output
  ↓
Copy / Weiterverwendung / Portfolio / Workflow
```

| Ebene | Umsetzung |
|---|---|
| Frontend | `index.html`, HTML/CSS/JavaScript |
| Backend | `server.py`, Python HTTP Server |
| KI-Anbindung | OpenAI Responses API |
| Deployment | Render |
| Versionierung | GitHub |
| Domain | prompterator.de |
| Prüfung | Healthcheck, Safe Shield Check, Git-Diff, CI-Guardrail |

---

## Live-Seiten

- https://www.prompterator.de/
- https://www.prompterator.de/ki-prompt-generator
- https://www.prompterator.de/ki-use-case-generator
- https://www.prompterator.de/operator-fischer-method
- https://www.prompterator.de/sitemap.xml
- https://www.prompterator.de/robots.txt

---

## Governance / Sicherheit / Betrieb

Prompterator wurde nicht nur funktional gebaut, sondern mit Betriebslogik versehen.

| Bereich | Umsetzung |
|---|---|
| Kostenkontrolle | Tages-/Monatslimits, Tokenlimits, Kill-Switch |
| Zugriffskontrolle | Origin-Prüfung, Admin-Token für interne Usage-Daten |
| Input-Schutz | Body-Limits, JSON-Feldprüfung, Content-Type-Prüfung |
| Informationsschutz | minimale Health-Ausgabe, keine Security-Details im UI |
| Betrieb | Rollback-Playbook, Emergency-Brake-Logik |
| Testing | defensiver Safe Shield Check |
| Git-Schutz | `.gitignore`, CI-/Guardrail-Logik |

Notbremse:

```text
GENERATE_ENABLED=false
```

---

## Dokumentierte Artefakte

| Artefakt | Zweck |
|---|---|
| `docs/PROMPTERATOR-CASE-STUDY-v1.md` | vollständige Case Study |
| `docs/ROLLBACK-RING-SYSTEM.md` | kontrollierter Rückbau |
| `docs/RING9-BLAST-RADIUS-AND-EMERGENCY-BRAKE.md` | Notfalllogik und Ausfallklassen |
| `tests/security/safe_prompterator_security_check.py` | defensiver Security-Testläufer |
| `docs/OPERATOR-FISCHER-NEW-CHAT-BOOT-v1.md` | reproduzierbarer Startkontext |
| `docs/HZ-SKILL-EXTRACTION-PROTOCOL.md` | Skill-Extraktionslogik |
| `docs/AI-CODING-WORKFLOW-ORCHESTRATION-SKILL.md` | Claude-/Codex-Workflow-Orchestrierung |
| `docs/WORKSPACE-AWARE-CODING-AGENT-ORCHESTRATION-SKILL.md` | Workspace-validierte Agentensteuerung |
| `docs/PROMPT-LAYER-SEPARATION-SKILL.md` | Trennung von Steuerlogik, Auftrag, Tests und Rollback |

---

## Operator-Fischer-Kompetenzen im Projekt

### Autodidaktische KI-Systemkompetenz

Eigenständiges Erarbeiten, Testen und Operationalisieren von KI-Workflows, Prompt-Architekturen und Coding-Agent-Steuerung ohne starre externe Vorlage.

### AI Coding Workflow Orchestration

Reproduzierbare Workflow-Prompts für Claude Code, Codex und vergleichbare Coding-LLMs mit Scope, Tests, Git-Workflow, Deployment-Prüfung und Rollback.

### Workspace-Aware Coding-Agent Orchestration

Coding-Agenten validieren vor jeder Änderung Workspace, Repository, Remote und Pflichtdateien. Bei falscher Umgebung wird gestoppt statt am falschen Projekt gearbeitet.

### Prompt Layer Separation

Komplexe Prompts werden in funktionale Schichten getrennt: Steuerung, Governance, Zielbild, Datei-/Pfadlogik, Tests, Git, Deployment und Rollback.

### HZ Skill Extraction

Wiederverwendbare Fähigkeiten werden aus Arbeitskontexten extrahiert und als KnowledgeOS-Artefakte dokumentiert.

---

## Realweltliche Positionierung

Peter Fischer verbindet operative Prozess- und Supply-Chain-Erfahrung mit autodidaktisch aufgebauter KI-Systemkompetenz.

Prompterator zeigt diese Arbeitsweise praktisch:

- ein reales Live-System
- ein nachvollziehbarer GitHub-Verlauf
- eine API-gestützte KI-Webapp
- Security- und Rollback-Logik
- dokumentierte Coding-Agent-Steuerung
- wiederverwendbare Skill- und Governance-Artefakte

Das Projekt ist kein fertiges Enterprise-SaaS und kein klassisches Fullstack-Developer-Portfolio. Es ist ein AI-Operations-Proof-of-Work: eine praktische Demonstration, wie KI kontrolliert in Arbeitsprozesse eingebunden werden kann.

---

## Abgrenzung

Prompterator ist aktuell nicht zu positionieren als:

- fertiges Enterprise-SaaS
- Security-Produkt
- SAP-Integration
- klassisches Fullstack-Senior-Developer-Projekt

Prompterator ist zu positionieren als:

- KI-Workflow-Orchestrierungsprojekt
- Prozessintelligenz-Demonstrator
- AI-Operations-Proof-of-Work
- praktisches MVP mit Governance-Logik
- Portfolio- und Bewerbungsnachweis

---

## Kurzfassung

Prompterator demonstriert, wie Rohinput durch KI-gestützte Workflow-Orchestrierung in strukturierte Use Cases, Arbeitsartefakte und wiederverwendbare Entscheidungslogiken überführt werden kann. Das Projekt verbindet Domain, Webapp, Backend, API-Anbindung, GitHub, Deployment, Sicherheitslogik, Rollback und dokumentierte KI-Systemkompetenz.
