# Projektnotizen metis_logos

Arbeitsnotizen für die selbstständige Arbeit im Modul AI Operations
(HS26, FHNW). Keine ausformulierte Doku, sondern Fakten, Zahlen und
Entscheidungen, damit sie im Dezember nicht rekonstruiert werden müssen.

Abgabe: 06.12.2026, 23:59, Moodle.

---

## Thema

Transkript-Korrektur für den Sprachassistenten Metis. Input ist der rohe
Text aus Whisper, Output ein validierter Smart-Home-Befehl mit Zielgerät
und Konfidenz, oder die Feststellung, dass kein Befehl vorliegt.

Moodle-Eintrag: "Transcript correction for a home voice assistant
(noisy STT text → validated smart-home command)".

## Architekturentscheidungen

**Ein Artefakt, mehrere Umgebungen.** Keine Umgebungsabfragen im Code.
Alles Variable steht in `app/config.py` als Umgebungsvariable mit einem
Default, und der Default ist der lokale Betrieb. Begründung: Das Modul
verlangt "experimentelle-betriebliche Symmetrie" (Maturity-Deck, Folie 9).

**Logik getrennt von HTTP.** `app/corrector/` kennt kein FastAPI,
`app/main.py` ist nur die Hülle. Dadurch ist die Logik testbar und die
modellbasierte Variante später austauschbar, ohne die API anzufassen.

**Der Dienst schaltet nichts.** Er gibt strukturiertes JSON zurück, das
Schalten macht Metis. Dadurch braucht er weder MQTT-Zugang noch das
Heimnetz und läuft in der Cloud identisch.

**Dockerfile als gemeinsames Artefakt.** Ohne Dockerfile baut render auf
eigene Weise und die Symmetrie wäre nur behauptet. Python-Version ist
damit festgenagelt (lokal lief 3.14, im Image 3.13).

**Lokal produktiv, Cloud als Demo.** Produktiv läuft der Dienst auf
Thoth. Die render-Instanz ist eine Demo mit synthetischen Beispielsätzen.
Echte Transkripte verlassen das Haus nicht.

## Teilaufgabe 1.1 — DevOps lokal

Status: erledigt. Screenvideo vorhanden.
FastAPI, `python -m uvicorn app.main:app --reload`, 127.0.0.1:8000,
Oberfläche unter /docs.

## Teilaufgabe 1.2 — DevOps Cloud

Status: erledigt. Screenvideo vorhanden.

- Repo: https://github.com/NoahRolli/metis_logos
- Dienst: https://metis-logos.onrender.com
- Runtime Docker, Branch main, Region Frankfurt, Free-Instanz
- Auto-Deploy bei Push nachgewiesen (Deploy 2, Trigger "Auto-Deploy")

Betriebsgrenze Free-Tier: Instanz schläft nach Inaktivität ein, erster
Aufruf danach dauert bis zu einer Minute.

## Messung

Testsatz: 299 echte Transkripte aus dem Whisper-Log auf Thoth, 95 davon
eindeutig, von Hand beschriftet mit dem tatsächlich gemeinten Befehl.
17 Zeilen als `unclear` ausgeschlossen, weil nicht mehr rekonstruierbar.
Bewertet werden 78 eindeutige Zeilen bzw. 268 Vorfälle.

Zwei Quoten: ungewichtet zeigt, ob auch seltene Formulierungen
funktionieren, gewichtet beschreibt den Alltag.

| Stand | direkt (unique / gewichtet) | mit Rückfrage |
|---|---|---|
| Baseline, 11.11.2026 | 84.6% / 94.8% | 87.2% / 95.5% |
| nach Vokabular-Korrektur, 15.11.2026 | 93.6% / 98.1% | 96.2% / 98.9% |
| nach strengem Index-Vergleich, 15.11.2026 | 93.6% / 98.1% | 97.4% / 99.3% |

## Fundstück: Datenqualität schlägt Algorithmus

In der ersten Messung waren 8 von 78 Fällen falsche Befehle. Sieben
davon lagen nicht an der Korrekturlogik, sondern am Vokabular:

- Die Schlafzimmerlampen waren falsch zugeordnet. Gesprochen "bedroom
  one" und "bedroom two", in Zigbee2MQTT heissen sie `bed 1` und
  `bedroom 1`. Der Name `bedroom 1` ist ein Überbleibsel einer früheren
  Benennung und meint die zweite Nachttischlampe.
- "Turn off the light" für alle Lichter hatte keinen Alias und traf
  stattdessen "bed light".

Nach der Korrektur stieg die Quote von 84.6 auf 93.6 Prozent, ohne eine
Zeile an der Logik zu ändern. Das ist die Requirements-Schuld aus der
Technical-Debt-Aufgabe, belegt an eigenen Zahlen.

Offene technische Schuld: Die Namen in Zigbee2MQTT stimmen nicht mit der
Sprechweise überein. Eine Umbenennung dort würde das MQTT-Topic ändern
und die Entitäten in Home Assistant neu anlegen, deshalb übersetzt
vorerst das Vokabular.

## Fundstück: selbstsichere Fehltreffer

Die Rückfragefunktion rettete anfangs nur 2 von 12 Fällen. Grund: Die
Hauptfehlerquelle waren nicht unsichere Treffer, sondern Treffer mit
Konfidenz 1.0 auf die falsche Entität. Gegen die hilft keine Schwelle,
nur korrekte Stammdaten.

## Fundstück: nicht alle Wortteile sind gleich wichtig

