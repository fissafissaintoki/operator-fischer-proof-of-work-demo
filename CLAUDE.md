# CLAUDE.md — Prompterator Development Guide

## Projekt

Prompterator ist ein Web-MVP von Operator Fischer.

Live-Domain:

```text
https://www.prompterator.de
```

Repository:

```text
fissafissaintoki/operator-fischer-proof-of-work-demo
```

## Ziel

Prompterator verwandelt Rohinput in strukturierte Arbeitsartefakte:

```text
Rohinput -> Problemklasse -> Modus -> Artefakt-Blueprint -> Qualitätsprüfung -> Governance -> Masterprompt -> nächste Schritte
```

## Aktueller Stack

- Python Standard Library HTTP Server
- OpenAI Responses API im Backend
- Render Deployment
- checkdomain DNS
- einfache HTML/CSS/JS-Oberfläche
- Ring-2 Security/Cost Guard im Backend

## Nicht brechen

Diese Punkte dürfen nicht entfernt oder geschwächt werden:

- OPENAI_API_KEY bleibt ausschließlich Environment Variable
- Kein API-Key im Frontend
- Kein API-Key im GitHub-Repo
- Rate Limit
- Input-Limit
- Output-Limit
- Tages-/Monatslimit
- restriktiver CORS
- Sicherheitsheader
- `/health`
- `/sitemap.xml`
- `/robots.txt`
- SEO-Landingpages
- Google Search Console / SEO-Grundstruktur

## Wichtige Dateien

```text
server.py        Backend, Security, API-Routen, SEO-Routen
index.html       Haupt-UI
pages/           SEO-Landingpages
README.md        Repo-Beschreibung
docs/            Operator-Fischer-Dokumente
Procfile         Render Start Command
requirements.txt aktuell leer/Standard-Library
```

## Arbeitsregeln für Claude

1. Keine Secrets ausgeben oder anfordern.
2. Keine Schlüssel, Tokens oder Zugangsdaten in Dateien schreiben.
3. Keine Änderungen direkt auf `main`, wenn ein PR-Workflow verfügbar ist.
4. Bei größeren Änderungen zuerst Plan ausgeben.
5. Änderungen klein halten und begründen.
6. Security vor UI-Spielerei.
7. Keine überkomplexe Architektur ohne Nutzen.
8. macOS-kompatible Befehle verwenden.
9. Prompterator soll einfach bleiben.
10. Mensch bleibt Owner, KI bleibt Werkzeug.

## Gewünschte Ausbauprioritäten

### Phase 1 — Stabilisierung

- Code strukturieren ohne Overengineering
- Fehlerseiten verbessern
- `/api/usage` sauber sichtbar oder intern halten
- Tests für Health, Sitemap, Robots, Landingpages
- einfache lokale Testbefehle dokumentieren

### Phase 2 — UI vorsichtig verbessern

- bestehende einfache Oberfläche behalten
- klarere Copy-Funktion optional ergänzen
- mobile Darstellung verbessern
- keine große UI-Revolution ohne Freigabe

### Phase 3 — Sicherheit

- serverseitiger Admin-Key optional für interne Routen
- stärkerer Abuse-Schutz
- robustere Origin-Prüfung
- klarere Kostenbremse
- Logging ohne personenbezogene Daten und ohne Secrets

### Phase 4 — SEO

- Landingpages ausbauen
- interne Links ergänzen
- bessere Snippets
- strukturierte Daten prüfen
- Sitemap aktuell halten

## Qualitätsprüfung vor jedem Vorschlag

Vor Ausgabe oder Änderung prüfen:

```text
1. Läuft lokal?
2. Bleibt OPENAI_API_KEY geheim?
3. Bricht Render nicht?
4. Bricht prompterator.de nicht?
5. Bleibt /health verfügbar?
6. Bleibt /sitemap.xml verfügbar?
7. Bleibt Ring-2 aktiv?
8. Ist die Änderung klein genug?
```

## Erwartetes Ausgabeformat für Claude

Bei Analyse:

```text
## Befund
## Risiko
## Empfohlene Änderung
## Dateien betroffen
## Testplan
## Rollback
```

Bei Codeänderung:

```text
## Ziel
## Änderung
## Patch / Dateien
## Testbefehle
## Deployment-Hinweis
```

## Kurzauftrag

Verbessere Prompterator schrittweise, sicher und produktionsnah. Keine Secrets. Keine unnötige Komplexität. Ring-2 bleibt Pflicht. UI nur vorsichtig verbessern. SEO und Stabilität priorisieren.
