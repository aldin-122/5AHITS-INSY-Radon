# Plan: Radon Data Analysis

## Status
Nutzer hat losgelegt („du sollst alles selbst herausfinden“, „Website wäre cool“) und will **weniger Phasen**,
Fragen und Verbesserungen laufend.

- [x] Phase 1 – Analyse: Daten aufbereiten, Auffälligkeiten, Ursachen, Wirkung von Lüften/KWL
- [x] Phase 2 – Website: Theorie + Daten-Geschichte mit vielen interaktiven Visualisierungen (fertig, wartet auf Feedback)
- [x] Phase 2b – Überarbeitung nach Feedback (17.11.): helles Design mit grünen Blasen, Wissen zugeklappt, Tooltip mit Uhrzeit,
  20.07. = Dunstabzug, „von Anfang an gelüftet“ eingearbeitet, Abgleich mit Lisas Recherche (wartet auf Feedback)
- [x] Phase 2c – Fazit „auf den Punkt“ (Lüften, Dichtheit, Druck, Winter/Sommer, 100 vs. 300), drehbare Weltkugel, Studienvergleich (wartet auf Feedback)
  - offen: Antwort des Hausbesitzers zum 31.03.
- [x] Phase 3 – Dokumentation (Quarto) und Abgabe über GitHub (Repo 5AHITS-INSY-Radon, GitHub Pages)

## Kontext
- Angabe (`5AHITS_VibeCoding.pdf`), Projekt „Radon Data Analysis“, Hinweise des Lehrers:
  - „Urlaub alles zu, niemand daheim“
  - „KWL IBN“ (Inbetriebnahme der kontrollierten Wohnraumlüftung)
  - „immer Fenster offen“
  - Dokumentation mit Quarto.
- Geschichte: Das Problem wurde durch die kostenlose offizielle Radonmessung (radon.gv.at) entdeckt.
  Danach eigene Sensoren, Versuche mit Lüften, schließlich Einbau einer Lüftungsanlage.
- Inhaltliche Fragen, die beantwortet werden sollen: Was passiert? Was sieht man? Wie kommt Radon ins Haus?
  Was kann man dagegen tun, und sieht man das in den Daten? Warum ist Radon ein Problem (Radioaktivität, Gesundheit)?

## Daten (erster Blick auf das Format, noch keine Auswertung)
- `radon_sample_data.csv`, 229 403 Zeilen, 24.03.2026 – 13.10.2026.
- „Langes“ Format: jede Zeile ist eine Meldung **eines** Sensors, alle anderen Spalten sind leer.
- 7 Radon-Sensoren: Büro, Küche, Küche-Sockel, Schlafzimmer, Technikraum, Werkstatt, Wohnzimmer
  (Messwert ca. alle 5 min, dazu „Betriebszeit“ = Laufzeit des Sensors seit dem letzten Einschalten).
- Raumklima (Druck, Temperatur, CO₂, ab Juli Luftfeuchte): Küche, Schlafzimmer (ab Mai).
- Wetter (stündlich): Temperatur, Luftdruck, Wind, Bodentemperatur in 0 / 6 / 54 cm.

## Phasen
**Phase 1 – Analyse**
Einlesen und in ein Zeitraster bringen, Datenqualität (Lücken, Sensor-Neustarts, Anlauf-Nullen),
Überblick + Grenzwerte, Räume/Stockwerke, Tages- und Wochengang, **jede Auffälligkeit** mit Erklärung,
Zeiträume Urlaub / „Fenster immer offen“ / KWL-Inbetriebnahme selbst finden, Ursachen
(Kamineffekt, Luftdruck, Wind, Boden, CO₂), Vorher/Nachher-Vergleich der Maßnahmen.

**Phase 2 – Website**
Eine einzige HTML-Datei (Python erzeugt sie, `webbrowser.open()`), dunkles Design, ganzer Bildschirm.
Theorie (Radon, Zerfall, Gesundheit, Weg ins Haus, Maßnahmen) + Daten-Geschichte mit vielen
interaktiven Diagrammen. Test per headless Chrome (1440×900 und schmal).

**Phase 3 – Dokumentation und Abgabe**
`dokumentation.qmd` → `dokumentation.html`, `DOKUMENTATION.md`, `README.md`, GitHub-Repo + Pages,
Test aus frischem Klon.

## Dateistruktur
```
radon_sample_data.csv     Rohdaten
daten.py                  Einlesen + Aufbereiten          ✔
analyse.py                Auswertungen → ergebnisse/      ✔
diagramme.py              PNGs für die Doku → diagramme/  ✔
test_analyse.py           20 Tests                        ✔
RECHERCHE.md              Fakten zu Radon mit Quellen     ✔
auffaelligkeiten.py       31 Auffälligkeiten als Daten     ✔
webseite.py               erzeugt radon.html              ✔
webseite_vorlage.html     HTML/CSS/JS der Website         ✔
radon_laender.py          Länderwerte für die Weltkugel   ✔
welt/laender_110m.json    Ländergrenzen (world-atlas)     ✔
dokumentation.qmd / .html
README.md, PLAN.md, PROMPTS.md, DOKUMENTATION.md
```

## Verifikation
- Kennzahlen stichprobenartig von Hand nachrechnen.
- Fehlerfälle: CSV fehlt, CSV kaputt/leer, fehlende Spalten.
- Webseite per headless Chrome (`?test`, Screenshots 1440×900 und schmal).
- Am Ende: frischer Klon + Live-Seite auf GitHub Pages.
