# PDF / HTML-CSS Dossier Template Brief

## Zweck

Prompterator produziert verdichtete Use-Case-Dossiers. Diese werden ueber zwei
Render-Pfade ausgegeben. Dieses Dokument haelt fest, welchen Zweck jeder Pfad
hat und wann welcher Pfad eingesetzt wird.

## Pfade

### ReportLab-PDF-Pfad

- **Status**: technischer Basispfad, stabil im Backend.
- **Funktion**: `build_pdf_portfolio()` in `server.py`.
- **Endpoint**: `POST /api/pdf`.
- **Ergebnis**: vollstaendiges PDF zum Download.
- **Stil**: klare Hierarchie, Tabellen, dezente Cyan-Akzente, Slate/Graphit.
- **Limitierungen**: Layoutfreiheit durch ReportLab beschraenkt, keine
  vollwertigen Infografiken oder Hero-Cover.

### HTML-CSS-Dossier-Pfad

- **Status**: High-End-Layoutpfad fuer Browser-Vorschau, Praesentation und
  Print-CSS-PDF aus dem Browser.
- **Template**: `pages/html-dossier-template.html`.
- **Funktion**: `render_executive_dossier_html()` in `server.py`.
- **Endpoint statisch**: `GET /dossier-preview` (liefert eine
  Beispielvariante mit Cold-Chain-Use-Case).
- **Endpoint dynamisch**: `POST /api/dossier-html` (rendert ein Dossier aus
  Title, Content und Source, parallel zum PDF-Endpoint).
- **Ergebnis**: HTML-Dokument mit Hero-Cover, Executive Dashboard, Use-Case-
  Canvas, Prozessmodell, Risiko-/Governance-Board und Management-Empfehlung.
- **Stil**: dunkles Hero-Cover, helle Sheets mit weissem Hintergrund, dezente
  Cyan- und Amber-Akzente, Tabellen mit Header-Bands, Process-Steps mit
  Pfeil-Indikatoren.

## Architekturprinzip

Beide Pfade lesen aus demselben Datenmodell.

```
parse_markdown_sections()
   ↓
build_usecase_dossier_model()
   ↓
   ├── build_pdf_portfolio()        → PDF
   └── render_executive_dossier_html() → HTML
```

Das bedeutet: Inhaltliche Verbesserung am Modell wirkt automatisch in beiden
Pfaden. Layout-Unterschiede sind reine Rendering-Entscheidungen, keine
inhaltlichen Diskrepanzen.

## Wann welcher Pfad?

| Anwendungsfall                          | Pfad             |
|-----------------------------------------|------------------|
| Download als finales Artefakt           | PDF              |
| Anschauen im Browser                    | HTML-Preview     |
| Praesentation am Bildschirm             | HTML-Preview     |
| Print aus Browser (mit Print-CSS)       | HTML-Preview     |
| Versand per Mail / Anhang               | PDF              |
| Schnelle Iteration am Layout            | HTML (CSS)       |

## Sicherheit und Datenschutz

- Beide Pfade speichern keine Inhalte serverseitig dauerhaft.
- Beide Pfade unterliegen dem `MAX_PDF_BODY_BYTES`-Limit fuer Eingaben.
- Beide Pfade unterliegen einem Rate-Limit pro IP.
- Keine Payloads werden in Logs geschrieben.
- HTML-Outputs werden HTML-escaped, um XSS-Risiken im Browser zu vermeiden.

## Was bewusst nicht enthalten ist

- Kein dynamisches Speichern von HTML-Dossiers im Repo.
- Keine separate Datenbank fuer Dossier-Versionen.
- Kein Print-zu-Server-PDF (Headless-Browser-Rendering wuerde Playwright oder
  WeasyPrint erfordern, was wir bewusst nicht einfuehren).

## Naechster moeglicher Schritt

Falls zu einem spaeteren Zeitpunkt ein hochwertiger Print-CSS-PDF-Pfad
gewuenscht wird, koennte das HTML-Dossier-Template via Browser-Print-Funktion
("Als PDF speichern") genutzt werden. Dafuer ist `@media print` im Template
bereits vorbereitet.
