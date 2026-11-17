# Radon Data Analysis – Dokumentation

> 5AHITS · INSY · Aldin Mukic & Lisa Hintermaier

## 1. Aufgabenstellung
Laut Angabe (`5AHITS_VibeCoding.pdf`) sollen die Radon-Messdaten eines Einfamilienhauses ausgewertet werden. Dazu gibt es drei Hinweise:
„Urlaub alles zu, niemand daheim“, „KWL IBN“ (Inbetriebnahme der kontrollierten Wohnraumlüftung) und „immer Fenster offen“.
Die Vorgeschichte: Eine kostenlose Messung über radon.gv.at hat das Problem aufgedeckt. Danach wurden eigene Sensoren aufgestellt, zuerst wurde
mit Lüften gegengesteuert, schließlich wurde eine Lüftungsanlage eingebaut.
Ziel der Arbeit: erklären, **was passiert, was man sieht, wie Radon ins Haus kommt, was hilft und ob man das in den Daten sieht**,
und **jede Auffälligkeit** finden. Weitere Angaben zum Haus gibt es nicht. Alles, was hier über das Haus steht, wurde aus den Daten abgeleitet.

## 2. Daten
`radon_sample_data.csv`, 229 403 Zeilen, **24.03.2026 – 13.10.2026**, rund 20 MB.

- **„Langes“ Format:** Jede Zeile ist die Meldung **eines** Geräts, alle anderen Spalten sind leer. Daraus wird pro Messgröße eine Zeitreihe gebaut,
  die auf ein 10-Minuten- und ein 1-Stunden-Raster gemittelt wird (`daten.py`).
- **7 Radon-Sensoren:** Technikraum, Werkstatt, Küche-Sockel, Küche, Wohnzimmer, Büro, Schlafzimmer. Etwa alle 10 min kommt ein Wert,
  die sechs gleichartigen Geräte melden zusätzlich ihre „Betriebszeit“ seit dem letzten Einschalten.
- **Raumklima** (Temperatur, Druck, CO₂, ab 10.07. auch die Luftfeuchte) gibt es nur in Küche und Schlafzimmer, und zwar ab 08.05. bzw. 13.05.
- **Wetter**, stündlich: Lufttemperatur, Luftdruck, Wind, Bodentemperatur in 0 / 6 / 54 cm Tiefe.

**Bereinigung:**
| Problem | Lösung | Anzahl |
|---|---|---|
| Nach einem Neustart meldet der Sensor zuerst 0 und dann stark springende Werte | Die erste Stunde nach jedem Neustart wird verworfen | 428 Werte |
| CO₂ unter 350 ppm (physikalisch unmöglich) | entfernt | 3 Werte |
| Doppelte Meldungen mit gleichem Zeitstempel | nur die erste behalten | 62 |
| Betriebszeit springt um ca. 30 min zurück | Das sind nur nachgeschickte alte Meldungen und **kein** Neustart (Schwelle: Rücksprung > 100 min) | – |

## 3. Vorgehen und Methoden
Alle Methoden sind bewusst einfach und erklärbar gehalten.

- **Zeiträume automatisch erkennen** (`analyse.py`, Abschnitt 1):
  - *Urlaub* ist die längste Zeit, in der das CO₂ in Küche **und** Schlafzimmer nie um mehr als 15 ppm in 10 min steigt. Dahinter steckt, dass Menschen CO₂ ausatmen.
  - *Fenster offen*: Eine Nacht (22–6 Uhr) gilt als „offen“, wenn das CO₂ im Schlafzimmer um weniger als 50 ppm steigt. Gesucht wird der längste Zeitraum, in dem
    über je 14 Nächte mindestens 2 von 3 Nächten „offen“ sind. Die Urlaubsnächte werden dabei übersprungen.
  - *Lüftungsanlage*: der erste Tag, ab dem der Keller (Tagesmittel) bis zum Datenende nie mehr über 100 Bq/m³ liegt.