"bedroom 1" und "bedroom 2" unterscheiden sich in einem Zeichen,
Ähnlichkeit 0.875, meinen aber verschiedene Lampen. Lösung: Ausdruck und
Alias werden in Basis und Index zerlegt, die Basis unscharf verglichen,
der Index exakt. Bei abweichendem Index fällt der Wert um den Faktor
`index_mismatch_penalty` (0.45) und landet im Rückfragebereich.

Wirkung: "bad room two" trifft trotz falsch gehörtem Raum die richtige
Lampe. "bedroom 3" existiert nicht und löst eine Rückfrage aus, statt
irgendetwas zu schalten.

## Synthetische Trainingsdaten

`scripts/generate.py`, fester Seed 20261115, 3625 Zeilen, 25 Klassen,
36 bis 223 Beispiele pro Klasse. Die Ungleichverteilung entsteht, weil
Gruppen mehr Aliase haben als einzelne Geräte; die kleinste Klasse ist
der Ventilator, der keine Helligkeitsbefehle kennt.

Rauschmuster stammen aus den echten Logs: zusammengesetzte Wörter
getrennt, Vokalverschiebung durch den Akzent (e wird als a gehört),
Ziffern als Zahlwort und deren Verhörungen.

Erste Fassung des Generators erzeugte unrealistische Sätze (doppelter
Artikel, "2b" als "toob", "brightness" als Satzanfang). Korrigiert,
bevor trainiert wurde. Lehre: Synthetische Daten brauchen dieselbe
Prüfung wie echte.

Methodisch wichtig: trainiert wird auf synthetischen Daten, gemessen auf
den echten. Sonst misst man nur, ob das Modell den Rauschgenerator
gelernt hat.

## Erwartung an Aufgabe 2

Die regelbasierte Version liegt bei 98.1 Prozent gewichtet. Ein Modell
wird das mit wenigen Dutzend echten Beispielen kaum übertreffen. Das ist
kein Misserfolg, sondern ein Ergebnis: geschlossenes Vokabular,
systematische statt zufällige Fehler, wenig Trainingsdaten.

## Offen

- Aufgabe 2: Azure ML, AutoML-Textklassifikation, Modell deployen
- Kostenmonitoring ab erstem Auftrag dokumentieren
- Aufgabe 3.1: Guardrail mit LiteLLM (Besprechung 24.11.)
- Aufgabe 3.2: Supply-Chain-Prüfung (Besprechung 01.12.)
- Reflexion der Gastvorträge: AWS 20.10., omegaML 17.11.
- Eigenständigkeitserklärung, Deklaration der KI-Nutzung
- Präsentation 08. oder 15.12., ca. 3.5 Minuten

## Einordnung nach Lektion 5 (Infrastructure Decisions)

Das Deck liefert den theoretischen Rahmen für Entscheidungen, die im
Projekt praktisch getroffen wurden.

**Paradigma.** Der Dienst läuft on-premises auf Thoth, als Demo in der
Public Cloud bei render.com, und die Spracherfassung geschieht am Edge
auf dem Voice-Puck. Die Architektur deckt damit alle drei Varianten ab,
die das Deck gegenüberstellt.

**"Welches ist das kleinste Modell, das die Aufgabe zuverlässig löst?"**
(Folie 15). Im Projekt durchgespielt: regelbasiert ohne Modell,
qwen3:30b-a3b, llama3.1:8b, qwen2.5:14b. Die regelbasierte Variante ist
die radikale Antwort auf diese Frage und erreicht 98.1 Prozent.

**Latenz.** Die Schwellen auf Folie 10 stufen alles über einer Sekunde
als "frustrierend" ein. Gemessen im Ollama-Log auf Thoth: 3.4 und 6.5
Sekunden pro Anfrage für qwen3:30b-a3b, bei mehreren Werkzeugrunden
entsprechend mehr. Die regelbasierte Korrektur antwortet in
Millisekunden. Für Sprachsteuerung ist Latenz das bindende Kriterium,
nicht Genauigkeit.

**Grenzen kleiner Modelle** (Folie 24): "Kleine Modelle tun sich schwer,
viele Regeln gleichzeitig zu befolgen." Im Projekt direkt beobachtet:
Der Systemprompt für den Konversationsagenten verlangt Namensauflösung,
Kürze, Mehrfachbefehle und Rückfragen zugleich. qwen3:30b-a3b hielt sich
nicht an die Kürze und gab seinen Denkprozess mit aus, der dann
vorgelesen wurde (rund drei Minuten). Das Schlüsselwort /no_think und
der entsprechende Schalter in Home Assistant blieben wirkungslos; erst
ein Modell ohne Denkmodus löste das Problem.

**Hybrides Routing** (Folie 19). Home Assistant bietet "Lokale
Verarbeitung von Befehlen bevorzugen": eindeutige Befehle gehen an die
regelbasierte Intent-Erkennung, nur der Rest an das Sprachmodell. Das
entspricht dem im Deck beschriebenen Muster.

**Dritter Beleg für Datenqualität vor Algorithmus.** Nach Verbesserung
des Whisper-Initial-Prompts wurden die Transkripte fehlerfrei — und die
Sprachsteuerung funktionierte schlechter als vorher. Grund: Home
Assistant kannte die nun korrekt verstandenen Gerätenamen nicht, weil
die Entitäten ohne passende Aliase freigegeben waren. Vorher hatte ein
ungenaues Transkript zufällig eine freigegebene Gruppe getroffen.

## Offene Frage

EU-AI-Act-Tabelle auf Folie 13 des Infrastructure-Decks (Art. 12, 14, 15
gegen On-Premises, Cloud, Edge): unklar, ob Abgabe oder nur
Unterrichtsdiskussion. Bei Mitstudierenden nachfragen.
