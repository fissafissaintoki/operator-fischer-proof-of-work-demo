# PDF Agent Pipeline

## Überblick

Der PDF-Export von Prompterator arbeitet intern als deterministische Agenten-Pipeline. Es werden keine externen Agenten-Frameworks verwendet und keine zusätzliche KI-Abfrage für den PDF-Export ausgelöst.

Pipeline:

1. Intake Agent
2. Structure Agent
3. Business Case Agent
4. Training Agent
5. Governance Agent
6. Visual Layout Agent
7. PDF Render Agent

## Funktionen

### Intake Agent

`intake_agent_validate_pdf_request(payload: dict) -> dict`

- validiert JSON
- akzeptiert nur `title`, `content`, `source`
- lehnt leeren oder zu großen Inhalt ab
- gibt deterministische Fehlerobjekte zurück

### Structure Agent

`structure_agent_parse_output(content: str) -> dict`

- erkennt `#`, `##`, `###`
- erhält Bulletpoints und nummerierte Listen
- bewahrt Unterabschnitte im Bereich `Direktes Artefakt`
- erkennt Masterprompt, Governance, Qualitätsprüfung und nächste Schritte

### Business Case Agent

`business_case_agent_build_model(sections: dict, title: str, source: str) -> dict`

- baut das Dossier-Modell
- verdichtet vorhandene Inhalte
- nutzt vorhandene Unterabschnitte gezielt
- erzeugt keine Halluzinationen

### Training Agent

`training_agent_add_learning_layer(model: dict) -> dict`

- ergänzt Lernziel
- Zielgruppe
- Anwendungssituation
- Praxisübung
- Prüffragen
- Transferaufgabe
- Trainerhinweis

### Governance Agent

`governance_agent_add_controls(model: dict) -> dict`

- fügt Governance- und Qualitätskontrollen hinzu
- markiert Hochrisikobereiche
- ergänzt Datenschutz-Hinweis
- hält fest: Mensch bleibt Owner, KI bleibt Werkzeug

### Visual Layout Agent

`visual_layout_agent_build_chapters(model: dict) -> list[dict]`

- übersetzt das Modell in ReportLab-Kapitel
- ergänzt Abschnittsseiten
- strukturiert Tabellen, Boxen, Fallbeispiele, Checklisten und Appendix

### PDF Render Agent

`pdf_render_agent_render_dossier(chapters: list[dict], metadata: dict) -> bytes`

- rendert das finale PDF mit ReportLab
- fügt Footer, Seitenzahlen, Kapitelbänder und Business-Module ein

## Qualitätsregeln

- kein Textdump
- keine verlorenen `###`-Unterabschnitte
- keine Halluzinationen
- Business-Dossier statt Chatprotokoll
- Fallbeispiele, Checkliste, Schulungsmodul und Management-Empfehlung müssen sichtbar sein
- Original-Output / Masterprompt gehören in den Anhang

## Testfälle

1. Dünner Input
2. Strukturierter Input mit `###`
3. Supply-Chain-Use-Case

Zusätzlich:

- Smoke-Test gegen `POST /api/pdf`
- `%PDF`-Prüfung
- Größenprüfung
- optionale Seitenzahlprüfung mit `pypdf`, falls vorhanden

## Grenzen

- die Qualität des PDFs hängt weiterhin von der Qualität des Ausgangsinputs ab
- der PDF-Export erzeugt keine neuen fachlichen Tatsachen
- bei dünnem Input entsteht ein professionell markiertes Gerüst, kein erfundener Fachinhalt
- ohne externe Bilder und Fonts bleibt der visuelle Stil bewusst dokumentenorientiert

## DSGVO- und Nicht-Speicherlogik

- keine dauerhafte Speicherung der PDF-Datei durch die App
- Test-PDFs nur außerhalb des Repositories, z. B. `/tmp`
- fixer Dateiname im Response
- `Cache-Control: no-store`
- keine Payload-Logs im Anwendungscode

## Review-Kriterien

- wirkt das PDF wie Business-Dossier statt Textdump?
- bleiben `###`-Unterabschnitte erhalten?
- sind Fallbeispiele, Schulungsmodul, Checkliste und Management-Empfehlung nutzbar?
- ist der Governance-Teil sichtbar?
- sind keine PDFs im Repository gespeichert?