- **Urlaub als natürliches Experiment:** Ist das Haus zu und niemand da, gelten einfache Formeln.
  - CO₂: C(t) = C_außen + (C₀ − C_außen)·e^(−n·t). Daraus ergibt sich der **Luftwechsel n**, also welcher Anteil der Luft pro Stunde ausgetauscht wird.
  - Radon: C(t) = C_gl + (C₀ − C_gl)·e^(−(n+λ)·t) mit λ = ln2 / 3,82 Tage. Daraus ergeben sich das **Gleichgewicht** und der **Zustrom** = C_gl·(n+λ).
  - Weil zwei unabhängige Messgrößen (CO₂ und Radon) den gleichen Luftwechsel liefern, ist das Ergebnis gut abgesichert.
- **Dunstabzug-Tag (20.07.):** gleiche Rechnung wie beim Urlaub, aber für einen einzelnen Tag (9–23 Uhr): Luftwechsel n aus dem CO₂-Abfall (Gerade durch ln(CO₂ − 420)),
  Zustrom = Anstieg pro Stunde + n · Radon. Vergleich mit dem Urlaubs-Zustrom (`analyse.dunstabzug_tag`).
- **Lüftungsereignisse:** Das Radon in Küche/Wohnzimmer fällt innerhalb von 90 min um mindestens 40 % (von mindestens 50 Bq/m³ aus). So schnell geht das nur mit Frischluft.
- **Kamineffekt:** Die Stundenwerte werden nach dem Temperaturunterschied innen − außen gruppiert und die Mittelwerte verglichen, getrennt vor und nach der Anlage.
- **Mehrfache lineare Regression** (Wohnräume ~ Temperaturunterschied + Wind + Druckänderung): zeigt den Einfluss jeder Größe, wenn die anderen gleich bleiben.
  Das ist nötig, weil sich Wetter-Größen überlagern (windige Tage sind oft kalte Tage).
- **Fairer Vorher/Nachher-Vergleich:** Verglichen werden nur Nächte mit **sicher geschlossenem Fenster** (CO₂ steigt um ≥ 100 ppm), gruppiert nach Außentemperatur.
  So wird nicht ein warmer Sommer mit einem kalten Herbst verglichen.
- **Druck durch den Kamineffekt:** Δp = g · h · (ρ_außen − ρ_innen) mit ρ = p / (R·T). Höhe h = 4,8 m (gemessener Abstand Küche ↔ Schlafzimmer).
  Sommer mit gemessenen Mitteltemperaturen, Winter mit Annahme 0 °C außen / 21 °C innen (`analyse.fazit_zahlen`).
- **Winter gegen Sommer:** gemessen = Wohnräume 24.–30.03. (Heizzeit, vor dem ungeklärten 31.03.) gegen Phase „Fenster offen“;
  mit Anlage = Stunden mit 15–25 °C Temperaturunterschied gegen 0–5 °C.
- **Stockwerk aus dem Luftdruck:** Δh = Δp / (ρ·g). Pro Meter Höhe sinkt der Luftdruck um ca. 0,11 hPa.
- **Korrelation:** zeigt, wie ähnlich zwei Räume über die Zeit verlaufen (+1 = gleich, 0 = unabhängig).

