# Workspace-Aware Coding-Agent Orchestration Skill

## Status
Aktiv als Operator-Fischer-Skill.

## Deutsche Bezeichnung
Workspace-bewusste Coding-Agent-Orchestrierung

## Internationale Bezeichnung
Workspace-Aware Coding-Agent Orchestration

## Definition
Operator Fischer kann Coding-Agenten wie Codex, Claude Code und vergleichbare Systeme so instruieren, dass sie vor jeder technischen Änderung zuerst ihre tatsächliche Ausführungsumgebung prüfen. Der Skill verhindert, dass ein Agent in einem falschen Workspace, falschen Repository oder fremden Projekt arbeitet.

## Auslöser / Wann nutzen?
Diesen Skill nutzen, wenn:

- Codex oder Claude Code an einem lokalen Projekt arbeiten soll.
- ein Pfad wie `/Users/ffooc/Downloads/prompterator-api` genannt wird.
- die Agentenumgebung möglicherweise isoliert ist, z. B. `/workspace/...`.
- ein Agent meldet, dass das erwartete Repo nicht existiert.
- Änderungen an `index.html`, `server.py`, Git, Render, Assets oder Deployment geplant sind.
- verhindert werden soll, dass der Agent versehentlich an einem falschen Projekt arbeitet.

## Kernlogik

```text
Zielauftrag
→ Workspace prüfen
→ Repo validieren
→ Projektdateien erkennen
→ Remote prüfen
→ Stoppkriterien anwenden
→ erst dann Dateiänderung erlauben
```

## Standard-Prüfsequenz

Ein workspace-bewusster Coding-Agent-Prompt enthält vor jeder Umsetzung:

```bash
pwd
ls -la
git status
git branch --show-current
git remote -v
test -f index.html && echo "index.html gefunden"
test -f server.py && echo "server.py gefunden"
```

## Stoppkriterien

Der Agent muss stoppen, wenn:

- das erwartete Repository nicht sichtbar ist.
- `server.py` fehlt, obwohl eine Backend-App erwartet wird.
- `index.html` fehlt, obwohl die UI geändert werden soll.
- kein Git-Remote konfiguriert ist.
- das Remote nicht zum erwarteten Repo passt.
- der Workspace offensichtlich ein anderes Projekt enthält.
- lokale private Dateien oder fremde Ordner drohen mitcommitted zu werden.

## Wiederverwendbares Prompt-Modul

```text
Bevor du Änderungen vornimmst, validiere den Workspace.
Arbeite nicht blind in einem falschen Projekt.

Prüfe:
- pwd
- ls -la
- git status
- git branch --show-current
- git remote -v
- Existenz von index.html
- Existenz von server.py

Wenn der Workspace nicht eindeutig das erwartete Projekt ist, ändere keine Dateien.
Gib stattdessen aus:
"Falscher Workspace. Bitte korrektes Repository mounten oder klonen."

Nur wenn Repository, Remote und Pflichtdateien passen, darfst du fortfahren.
```

## Teilfähigkeiten

- Agentenumgebungen von lokalen Mac-Pfaden unterscheiden.
- falsche Codex-/Claude-Workspaces erkennen.
- Repository-Identität über Dateien und Remote validieren.
- technische Umsetzungsaufträge mit Stoppkriterien absichern.
- fehlerhafte Agentenarbeit an falschen Projekten verhindern.
- Git- und Deployment-Risiken vor der Änderung reduzieren.

## Qualitätskriterien

Ein guter Workflow erfüllt:

- keine Dateiänderung vor Workspace-Validierung
- keine Arbeit in falschen Projektordnern
- klare Ausgabe bei falschem Workspace
- keine Secrets, keine privaten Dokumente, kein Force-Push
- nur relevante Dateien adden und committen
- klare Tests vor Commit und Push

## Risiken / Grenzen

- Der Skill ersetzt keinen Zugriff auf das richtige Repo.
- Wenn Codex den lokalen Mac-Pfad nicht mounten kann, muss das Repo explizit bereitgestellt oder geklont werden.
- Ein Agent darf nicht improvisieren, wenn Projektstruktur und Remote nicht passen.

## Portfolio-Formulierung

Operator Fischer kann Coding-Agenten workspace-bewusst orchestrieren. Vor jeder technischen Änderung werden Ausführungsumgebung, Repository, Remote, Pflichtdateien und Stoppkriterien geprüft. Dadurch wird verhindert, dass KI-Agenten versehentlich an falschen Projekten arbeiten oder unkontrollierte Änderungen ausführen.

## Kurzform

Workspace-bewusste Coding-Agent-Orchestrierung: kontrollierte Steuerung von Codex, Claude Code und ähnlichen Systemen durch verpflichtende Workspace-, Repository- und Remote-Validierung vor jeder Dateiänderung.
