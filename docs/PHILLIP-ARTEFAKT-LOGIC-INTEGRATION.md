# Phillip-Artefaktlogik Integration

## Ziel

Prompterator erzeugt kein Chatprotokoll und keine Muellhalde, sondern verdichtetes,
wiederverwendbares Denkmaterial. Jeder Use-Case-Lauf muss in einem Artefakt enden,
das ohne den urspruenglichen Chat-Verlauf weiternutzbar ist.

## Prinzipien

1. **Rohinput ist nur Ausgangsmaterial.** Der vom Nutzer eingegebene Text dient als
   Trigger fuer Strukturarbeit, nicht als Endprodukt.
2. **Der Output muss in Artefakte ueberfuehrt werden.** Direkt nutzbare Dossiers,
   Masterprompts oder Entscheidungsvorlagen, nicht zusammenhanglose Chatfetzen.
3. **Artefakte muessen wiederverwendbar sein.** Was Prompterator produziert, soll
   ohne den urspruenglichen Chat-Kontext bestehen koennen.
4. **Masterprompts sind steuerbare Arbeitsanweisungen, keine Chat-Zitate.** Der
   Masterprompt ist ein deterministisches Werkzeug fuer Wiederverwendung, nicht
   eine zufaellig wirksame Formulierung aus einer Session.
5. **Governance trennt Nutzung, Pruefung und Verantwortung.** Owner, Pruefende
   und Freigebende sind unterschiedliche Rollen, auch wenn sie in einer Person
   liegen.
6. **Modellagnostische Ausgabeformate sichern Anschlussfaehigkeit.** Markdown,
   HTML und PDF, nicht modellspezifische Tokens oder Formate.
7. **Externes Arbeitsgedaechtnis entsteht durch kuratierte Dokumente, nicht durch
   unkontrollierte Speicherung.** Was nicht im Dossier steht, gilt als
   nicht gesagt.

## Schichtenmodell

```
Rohinput
   ↓
Analyse          (Problemklasse erkennen)
   ↓
Artefakt         (direkt nutzbares Arbeitsergebnis)
   ↓
Masterprompt     (wiederverwendbare Arbeitsanweisung)
   ↓
Governance       (Pruefpflicht, Owner, Eskalation)
   ↓
Dossier          (Management- oder Schulungsdokument)
   ↓
Wiederverwendung (Weitergabe, Pilotierung, Skalierung)
```

Jede Schicht hat eine eigene Pruefverantwortung. Wer nur eine Schicht liest, soll
die jeweilige Pruefung trotzdem durchfuehren koennen.

## Umsetzung in Prompterator-Agenten

Prompterator nutzt keine externen Agentenbibliotheken (kein LangChain, kein
CrewAI, kein AutoGen). Stattdessen wird die Agentenlogik als deterministische,
pruefbare Funktionspipeline realisiert.

- **Intake Agent.** Nimmt Rohinput auf, validiert Eingabegroesse und prueft auf
  unerwuenschte Inhalte. Implementierungspunkt: `/api/generate` Vorverarbeitung
  in `server.py`.
- **Structure Agent.** Erkennt Problemklasse und unterteilt den Output in
  Abschnitte. Implementierungspunkt: `parse_markdown_sections()` plus die
  `## ###` Header-Konvention im Systemprompt.
- **Business Case Agent.** Erzeugt das Use-Case-Modell mit Steckbrief, Zielbild,
  Loesungslogik. Implementierungspunkt: `build_usecase_dossier_model()`.
- **Artifact Agent.** Verdichtet den Output zu einem direkt nutzbaren
  Arbeitsartefakt (z.B. Entscheidungsvorlage, Schulungsmodul). Implementierungs-
  punkt: `_ch_steckbrief`, `_ch_fallbeispiele`, `_ch_schulungsmodul` in der
  Dossier-Engine.
- **Prompt Agent.** Liefert einen wiederverwendbaren Masterprompt als
  Sub-Section im Output. Implementierungspunkt: `## Masterprompt` Section im
  Output-Schema, separat extrahiert in `index.html` (Bay 04).
- **Governance Agent.** Markiert Pruefpflichten und Grenzen. Implementierungs-
  punkt: `_ch_governance`, `ex_governance_box`, Governance-Hinweise im
  Dossier-Template.
- **Dossier Agent.** Bereitet Management- oder Schulungsdokument auf.
  Implementierungspunkt: PDF-Pfad (`build_pdf_portfolio`) und HTML-Pfad
  (`render_executive_dossier_html`).

## Schutzregel

Keine privaten Gespraechsinhalte veroeffentlichen. Nur abstrahierte
Konzeptlogik verwenden. Wenn aus einer realen Konversation eine
Strukturidee uebernommen wird, muss sie umformuliert, generalisiert und vom
urspruenglichen Kontext geloest werden.

## Beziehung PDF vs. HTML

Beide Pfade sind im Dossier-Modell gleichwertige Renderer:

| Aspekt              | PDF-Pfad (ReportLab)         | HTML-Pfad (Browser/Print)     |
|---------------------|------------------------------|-------------------------------|
| Status              | technischer Basispfad        | High-End-Layoutpfad           |
| Stabilitaet         | hoch, stabil im Backend      | rendert je nach Browser       |
| Layout-Freiheit     | begrenzt durch ReportLab     | volle CSS-Freiheit            |
| Anwendung           | Download-Artefakt            | Vorschau, Praesentation       |

Das Datenmodell (`build_usecase_dossier_model`) ist Single Source of Truth.
Beide Renderer lesen aus demselben Modell, damit kein Pfad strukturell
abweicht.

## Was die Phillip-Logik nicht ist

- Kein autonomer Agent, der eigenstaendig Entscheidungen trifft.
- Kein Replacement fuer fachliche Pruefung.
- Kein Speichersystem fuer reale Konversationen.
- Keine Garantie fuer rechtliche oder geschaeftliche Belastbarkeit der Inhalte.

## Was die Phillip-Logik leistet

- Sie verdichtet Rohinput zu Artefakten, die ohne Chat-Kontext lesbar sind.
- Sie trennt Masterprompt, Artefakt und Dossier sauber, damit jede Schicht
  einzeln pruefbar ist.
- Sie macht die Governance-Verantwortung sichtbar, statt sie zu kaschieren.
- Sie hinterlegt eine deterministische Pipeline, die im Code nachvollziehbar
  ist und keine Black-Box-Logik einfuehrt.