## 4. Aufbau des Codes
| Datei | Aufgabe |
|---|---|
| `daten.py` | CSV einlesen und prüfen (`DatenFehler` bei fehlender, leerer oder kaputter Datei), bereinigen, Zeitraster, Neustarts, Lücken |
| `analyse.py` | alle Auswertungen, schreibt `ergebnisse/ergebnisse.json` |
| `diagramme.py` | 10 PNG-Diagramme nach `diagramme/` |
| `auffaelligkeiten.py` | alle 31 Auffälligkeiten als Daten (Zeitraum, Messreihen, Text); Zahlen kommen aus der Analyse |
| `webseite.py` | setzt die Daten als JSON in die Vorlage ein → `radon.html` (eine Datei, ohne Server, offline) und öffnet sie |
| `webseite_vorlage.html` | HTML/CSS/JavaScript der Website; alle Diagramme selbst gezeichnet (SVG/Canvas), ohne Bibliotheken |
| `radon_laender.py` | Radon-Mittelwerte von 60 Ländern (UNSCEAR 2006, Österreich ÖNRAP) für die Weltkugel |
| `welt/laender_110m.json` | Ländergrenzen (world-atlas 2.0.2 / Natural Earth, ISC-Lizenz in `welt/LIZENZ_world-atlas.txt`) |
| `test_analyse.py` | 20 Tests: Fehlerfälle, Bereinigungsregeln, Ende-zu-Ende mit echten Daten, ein Mittelwert von Hand nachgerechnet, Website-Erzeugung |
| `RECHERCHE.md` | Fakten zu Radon mit Quellen (für Website und Doku) |

## 5. Ergebnisse

### 5.1 Die Geschichte in Phasen
| Phase | Zeitraum (automatisch erkannt) | Wohnräume Ø | Keller Ø | Schlafzimmer Ø |
|---|---|---|---|---|
| Frühling: morgens lüften | 24.03. – 21.06. | 34–45 | 18–19 | 46 |
| Sommer: Fenster immer offen | 22.06. – 22.08. (ohne Urlaub) | 26–31 | **91–96** | 45 |
| Urlaub: alles zu | 31.07. 05:00 – 06.08. 19:50 | **237–275** | **257–274** | **322** |
| Lüftungsanlage | ab 23.08. | 27–31 | 36–43 | 39 |

Alle Werte in Bq/m³ (Stundenmittel). WHO-Empfehlung: 100, Referenzwert in Österreich: 300 (jeweils als **Jahresmittel**).

### 5.2 Kernaussagen
1. **Das Haus ist sehr dicht.** Im Urlaub wurden nur **2–4 % der Luft pro Stunde** ausgetauscht (CO₂: 1,9 % bzw. 3,8 %, Radon: ≈ 2 %).
   Ohne Lüften strömen in die Wohnräume etwa **10 Bq/m³ pro Stunde** nach, und das Radon pendelt sich bei **360–400 Bq/m³** ein, also **über dem Referenzwert**.
2. **Lüften wirkt sofort, aber nur kurz.** Das Morgenlüften senkt das Radon in etwa 2 Stunden auf ca. 40 %. Nachts baut es sich wieder auf.
3. **Kamineffekt:** In den Wohnräumen steigt das Radon, je kälter es draußen ist (vor der Anlage bei 15–25 °C Unterschied ca. 82 statt 22 Bq/m³).
4. **Die Lüftungsanlage halbiert das Radon:** Bei geschlossenen Fenstern und gleicher Außentemperatur liegt es um **ca. 50 % niedriger** (21 gegen 22 Nächte),
   und der nächtliche Anstieg ist fast verschwunden. Den Keller hält sie dauerhaft unter 100.
5. **Winter gegen Sommer:** In der Heizzeit (Ende März) war es ohne Anlage **5,7-mal** so viel wie im Sommer (165 gegen 29 Bq/m³). Mit Anlage ist es bei Kälte nur noch
   ca. **2,4-mal** so viel (51 gegen 21). Der Sog durch den Kamineffekt beträgt im Sommer ca. **0,4 Pa**, im Winter ca. **4 Pa** (etwa 11-mal so viel), viel weniger als die Schwankung der Drucksensoren (± 2,8 Pa).
6. **Dichtheit:** 2–4 % Luftwechsel pro Stunde, empfohlen sind 30–50 %, also **8- bis 26-mal zu wenig**.
7. **Risiko:** Darby 2005: +16 % Lungenkrebs-Risiko pro 100 Bq/m³ (linear). Gemessener Schnitt (43) → ca. +7 %, geschlossenes Haus (≈ 360) → ca. +58 %.
8. **Es fehlt der Winter.** Der Messzeitraum geht von März bis Oktober. Die ersten Tage Ende März (Küche bis 707 Bq/m³) und der Anstieg ab Ende September
   zeigen, dass der Winter mit großem Temperaturunterschied und geschlossenen Fenstern der kritische Zeitraum ist.

