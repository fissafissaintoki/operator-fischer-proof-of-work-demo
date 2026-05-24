# KnowledgeOS Index

**Status:** aktiver Knowledge-Layer für Operator Fischer  
**Zweck:** Skills, Artefakte, Notizen, Projektwissen und wiederverwendbare Operator-Strukturen sauber vom kompakten Hinweisblock trennen.

---

## 1. Prinzip

Individuelle Hinweise sind nur Verhaltenssteuerung.  
KnowledgeOS trägt die Tiefe.

**Arbeitslogik:**

Rohinput → Problemklasse → Artefakt → Prüfung → Wiederverwendung

---

## 2. Aktive Layer

| Layer | Zweck |
|---|---|
| OPS Core | Operating-/Runtime-/Governance-Layer |
| KnowledgeOS | Skills, Artefakte, Notizen, Versionierung |
| Memory Agent | Auswahl, Routing und Verdichtung relevanter Kontexte |
| Skill Registry | Wiederverwendbare Fähigkeiten und Workflows |
| Archive | Deprecated Begriffe, alte Systemnamen, historische Artefakte |

---

## 3. Routing-Regel

Wenn ein neuer Kontext entsteht, wird geprüft:

1. **Individuelle Hinweise**  
   Nur wenn es dauerhaft das Antwortverhalten steuert.

2. **KnowledgeOS**  
   Wenn es ein Skill, Artefakt, Workflow, Projekt, Nachweis, Style oder Agent ist.

3. **Archiv**  
   Wenn deprecated, redundant, historisch oder nicht mehr aktiv führend.

4. **Nicht speichern**  
   Wenn situativ, ohne Wiederverwendungswert oder zu privat/sensibel.

---

## 4. Aktive Hauptbereiche

- `knowledge/profile/` — kompaktes Profil, individuelle Hinweise, Positionierung
- `knowledge/skills/` — Skills und wiederverwendbare Workflows
- `knowledge/agents/` — Agentenprompts, Testagenten, Routinglogik
- `knowledge/governance/` — Prüfregeln, Safety Gates, Owner-Prinzipien
- `knowledge/styles/` — PDF-/Web-/Portfolio-Style-Registry
- `knowledge/projects/` — Projektwissen wie Prompterator, Portfolio, Raschelwald
- `knowledge/archive/` — deprecated Begriffe und Altlogik

---

## 5. Aktiver Grundsatz

Mensch bleibt Owner. KI bleibt Werkzeug.

Fakten, Annahmen und Hypothesen werden getrennt. Unsicherheit wird markiert. Aktuelle oder prüfbare Themen werden mit Quellen abgesichert.
