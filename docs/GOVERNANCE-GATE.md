# OPS Core Governance Gate

## Zweck

Das Governance Gate ist der Pruef- und Freigabelayer fuer OPS Core, KnowledgeOS und Prompterator.

Es stellt sicher, dass aus Rohinput keine unkontrollierten, riskanten oder nicht wiederverwendbaren Ergebnisse entstehen. Jedes Artefakt wird vor Nutzung, Veroeffentlichung oder Automatisierung entlang fester Kriterien bewertet.

## Grundsatz

> Mensch bleibt Owner. KI bleibt Werkzeug.

KI darf strukturieren, vorschlagen, verdichten und vorbereiten. Die Verantwortung fuer Nutzung, Freigabe, Weitergabe und Umsetzung bleibt beim menschlichen Owner.

## Kernfluss

```text
Rohinput
  -> Problemklasse
  -> Output-Ziel
  -> Risiko-Klasse
  -> Artefakt-Pruefung
  -> Public-Safe-Pruefung
  -> Freigabe / Block / Rueckfrage
  -> Wiederverwendung
```

## Risiko-Klassen

| Klasse | Bedeutung | Behandlung |
|---|---|---|
| SAFE | Dokumentation, Strukturierung, interne Notizen ohne sensible Inhalte | Direkt bearbeitbar |
| LOW | Kleine Text-, README-, Portfolio- oder Layout-Anpassungen | Bearbeitbar mit Kurzpruefung |
| MEDIUM | Prozesslogik, Dossier, Backend-nahe Dokumentation, externe Wirkung | Pruefung und klare Annahmen erforderlich |
| HIGH | Recht, Datenschutz, HR, Finanzen, Sicherheit, produktive Prozesse, API-/Deployment-Kontext | Nur mit Owner-Freigabe und Pruefhinweis |
| BLOCK | Secrets, personenbezogene Daten, Datenabfluss, schädliche Automatisierung, destruktive Befehle | Nicht ausfuehren |

## Public-Safe-Pruefung

Ein Artefakt ist nur public-safe, wenn alle Punkte erfuellt sind:

- Keine Kundennamen.
- Keine Kennzeichen.
- Keine internen Standort-, Lager-, Touren- oder Systemnummern.
- Keine personenbezogenen Daten.
- Keine echten Betriebsdaten mit Rueckschlussrisiko.
- Keine API-Keys, Tokens, Secrets oder Credentials.
- Keine vertraulichen Prozessdetails.
- Keine nicht freigegebenen Bilder, Screenshots oder Dokumente.
- Keine irrefuehrenden Leistungs-, Rechts- oder Compliance-Behauptungen.

## Artefakt-Qualitaetsgate

Ein Artefakt darf erst wiederverwendet werden, wenn diese Punkte erfuellt sind:

| Prueffeld | Leitfrage | Status |
|---|---|---|
| Problemklasse | Ist klar, welches Problem geloest wird? | Pflicht |
| Zielgruppe | Fuer wen ist das Artefakt geschrieben? | Pflicht |
| Outputformat | Ist das Zielformat eindeutig? | Pflicht |
| Fakten / Annahmen / Hypothesen | Sind Aussagen sauber getrennt? | Pflicht |
| Risiken | Sind operative, rechtliche oder technische Risiken markiert? | Pflicht |
| Governance | Ist klar, wer prueft und freigibt? | Pflicht |
| Wiederverwendung | Kann das Artefakt ohne Originalchat verstanden werden? | Pflicht |
| Public-Safe | Ist externe Weitergabe unkritisch? | Pflicht bei oeffentlichen Artefakten |

## Freigabe-Entscheidung

| Ergebnis | Bedeutung | Aktion |
|---|---|---|
| RELEASE | Artefakt ist verwertbar und public-safe | Nutzen / verlinken / weitergeben |
| REVIEW | Artefakt ist verwertbar, braucht aber fachliche Pruefung | Owner prueft vor Nutzung |
| REWORK | Artefakt ist noch nicht sauber genug | Ueberarbeiten |
| HOLD | Risiken oder offene Punkte verhindern Freigabe | Nicht weitergeben |
| BLOCK | Sicherheits-, Datenschutz- oder Missbrauchsrisiko | Nicht ausfuehren / nicht speichern / nicht veroeffentlichen |

