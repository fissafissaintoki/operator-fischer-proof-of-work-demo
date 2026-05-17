# Codex Workflow – Prompterator Phase 3: ReportLab PDF Export

## Ziel

Prompterator bekommt einen serverseitigen PDF-Export mit ReportLab. Der bestehende Output wird als professionelles Use-Case-Portfolio-PDF aufbereitet und als Download ausgeliefert.

## Codex-Prompt

```text
Du arbeitest als Senior Backend-/Frontend-Fixer fuer das Projekt Prompterator.

AUFGABE:
Baue Phase 3: serverseitiger PDF-Export mit ReportLab.

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
Der PDF-Button in der Prompterator-Webseite soll aus dem aktuellen Output ein professionelles PDF-Use-Case-Portfolio erzeugen und herunterladen.

Technisches Ziel:
- serverseitiger Endpoint: POST /api/pdf
- PDF-Erzeugung mit ReportLab
- kein Speichern von PDFs auf dem Server
- direkte Antwort als application/pdf
- Download-Dateiname: prompterator-usecase-portfolio.pdf
- bestehendes /api/generate darf nicht kaputtgehen
- bestehende Security-/Rate-Limit-Logik soll erhalten bleiben

ABHÄNGIGKEIT:
Pruefe, ob ReportLab installiert ist.
- Wenn requirements.txt existiert: fuege `reportlab` hinzu, falls noch nicht vorhanden.
- Wenn keine requirements.txt existiert: erstelle eine minimale requirements.txt mit `reportlab` und dokumentiere, dass Render diese installieren muss.
- Keine schweren Browser-/PDF-Engines wie Playwright, Puppeteer oder WeasyPrint einbauen.

BACKEND-AENDERUNG IN server.py:

1. Imports ergaenzen:
- io.BytesIO
- ReportLab imports fuer SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
- Styles: getSampleStyleSheet, ParagraphStyle
- Pagesizes: A4
- Units: mm
- Colors

2. Neue Limits einfuehren:
- MAX_PDF_BODY_BYTES = env default 120000
- MAX_PDF_CONTENT_CHARS = env default 50000
- PDF_RATE_LIMIT_MAX_REQUESTS = env default 5
Optional: Verwende bestehendes Rate-Limit, wenn eigene PDF-Limits zu viel Umbau waeren.

3. Neuen Endpoint bauen:
POST /api/pdf

Erwartetes JSON:
{
  "title": "optional",
  "content": "Output-Text aus Prompterator",
  "source": "optional"
}

Validierung:
- Content-Type muss application/json sein.
- Body darf MAX_PDF_BODY_BYTES nicht ueberschreiten.
- Nur erlaubte Felder: title, content, source.
- content muss nicht leer sein.
- content darf MAX_PDF_CONTENT_CHARS nicht ueberschreiten.
- bei Fehlern klare JSON-Fehler ausgeben.

4. PDF-Struktur:
Erzeuge ein professionelles PDF mit diesen Bereichen:

Seite 1: Deckblatt
- Titel: Prompterator Use-Case Portfolio
- Untertitel: KI-gestuetztes Arbeitsartefakt
- Datum
- Hinweis: Erstellt mit Prompterator / Operator Fischer

Danach:
- Executive Summary
- Strukturierter Use Case
- Problemklasse und Zielbild
- Artefakt / Direktes Arbeitsprodukt
- Qualitaetspruefung
- Governance
- Naechste Schritte
- Anhang: Original-Output

WICHTIG:
Wenn der Content Markdown-Ueberschriften enthaelt, zerlege nach Zeilen mit `## ` und mache daraus PDF-Abschnitte.
Wenn keine Ueberschriften vorhanden sind, schreibe den gesamten Content in den Abschnitt "Use-Case Inhalt".