### 5.3 Alle Auffälligkeiten
**Verhalten und Maßnahmen**
| Nr. | Wann | Was man sieht | Erklärung |
|---|---|---|---|
| A1 | 24.–30.03. | Küche im Tagesmittel bis 433, Spitze 707 Bq/m³; Küche-Sockel 293 | Ende der Heizzeit (außen 0–5 °C), starker Kamineffekt. Morgens wurde schon gelüftet, dazwischen waren die Fenster zu. **Ab 31.03. plötzlich nur noch 50–60**, die Ursache ist offen (siehe Fragen) |
| A2 | März – Juli | **107 plötzliche Abfälle**, davon 65 zwischen 5 und 8 Uhr, schon ab 24.03. | **Morgendliches Stoßlüften** von Anfang an (vom Hausbesitzer bestätigt), am Wochenende später. Nach Start der Anlage fast keine mehr |
| A3 | Frühling | In den Wohnräumen ist das Radon nachts 3–5-mal so hoch wie am Nachmittag (Höchstwert um 6 Uhr) | nachts kalt = starker Sog + Fenster zu; morgens gelüftet |
| A4 | April – Mai | Keller fast radonfrei (Ø 19), unabhängig von den Wohnräumen | Kellerfenster offen; der Keller ist ein getrennter Luftraum (Korrelation mit den Wohnräumen ≈ 0) |
| A5 | 22.–27.05. | Keller steigt 5 Tage lang gleichmäßig auf 230 und fällt am 27.05. abends schlagartig | Keller geschlossen, dann geöffnet. Die gleichmäßige Rampe zeigt, wie langsam sich ein geschlossener Raum füllt |
| A6 | vor der Anlage | Im Keller ist das Radon an **heißen** Tagen am höchsten, also umgekehrt zum Kamineffekt | Verhalten: Bei Hitze werden die Kellerfenster zugemacht (gegen Feuchte), bei kühlem Wetter geöffnet |
| A7 | 22.06. – Ende Aug. | Nachts steigen weder CO₂ noch Radon an | **„Immer Fenster offen“**: Die Wohnräume sind am niedrigsten, der **Keller aber am höchsten** (Ø 91–96, 40 % der Zeit über 100) |
| A8 | 20.07. | Wohnräume ab ca. 8:30 Uhr gleichmäßig bis 244, Küche-Sockel bis 502; nach Mitternacht in 2 h unter 50 | **Dunstabzug** (Hinweis des Hausbesitzers): Er bläst Luft aus dem dichten Haus, Bodenluft wird nachgesaugt. Zustrom **20 Bq/m³/h**, doppelt so viel wie im Urlaub (10), obwohl außen ≈ innen (23,9 gegen 23,3 °C), also ohne Kamineffekt. Am stärksten steigt der Sensor am Boden |
| A9 | 31.07. – 06.08. | Alle Räume steigen auf über 300, das CO₂ sinkt glatt auf 400 | **Urlaub** (vom Hausbesitzer bestätigt). Abreise ca. 31.07. 05:00, Heimkehr 06.08. ca. 20:00. Danach fällt das Radon in 3 h von 330 auf 14 (alles aufgerissen) |
| A10 | Urlaub | Luftfeuchte und Temperatur sind fast konstant | geschlossenes Haus, niemand kocht oder duscht. Das ist **kein** Sensorfehler (geprüft) |
| A11 | 07.–22.08. | Keller wieder bis 250. Am 14.08. ein Abfall von 230 auf 10, dann baut es sich über 6 Tage wieder auf | Kellerfenster nach dem Urlaub wieder zu; am 14.08. einmal gelüftet |
| A12 | ab 20.–23.08. | Keller sinkt dauerhaft unter 100; die Korrelation Keller ↔ Wohnräume geht von **−0,09 auf 0,70** | **Inbetriebnahme der Lüftungsanlage** (laut Hausbesitzer „ca. Ende August“, passt). Sie verbindet die Stockwerke und tauscht die Kellerluft aus |
| A13 | 23.08. früh | kurze Spitze in Wohnräumen und Schlafzimmer (bis ca. 150), während der Keller fällt | Vermutung: Beim Einregulieren der Anlage wurde Kellerluft nach oben verteilt |
| A14 | mit Anlage | Der Keller folgt jetzt dem normalen Kamineffekt (mehr Radon bei Kälte) | Der Keller wird nicht mehr per Fenster gelüftet, sondern ist Teil des gelüfteten Hauses |
| A15 | ab ca. 22.09. | langsamer Anstieg in allen Räumen (Werkstatt bis 88) | es wird kälter, der Kamineffekt wird stärker. Mit Anlage bleibt es aber unter 100 |
| A16 | Aug. → Sept. | Das Aufstehen (CO₂ im Schlafzimmer fällt) verschiebt sich von ca. 8:30 auf 7:20, am Wochenende ca. 1 h später | Ende der Sommerferien. Man sieht den Tagesablauf der Bewohner |

