# Claude Safe Security Audit Prompt

Ziel: Claude Code soll Prompterator defensiv prüfen und Schutzringe verbessern, ohne Lastangriffe, Exploits, Umgehungslogik oder Tests gegen fremde Systeme zu erzeugen.

## Claude-Befehl

```text
Du arbeitest im lokalen Repository `prompterator-api` als defensiver Security-, Reliability- und Governance-Reviewer.

WICHTIGER SCOPE:
- Zielsystem ist ausschließlich mein eigenes Projekt Prompterator.
- Keine fremden Domains testen.
- Keine Massenscans.
- Keine DDoS-, Flood-, Stress- oder Parallel-Lasttests.
- Keine Exploit-Payload-Sammlungen.
- Keine Umgehungslogik für Schutzmechanismen.
- Keine Secrets auslesen, anzeigen oder in Dateien schreiben.
- Keine Environment-Dateien committen.

AUFGABE:
1. Prüfe die bestehende Schutzarchitektur im Repo:
   - `server.py`
   - `index.html`
   - `.gitignore`
   - `.github/workflows/ring7-ci.yml`
   - `tests/security/safe_prompterator_security_check.py`
   - `docs/ROLLBACK-RING-SYSTEM.md`
   - `docs/RING9-BLAST-RADIUS-AND-EMERGENCY-BRAKE.md`

2. Erstelle eine defensive Bewertung:
   - Welche Schutzringe existieren?
   - Welche Risiken sind bereits reduziert?
   - Welche Single Points of Failure bleiben?
   - Welche Kostenrisiken bleiben?
   - Welche Fehlkonfigurationen wären kritisch?

3. Verbessere nur sichere Schutzmaßnahmen:
   - bessere Dokumentation
   - bessere Testausgaben
   - klarere Fehlinterpretationshinweise
   - bessere README-Struktur
   - CI-Prüfung für sichere Dateien
   - keine öffentlichen Security-Details im UI
   - keine riskanten Testfunktionen

4. Erzeuge, falls sinnvoll, eine neue Datei:
   `docs/RING10-MONITORING-AND-INCIDENT-PLAYBOOK.md`

5. Falls Code geändert wird:
   - nur defensive, niedrigriskante Änderungen
   - `python3 -m py_compile server.py` prüfen
   - keine Live-Last erzeugen
   - keinen API-Key benötigen
   - Änderungen klar im Committext beschreiben

AUSGABEFORMAT:
## Defensive Security Review
## Gefundene Risiken
## Empfohlene Verbesserungen
## Geänderte Dateien
## Tests
## Nächste sichere Schritte

ZIEL:
Prompterator soll robuster, kontrollierbarer und besser dokumentiert werden, ohne einen Angriffsmodus oder Missbrauchswerkzeuge einzubauen.
```

## Nutzung

Diesen Prompt in Claude Code im lokalen Repo verwenden. Claude darf damit prüfen und verbessern, aber nicht angreifen.

## Zweck

Dieses Artefakt ersetzt destruktive Angriffsbefehle durch einen sicheren Red-Team-ähnlichen Defensive-Review-Prozess.
