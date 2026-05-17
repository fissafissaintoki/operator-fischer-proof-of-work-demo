# AI Coding Workflow Orchestration Skill

## Status
Als Operator-Fischer-Kompetenz gesetzt.

## Definition
Operator Fischer kann hochwertige Workflow-Prompts fuer Claude Code, Codex und vergleichbare Coding-LLMs entwerfen. Die Kompetenz besteht darin, technische Ziele in kontrollierte, reproduzierbare und pruefbare Ausfuehrungsprotokolle zu uebersetzen.

## Kernlogik
Rohproblem -> Zielbild -> Scope -> Arbeitsverzeichnis -> Dateien -> Sicherheitsgrenzen -> Arbeitsschritte -> Tests -> Git-Diff -> Commit -> Push -> Deployment-Pruefung -> Rollback.

## Qualitaetsstandard
Ein guter Coding-Workflow-Prompt enthaelt:

1. Rolle und Arbeitsmodus
2. exaktes Repository oder Arbeitsverzeichnis
3. Zielbild mit pruefbaren Akzeptanzkriterien
4. klare Verbote und Sicherheitsgrenzen
5. konkrete Datei- und Pfadlogik
6. sequenzielle Arbeitsschritte
7. lokale Tests und Abnahmekriterien
8. Git-Strategie mit Status, Diff, Commit und Push
9. Stoppkriterien bei Konflikten
10. Rollback-Plan
11. strukturiertes Ausgabeformat

## Tool-spezifische Anpassung
- Claude Code: gut fuer lokale Repo-Arbeit, Refactoring, Dateioperationen und Terminal-Workflows.
- Codex: gut fuer zielgerichtete Codeaenderungen, Patches, Tests und Umsetzung in bestehenden Projekten.
- ChatGPT: gut fuer Architektur, Prompt-Design, Fehleranalyse, Governance, Review und Steuerungslogik.

## Governance
Mensch bleibt Owner. KI bleibt Werkzeug. Keine Secrets lesen oder ausgeben. Keine .env-Dateien committen. Kein Force-Push als Standard. Keine fremden Systeme testen. Keine riskanten Nebenwirkungen ohne explizite Freigabe.

## Bewerbungsnahe Kurzform
Operator Fischer entwickelt reproduzierbare Workflow-Prompts fuer agentische Coding-Systeme wie Claude Code und Codex. Dadurch lassen sich technische Aufgaben mit Scope, Tests, Git-Workflow, Deployment-Pruefung, Rollback und Governance kontrolliert ausfuehren.
