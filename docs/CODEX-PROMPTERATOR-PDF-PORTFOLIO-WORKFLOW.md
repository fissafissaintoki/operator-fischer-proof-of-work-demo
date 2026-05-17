# Codex Workflow – Prompterator PDF-Usecase-Portfolio

## Ziel

Prompterator soll um eine klare PDF-Portfolio-Logik erweitert werden. Die UI soll wieder stärker als Zwei-Spalten-Interface funktionieren: Input links, Output rechts, dazwischen ein zentraler PDF-Button mit kurzer Nutzenbeschreibung.

## Codex-Prompt

```text
Du arbeitest als Senior Frontend-/Backend-Fixer für das Projekt Prompterator.

WICHTIGER WORKSPACE-CHECK:
Bevor du irgendetwas änderst, validiere die Umgebung.

Führe aus:
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
- ändere keine Dateien
- erstelle keinen Commit
- mache keinen Push
- gib exakt aus:
"Falscher Workspace. Bitte Prompterator-Repo in Codex mounten oder klonen."

Nur wenn Workspace, Pflichtdateien und Remote stimmen, darfst du fortfahren.

ZIELBILD:
Prompterator soll ein professionelles, ruhiges, dunkles AI-Operations-Control-Interface bleiben. Die UI soll aus diesen Hauptbereichen bestehen:

1. schmaler laufender FissaFissa-Out-of-Control-Banner oben
2. Titelbereich Prompterator
3. Erklärungstext:
   "Prompterator macht aus rohem Input arbeitsfähige Use Cases."
4. darunter ein zweispaltiger Arbeitsbereich:
   - links: Input-Block
   - Mitte: PDF-Portfolio-CTA
   - rechts: Output-Block
5. unter oder im Output-Block: Copy / Delete
6. keine Prompt-Bibliothek
7. keine Startprompts
8. keine Security-Ring-Anzeige

UI-ÄNDERUNG:

A) Layout
- Stelle Input und Output wieder nebeneinander dar, mindestens auf Desktop.
- Nutze ein responsives Grid:
  Desktop: 1fr auto 1fr
  Mobile: einspaltig untereinander
- Der PDF-Button sitzt zentral zwischen Input und Output.

B) PDF-Button / CTA
- Der Button soll zwischen den Blöcken stehen.
- Button-Text: "PDF"
- Darunter oder daneben kurze Erklärung:
  "Erstellen Sie hier Ihr perfektes PDF-Usecase-Portfolio."
- Der Button soll professionell wirken, nicht verspielt.
- Bis ein Backend existiert, soll der Klick eine klare Meldung anzeigen:
  "PDF-Portfolio-Export folgt. Aktueller Output kann bereits kopiert und weiterverarbeitet werden."

C) Output-Aufbereitung
- Der erzeugte Output soll als Grundlage für ein professionelles PDF-Usecase-Portfolio gedacht sein.
- Füge im Frontend keine komplexe PDF-Library ein.
- Kein clientseitiges PDF-Rendering mit externen Libraries.
- Keine neue Abhängigkeit.
- Optional nur Struktur vorbereiten: CSS-Klasse und JS-Funktion `pdfNotice()`.

D) Backend-Vorbereitung, nur wenn sinnvoll und klein
- Keine komplette PDF-Engine bauen.
- Falls server.py geändert wird, nur minimal vorbereiten.
- Kein neues OpenAI-Verhalten ohne ausdrücklichen Auftrag.
- /api/generate muss unverändert funktionieren.

E) Button-Logik
- Create bleibt für Generierung.
- Copy kopiert Output.
- Delete setzt Output auf "Noch kein Output."
- PDF zeigt vorerst die PDF-Hinweismeldung.
- Keine Daten löschen, keine Server-Aktion bei Delete.

F) Design
- Stil: Deep Dark Industrial / AI Operations / Leitstand.
- Ruhig, lesbar, hochwertig.
- Input und Output als gleichwertige Panels.
- PDF-CTA als zentrale Brücke zwischen Rohinput und Portfolio-Ergebnis.

AKZEPTANZKRITERIEN:
- Desktop: Input links, PDF-CTA Mitte, Output rechts.
- Mobile: Input, PDF, Output untereinander.
- /api/generate funktioniert weiter.
- Copy funktioniert.
- Delete funktioniert.
- PDF-Button zeigt Meldung.
- Keine neuen externen Libraries.
- Keine privaten Dateien committen.
- Keine .env lesen oder committen.
- Kein Force-Push.

TESTS:
- python3 -m py_compile server.py
- git diff -- index.html server.py
- git status

GIT:
- Erstelle einen Arbeitsbranch:
  git checkout -b feature/pdf-portfolio-cta
- Nur relevante Dateien adden:
  index.html
  server.py nur falls wirklich geändert
- Nicht adden:
  .env
  PDFs
  mockups/
  frontend/
  Backup-Dateien
  private Dokumente
- Commit:
  git commit -m "Add PDF portfolio CTA to Prompterator interface"
- Push:
  git push origin feature/pdf-portfolio-cta

AUSGABEFORMAT:
## Workspace
## Repo-Validierung
## Umsetzung
## Tests
## Git
## Browser-Prüfung
## Nächster Schritt
```

## Fachliche Einordnung

Der PDF-Button ist zunächst ein CTA und Workflow-Anker. Die eigentliche PDF-Generierung sollte als eigener Schritt umgesetzt werden, damit UI, Backend und Kosten-/Sicherheitslogik nicht gleichzeitig verändert werden.

## Empfohlene Phasen

1. UI-Phase: Zwei-Spalten-Layout plus PDF-CTA.
2. Output-Phase: Prompterator-Output stärker portfoliofähig strukturieren.
3. PDF-Phase: kontrollierter Server-Endpunkt `/api/pdf` oder externer Export-Workflow.
4. Governance-Phase: Limits, Dateigröße, Speicherung, Datenschutz und Löschlogik definieren.
