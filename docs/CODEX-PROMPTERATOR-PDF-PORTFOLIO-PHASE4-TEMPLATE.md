# Codex Workflow – Prompterator Phase 4: Professionelles 20-Seiten PDF-Use-Case-Portfolio

## Ziel

Phase 4 veredelt den bestehenden ReportLab-PDF-Export zu einem professionellen, schulungs- und portfoliofähigen PDF-Use-Case-Dossier. Voraussetzung: Phase 3 mit serverseitigem `/api/pdf`-Endpoint und ReportLab ist bereits umgesetzt.

## Codex-Prompt

```text
Du arbeitest als Senior Backend-/Frontend-Fixer, PDF-Layout-Engineer und AI-Operations-Dokumentationsarchitekt fuer das Projekt Prompterator.

AUFGABE:
Baue Phase 4: Professionelles 20-Seiten PDF-Use-Case-Portfolio auf Basis des bestehenden ReportLab-PDF-Exports.

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

Wenn Phase 3 nicht vorhanden ist, also kein `/api/pdf` und kein ReportLab-Import existiert:
- aendere nichts
- gib exakt aus:
"Phase 3 fehlt. Erst ReportLab-PDF-Export implementieren."

Nur wenn Workspace, Pflichtdateien, Remote und Phase 3 stimmen, darfst du fortfahren.

ZIELBILD:
Der PDF-Button soll nicht nur einen einfachen PDF-Dump erzeugen, sondern ein professionelles PDF-Use-Case-Portfolio, das fuer Schulung, Prozessdokumentation, Bewerbung/Portfolio und Management-Kommunikation nutzbar ist.

PHASE-4-ZIEL:
- 20-seitige Zielstruktur als ReportLab-Template
- professionelle Business-Optik
- klare Seitentitel
- Seitenzahlen und Footer
- strukturierte Abschnitte
- lange Inhalte sauber umbrechen
- fehlende Abschnitte mit "Noch nicht ausreichend befuellt" kennzeichnen
- kein Speichern der PDF-Datei auf Server
- keine externen Fonts
- keine schweren Browser-Engines
- keine .env anfassen

GEWÜNSCHTE PDF-STRUKTUR:

1. Deckblatt
   - Titel: Prompterator Use-Case Portfolio
   - Untertitel: KI-gestuetztes Arbeitsartefakt
   - Datum
   - Operator Fischer / AI Operations

2. Executive Summary
3. Ausgangslage
4. Zielbild
5. Problemklasse
6. Use-Case-Kontext
7. Akteure und Rollen
8. Prozessuebersicht
9. Hauptablauf
10. Alternativablaeufe / Fehlerfaelle
11. Daten / Inputs / Outputs
12. Entscheidungslogik
13. Risiken und Annahmen
14. Governance
15. Qualitaetspruefung
16. KPIs / Erfolgskriterien
17. Schulungsmodul
18. Checkliste
19. Umsetzungsplan
20. Fazit / naechste Schritte
21. Anhang: Original-Output, falls noetig

Hinweis:
Es muessen nicht kuenstlich exakt 20 Seiten gefuellt werden, aber die PDF-Struktur muss auf diese 20 Kernkapitel ausgelegt sein. Wenn ein Abschnitt wenig Inhalt hat, kurz und professionell kennzeichnen, nicht halluzinieren.

BACKEND-AENDERUNGEN IN server.py:

1. Refactoring:
- Extrahiere PDF-Erstellung in klare Hilfsfunktionen, z. B.:
  - sanitize_pdf_text(text)
  - parse_markdown_sections(content)
  - get_section(sections, possible_names)
  - build_pdf_portfolio(title, content, source)
  - add_footer(canvas, doc)

2. Markdown-Parsing:
- Erkenne Abschnitte anhand von `## ` und `# `.
- Ordne bekannte Prompterator-Abschnitte in das Portfolio-Template ein:
  - Problemklasse
  - Fakten / Annahmen / Hypothesen
  - Modus
  - Artefakt-Blueprint
  - Direktes Artefakt
  - Qualitaetspruefung
  - Governance
  - Masterprompt
  - Naechste Schritte
- Wenn Abschnitte fehlen, nutze fallback aus Originalcontent.

3. PDF-Layout:
- A4
- Rand ca. 15–16mm
- Business-Styles mit ReportLab ParagraphStyle
- Titel gross, Untertitel kleiner
- Abschnittstitel klar und wiederholbar
- dezente Linien / Akzentfarbe
- Tabellen nur wenn robust und nicht layout-riskant
- Footer mit Seitenzahl:
  "Prompterator · Operator Fischer · AI Operations · Seite X"

