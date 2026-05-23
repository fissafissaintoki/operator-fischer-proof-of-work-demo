# OPS Core Skill: Command Safety Gate

**Status:** Canonical Skill Artifact  
**Owner:** Operator Fischer  
**Layer:** OPS Core / KnowledgeOS / Defensive KI-Ausführungsgovernance  
**Purpose:** Sichere Prüfung von KI-generierten Terminalbefehlen, Coding-Agent-Aktionen und Automationsvorschlägen vor realer Ausführung.

---

## 1. Executive Summary

Das **Command Safety Gate** ist ein defensiver Governance-Baustein für produktionsnahe KI-Nutzung.

KI-generierte Terminalbefehle, Shell-Skripte, Coding-Agent-Aktionen und Automationsvorschläge werden nicht blind ausgeführt, sondern vorab nach Wirkung, Risiko, Rechtebedarf, Datei-/Netzwerkzugriff, Persistenz, Secret-Risiko und Rückrollbarkeit bewertet.

**Leitsatz:**

> Ich lasse KI nicht einfach ausführen. Ich lasse KI vorschlagen, prüfe Wirkung, Risiko, Rechte und Rückrollbarkeit und entscheide als Owner kontrolliert über Ausführung.

---

## 2. Governance-Grundsatz

**Mensch bleibt Owner. KI bleibt Werkzeug.**

Terminalausführung ist keine Vertrauenshandlung, sondern ein prüfpflichtiger Eingriff in ein System.

Jeder Command wird behandelt als:

```text
KI-Vorschlag -> Wirkungsprüfung -> Risikoklasse -> Owner-Freigabe -> kontrollierte Ausführung -> Log / Rollback
```

---

## 3. Problemklasse

Ungefilterte KI-Systeme, Coding-Agenten oder fremde Scripts können Befehle erzeugen, die:

- Daten löschen,
- Secrets auslesen,
- fremden Code ungeprüft ausführen,
- Persistenz einrichten,
- Systemrechte verändern,
- Netzwerkverbindungen öffnen,
- Repositorys oder Workspaces beschädigen,
- Supply-Chain-Risiken erzeugen.

Das Risiko entsteht nicht nur durch bösartige Absicht, sondern auch durch:

- Halluzination,
- unvollständigen Kontext,
- falsche Annahmen,
- blindes Copy-Paste,
- fehlenden Rollback,
- zu weit gefasste Befehle.

---

## 4. Command-Risikoklassen

| Klasse | Beschreibung | Beispiele | Entscheidung |
|---|---|---|---|
| C0 | Lesend / harmlos | `pwd`, `ls`, `git status` | Allow |
| C1 | Lokal analysierend | Tests, Version Checks, Suche | Allow nach Kurzprüfung |
| C2 | Lokal verändernd | Dateiänderung, Install, Build | Review |
| C3 | Systemnah | `sudo`, Rechte, Dienste | Manuelle Freigabe |
| C4 | Netzwerk / Supply Chain | Downloads, Paketquellen, Installer | Quellenprüfung + Isolation |
| C5 | Destruktiv / obfuskiert / exfiltrativ | Löschung, Secrets, Base64-Exec, Persistenz | Block |

---

## 5. Harte Stoppsignale

Folgende Muster lösen eine Sperr- oder Eskalationsprüfung aus:

| Muster | Risiko |
|---|---|
| `curl ... | sh` / `wget ... | bash` | Fremdcode wird ungeprüft ausgeführt |
| `sudo` ohne klare Begründung | Systemweite Änderung |
| Rekursive Löschbefehle | Datenverlust |
| Weite Rechtevergabe | Sicherheitsmodell wird geschwächt |
| Base64-Decoding + Ausführung | Verschleierte Codeausführung |
| `eval` | Dynamische und schwer prüfbare Ausführung |
| LaunchAgent-/Daemon-Manipulation | Persistenz auf macOS |
| Cronjobs / Autostart | Versteckte Wiederholung |
| Zugriff auf `.env`, SSH-Keys, Tokens, Keychain | Secret- oder Identitätsrisiko |
| Uploads zu unbekannten Hosts | Exfiltrationsrisiko |
| Fremde Binaries ohne Signatur/Quelle | Supply-Chain-Risiko |

---

## 6. macOS-Risikozonen

| Bereich | Bedeutung |
|---|---|
| `~/Library/LaunchAgents` | Benutzer-Autostart |
| `/Library/LaunchDaemons` | Systemweiter Autostart |
| `~/.ssh/` | SSH-Schlüssel / Identität |
| `.env` Dateien | API-Keys / Secrets |
| Keychain | Passwörter / Zertifikate |
| Shell-Profile | Persistente Terminal-Manipulation |
| Homebrew Taps | Externe Paketquellen |
| Gatekeeper-/Quarantine-Änderungen | Sicherheitsmechanismen |

---

## 7. Prüfmatrix vor Ausführung

Vor Ausführung muss beantwortet werden:

| Prüfdimension | Leitfrage |
|---|---|
| Ziel | Warum wird der Befehl benötigt? |
| Wirkung | Was verändert der Befehl konkret? |
| Pfade | Welche Dateien oder Ordner sind betroffen? |
| Rechte | Werden Adminrechte benötigt? |
| Netzwerk | Wird etwas heruntergeladen oder hochgeladen? |
| Secrets | Werden Tokens, Keys, `.env` oder Keychain berührt? |
| Persistenz | Wird Autostart, Cron oder Daemon-Logik eingerichtet? |
| Reversibilität | Gibt es einen Rollback? |
| Isolation | Muss der Befehl in Sandbox/Testordner laufen? |
| Entscheidung | Allow / Review / Sandbox / Replace / Block |

