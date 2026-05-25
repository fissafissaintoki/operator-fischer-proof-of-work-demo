# Codex Handoff: Warehouse Drive Simulator

## Ziel

Baue einen browserbasierten, public-safe Warehouse Drive Simulator als Portfolio-/Proof-of-Work-Demo.

Der Nutzer soll virtuell durch ein Lager fahren koennen. Die Demo soll an ein reales Hochregallager-Video angelehnt sein, aber keine echten Betriebsdaten, Kundendaten, Produktlabels, Kennzeichen oder personenbezogenen Details uebernehmen.

## Ziel-Datei

```text
pages/warehouse-drive-simulator.html
```

Optional spaeter als Route:

```text
/warehouse-drive-simulator
```

## Video-Referenz: abstrahierte Beobachtungen

Die hochgeladene Referenz zeigt sinngemaess:

- schmaler Hochregallager-Gang,
- Regale links und rechts,
- blau/orange Regaltraeger,
- Paletten und Kartons an den Seiten,
- Kommissionierfahrzeug / LHM im Gang,
- rote Sicherheitsprojektion am Boden,
- Bewegung geradeaus durch den Gang,
- Pick-/Greif-Situation am Regal,
- Gangende mit Wandmarkierung,
- operative Lagerrealitaet ohne Showroom-Aesthetik.

Diese Elemente sollen stilisiert und abstrahiert nachgebaut werden. Keine echten Produktnamen, Barcodes, Personen, Firmendetails oder internen Lagerkennzeichen uebernehmen.

## Simulator-Konzept

### Perspektive

Baue eine visuelle Fahransicht durch einen Lagergang.

Erlaubte Umsetzung:

- Canvas 2D oder reines HTML/CSS/JS.
- Keine externen Libraries.
- Keine Build-Tools.
- Eine einzige HTML-Datei.

### Steuerung

Pflichtsteuerung:

| Taste | Funktion |
|---|---|
| `W` oder Pfeil hoch | beschleunigen / vorwaerts fahren |
| `S` oder Pfeil runter | bremsen / rueckwaerts |
| `A` oder Pfeil links | links lenken |
| `D` oder Pfeil rechts | rechts lenken |
| `Space` | Pick bestaetigen / stoppen |
| `R` | Reset |

Optional zusaetzlich Mobile-Buttons.

## Szenen-Elemente

Baue mindestens:

- Lagergang mit Tiefenwirkung.
- Regale links und rechts.
- Paletten-/Kartonstapel als Hindernisse.
- Kommissionierfahrzeug als spielbares Objekt.
- Rote Safety-Light-Projektion vor oder hinter dem Fahrzeug.
- Pick-Ziele an Regalen.
- Gangabschnitte / Zonen.
- Minimap oder Statusanzeige.
- KPI-Panel.
- Eventlog.

## Spiel-/Demo-Logik

### Pflichtfunktionen

1. Nutzer kann durch den Gang fahren.
2. Kollision mit Regal oder Palette erzeugt `REVIEW` oder `BLOCK` Event.
3. Pick-Zone kann angefahren werden.
4. Pick kann mit `Space` bestaetigt werden.
5. Richtiges Pick-Ziel erzeugt `RELEASE`.
6. Falsche Zone oder Kollision erzeugt `REVIEW`.
7. Eventlog zeigt OPS-Core-Governance.
8. KPI-Kacheln zeigen z.B. Picks, Risiko, Geschwindigkeit, Reviews.

### Beispiel-Events

```text
RELEASE · Pick B-14 bestaetigt
REVIEW · Fahrzeug zu nah am Regal
BLOCK · Kollision mit Palette
REVIEW · falsche Pick-Zone
RELEASE · Trainingsdaten-Event gelabelt
```

## Visual Style

Orientierung am bestehenden Portfolio:

- dunkler Operator-/Warehouse-Stil,
- gelb/goldene Akzente,
- cyan/gruene technische Hinweise,
- rote Warn-/Safety-Signale,
- industrielle Lageroptik,
- keine Comic-Optik,
- keine realen Logos,
- keine echten Lagerdaten.

## OPS-Core-Integration

Die Demo soll sichtbar machen:

```text
Fahren
  -> Prozesssignal
  -> Risiko pruefen
  -> Pick / Review / Block
  -> Event speichern
  -> Trainingsdaten-Logik
```

## UI-Elemente

Pflichtbereiche:

1. **Simulator View**
   - Lagergang
   - Fahrzeug
   - Hindernisse
   - Pick-Ziele

2. **Control Panel**
   - aktuelle Geschwindigkeit
   - aktiver Auftrag
   - Zielslot
   - Risiko-Klasse
   - Pick-Zähler
   - Review-Zähler

3. **Eventlog**
   - RELEASE / REVIEW / BLOCK
   - kurze Begründung
   - Zeitstempel

4. **Governance Box**
   - Mensch bleibt Owner. KI bleibt Werkzeug.
   - Demo ersetzt keine produktive Lagersteuerung.

## Public-Safe-Regeln

- Keine echten Personen darstellen.
- Keine Gesichter.
- Keine echten Barcodes.
- Keine echten Kundennamen.
- Keine internen Lagerplatznummern aus dem Video übernehmen.
- Keine Betriebsdaten.
- Keine Aussage, dass dies produktive Lagersteuerung ist.
- Keine echte Mitarbeiterleistungsbewertung.

## Akzeptanzkriterien

- `pages/warehouse-drive-simulator.html` existiert.
- Datei laeuft standalone im Browser.
- Keine externen Dependencies.
- Fahrsteuerung funktioniert mit WASD oder Pfeiltasten.
- Fahrzeug kann durch den Gang bewegt werden.
- Mindestens 3 Pick-Zonen existieren.
- Kollisionen werden erkannt.
- Eventlog funktioniert.
- KPI-Panel funktioniert.
- Mobile Ansicht ist brauchbar.
- README wird um die Demo-Datei ergaenzt.

## Nicht-Ziele

- Keine echte 3D-Engine.
- Keine echte WMS-/ERP-Anbindung.
- Keine echten Sensoren.
- Keine personenbezogene Auswertung.
- Keine Verbindung zur OpenAI-API.
- Keine Veraenderung der bestehenden Prompterator-API.

## Empfohlene technische Umsetzung

### Minimal robust

- `<canvas>` fuer Lagergang und Fahrzeug.
- JavaScript Game Loop mit `requestAnimationFrame`.
- Player-Objekt: x, y, angle, speed.
- Rechteck-/Kreis-Kollision fuer Regale und Paletten.
- Pick-Zonen als farbige Rechtecke.
- UI ueber normale HTML-Divs.

### Dateistruktur

Nur eine Datei:

```text
pages/warehouse-drive-simulator.html
```

## Testplan

Lokal:

```bash
open pages/warehouse-drive-simulator.html
```

Wenn Route spaeter eingebunden wird:

```bash
python3 server.py
open http://localhost:8787/warehouse-drive-simulator
```

## Rueckgabeformat fuer Codex

```text
Status:
Geaenderte Dateien:
Kurzbeschreibung der Steuerung:
Umgesetzte Video-Merkmale:
Governance-Check:
Tests:
Offene Punkte:
```

## Governance-Check

```text
Problemklasse: Portfolio-Demo / Process-AI Simulation
Risiko-Klasse: LOW-MEDIUM
Public-Safe: ja, wenn abstrahiert
Owner-Freigabe erforderlich: ja vor externer Nutzung
Ergebnisziel: RELEASE nach Review
```
