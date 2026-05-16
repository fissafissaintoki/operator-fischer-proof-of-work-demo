# Ring 9 – Blast Radius & Emergency Brake

Ziel: Verstehen, wie Prompterator durch einzelne Fehlbedienungen ausfallen kann, und dafür sichere Gegenmaßnahmen definieren.

## Grundsatz

Dieses Dokument liefert keine destruktiven Befehle. Es beschreibt Ausfallklassen, Schutzlogik und sichere Abschalt-/Rollback-Wege.

## One-Command-Failure-Klassen

| Klasse | Was schiefgehen kann | Schutz / Gegenmaßnahme |
|---|---|---|
| Bad Deploy | Ein fehlerhafter Commit wird deployed | CI, `python -m py_compile`, Rollback via `git revert` |
| Env Misconfiguration | falsche oder fehlende Environment Variable | Render-Env prüfen, dokumentierte Defaults, Healthcheck |
| API Cost Runaway | zu viele erfolgreiche Generator-Anfragen | Rate-Limit, Tages-/Monatslimit, OpenAI-Budget, Kill-Switch |
| Public Info Leak | Healthcheck oder UI verrät interne Details | Stealth-Health, keine Ring-Anzeige im UI |
| Admin Exposure | interne Endpunkte sind sichtbar | `/api/usage` ohne Token = 404 |
| Backup Leak | lokale Backup-Dateien landen im Repo | `.gitignore`, CI-Guardrail |
| DNS/CDN Misroute | Domain zeigt falsch oder gar nicht | DNS-Änderungen nur dokumentiert, keine Schnelländerungen ohne Test |

## Sicherer Emergency Brake

Wenn Kosten, Missbrauch oder Fehler auftreten:

1. In Render `GENERATE_ENABLED=false` setzen.
2. Deployment abwarten.
3. Healthcheck prüfen.
4. Ursache trennen: Code, Env, DNS, Rate-Limit, Origin, OpenAI.
5. Erst danach patchen oder revertieren.

## Sicherer Rollback

```bash
git pull origin main
git log --oneline -10
git revert <COMMIT_SHA>
git push origin main
```

Kein Force-Push auf `main`, außer als bewusst dokumentierter Notfall.

## Defensive Test-Routine

```bash
python3 tests/security/safe_prompterator_security_check.py
```

Bei wiederholten Testläufen 60–90 Sekunden warten, damit das Rate-Limit nicht die übrigen Prüfergebnisse überdeckt.

## Ring-9-Entscheidungslogik

| Signal | Sofortmaßnahme | Danach |
|---|---|---|
| Kosten steigen | `GENERATE_ENABLED=false` | Usage prüfen, Limits prüfen |
| Generator 500/502 | Healthcheck prüfen | OpenAI/Backend-Logs prüfen |
| viele 404/429 | nichts panisch ändern | Monitoring prüfen, Rate-Limit belassen |
| UI kaputt | letzten Interface-Commit revertieren | Browser hart neu laden |
| CI rot | nicht deployen / nicht weiter patchen | Fehler lokal reproduzieren |

## Nicht tun

- keine destruktiven Ein-Befehl-Aktionen als Routine
- keine Secrets posten
- keine API-Keys in Chat, README oder Screenshot
- kein `git push --force` auf `main` als Standardmittel
- keine Lasttests gegen Live-System

## Zielbild

Ring 9 macht das System nicht nur härter, sondern kontrollierbarer:

- Ausfallklassen bekannt
- Notbremse definiert
- Rollback dokumentiert
- Tests vorhanden
- Kostenrisiko begrenzt
- Sicherheitsdetails nicht öffentlich beworben
