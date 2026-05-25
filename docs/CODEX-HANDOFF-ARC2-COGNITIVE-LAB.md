# Codex Handoff: ARC2 Cognitive Lab

## Ziel

Erweitere und veroeffentliche das bestehende `ARC2 Cognitive Lab` als public-safe Proof-of-Work-Demo.

Aktuelle Datei:

```text
pages/arc2-cognitive-lab.html
```

Gewuenschte Route:

```text
/arc2-cognitive-lab
```

## Zweck

Das Lab soll ARC-/ARC2-artige JSON/Grid-Aufgaben lokal im Browser visualisieren, analysieren und durch primitive sowie kombinierte Transformationen pruefbar machen.

Es ist kein Erfolgsversprechen fuer ARC2-Loesung. Es ist ein kognitives Testlabor fuer:

- Grid-Visualisierung,
- Mustererkennung,
- Hypothesenbildung,
- Primitive Checks,
- Kandidatenbildung,
- OPS-Core-Governance.

## Bestand

Die bestehende HTML-Datei enthaelt bereits:

- JSON-Eingabefeld,
- Demo-Aufgabe,
- Train-/Test-Grid-Rendering,
- Palette-/Dimensionserkennung,
- Hypothesenbereich,
- Primitive Checks:
  - Identity,
  - Rotate90,
  - Rotate180,
  - FlipH,
  - FlipV,
  - CropNonZero,
- Candidate Rendering,
- OPS-Core-Log.

## Auftrag an Codex

### 1. Route einhaengen

In `server.py` die SEO_ROUTES-Map um folgende Route erweitern:

```python
"/arc2-cognitive-lab": "pages/arc2-cognitive-lab.html",
```

Nicht aendern:

- OpenAI-/API-Logik,
- Rate-Limits,
- Sicherheitsheader,
- PDF-/HTML-Dossier-Renderer,
- Firewall-Blockliste,
- Secrets / Environment Handling.

### 2. README aktualisieren

README muss die Live-Route und die Datei sichtbar machen:

```text
pages/arc2-cognitive-lab.html
/arc2-cognitive-lab
```

### 3. Lab-Funktionen verbessern

Erweitere die HTML-Datei ohne externe Dependencies.

Priorisierte Verbesserungen:

1. **File Upload fuer JSON**
   - Nutzer kann lokale `.json` Datei laden.
   - Keine Daten werden hochgeladen; Verarbeitung bleibt im Browser.

2. **Task Navigation**
   - Wenn JSON mehrere Tasks enthaelt, Auswahl per Dropdown.
   - Support fuer einzelne ARC-Datei oder Bundle-Objekt.

3. **Weitere Primitive Checks**
   - Rotate270,
   - transpose,
   - color map / recolor detection,
   - bounding box per Farbe,
   - object count,
   - connected components,
   - background fill detection.

4. **Composed Primitive Sweep**
   - 2-Step-Kombinationen testen, z.B. crop -> rotate, crop -> flip, recolor -> crop.
   - Nur begrenzte Kombinationen, damit Browser stabil bleibt.

5. **Hypothesen Export**
   - Hypothesen und Kandidaten als Markdown kopierbar machen.

6. **Public-Safe Hinweis sichtbar halten**
   - Local only.
   - Kein Solver-Versprechen.
   - Keine API.
   - Mensch bleibt Owner.

## UI-Anforderungen

- Bestehender dunkler Operator-Stil bleibt erhalten.
- Layout muss mobil brauchbar bleiben.
- Keine externen Libraries.
- Keine Build-Tools.
- Keine API Calls.
- Alle Funktionen in einer HTML-Datei.

## Akzeptanzkriterien

- `pages/arc2-cognitive-lab.html` laeuft standalone im Browser.
- `/arc2-cognitive-lab` liefert die Seite lokal ueber `server.py` aus.
- JSON-Datei-Upload funktioniert.
- Demo-Task funktioniert weiterhin.
- Mindestens 4 neue Primitive Checks sind eingebaut.
- Hypothesen werden sichtbar und als Markdown kopierbar.
- README verlinkt Datei und Route.
- Keine OpenAI-/API-Logik wurde geaendert.
- Keine externen Dependencies.

## Testplan

```bash
python3 -m py_compile server.py
python3 server.py
open http://localhost:8787/arc2-cognitive-lab
open pages/arc2-cognitive-lab.html
```

Browser-Test:

- Demo laden,
- JSON analysieren,
- Primitive Sweep starten,
- lokale JSON-Datei hochladen,
- Hypothesen exportieren,
- Reset testen.

## Governance-Check

```text
Problemklasse: Cognitive Lab / ARC2 Pattern Testing
Risiko-Klasse: LOW
Public-Safe: ja
Datenverarbeitung: lokal im Browser
Owner-Freigabe erforderlich: ja vor externer Nutzung
Ergebnisziel: RELEASE nach Review
```

## Rueckgabeformat fuer Codex

```text
Status:
Geaenderte Dateien:
Neue Funktionen:
Route:
Tests:
Governance-Check:
Offene Punkte:
```
