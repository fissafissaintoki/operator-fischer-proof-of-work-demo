# OPS Core / KnowledgeOS GitHub Build

## Zweck

Dieses Dokument beschreibt den oeffentlichen Build-Layer fuer OPS Core und KnowledgeOS innerhalb des Repositorys `operator-fischer-proof-of-work-demo`.

Der Build soll zeigen, dass Prompterator nicht nur eine Prompt-Oberflaeche ist, sondern ein kontrollierter Artefakt-, Governance- und Wiederverwendungsprozess.

## Kernlogik

```text
Rohinput
  -> Problemklasse
  -> Modus
  -> Artefakt
  -> Qualitaetspruefung
  -> Governance
  -> Wiederverwendung
```

## Systemrollen

| Rolle | Funktion | Grenze |
|---|---|---|
| Menschlicher Owner | Ziel, Freigabe, Verantwortung | Wird nicht durch KI ersetzt |
| OPS Core | Runtime-, Routing- und Governance-Layer | Entscheidet nicht autonom |
| KnowledgeOS | Artefakt-, Skill-, Notiz- und Versionierungs-Layer | Speichert nur kuratierte Inhalte |
| Prompterator | UI- und Generator-Schicht | Kein rechts-/fachverbindliches System |
| Verifier | Pruefung auf Plausibilitaet, Risiko und Wiederverwendbarkeit | Keine Garantie auf Wahrheit |

## Architekturposition

OPS Core ist der operative Steuerungslayer. KnowledgeOS ist der Wissens- und Artefaktlayer. Prompterator ist die sichtbare Proof-of-Work-Oberflaeche.

```text
User Input
  -> Prompterator UI
  -> OPS Core Routing
  -> Artefakt Generator
  -> KnowledgeOS Struktur
  -> Governance Gate
  -> Markdown / HTML / PDF / Repo-Dokumentation
```

## Build-Ziele

1. Oeffentlich verstaendliche Architektur dokumentieren.
2. Reale Prozesslogik in KI-faehige Artefakte uebersetzen.
3. Governance sichtbar machen: Owner, Pruefung, Risiko, Grenzen.
4. Skills und Use Cases wiederverwendbar strukturieren.
5. Repo als professionellen Proof of Work nutzbar machen.

## Nicht-Ziele

- Kein autonomes Agentensystem.
- Kein Ersatz fuer fachliche, rechtliche oder technische Pruefung.
- Keine Verarbeitung vertraulicher Betriebsdaten im oeffentlichen Repo.
- Keine Speicherung personenbezogener oder sensibler Inhalte.
- Keine Behauptung produktiver DSGVO-Konformitaet ohne externe Pruefung.

## Public-Safe-Regeln

- Keine Kundennamen.
- Keine Kennzeichen.
- Keine internen Standort-, Lager- oder Systemnummern.
- Keine personenbezogenen Daten.
- Keine Secrets, API-Keys, Tokens oder Credentials.
- Keine echten Betriebsdaten, wenn sie Rueckschluesse auf Unternehmen, Personen oder Prozesse erlauben.

## Mindestartefakte im Build

| Artefakt | Zweck |
|---|---|
| OPS-Core-Build-Dokument | Systemerklaerung und Architekturrahmen |
| KnowledgeOS Skill Registry | Wiederverwendbare Kompetenz- und Skill-Struktur |
| Governance Gate | Pruefung vor Nutzung, Publikation oder Automatisierung |
| Coding Agent Handoff | Sichere Uebergabe an Codex/Claude/GitHub-Agenten |
| Proof-of-Work Dossier | Extern sichtbares Ergebnis fuer Portfolio und Bewertung |

## Qualitaetsgate

Ein Artefakt ist erst verwertbar, wenn diese Punkte erfuellt sind:

- Problemklasse ist benannt.
- Zielgruppe ist klar.
- Outputformat ist definiert.
- Annahmen sind von Fakten getrennt.
- Risiken sind markiert.
- Wiederverwendung ist moeglich.
- Menschliche Freigabe bleibt erforderlich.

## Status

Build-Status: `v0.1 public-safe architecture layer`

Dieses Dokument ist ein additiver Architektur-Layer. Es veraendert keine bestehende Prompterator-Logik und keine Renderpfade.
