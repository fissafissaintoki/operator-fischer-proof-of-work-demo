# Prompterator Rollback Playbook

Ziel: Sicherheits- oder Interface-Änderungen kontrolliert zurückbauen, ohne Secrets offenzulegen und ohne unkontrollierte Force-Pushes.

## Aktuelle relevante Sicherheits-Commits

- Ring 7 CI: `516d9b321df757d817dc89a1962e9661a3f041fe`
- Ring 6 Defaults: `9e67e82137ab9f2292a4d56f3a4715b411b1ddd6`
- Ring 5 Stealth: `0ef7d49f7c90de7e51738f64c71d3469b27b7c43`
- Ring 3 App Firewall: `5a265a98a0b9cd5f4f728b46e48265a37230cbe4`

## Grundsatz

Bevorzugt wird `git revert`, nicht `git reset --hard` auf `main`. Dadurch bleibt die Historie nachvollziehbar und Render kann sauber neu deployen.

## Standard-Rollback: letzten Commit zurücknehmen

```bash
git pull origin main
git revert HEAD
git push origin main
```

## Einen bestimmten Commit zurücknehmen

```bash
git pull origin main
git revert <COMMIT_SHA>
git push origin main
```

Beispiel Ring 7 zurücknehmen:

```bash
git revert 516d9b321df757d817dc89a1962e9661a3f041fe
git push origin main
```

## Mehrere Commits kontrolliert zurücknehmen

Neueste Commits zuerst revertieren.

```bash
git revert 516d9b321df757d817dc89a1962e9661a3f041fe
git revert 9e67e82137ab9f2292a4d56f3a4715b411b1ddd6
git push origin main
```

## Sofort-Entschärfung ohne Code-Rollback über Render

Diese Environment-Werte können kurzfristig gesetzt werden:

```text
GENERATE_ENABLED=false
REQUIRE_ORIGIN_FOR_GENERATE=false
RATE_LIMIT_MAX_REQUESTS=6
MAX_INPUT_CHARS=4000
MAX_OUTPUT_TOKENS=1800
DAILY_REQUEST_LIMIT=30
MONTHLY_REQUEST_LIMIT=300
```

## Nach jedem Rollback testen

```bash
curl -i https://www.prompterator.de/health
curl -i https://www.prompterator.de/api/usage
```

Erwartung öffentlich:

```json
{"status":"ok"}
```

`/api/usage` ohne Token muss `404` liefern.

## Nicht tun

- Keine API-Keys posten.
- Keine `.env` committen.
- Kein `git push --force` auf `main`, außer bewusst als Notfallmaßnahme.
- Keine Backup-Dateien committen.
