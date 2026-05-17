# DSGVO Stabilization Checklist

Hinweis: Dies ist keine Rechtsberatung. Die technische und dokumentarische Vorbereitung ersetzt keine juristische Endpruefung.

## Umgesetzte technische Massnahmen

- Sichtbarer Datenschutz-Hinweis direkt am Input-Bereich.
- Sichtbarer PDF-Hinweis direkt am PDF-CTA.
- Impressum- und Datenschutz-Modal mit klar markierten Platzhaltern statt erfundener Angaben.
- `POST /api/generate` und `POST /api/pdf` akzeptieren nur `application/json`.
- Unerwartete JSON-Felder werden bei beiden Endpunkten abgelehnt.
- Leere Inhalte und Groessenlimits werden serverseitig geprueft.
- HTML-, API- und PDF-Antworten werden mit `Cache-Control: no-store` ausgeliefert.
- PDF-Dateien werden direkt gestreamt und nicht auf dem Server gespeichert.
- PDF-Dateiname ist fest vorgegeben: `prompterator-usecase-portfolio.pdf`.
- Sicherheitsheader bleiben restriktiv, inklusive CSP ohne externe Skripte.

## UI-Hinweise

- Nutzer werden vor der Eingabe aufgefordert, keine personenbezogenen, sensiblen oder vertraulichen Daten einzugeben.
- Nutzer werden darauf hingewiesen, dass Eingaben technisch verarbeitet und an einen KI-Dienst uebermittelt werden koennen.
- Nutzer werden darauf hingewiesen, dass der aktuelle Output fuer den PDF-Export verarbeitet wird.

## Nicht-Speicherlogik

- Die App speichert Eingaben und PDFs nach aktuellem technischen Stand nicht dauerhaft selbst.
- Hosting- und Providerlogs koennen dennoch nach Infrastruktur- und Anbieterbedingungen anfallen.
- Generierte PDFs werden nicht im Repository und nicht in einem App-seitigen Exportordner abgelegt.

## Drittanbieter-Platzhalter

- KI-Dienst: OpenAI API / `<ANBIETER_ERGAENZEN>`
- Hosting: Render / `<HOSTER_ERGAENZEN>`
- Domain/DNS: checkdomain / `<ANBIETER_ERGAENZEN>`
- Rechtsgrundlage: `<RECHTSGRUNDLAGE_JURISTISCH_PRUEFEN>`
- Drittlandtransfer / Anbieterbedingungen: `<JURISTISCH_PRUEFEN>`

## Offene juristische Pruefpunkte

- Vollstaendige Anbieter- und Verantwortlichendaten im Impressum ergaenzen.
- Rechtsgrundlage und Rollenverteilung juristisch pruefen.
- AVV, TOMs und Drittlandtransfer mit allen beteiligten Anbietern pruefen.
- Hosting-, DNS- und KI-Anbieterbedingungen final gegen die Datenschutztexte spiegeln.
- Keine Aussage wie "DSGVO-konform" ohne rechtliche Freigabe veroeffentlichen.

## Red-Team-Ergebnis

- Die App macht jetzt vor Eingabe sichtbar, dass keine sensiblen oder personenbezogenen Daten eingegeben werden sollen.
- Die Uebermittlung an einen KI-Dienst wird transparent angedeutet, nicht versteckt.
- In `server.py` wurden keine Payload-Logs fuer Eingaben oder PDF-Inhalte gefunden.
- Der PDF-Export nutzt einen festen Dateinamen und speichert keine PDF-Datei auf dem Server.
- Die aktuellen Platzhalter in Impressum und Datenschutz sind klar als unvollstaendig markiert.
- Harte Veroeffentlichungsblocker bleiben: fehlende echte Impressumsdaten, ungepruefte Rechtsgrundlage, ungepruefte Anbieter-/Drittlandtransfer-Lage.