**Haus und Räume**
| Nr. | Was man sieht | Erklärung |
|---|---|---|
| B1 | Küche ↔ Wohnzimmer: Korrelation 0,93 | offener Wohn-Ess-Bereich, ein gemeinsamer Luftraum |
| B2 | Technikraum ↔ Werkstatt: 0,97, Lücken immer gleichzeitig | gemeinsamer Kellerraum bzw. offene Tür; beide Sensoren hängen am selben Strom/Netzwerk |
| B3 | Küche-Sockel ist meist höher als die Küche (Ø 60 gegen 44), mit vielen Einzelspitzen (bis 584) | Sensor in Bodennähe, vermutlich nahe einer **Eintrittsstelle** (Fuge/Durchführung). Mit Anlage ist er nicht mehr höher |
| B4 | Druck in der Küche immer 0,54 hPa höher als im Schlafzimmer (Streuung nur 0,03) | Das Schlafzimmer liegt ca. **4,8 m höher**, also im Obergeschoss (*Vermutung*, auch ein Kalibrierunterschied ist möglich) |
| B5 | Schlafzimmer trotz Obergeschoss höher als das Erdgeschoss (Ø 55 gegen 44) | Tür nachts zu und wenig Luftaustausch (CO₂ bis über 1 000 ppm). Möglich ist auch ein Unterschied durch den anderen Gerätetyp |
| B6 | Wind senkt das Radon ein wenig: mit Anlage 38 → 22 Bq/m³. Vor der Anlage sieht man das im einfachen Vergleich **nicht**, weil die windigen Tage Ende März zugleich die radonreichsten waren | Mit herausgerechneter Temperatur (Regression) ergibt sich vorher wie nachher dasselbe: ca. **−4,5 Bq/m³ pro 10 km/h**. Wind presst Außenluft durch Undichtigkeiten und verdünnt so. Der Effekt ist viel kleiner als der Kamineffekt |
| B7 | Luftdruckänderung: vorher +0,6, mit Anlage −0,6 Bq/m³ pro hPa | Die Richtung wechselt, also **kein verlässlicher Zusammenhang** |