## Command Safety Gate

Terminalbefehle, Coding-Agent-Aktionen und Installationsanweisungen werden gesondert geprueft.

### Pruefschema

```text
Befehl / Aktion:
Zweck:
Betroffene Dateien:
Dateizugriff:
Netzwerkzugriff:
Rechtebedarf:
Loesch-/Ueberschreibungsrisiko:
Secret-Risiko:
Persistenz / Autostart:
Rollback-Moeglichkeit:
Risiko-Klasse: SAFE / LOW / MEDIUM / HIGH / BLOCK
Urteil:
```

### BLOCK-Signale

- `curl | sh` oder `wget | sh` ohne manuelle Pruefung.
- `sudo` ohne klare Notwendigkeit.
- Zugriff auf `.env`, `.ssh`, API-Keys, Tokens oder Credentials.
- Obfuskierter Code, Base64-Ausfuehrung oder verschleierte Scripts.
- Rekursives Loeschen ohne vorherige Dateiliste.
- Persistenz ueber LaunchAgents, Daemons oder Autostart ohne Freigabe.
- Netzwerkverbindungen zu unbekannten Quellen.
- Datenabfluss, Exfiltration oder unklare Uploads.

## KnowledgeOS-Aufnahmegate

Nicht jeder Output wird gespeichert. KnowledgeOS speichert nur kuratierte, wiederverwendbare Inhalte.

Eintrag erlaubt, wenn:

- Skill oder Artefakt wiederverwendbar ist.
- Problemklasse klar benannt ist.
- Governance-Grenzen enthalten sind.
- keine vertraulichen Inhalte enthalten sind.
- der Eintrag ohne Chatkontext verstaendlich ist.

Eintrag nicht erlaubt, wenn:

- es nur ein Chatdump ist.
- personenbezogene oder vertrauliche Daten enthalten sind.
- der Nutzen nicht wiederverwendbar ist.
- der Inhalt spekulativ als Fakt gespeichert wuerde.

## OPS-Core-Routing

| Inputtyp | Modus | Governance |
|---|---|---|
| Idee / Rohnotiz | Strukturieren | LOW |
| Bewerbungs-/Portfolioinhalt | Public-Safe Packaging | MEDIUM |
| Prozess-Use-Case | Process-AI Mapping | MEDIUM |
| Terminalbefehl | Command Safety Gate | HIGH |
| API-Key / Secret / Credential | Block / Setup-Sicherheitsflow | BLOCK / HIGH |
| Recht / Datenschutz / HR | Pruefhinweis + keine Rechtsberatung | HIGH |
| Oeffentliches Repo | Public-Safe Review | MEDIUM |

## Standard-Pruefvermerk

```text
Governance Check
- Problemklasse:
- Risiko-Klasse:
- Public-Safe: ja / nein / pruefen
- Fakten sauber getrennt: ja / nein
- Annahmen markiert: ja / nein
- Owner-Freigabe erforderlich: ja / nein
- Ergebnis: RELEASE / REVIEW / REWORK / HOLD / BLOCK
```

## Anwendung im Prompterator-Kontext

Das Governance Gate wird genutzt fuer:

- README- und Repo-Dokumentation.
- Portfolio-Onepager.
- Use-Case-Dossiers.
- PDF-/HTML-Renderpfade.
- KnowledgeOS Skill Registry.
- Coding-Agent-Handoffs.
- oeffentliche Proof-of-Work-Artefakte.

## Grenzen

Dieses Dokument ersetzt keine rechtliche, steuerliche, datenschutzrechtliche, medizinische, sicherheitstechnische oder fachliche Pruefung.

Es ist ein operatives Kontrollmodell fuer strukturierte KI-Arbeit, nicht fuer autonome Entscheidung.

## Status

Build-Status: `v0.1 OPS Core Governance Gate`

Dieses Dokument ist ein additiver Governance-Layer. Es veraendert keine bestehende Prompterator-Logik und keine Renderpfade.
