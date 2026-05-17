# Prompt Layer Separation Skill

## Status
Aktiv als Operator-Fischer-Skill.

## Deutsche Bezeichnung
Prompt-Schichten-Trennung

## Internationale Bezeichnung
Prompt Layer Separation

## Definition
Operator Fischer kann komplexe Prompts in getrennte Schichten zerlegen: Steuerlogik, Governance, Workspace-Pruefung, Zielauftrag, Ausfuehrungsschritte, Tests, Git-/Deployment-Regeln und Outputformat. Dadurch wird klar, welcher Teil eines Prompts die eigentliche Agentensteuerung ist und welcher Teil nur den fachlichen Wunsch beschreibt.

## Ausloeser / Wann nutzen?
Diesen Skill nutzen, wenn:

- Claude Code, Codex oder ein anderer Coding-Agent gesteuert wird.
- ein Prompt zu lang, chaotisch oder vermischt wirkt.
- unklar ist, ob der Agent den richtigen Kontext hat.
- technische Aufgaben sicher, reproduzierbar und rueckbaubar ausgefuehrt werden sollen.
- zwischen Wunsch, Arbeitsrahmen, Pruefung und Umsetzung getrennt werden muss.

## Kernlogik

```text
Fachlicher Wunsch
→ Steuerblock
→ Sicherheitsgrenzen
→ Workspace-/Repo-Pruefung
→ konkrete Arbeitsschritte
→ Tests
→ Git-/Deployment-Regeln
→ Ausgabeformat
→ Rollback
```

## Prompt-Schichten

| Schicht | Funktion |
|---|---|
| Rolle | definiert, aus welcher Perspektive der Agent arbeitet |
| Workspace-Check | verhindert Arbeit im falschen Projekt |
| Scope | begrenzt, was geaendert werden darf |
| Verbote | verhindert Secrets, falsche Commits, Force-Push, private Dateien |
| Zielbild | beschreibt den gewuenschten Endzustand |
| Datei-/Pfadlogik | sagt exakt, welche Dateien relevant sind |
| Ausfuehrung | beschreibt die konkrete technische Aenderung |
| Tests | macht Ergebnis pruefbar |
| Git-Regeln | regelt Diff, Commit, Push, Rebase und Konflikte |
| Rollback | definiert Rueckweg bei Fehlern |
| Ausgabeformat | zwingt klare Rueckmeldung statt Chaosbericht |

## Wiederverwendbares Prompt-Modul

```text
Trenne den Auftrag in Schichten:

1. Steuerlogik: Rolle, Arbeitsmodus, Workspace-Pruefung.
2. Governance: Verbote, Scope, Stoppkriterien.
3. Zielbild: Was soll am Ende sichtbar/funktional anders sein?
4. Umsetzung: Welche Dateien und Funktionen werden geaendert?
5. Pruefung: Welche Tests und Diffs sind Pflicht?
6. Git/Deployment: Commit, Rebase, Push, Deploy-Check.
7. Rueckmeldung: Ausgabeformat mit Zustand, Umsetzung, Tests, Git und naechster Aktion.

Aendere nichts, bevor Steuerlogik und Workspace validiert sind.
```

## Qualitaetskriterien

Ein guter geschichteter Prompt:

- trennt Wunsch von Steuerung.
- beginnt mit Workspace- und Repo-Validierung.
- enthaelt harte Stoppkriterien.
- nennt relevante Dateien und Pfade.
- gibt Tests und Abnahmekriterien vor.
- verhindert private oder geheime Daten im Commit.
- definiert Git- und Deployment-Verhalten.
- gibt ein strukturiertes Rueckgabeformat vor.

## Risiken / Grenzen

- Zu viele Schichten koennen einfache Aufgaben ueberladen.
- Der Skill ersetzt keine fachliche Pruefung des Ergebnisses.
- Bei falschem Workspace muss der Agent stoppen, nicht improvisieren.
- Bei produktiven Systemen bleibt menschliche Freigabe noetig.

## Portfolio-Formulierung

Operator Fischer kann komplexe KI- und Coding-Agent-Prompts in funktionale Schichten zerlegen. Dadurch werden technische Agenten nicht nur mit Aufgaben beauftragt, sondern mit klarer Steuerlogik, Governance, Tests, Git-Regeln, Deployment-Pruefung und Rollback gefuehrt.

## Kurzform

Prompt-Schichten-Trennung: professionelle Zerlegung von Agenten-Prompts in Steuerung, Governance, Zielbild, Ausfuehrung, Tests, Git-Logik, Deployment und Rollback.