---

## 8. Entscheidungslogik

```text
IF Command is read-only:
    ALLOW
ELSE IF Command modifies local project files:
    REVIEW + Path Check + Rollback
ELSE IF Command uses admin rights or system paths:
    MANUAL OWNER APPROVAL
ELSE IF Command downloads or executes external code:
    SOURCE CHECK + NO DIRECT EXECUTION
ELSE IF Command touches secrets, persistence, obfuscation or destructive actions:
    BLOCK OR SANDBOX ONLY
```

---

## 9. Sichere Ersatzlogik

Unsichere One-Liner werden ersetzt durch getrennte Prüfschritte:

1. Quelle identifizieren.
2. Datei herunterladen, aber nicht ausführen.
3. Inhalt lesen.
4. Auffällige Muster prüfen.
5. Hash / Version / Herkunft prüfen, sofern möglich.
6. Nur begrenzt und bewusst ausführen.
7. Ergebnis dokumentieren.

**Prinzip:** Download und Ausführung werden niemals ungeprüft gekoppelt.

---

## 10. Coding-Agent-Handoff Template

Jeder Coding-Agent muss vor einer Terminalaktion diese Sicherheitsprüfung liefern:

```text
Ziel:
Befehl:
Risikoklasse: C0 / C1 / C2 / C3 / C4 / C5
Betroffene Dateien/Pfade:
Netzwerkzugriff: ja/nein
Benötigt sudo/Adminrechte: ja/nein
Persistenzrisiko: ja/nein
Datenverlust-Risiko: ja/nein
Secret-/Token-Risiko: ja/nein
Dry-Run oder sichere Alternative:
Rollback:
Empfehlung: ausführen / prüfen / sandboxen / ersetzen / blockieren
```

---

## 11. Skill-Einsatzfelder

- OPS Core Governance
- KnowledgeOS Skill Registry
- Prompterator Coding-Agent-Handoffs
- GitHub/Codex/Claude Orchestration
- macOS-Terminalarbeit
- Defensive OPSEC
- Bewerbungsportfolio / Everlast AI Positionierung
- Proof-of-Work-Artefakte
- Prozessautomatisierung mit Sicherheitsprüfung

---

## 12. Bewerbungsportfolio-Verankerung

### Kompetenzkarte

| Feld | Inhalt |
|---|---|
| Kompetenz | Defensive KI-Ausführungsgovernance |
| Artefakt | Command Safety Gate |
| Problem | KI kann riskante technische Vorschläge erzeugen |
| Lösung | Befehle werden klassifiziert, geprüft und freigegeben |
| Nutzen | Schutz vor Datenverlust, Secret-Leaks, Supply-Chain-Risiken und blinder Automatisierung |
| Business-Relevanz | Produktive KI braucht Governance, Nachvollziehbarkeit und Owner-Entscheidung |

### Portfolio-Formulierung

Operator Fischer bewertet KI-generierte Terminalbefehle und Coding-Agent-Aktionen nicht als neutrale Hilfestellung, sondern als prüfpflichtige Ausführungsobjekte. Jeder Command wird nach Wirkung, Rechtebedarf, Datei- und Netzwerkzugriff, Persistenz, Secret-Risiko, Datenverlust und Rückrollbarkeit bewertet. Dadurch entsteht eine sichere Brücke zwischen KI-Orchestrierung, technischer Umsetzung und operativer Verantwortung.

---

## 13. Interview-Formulierung

Wenn ein KI-System oder Coding-Agent einen Terminalbefehl vorschlägt, prüfe ich nicht nur, ob der Befehl funktionieren könnte. Ich prüfe, was er verändert, welche Rechte er benötigt, welche Dateien betroffen sind, ob Netzwerk- oder Secret-Risiken bestehen und ob es einen Rückrollweg gibt. Das ist für mich der Unterschied zwischen naiver KI-Nutzung und produktionsnaher KI-Orchestrierung.

---

## 14. Output-Entscheidungen

| Ergebnis | Bedeutung |
|---|---|
| ALLOW | Ausführung nach Kurzprüfung möglich |
| REVIEW | Manuelle Prüfung erforderlich |
| SANDBOX | Nur isoliert testen |
| REPLACE | Sichere Alternative verwenden |
| BLOCK | Nicht ausführen |

---

## 15. Qualitätsregel

Ein Command ist erst freigabefähig, wenn mindestens diese Punkte klar sind:

- Zweck verstanden
- Wirkung beschrieben
- betroffene Pfade bekannt
- Rechtebedarf geklärt
- Netzwerkzugriff geprüft
- Secret-Risiko ausgeschlossen oder kontrolliert
- Rollback möglich oder Risiko bewusst akzeptiert
- Owner-Freigabe erfolgt

---

## 16. Finaler Leitsatz

**Terminalbefehle aus KI-Systemen sind keine Befehle an den Menschen, sondern Vorschläge an den Owner. OPS Core prüft Wirkung, Risiko, Rechte und Rückrollbarkeit, bevor irgendetwas ausgeführt wird.**
