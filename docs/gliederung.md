# Gliederung der selbstständigen Arbeit

Stand 19.11.2026. Abgabe 06.12.2026.
Legende: [OK] Material vorhanden · [TEIL] angefangen · [FEHLT] nichts da

---

## 1. Einleitung

**1.1 Ausgangslage** [OK]
Sprachassistent Metis im eigenen Haushalt: Whisper auf Thoth, Home
Assistant auf Talos, Zigbee-Lampen. Beobachtetes Problem: systematische
Fehltranskriptionen bei schweizerdeutschem Akzent. 299 echte
Transkripte als Datengrundlage.

**1.2 Zielsetzung** [OK]
Ein Dienst, der rohe Spracherkennungstexte zu validierten
Smart-Home-Befehlen korrigiert. Nachweis der Verbesserung über eine
gemessene Trefferquote.

**1.3 Abgrenzung** [OK]
Der Dienst schaltet nicht selbst, er liefert strukturierte Befehle.
Keine Veränderung an Whisper selbst. Hierarchie bis Leuchtenebene,
Glühbirnenebene nur modelliert.

## 2. Vorgehensmodell

**2.1 SAFe als Rahmen** [FEHLT]
Die Modulbeschreibung verlangt ein an AI Operations angepasstes
Vorgehensmodell auf Basis von SAFe. Bisher nicht bearbeitet.
Nötig: Grundbegriffe (ART, PI Planning, Lean Portfolio Management) und
eine begründete Anpassung auf ein Einpersonenprojekt.

**2.2 Eingesetzte Werkzeuge** [OK]
Git/GitHub, Docker, FastAPI, render.com, Azure ML, pytest.

## 3. Teilaufgabe 1.1 — DevOps lokal

**3.1 Umsetzung** [OK]
Architektur: Konfiguration über Umgebungsvariablen, Logik getrennt von
HTTP, Vokabular als eigene Wissensbasis.

**3.2 Die Korrekturlogik** [OK]
Normalisierung, Aktionserkennung, Zielauflösung über Ähnlichkeit ohne
Leerzeichen, Konfidenzschwellen. Strenger Vergleich der Nummer,
unscharfer Vergleich der Wortbasis.

**3.3 Rückfragen statt Raten** [OK]
Drei Zustände: Befehl, Rückfrage, kein Befehl.

**3.4 Nachweis** [OK] Screenvideo vorhanden.

## 4. Teilaufgabe 1.2 — DevOps Cloud

**4.1 Reproduzierbarkeit über Docker** [OK]
Warum ohne Dockerfile keine Symmetrie entsteht. Python-Version lokal
3.14, im Image 3.13.

**4.2 Deployment auf render.com** [OK]
Konfiguration, Free-Tier-Grenzen, Kaltstart.

**4.3 Continuous Deployment** [OK]
Auto-Deploy bei Push, belegt durch Deploy 2 mit Trigger "Auto-Deploy".

**4.4 Nachweis** [OK] Screenvideo vorhanden.

## 5. Messung und Ergebnisse

**5.1 Aufbau des Testsatzes** [OK]
299 echte Transkripte, 95 eindeutig, von Hand beschriftet, 17 als
unclear ausgeschlossen. Trennung von Trainings- und Testdaten.

**5.2 Zwei Kennzahlen** [OK]
Ungewichtet und nach Häufigkeit gewichtet, und warum beide nötig sind.

**5.3 Ergebnisse** [OK]
Baseline 84.6/94.8 Prozent, nach Vokabularkorrektur 93.6/98.1, mit
Rückfrage 97.4/99.3.

**5.4 Fehleranalyse** [OK]
Sieben von acht Fehlern waren Stammdatenfehler. Selbstsichere
Fehltreffer lassen sich nicht über Schwellen abfangen.

## 6. Teilaufgabe 2 — Azure ML

**6.1 Synthetische Trainingsdaten** [OK]
Generator mit festem Seed, 3625 Zeilen, 25 Klassen. Rauschmuster aus
den echten Logs. Erste Fassung erzeugte unrealistische Sätze.

**6.2 Wahl des Verfahrens** [TEIL]
Klassisches AutoML auf CPU statt NLP-Textklassifikation auf GPU, mit
Begründung. Noch nicht durchgeführt.

**6.3 Training und Ergebnis** [FEHLT]

**6.4 Deployment als Endpunkt** [FEHLT]

**6.5 Verbesserung und erneutes Deployment** [FEHLT]
Die Aufgabe verlangt zwei Durchläufe.

**6.6 Vergleich mit der regelbasierten Version** [FEHLT]
Erwartung: Das Modell übertrifft 98.1 Prozent nicht. Begründung
vorbereitet.

**6.7 Nachweis** [FEHLT] Screenvideo.

## 7. Teilaufgabe 3.1 — Guardrail

[FEHLT] Besprechung am 24.11.
Anwendungsfall vorhanden: Diktierte Tagebucheinträge dürfen nicht
ungefiltert an ein Cloud-Modell gehen.

## 8. Teilaufgabe 3.2 — Supply Chain

[FEHLT] Besprechung am 01.12.
Vorarbeit vorhanden: Container läuft nicht als root.

## 9. Einordnung

**9.1 Reifegrad nach Google** [OK]
Das Projekt steht auf Stufe 0, manueller Prozess. Was Stufe 1
erfordern würde.

**9.2 Infrastrukturparadigma** [OK]
On-premises, Cloud und Edge im selben Projekt. Latenzschwellen gegen
gemessene Werte: 3.4 bis 6.5 Sekunden für das Sprachmodell gegen
Millisekunden für die Regel.

**9.3 Kleinstes ausreichendes Modell** [OK]
Vier Varianten durchgespielt. Grenzen kleiner Modelle bei vielen
gleichzeitigen Regeln, belegt am eigenen Fall.

**9.4 Technische Schulden** [OK]
Die sieben Kategorien, bezogen auf das Projekt. Requirements-Schuld an
eigenen Zahlen belegt.

**9.5 Reproduzierbarkeit, Testing, Monitoring, Automation** [TEIL]
Die Reflexionsfolie als Ausgangspunkt, und was seither geschlossen
wurde. Tests fehlen noch.

## 10. Kostenmonitoring

[TEIL] Nullpunkt-Screenshot steht aus, da Azure noch nicht genutzt.
Vorgehen und Abgrenzung auf die eigene Ressourcengruppe beschreiben.

## 11. Reflexion der Gastvorträge

**11.1 AWS, 20.10.** [FEHLT] Notizen?
**11.2 omegaML, 17.11.** [FEHLT] Teilgenommen?

## 12. Fazit und Ausblick

**12.1 Erkenntnisse** [OK]
Datenqualität vor Algorithmus, dreifach belegt. Messen vor Optimieren.

**12.2 Ausblick** [OK]
Glühbirnenebene, Anbindung als Konversationsagent, hybrides Routing.

## 13. Anhang

- Eigenständigkeitserklärung [FEHLT]
- Deklaration der KI-Nutzung [FEHLT]
- Repository-Link, Screenvideos