5. Layout-Regeln:
- A4
- Rand ca. 16mm
- professionelle Business-Optik
- keine Comic-Optik
- keine externen Fonts
- dunkle Akzentlinie oder dezente Tabellen moeglich
- Text muss umbrechen
- lange Inhalte auf mehrere Seiten verteilen
- keine HTML-Injection, Text escapen

6. Footer / Seitenzahlen:
- Fuege unten Seitenzahlen ein.
- Footer-Text: "Prompterator · Operator Fischer · AI Operations"

7. Security:
- Keine PDFs auf Platte speichern.
- Kein Dateiname aus Userinput direkt verwenden.
- Keine Secrets ausgeben.
- Fehler nicht mit Stacktrace an User geben.
- /api/pdf darf keine internen Pfade ausgeben.

FRONTEND-AENDERUNG IN index.html:

1. PDF-Button soll echten Export ausloesen.
- Ersetze pdfNotice() oder erweitere sie zu exportPdfPortfolio().
- Der Button soll den aktuellen Output aus `#out` nehmen.
- Wenn kein Output vorhanden ist: Statusmeldung "Erst Output erzeugen."
- Dann POST /api/pdf mit JSON senden:
  { title: "Prompterator Use-Case Portfolio", content: outputText, source: "prompterator" }
- Response als Blob lesen.
- Download-Link erzeugen.
- Datei herunterladen als `prompterator-usecase-portfolio.pdf`.
- Statusmeldung: "PDF erstellt."

2. Button-Text bleibt:
PDF

3. CTA-Text bleibt:
"Erstellen Sie hier Ihr perfektes PDF-Usecase-Portfolio."

4. Keine externen JS-Libraries.

TESTS:
1. Syntaxcheck:
python3 -m py_compile server.py

2. Lokaler Smoke-Test, falls moeglich:
- Server lokal starten oder vorhandenen Testmodus nutzen.
- POST /api/pdf mit kleinem Beispielcontent testen.
- Erwartung:
  HTTP 200
  Content-Type application/pdf
  PDF-Bytes beginnen mit %PDF

Beispiel-curl:
curl -s -X POST http://127.0.0.1:8787/api/pdf \
  -H 'Content-Type: application/json' \
  -d '{"title":"Test","content":"## Executive Summary\nDies ist ein Test.\n\n## Governance\nMensch bleibt Owner."}' \
  -o /tmp/prompterator-test.pdf

Dann pruefen:
file /tmp/prompterator-test.pdf
ls -lh /tmp/prompterator-test.pdf

3. Bestehenden Healthcheck nicht brechen:
curl -i http://127.0.0.1:8787/health

4. Kein Live-Lasttest.
5. Keine wiederholten Security-Testlaeufe.

GIT:
- Erstelle einen Arbeitsbranch, falls nicht schon auf Feature-Branch:
  git checkout -b feature/reportlab-pdf-export
- Aendere nur:
  server.py
  index.html
  requirements.txt falls noetig
- Nicht adden:
  .env
  PDFs
  mockups/
  frontend/
  Backup-Dateien
  private Dokumente
- Diff anzeigen:
  git diff -- index.html server.py requirements.txt
- Commit:
  git add index.html server.py requirements.txt
  git commit -m "Add ReportLab PDF portfolio export"
- Push:
  git push origin feature/reportlab-pdf-export

AUSGABEFORMAT:
## Workspace
## Repo-Validierung
## Umsetzung
## PDF-Endpoint
## Frontend
## Tests
## Git
## Risiken / offene Punkte
## Naechster Schritt

STOPPKRITERIEN:
- falscher Workspace
- falsches Repo
- kein server.py
- kein index.html
- ReportLab kann nicht installiert/importiert werden
- PDF-Test erzeugt keine gueltige PDF-Datei
- Rebase-/Merge-Konflikt
```

## Hinweis

Phase 3 baut den echten PDF-Export. Phase 4 sollte danach das 20-Seiten-Template, Schulungslogik, Deckblattgrafik und erweiterte Portfolio-Abschnitte verfeinern.