**Datenqualität**
| Nr. | Was | Bedeutung |
|---|---|---|
| C1 | 48 Sensor-Neustarts; danach jeweils Nullen und ca. 1 h springende Werte | Anlaufzeit des Zählers, die Werte wurden entfernt (Diagramm 10) |
| C2 | 5-mal starten **alle** Sensoren gleichzeitig neu: 16.04., 06.07., 30.08., 10.09., 16.09. | Stromausfall oder Router-Neustart; 3 davon kurz nach dem Einbau der Anlage (Elektroarbeiten?) |
| C3 | Lücken: beide Kellersensoren 11.–13.06. (39 h), 13.–14.06., 19.–20.06., 22.–23.06., 27.–28.08.; Wetter 15.07. (14 h) | gemeinsamer Ausfall im Keller |
| C4 | CO₂ einmal 313 ppm (06.08.); im Urlaub liegt der „Außenwert“ bei 400–410 statt der realen ca. 425 ppm | Messfehler bzw. automatische Selbstkalibrierung des Sensors auf 400 |
| C5 | Betriebszeit springt um ca. 30 min zurück, 62 doppelte Meldungen | nachgeschickte alte Werte, kein Neustart |
| C6 | Schlafzimmer-Radon mit Kommazahlen und ohne Betriebszeit | anderes Gerätemodell als die übrigen sechs |
| C7 | Innendruck ca. 1 hPa über dem Wetterdruck | Die Wetterdaten gelten für eine etwas andere Höhe (Wettermodell bzw. Station) |
| C8 | Raumklima erst ab Mai, Luftfeuchte erst ab 10.07. | Sensoren wurden nach und nach ergänzt |

## 6. Entscheidungen
- **Erste Stunde nach einem Neustart verwerfen**, statt nur die Nullen zu entfernen: Auch die Werte nach den Nullen springen noch stark (Diagramm 10).
- **Regel „Fenster offen“ geändert:** Problem: Die erste Regel (5 von 7 Nächten) fand nur 07.–31.08., weil der Urlaub und drei kühle Nächte (11.–13.07.) den Zeitraum zerteilten.
  Versuche: Urlaubsnächte auf „unbekannt“ setzen (dann wurde 15.07.–31.08. gefunden) und verschiedene Fenster ausprobiert (7/4, 14/0,6, 14/⅔, 10/0,7).
  Lösung: Urlaubsnächte ganz überspringen, Regel „2 von 3 Nächten über 14 Nächte“. Ergebnis: 22.06.–30.08., passt zu den Diagrammen.
- **Luftwechsel aus nächtlichem CO₂-Abfall verworfen:** Im Alltag schlafen nachts Menschen im Haus, deshalb waren die Werte unbrauchbar (teils negativ). Verwendet wird nur der Urlaub.
- **Aussage zum Wind korrigiert:** Zuerst stand „mehr Wind → weniger Radon (40 → 26)“. Das stammte aus einer Probeauswertung ohne die ersten Märztage.
  Mit allen Daten verschwand der Effekt vor der Anlage. Grund: Ende März war es windig **und** sehr radonreich (Heizzeit). Lösung: eine Regression, die den
  Temperaturunterschied herausrechnet. Damit ist der Effekt vorher und nachher gleich groß (ca. −4,5 Bq/m³ pro 10 km/h), aber klein.
- **Gesamtdiagramm auf der Website:** Stundenwerte über 7 Monate waren zu unruhig (`diagramme/alt_gesamt_stundenwerte.png`). Jetzt wird je nach Zoom automatisch
  zu 3-/6-/12-/24-Stunden-Mitteln zusammengefasst. Beim Hineinzoomen erscheinen wieder die Stundenwerte.
- **Sieben Sensoren zu vier Gruppen zusammengefasst** (Wohnräume, Keller, Schlafzimmer, Küche-Sockel). Das ist erlaubt, weil Küche/Wohnzimmer/Büro bzw. Technikraum/Werkstatt
  fast gleich verlaufen, und die Diagramme bleiben so lesbar.

- **Dunkles Design → helles Design mit grünen Blasen** (Wunsch nach dem Feedback am 17.11.): Das dunkle Schema war ursprünglich so geplant (VS Code im Vollbild).
  Neu: heller, leicht grüner Hintergrund, weiße Karten mit Schatten, grüner Akzent und langsam schwebende grüne Blasen (reine CSS-Animation, abgeschaltet bei
  „Bewegung reduzieren“). Alle Farben im Code liefen schon über CSS-Variablen, deshalb mussten vor allem die Variablen und die fest eingetragenen Farben der zwei
  Schaubilder (Zerfallskette, Haus-Schnitt) und der Heatmap geändert werden. Alte Version: `diagramme/alt_website_dunkel.png`.
