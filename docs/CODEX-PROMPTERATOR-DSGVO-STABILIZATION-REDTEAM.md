# Codex Workflow – Prompterator DSGVO-Stabilisierung mit Red-Team-Pruefung

## Ziel

Prompterator soll nach Phase 4 datenschutzseitig stabilisiert werden: Transparenz, Datenminimierung, keine Server-Speicherung von PDFs/Inhalten, klare UI-Hinweise, Impressum-/Datenschutzseiten, technische Schutzpruefung und Red-Team-Gegencheck.

## Codex-Prompt

```text
Du arbeitest als Senior Privacy-by-Design Engineer, Webapp-Security-Reviewer und Red-Team-Pruefer fuer das Projekt Prompterator.

AUFGABE:
Mache Prompterator DSGVO-stabiler und fuehre eine defensive Red-Team-Gegenpruefung durch.

WICHTIG:
Dies ist keine Rechtsberatung. Ziel ist technische und dokumentarische Datenschutz-Stabilisierung. Rechtliche Endfreigabe bleibt menschlich/juristisch.

WICHTIGER WORKSPACE-CHECK:
Bevor du irgendetwas aenderst, validiere die Umgebung.

Fuehre aus:
- pwd
- ls -la
- git status
- git branch --show-current
- git remote -v
- test -f index.html && echo "index.html gefunden"
- test -f server.py && echo "server.py gefunden"
- test -f requirements.txt && echo "requirements.txt gefunden" || true
- grep -R "api/pdf\|ReportLab\|reportlab" -n server.py requirements.txt 2>/dev/null || true

Erwartetes Projekt:
Prompterator

Erwartetes Remote:
fissafissaintoki/operator-fischer-proof-of-work-demo

Wenn du nicht eindeutig im richtigen Prompterator-Repository bist:
- aendere keine Dateien
- erstelle keinen Commit
- mache keinen Push
- gib exakt aus:
"Falscher Workspace. Bitte Prompterator-Repo in Codex mounten oder klonen."

Nur wenn Workspace, Pflichtdateien und Remote stimmen, darfst du fortfahren.

ZIELBILD:
Prompterator soll technisch und transparent so vorbereitet werden, dass Nutzer vor Eingabe und PDF-Export verstehen:
- welche Daten sie eingeben sollten oder nicht,
- dass Eingaben zur Generierung an einen KI-Dienst uebermittelt werden koennen,
- dass der PDF-Export nur zur Erstellung verarbeitet wird,
- dass keine dauerhafte Server-Speicherung von Eingaben/PDFs erfolgen soll,
- dass keine sensiblen oder vertraulichen personenbezogenen Daten eingegeben werden sollen,
- wer verantwortlich ist und wie Datenschutzinformationen abrufbar sind.

DSGVO-GRUNDPRINZIPIEN FUER DIE UMSETZUNG:
- Transparenz
- Datenminimierung
- Zweckbindung
- Speicherbegrenzung
- Integritaet und Vertraulichkeit
- Privacy by Design / Privacy by Default
- Nachvollziehbarkeit / Accountability

AENDERUNGEN IN index.html:

1. Input-Datenschutzhinweis direkt sichtbar unter oder am Input-Block:
Text exakt oder sinngemaess:
"Datenschutz-Hinweis: Bitte geben Sie keine personenbezogenen, sensiblen oder vertraulichen Daten ein. Eingaben werden zur Generierung des Outputs technisch verarbeitet und koennen an einen KI-Dienst uebermittelt werden."

2. PDF-Hinweis direkt am PDF-CTA:
Text exakt oder sinngemaess:
"PDF-Hinweis: Der aktuelle Output wird zur Erstellung des PDFs verarbeitet. Es erfolgt keine dauerhafte Speicherung der PDF-Datei auf dem Server."
Nur verwenden, wenn server.py das tatsaechlich einhaelt. Wenn nicht sicher, formuliere vorsichtiger:
"Der PDF-Export soll ohne dauerhafte Server-Speicherung erfolgen."

3. Footer-/Kleingedruckt-Bereich:
- Fuege Links/Buttons hinzu:
  - Impressum
  - Datenschutz
- Kein externes Tracking.
- Keine Cookie-Banner, sofern keine nicht notwendigen Cookies gesetzt werden.

4. Modal oder einfache Seitenabschnitte:
Baue einfache, zugängliche Modals fuer:
- Impressum
- Datenschutz

Keine komplexe Library verwenden.
Keine externen Skripte.
Modals muessen per ESC oder Schliessen-Button schliessbar sein.

5. Impressum-Modal:
Da echte Pflichtdaten nicht sicher bekannt sind, KEINE falschen Daten erfinden.
Nutze Platzhalter klar markiert:
- Verantwortlich: Peter Fischer
- Anschrift: <ANSCHRIFT_ERGAENZEN>
- E-Mail: <E-MAIL_ERGAENZEN>
- Hinweis: "Bitte vor Veroeffentlichung vollstaendig ergaenzen und rechtlich pruefen."

6. Datenschutz-Modal:
Baue eine kurze, transparente Datenschutzerklaerungs-Vorlage mit Platzhaltern:
- Verantwortlicher
- Zweck der Verarbeitung
- Verarbeitete Daten: Eingabetext, Output, technische Zugriffsdaten, IP/Serverlogs soweit durch Hosting erforderlich
- KI-Dienst: OpenAI API / <ANBIETER_ERGAENZEN>
- Hosting: Render / <HOSTER_ERGAENZEN>
- Domain/DNS: checkdomain / <ANBIETER_ERGAENZEN>
- Speicherdauer: keine dauerhafte Speicherung von Eingaben/PDFs durch die App; Hosting-/Providerlogs nach Anbieterbedingungen
- Rechtsgrundlage: <RECHTSGRUNDLAGE_JURISTISCH_PRUEFEN>
- Betroffenenrechte: Auskunft, Berichtigung, Loeschung, Einschraenkung, Widerspruch, Datenuebertragbarkeit, Beschwerde bei Aufsichtsbehoerde
- Hinweis auf keine sensiblen Daten
- Drittlandtransfer / Anbieterbedingungen: <JURISTISCH_PRUEFEN>

7. UI darf nicht ueberladen werden:
- Hinweise klein, aber sichtbar.
- Kein Angsttext.
- Professionell, sachlich, lesbar.

AENDERUNGEN IN server.py:

1. Keine Payload-Logs:
Pruefe, dass nirgendwo steht:
- print(raw_input)
- print(payload)
- print(content)
- print(body)
Wenn vorhanden: entfernen oder durch neutrale Metadaten ersetzen, z. B. "request received" ohne Inhalt.

2. PDF-Export:
Falls /api/pdf existiert:
- Keine PDFs auf Platte speichern.
- Keine Userinhalte in Dateinamen.
- Content-Disposition fixer Dateiname:
  prompterator-usecase-portfolio.pdf
- Content-Type: application/pdf
- Fehler ohne Stacktrace an User.
- Keine internen Pfade in Fehlermeldungen.
- Maximalgroessen pruefen.

3. Header:
Pruefe Security-Header:
- Strict-Transport-Security
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY oder CSP frame-ancestors none
- Referrer-Policy: no-referrer oder strict-origin-when-cross-origin
- Permissions-Policy restriktiv
- Content-Security-Policy ohne externe Skripte

4. Cache:
- HTML/API: no-store
- Assets duerfen gecacht werden
- PDF-Antworten: no-store

5. Admin-/Usage-Endpunkte:
- /api/usage ohne gueltigen Admin-Token bleibt verborgen oder 404
- keine internen Kosten-/Securitydetails oeffentlich ausgeben

6. API-Validierung:
- /api/generate und /api/pdf akzeptieren nur application/json
- unerwartete JSON-Felder ablehnen
- Leere Inhalte ablehnen
- Groessenlimits einhalten

DOKUMENTATION:
Erstelle oder aktualisiere eine kurze Datei:
`docs/DSGVO-STABILIZATION-CHECKLIST.md`

Inhalt:
- Umgesetzte technische Massnahmen
- UI-Hinweise
- Nicht-Speicherlogik
- Drittanbieter-Platzhalter
- Offene juristische Pruefpunkte
- Red-Team-Ergebnis

RED-TEAM-GEGENPRUEFUNG:
Fuehre eine defensive Review durch und dokumentiere im Output:

1. Kann ein Nutzer vor Eingabe erkennen, dass keine personenbezogenen/sensiblen Daten eingegeben werden sollen?
2. Ist klar, dass Inhalte an KI-Dienst/Provider uebermittelt werden koennen?
3. Wird irgendwo Inhalt geloggt?
4. Werden PDFs auf Server gespeichert?
5. Gibt es irrefuehrende Datenschutzversprechen?
6. Sind Impressum/Datenschutz mit Platzhaltern markiert statt falscher Angaben?
7. Sind /api/generate und /api/pdf validiert?
8. Sind Fehlerausgaben neutral?
9. Ist der PDF-Export cache-arm/no-store?
10. Gibt es einen klaren Blocker vor Veroeffentlichung?

TESTS:

1. Syntaxcheck:
python3 -m py_compile server.py

2. Grep-Checks gegen Payload-Logging:
grep -R "print(raw_input)\|print(payload)\|print(content)\|print(body)" -n server.py || true

3. Healthcheck lokal, falls Server startbar:
curl -i http://127.0.0.1:8787/health

4. PDF-Test, falls /api/pdf existiert:
curl -i -X POST http://127.0.0.1:8787/api/pdf \
  -H 'Content-Type: application/json' \
  -d '{"title":"DSGVO Test","content":"## Executive Summary\nTestinhalt ohne personenbezogene Daten."}' \
  -o /tmp/dsgvo-test.pdf

Pruefe, dass keine PDF im Repo erzeugt wurde:
find . -maxdepth 2 -name "*.pdf" -print

5. Kein Live-Lasttest.
6. Keine externen Scans.
7. Keine echten personenbezogenen Testdaten verwenden.

GIT:
- Erstelle Arbeitsbranch falls noetig:
  git checkout -b feature/dsgvo-stabilization
- Aendere nur:
  index.html
  server.py
  docs/DSGVO-STABILIZATION-CHECKLIST.md
  ggf. requirements.txt nur wenn noetig
- Nicht adden:
  .env
  generierte PDFs
  private Dokumente
  mockups/
  frontend/
  Backup-Dateien
- Diff anzeigen:
  git diff -- index.html server.py docs/DSGVO-STABILIZATION-CHECKLIST.md requirements.txt
- Commit:
  git add index.html server.py docs/DSGVO-STABILIZATION-CHECKLIST.md requirements.txt
  git commit -m "Add GDPR stabilization and privacy notices"
- Push:
  git push origin feature/dsgvo-stabilization

AUSGABEFORMAT:
## Workspace
## Repo-Validierung
## DSGVO-Umsetzung
## Impressum / Datenschutz
## Server-Schutz
## Red-Team-Gegenpruefung
## Tests
## Git
## Harte Blocker vor Veroeffentlichung
## Naechster Schritt

HARTE BLOCKER:
- echte Anschrift/E-Mail fehlen im Impressum
- Rechtsgrundlage nicht juristisch geprueft
- Anbieter-/AVV-/Drittlandtransfer nicht geprueft
- App behauptet "DSGVO-konform" ohne juristische Freigabe
- PDF-Export speichert Inhalte dauerhaft
- Payloads werden geloggt
```

## Einordnung

Dieser Workflow macht Prompterator nicht automatisch juristisch final DSGVO-konform. Er stabilisiert Technik, UI-Transparenz, Nicht-Speicherung, Hinweise und Red-Team-Pruefung. Die finale Veroeffentlichung braucht echte Impressumsdaten und juristische Pruefung.
