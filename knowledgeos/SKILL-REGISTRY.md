# KnowledgeOS Skill Registry

## Zweck

Diese Registry sammelt wiederverwendbare Skills, Artefaktmuster und Operator-Faehigkeiten fuer den Prompterator-/OPS-Core-Kontext.

Sie ist kein Chatarchiv. Sie ist ein kuratierter Wiederverwendungslayer.

## Skill-Format

Jeder Skill folgt dieser Struktur:

```text
Skill-ID:
Name:
Problemklasse:
Input:
Output:
Pruefung:
Governance-Hinweis:
Wiederverwendung:
```

## Aktive Skill-Cluster

### SKILL-001: Artefakt-Verdichtung

**Problemklasse:** Rohinput ist diffus, aber enthaelt verwertbare Struktur.

**Input:** Notizen, Chatfragmente, Prozessbeobachtungen, Ideen, Use Cases.

**Output:** Sauberes Artefakt mit Ziel, Kontext, Struktur, Pruefung und Wiederverwendung.

**Pruefung:** Ist das Ergebnis ohne Originalchat verstaendlich?

**Governance-Hinweis:** Keine vertraulichen oder personenbezogenen Details uebernehmen.

**Wiederverwendung:** README, Dossier, SOP, Prompt, Portfolio-Seite.

---

### SKILL-002: Prozesslogik zu KI-Use-Case

**Problemklasse:** Reale operative Prozesse sollen in KI-faehige Entscheidungs- oder Assistenzlogik uebersetzt werden.

**Input:** Prozessschritte, Rollen, Risiken, Datenpunkte, Eskalationslogik.

**Output:** Use-Case-Canvas, Decision Engine, Governance Gate, Dossier.

**Pruefung:** Sind Inputdaten, Entscheidungskriterien und menschliche Freigabe getrennt?

**Governance-Hinweis:** KI empfiehlt oder strukturiert; Mensch bleibt Owner.

**Wiederverwendung:** Tourenfreigabe, Wareneingang, Lagerleitstand, Safety Gate.

---

### SKILL-003: Command Safety Gate

**Problemklasse:** KI-generierte Terminalbefehle oder Coding-Agent-Aktionen koennen riskant sein.

**Input:** Terminalbefehl, Script, Installationsanweisung, Agent-Handoff.

**Output:** Zeile-fuer-Zeile-Pruefung, Risiko-Klasse, sichere Alternative, Ausfuehrungsurteil.

**Pruefung:** Dateizugriff, Netzwerkzugriff, Rechtebedarf, Loeschrisiko, Secret-Risiko, Persistenz.

**Governance-Hinweis:** Keine blinde Ausfuehrung. Erst Wirkung, Risiko und Rueckrollbarkeit pruefen.

**Wiederverwendung:** macOS-Terminal, Codex-Handoff, Repo-Aenderungen, Security Review.

---

### SKILL-004: Public-Safe Portfolio Packaging

**Problemklasse:** Interne Kompetenz soll extern sichtbar gemacht werden, ohne vertrauliche Details preiszugeben.

**Input:** Nachweise, Projektartefakte, Use Cases, Screenshots, Prozessbeschreibungen.

**Output:** Portfolio-Dossier mit Problem, Loesung, Governance, Nutzen und Nachweiswert.

**Pruefung:** Keine sensiblen Daten, keine internen Nummern, keine Kundendaten, keine proprietaeren Details.

**Governance-Hinweis:** Abstrahieren statt offenlegen.

**Wiederverwendung:** Bewerbung, Everlast-Profil, Proof-of-Work, GitHub README.

---

### SKILL-005: Multi-Model Handoff

**Problemklasse:** Unterschiedliche KI-Systeme sollen arbeitsteilig genutzt werden.

**Input:** Ziel, Kontext, Repo-Status, Dateien, Constraints, gewuenschtes Ergebnis.

**Output:** Handoff-Prompt fuer Codex, Claude oder andere Coding-/Review-Agenten.

**Pruefung:** Sind Scope, Nicht-Ziele, Sicherheitsgrenzen und Rueckgabeformat klar?

**Governance-Hinweis:** Keine Secrets. Keine riskanten Befehle ohne Begruendung. Erst pruefen, dann aendern.

**Wiederverwendung:** GitHub Issues, PR-Beschreibungen, Agent-Auftraege, Review-Protokolle.

## Registry-Regel

Neue Skills werden nur aufgenommen, wenn sie:

1. wiederverwendbar sind,
2. eine klare Problemklasse loesen,
3. ein pruefbares Outputformat besitzen,
4. Governance-Grenzen enthalten,
5. nicht nur eine einzelne Chatantwort konservieren.
