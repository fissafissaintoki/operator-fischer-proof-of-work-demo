# Ring 8 Safe Shield Check

Ziel: defensive Prüfung der Prompterator-Schutzschichten ohne Lasttest, ohne Exploit-Payloads und ohne fremde Ziele.

## Grundsatz

Dieses Verzeichnis ist für kontrollierte Tests auf eigenen oder ausdrücklich autorisierten Systemen gedacht.

Nicht enthalten:

- keine Massenscans
- keine Exploit-Sammlungen
- keine Umgehungslogik
- keine fremden Ziele
- keine Secrets
- keine API-Key-Ausgabe

## Ausführen

```bash
python3 tests/security/safe_prompterator_security_check.py
```

Optional mit anderem autorisiertem Ziel:

```bash
PROMPTERATOR_TARGET=https://www.prompterator.de \
PROMPTERATOR_ORIGIN=https://www.prompterator.de \
python3 tests/security/safe_prompterator_security_check.py
```

## Geprüfte Muster

- öffentlicher Healthcheck bleibt minimal
- interner Usage-Endpunkt bleibt ohne Token verborgen
- Generator ohne Origin wird blockiert
- falscher Content-Type wird blockiert
- unerwartete JSON-Felder werden blockiert
- große Eingaben werden blockiert
- kontrollierte Low-Volume-Rate-Limit-Prüfung

## Erwartete Statuscodes

| Status | Bedeutung |
|---:|---|
| 200 | Anfrage akzeptiert |
| 400 | ungültige Anfrage |
| 403 | Zugriffskontext nicht erlaubt |
| 404 | nicht vorhanden oder bewusst verborgen |
| 413 | Eingabe zu groß |
| 415 | falscher Content-Type |
| 429 | Rate-Limit greift |

## Betriebsregel

Wenn die Tests Fehler zeigen: nicht panisch weiter härten. Erst Ursache trennen:

1. Codefehler
2. Render-Environment
3. Browser-/Origin-Kontext
4. Rate-Limit zu streng
5. erwartetes Verhalten falsch interpretiert

Danach gezielt patchen oder per Render-Environment entschärfen.