- **Grenzwert-Linien gestrichelt:** Im hellen Schema hatten die WHO-Linie (gelb) und der Küche-Sockel-Sensor (gelbbraun) fast dieselbe Farbe. Lösung: Grenzwerte gestrichelt mit weiß umrandeter Beschriftung.
- **Wissens-Fragen anfangs zugeklappt** (Feedback): Vorher war alles offen, die Seite war dadurch sehr lang. Jetzt stehen die Fragen kompakt in zwei Spalten, ein Knopf klappt alle auf.
  Problem dabei: Zugeklappte, breite Fragen hinterließen Lücken im Raster. Lösung: Breite Antworten nehmen erst aufgeklappt die ganze Zeile ein (`grid-auto-flow: dense`).
- **Tooltip mit Uhrzeit** (Feedback): In der Gesamtansicht zeigte der Tooltip nur das Datum und das Tagesmittel. Jetzt zeigt er immer Datum + Uhrzeit und den
  **Stundenwert** an der Mausposition, mit dem Hinweis, dass die Linie ein Mittelwert ist.
- **20.07. neu erklärt:** Zuerst als „Mini-Urlaub“ (Fenster einen Tag zu) gedeutet. Der Hausbesitzer gab den Tipp „Dunstabzug“. Nachgerechnet: Ohne Kamineffekt
  strömte doppelt so viel Radon nach wie im Urlaub, also muss ein zusätzlicher Sog gewirkt haben. Die alte Deutung erklärt den starken Zustrom nicht.

- **Weltkugel selbst gezeichnet statt mit einer Bibliothek** (Wunsch 17.11.): Wie die übrigen Diagramme ohne externe Bibliothek, damit die Seite eine einzige Datei bleibt und offline läuft.
  Orthografische Projektion auf einem Canvas; Punkte auf der Rückseite werden an den Kugelrand geschoben. Antarktis weggelassen (am Pol stark verzerrt, keine Wohnungen).
  Auf dem Handy dreht nur waagrechtes Wischen die Kugel, damit man über ihr weiterhin scrollen kann.
- **Länderwerte:** Die WHO-/UNSCEAR-PDFs ließen sich nicht direkt laden (Sperrseiten); die vollständige Tabelle kam aus dem UNSCEAR-2006-Bericht (Annex E, Tabelle 1).
  **Österreich:** UNSCEAR nennt nur einen alten Wert aus wenigen Messungen (15 Bq/m³), deshalb wird der Mittelwert der österreichischen Erhebung ÖNRAP verwendet (99 Bq/m³, Friedmann 2005).
  Der alte Quellenlink zu WHO/ENHIS war nicht mehr erreichbar und wurde durch UNSCEAR 2006 ersetzt; die Europa-Balken nutzen jetzt dieselben Werte.
- **100 gegen 300 Bq/m³:** Werte für 0/100/400 aus Darby 2005, der Wert für 300 ist interpoliert (so auf der Seite vermerkt).

## 6b. Rückmeldung des Hausbesitzers (17.11.)
| Aussage | Abgleich mit den Daten |
|---|---|
| Lüftungsanlage kam ca. Ende August | passt: automatisch erkannt ab 23.08., Abfall beginnt 20./21.08. |
| 20.07. hoher Wert in der Küche → Tipp Dunstabzug | passt: Zustrom 20 statt 10 Bq/m³/h ohne Kamineffekt, Sockel am höchsten (A8 neu) |
| Fenster wurden von Anfang an geöffnet, nur nicht so lange wie im Sommer | passt: Lüftungsereignisse schon ab 24.03. jeden Morgen; Texte A1/A2/Kapitel 1–2 angepasst |
| Urlaub stimmt | 31.07. 05:00 – 06.08. 19:50 bestätigt |
| 31.03. (plötzlicher Abfall) | noch offen |

