# HZ Skill Extraction Protocol

## Zweck

Dieses Protokoll definiert die Kurzform `hz` fuer Operator Fischer.

Wenn Operator Fischer schreibt:

- `füge hinzu`
- `hinzufügen`
- `hz`

soll daraus ein wiederverwendbarer Skill-, Muster- oder Kompetenz-Extrakt erzeugt werden.

## Standardverhalten

Bei `hz` wird nicht der ganze Chat gespeichert. Stattdessen wird ein kompakter, kuratierter Extrakt erstellt.

Arbeitslogik:

Rohinput -> Skill erkennen -> Kompetenz benennen -> Struktur extrahieren -> Wiederverwendung definieren -> Governance pruefen -> Artefakt speichern

## Output-Struktur

Ein HZ-Extrakt sollte enthalten:

1. Skillname
2. deutsche Bezeichnung
3. internationale Bezeichnung
4. kurze Definition
5. Trigger / Wann nutzen?
6. Arbeitslogik
7. Teilfaehigkeiten
8. Qualitaetskriterien
9. Risiken / Grenzen
10. wiederverwendbares Template
11. Portfolio- oder Bewerbungsformulierung
12. Status: aktiv / experimentell / deprecated

## Speicherlogik

Primaerer Speicherort ist KnowledgeOS / GitHub-Artefakt, z. B.:

`docs/<SKILLNAME>.md`

Der normale ChatGPT-Memory soll nicht automatisch mit jedem Detail vollgeschrieben werden. Nur stabile, kanonische Skill-Definitionen sollen bei ausdruecklicher Freigabe als Memory-Kern betrachtet werden.

## Governance

- Keine Secrets speichern.
- Keine privaten Daten unnoetig speichern.
- Keine kompletten Chats dumpen.
- Nur verdichtete, wiederverwendbare Kompetenz- oder Musterextrakte speichern.
- Mensch bleibt Owner; KI extrahiert und strukturiert nur.

## Beispiele

### Beispiel 1
Input:
`hz: Claude Workflow Prompting`

Output:
Skill-Extrakt fuer Claude-Code Workflow-Orchestrierung.

### Beispiel 2
Input:
`füge hinzu: Ich habe mir KI-Systemkompetenz autodidaktisch erarbeitet`

Output:
Skill-Extrakt fuer Autodidaktische KI-Systemkompetenz.

## Kurzregel

`hz` bedeutet:
Extrahiere aus dem aktuellen Kontext eine wiederverwendbare Fähigkeit oder Arbeitslogik und speichere sie als sauberes KnowledgeOS-Artefakt, ohne den Chat ungefiltert in Memory zu kippen.
