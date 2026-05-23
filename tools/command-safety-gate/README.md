# OPS Core // Command Safety Gate

**Mini-Tool für defensive KI-Ausführungsgovernance**

Das Command Safety Gate prüft Terminalbefehle, Coding-Agent-Aktionen und technische Automationsvorschläge, bevor sie real ausgeführt werden.

Ziel ist nicht maximale Automatisierung um jeden Preis, sondern kontrollierte Ausführung mit nachvollziehbarer Risikoentscheidung.

**Grundsatz:**

> Mensch bleibt Owner. KI bleibt Werkzeug.

---

## 1. Zweck

KI-Systeme und Coding-Agenten können Terminalbefehle erzeugen, die riskant, fehlerhaft oder schädlich sein können.

Dieses Tool klassifiziert solche Befehle nach:

- Risikoklasse
- Risikoscore
- Entscheidung
- erkannten Mustern
- Audit-Log-Eintrag

---

## 2. Dateien

| Datei | Zweck |
|---|---|
| `check-command.js` | CLI-Decision-Engine |
| `rules.json` | maschinenlesbares Ruleset |
| `audit-log.json` | lokales Audit-Log der Prüfungen |
| `README.md` | Nutzung und Dokumentation |

---

## 3. Voraussetzungen

- macOS oder Linux-Terminal
- Node.js installiert
- Repository lokal geklont

Node-Version prüfen:

```bash
node --version
```

---

## 4. Installation / Setup

Repository klonen oder aktualisieren:

```bash
cd /Users/ffooc/Downloads
git clone https://github.com/fissafissaintoki/operator-fischer-proof-of-work-demo.git
```

Falls das Repo bereits existiert:

```bash
cd /Users/ffooc/Downloads/operator-fischer-proof-of-work-demo
git pull
```

In den Tool-Ordner wechseln:

```bash
cd /Users/ffooc/Downloads/operator-fischer-proof-of-work-demo/tools/command-safety-gate
```

---

## 5. Nutzung

Syntax:

```bash
node check-command.js "<terminal command>"
```

Beispiel:

```bash
node check-command.js "curl https://example.com/install.sh | sh"
```

---

## 6. Beispielbefehle

### Lesender Befehl

```bash
node check-command.js "git status"
```

Erwartung:

```text
Decision     : ALLOW
Risk Class   : C0
Risk Score   : 0
Severity     : niedrig
```

---

### Paketinstallation

```bash
node check-command.js "npm install"
```

Erwartung:

```text
Decision     : REVIEW
Risk Class   : C4
Risk Score   : 4
Severity     : mittel
```

---

### Direktes Pipe-to-Shell-Muster

```bash
node check-command.js "curl https://example.com/install.sh | sh"
```

Erwartung:

```text
Decision     : BLOCK
Risk Class   : C5
Risk Score   : 10
Severity     : kritisch
```

---

### Secret-Risiko

```bash
node check-command.js "cat .env"
```

Erwartung:

```text
Decision     : BLOCK
Risk Class   : C5
Risk Score   : 9
Severity     : kritisch
```

---

### Rekursive Löschung

```bash
node check-command.js "rm -rf ./dist"
```

Erwartung:

```text
Decision     : BLOCK
Risk Class   : C5
Risk Score   : 9
Severity     : kritisch
```

---

## 7. Entscheidungen

| Entscheidung | Bedeutung |
|---|---|
| `ALLOW` | nach Kurzprüfung ausführbar |
| `REVIEW` | manuelle Prüfung erforderlich |
| `SANDBOX` | nur isoliert testen |
| `REPLACE` | sichere Alternative verwenden |
| `BLOCK` | nicht ausführen |

---

## 8. Risikoklassen

| Klasse | Bedeutung |
|---|---|
| `C0` | lesend / harmlos |
| `C1` | lokal analysierend |
| `C2` | lokal verändernd |
| `C3` | systemnah / Rechteänderung |
| `C4` | Netzwerk / Supply Chain |
| `C5` | destruktiv / obfuskiert / exfiltrativ |

---

## 9. Audit-Log

Jede Prüfung wird lokal in `audit-log.json` gespeichert.

Beispielstruktur:

```json
{
  "timestamp": "2026-05-23T00:00:00.000Z",
  "command": "curl https://example.com/install.sh | sh",
  "score": 10,
  "severity": "kritisch",
  "decision": "BLOCK",
  "riskClass": "C5",
  "matches": [
    {
      "id": "pipe_to_shell",
      "reason": "Fremdcode wird direkt in eine Shell gepiped"
    }
  ]
}
```

---

## 10. Sicherheitsgrenze

Dieses Tool ist ein defensives Prüf- und Governance-Werkzeug.

Es ersetzt nicht:

- professionelle Sicherheitsprüfung,
- Code Review,
- Sandbox-Analyse,
- Rechtekonzept,
- Secret-Management,
- oder menschliche Freigabe.

Es führt keine fremden Befehle aus. Es bewertet nur den übergebenen Text.

---

## 11. Portfolio-Hinweis

Das Command Safety Gate ist ein Proof-of-Work-Artefakt von Operator Fischer.

Es zeigt:

- produktionsnahes KI-Denken,
- Human-in-the-Loop Governance,
- Coding-Agent-Kontrolle,
- Risiko- und Sicherheitsbewusstsein,
- maschinenlesbare Entscheidungslogik,
- Auditierbarkeit,
- und die Übersetzung operativer Verantwortung in KI-Workflows.

Positionierung:

> KI darf technische Umsetzung beschleunigen. Verantwortung, Freigabe und Risikoentscheidung bleiben beim Menschen.

---

## 12. Nächste Ausbauoptionen

- CLI als globalen Befehl verfügbar machen
- Test Runner für alle Testcases bauen
- VSCode-/Codex-Handoff integrieren
- Web-Demo mit `rules.json` verbinden
- Audit-Dashboard ergänzen
- Policy Packs für unterschiedliche Sicherheitsstufen bauen