## 6c. Abgleich mit Lisas Recherche („Radon – Entstehung, Wirkung und Schutz“)
- **Übereinstimmend:** Edelgas, Halbwertszeit 3,82 Tage, Folgeprodukte und Lunge, 10 % der Lungenkrebsfälle (~400/Jahr), Referenzwert 300, OÖ fast ganz Vorsorgegebiet außer Bezirk Ried, 37 Schutzgebiete.
- **Übernommen auf die Website:** Anteil an der Strahlenbelastung (ca. ein Drittel, geprüft: WKO/BMK-Leitfaden), im Freien unbedenklich, chemisch inert, Rechtslage
  (Strahlenschutzgesetz, RnV, Pflichten in Schutz-/Vorsorgegebieten), Kurz- vs. Langzeitmessung, Baustoffe und Brunnenwasser, Förderung OÖ (20 %, max. 2 000 €, ab 500 Bq/m³ Langzeitmessung, geprüft: Land OÖ 2023), Aufenthaltsräume nicht im Keller.
- **Korrigiert:** Lisa schreibt „Abluft- oder Überdruck-Lüftung hält Radon durch Druckausgleich fern“. Eine **reine Abluftanlage** erzeugt aber **Unterdruck** und damit mehr Radon
  (Studie Kanada); gut sind ausgeglichene Zu-/Abluft oder Überdruck. Unsere eigenen Daten zeigen genau diesen Effekt am Dunstabzug (A8).
- **Offene Frage von Lisa beantwortet:** Liegt eine Braunauer Gemeinde in einem Schutzgebiet? Laut Land OÖ (Radongebiete gemäß RnV) liegen alle 37 Schutzgebiete im Mühlviertel; Mining ist Vorsorgegebiet.
- **Nicht übernommen:** die Einstufung von Lochen laut einer Landeskarte von 2012 (laut Lisa selbst veraltet, nicht geprüft).

## 7. Anleitung zum Ausführen
```bash
git clone https://github.com/aldin-122/5AHITS-INSY-Radon.git
cd 5AHITS-INSY-Radon
python3 analyse.py        # Auswertung → ergebnisse/ergebnisse.json
python3 diagramme.py      # Diagramme → diagramme/
python3 webseite.py       # Website → radon.html, öffnet sich im Browser
python3 -m unittest -v test_analyse
```
Die Website hat einen **Testmodus**: `radon.html?test` prüft 34 Punkte (Wissen anfangs zugeklappt, Tooltip mit Uhrzeit, Weltkugel gezeichnet und drehbar, Fazit-Zahlen befüllt, alle Diagramme gezeichnet, alle 31 Auffälligkeiten in der Lupe, Rechner plausibel,
keine JavaScript-Fehler, kein waagrechtes Scrollen) und schreibt das Ergebnis in den Seitentitel und in `#testbericht`.
Mit `radon.html?zu=k-urlaub` springt man direkt zu einem Abschnitt.
Benötigt werden Python 3, pandas, numpy, scipy und matplotlib (auf diesem Mac vorhanden).

### Website (Phase 2)
Eine einzige Seite in vier Teilen: **1 Wissen** (12 Fragen, anfangs zugeklappt, Zerfallskette, Haus-Schnitt zum Kamineffekt, Boden-Vergleich, Risiko-Diagramme, Quellen),
**2 Geschichte** (Gesamtverlauf mit Phasen-Zoom, 5 Kapitel, Radon-Rechner), **3 Auffälligkeiten** (31 Karten mit Filter, Klick zeigt sie in der „Lupe“), **4 Fazit** (6 Karten „auf den Punkt“: wie schlimm, Lüften, Dichtheit, Druck, Winter/Sommer, 100 oder 300, darunter die Zusammenfassung). Im Wissen-Teil zusätzlich eine **drehbare Weltkugel** mit 60 Ländern.
Getestet mit headless Chrome bei 1440×900 und 390 px Breite (über einen iframe, weil headless Chrome mindestens 500 px breit ist).

## 8. Arbeit mit der KI
*(siehe `PROMPTS.md`)*