4. Kapitel-Funktion:
Baue eine Funktion, die Kapitel einheitlich erzeugt:
- PageBreak optional vor Hauptkapiteln
- Heading
- kurzer Zwecktext
- Inhalt
- falls leer: "Noch nicht ausreichend befuellt."

5. Schulungs- und Portfolio-Mehrwert:
Ergaenze aus vorhandenen Inhalten, ohne zu halluzinieren:
- Lernziel
- typische Anwendung
- Checkfragen
- Umsetzungsnotiz
Wenn dafuer keine Daten vorhanden sind, formuliere neutral:
"Dieser Punkt muss fachlich ergaenzt werden."

6. Security / Governance:
- Keine PDF-Dateien speichern.
- Keine User-Dateinamen direkt verwenden.
- Keine HTML-Interpretation.
- Text escapen.
- Keine Stacktraces an User.
- Maximalgroessen beibehalten.
- /api/generate nicht veraendern, ausser zwingend noetig.

FRONTEND-AENDERUNGEN IN index.html:

1. PDF-Button bleibt sichtbar zwischen Input und Output.
2. CTA-Text professioneller setzen:
   "Erstellen Sie hier Ihr professionelles PDF-Use-Case-Portfolio."
3. Button ruft den echten Export auf.
4. Statusmeldungen:
   - Kein Output: "Erst Output erzeugen."
   - Waerend Export: "PDF wird erstellt..."
   - Erfolg: "PDF erstellt."
   - Fehler: "PDF konnte nicht erstellt werden."
5. Keine externen JS-Libraries.
6. Bestehende Copy/Delete/Create-Funktion darf nicht brechen.

TESTS:

1. Syntaxcheck:
python3 -m py_compile server.py

2. Lokaler PDF-Test:
Starte lokalen Server, wenn moeglich:
python3 server.py

Dann in zweitem Terminal oder testbar durch Codex:
curl -s -X POST http://127.0.0.1:8787/api/pdf \
  -H 'Content-Type: application/json' \
  -d '{"title":"Test Use Case","content":"## Problemklasse\nUse Case / Prozessanalyse\n\n## Direktes Artefakt\nDies ist ein Testartefakt.\n\n## Governance\nMensch bleibt Owner. KI bleibt Werkzeug.\n\n## Naechste Schritte\n1. Pruefen\n2. Umsetzen"}' \
  -o /tmp/prompterator-phase4-test.pdf

Pruefen:
file /tmp/prompterator-phase4-test.pdf
ls -lh /tmp/prompterator-phase4-test.pdf
python3 - <<'PY'
from pathlib import Path
p = Path('/tmp/prompterator-phase4-test.pdf')
data = p.read_bytes()
assert data.startswith(b'%PDF'), 'PDF beginnt nicht mit %PDF'
assert len(data) > 1000, 'PDF zu klein'
print('PDF smoke test ok:', len(data), 'bytes')
PY

3. Healthcheck:
curl -i http://127.0.0.1:8787/health

4. Kein Live-Lasttest.
5. Keine wiederholten Security-Testlaeufe.

GIT:
- Erstelle einen Arbeitsbranch, falls nicht bereits Feature-Branch:
  git checkout -b feature/pdf-portfolio-template-phase4
- Aendere nur:
  server.py
  index.html
  requirements.txt nur falls noetig
  docs nur falls du eine kurze Phase-4-Notiz ergaenzt
- Nicht adden:
  .env
  generierte PDFs
  private Dokumente
  mockups/
  frontend/
  Backup-Dateien
- Diff anzeigen:
  git diff -- index.html server.py requirements.txt
- Commit:
  git add index.html server.py requirements.txt
  git commit -m "Enhance PDF export with portfolio template"
- Push:
  git push origin feature/pdf-portfolio-template-phase4

AUSGABEFORMAT:
## Workspace
## Repo-Validierung
## Phase-3-Pruefung
## Umsetzung
## PDF-Template
## Frontend
## Tests
## Git
## Risiken / offene Punkte
## Naechster Schritt

STOPPKRITERIEN:
- falscher Workspace
- falsches Repo
- Phase 3 fehlt
- kein server.py
- kein index.html
- ReportLab fehlt und kann nicht installiert/importiert werden
- PDF-Smoke-Test erzeugt keine gueltige PDF-Datei
- Rebase-/Merge-Konflikt
```

## Einordnung

Phase 4 ist die Veredelungsphase. Es wird nicht mehr nur irgendein PDF erzeugt, sondern ein professionelles Use-Case-Portfolio mit Schulungs- und Dokumentationslogik.
