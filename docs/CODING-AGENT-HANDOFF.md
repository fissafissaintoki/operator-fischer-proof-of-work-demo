# Coding Agent Handoff

## Zweck

Dieses Dokument ist die sichere Uebergabevorlage fuer Codex, Claude, GitHub-Agenten oder andere Coding-Assistenten, die am Prompterator-/OPS-Core-Repository arbeiten.

Ziel ist kontrollierte Ausfuehrung: erst pruefen, dann aendern.

## Standardauftrag

```text
Du arbeitest in einem bestehenden GitHub-Repository.

Arbeitsprinzip:
1. Repo-Zustand pruefen.
2. Relevante Dateien lesen.
3. Risiko und Scope markieren.
4. Kleine additive Aenderungen bevorzugen.
5. Keine Secrets lesen, erzeugen oder ausgeben.
6. Keine destruktiven Befehle ohne explizite Begruendung.
7. Ergebnis als Diff-/Dateiliste und Pruefprotokoll zurueckgeben.
```

## Pflichtpruefung vor Aenderung

- Welche Dateien sind betroffen?
- Welche Endpoints oder Renderpfade koennen brechen?
- Gibt es personenbezogene, vertrauliche oder unternehmensinterne Daten?
- Sind API-Keys, Tokens, `.env`-Dateien oder Credentials betroffen?
- Gibt es Loesch-, Ueberschreibungs- oder Deployment-Risiko?
- Ist ein Rollback moeglich?

## Zulassungsklassen

| Klasse | Bedeutung | Erlaubnis |
|---|---|---|
| SAFE | Dokumentation, README, additive Markdown-Dateien | Direkt moeglich |
| LOW | Kleine UI-/Textkorrekturen ohne Logikbruch | Nach Sichtpruefung |
| MEDIUM | Backend-/Endpoint-Aenderungen | Nur mit Testplan |
| HIGH | Auth, Datenverarbeitung, Deployment, API-Keys | Nur mit Freigabe |
| BLOCK | Secrets, Datenexfiltration, destructive commands | Nicht ausfuehren |

## macOS Command Safety Gate

Vor Terminalbefehlen immer pruefen:

```text
Befehl:
Wirkung:
Dateizugriff:
Netzwerkzugriff:
Rechtebedarf:
Loeschrisiko:
Secret-Risiko:
Rollback:
Urteil: SAFE / LOW / MEDIUM / HIGH / BLOCK
```

## Repo-spezifische Hinweise

- Projekt: Prompterator / Operator-Fischer Proof of Work.
- Default-Branch: `main`.
- Oeffentliches Repository: keine vertraulichen Betriebsdaten.
- Bestehender README-Status: MVP / Proof of Work, nicht produktionsreifes SaaS.
- Bestehende Architektur: PDF- und HTML-Pfad lesen aus demselben Use-Case-Modell.
- Bestehende Governance-Regel: Mensch bleibt Owner. KI bleibt Werkzeug.

## Aenderungsstrategie

Prioritaet:

1. Dokumentation und Architektur sichtbar machen.
2. Bestehende Renderpfade nicht brechen.
3. Public-safe Portfolio-Wert erhoehen.
4. Governance klarer machen.
5. Erst danach Code erweitern.

## Rueckgabeformat fuer Agenten

```text
Status:
Geaenderte Dateien:
Nicht geaenderte Dateien:
Risiko-Einstufung:
Tests / Pruefung:
Offene Punkte:
Empfohlener naechster Schritt:
```

## Nicht erlaubt

- Keine echten API-Keys oder Tokens in Dateien schreiben.
- Keine `.env`-Inhalte ausgeben.
- Keine fremden Installationsskripte blind ausfuehren.
- Kein `curl | sh` ohne manuelle Pruefung.
- Kein `sudo` ohne harte Notwendigkeit.
- Kein rekursives Loeschen ohne vorherige Dateiliste und Freigabe.
- Keine echten Betriebsdaten in Demoartefakte einbauen.
