# Recherche: Fakten zu Radon (für Website und Doku)

Gesammelt am 13.10.2026. Jede Aussage mit Quelle. Zahlen, die nur aus Sekundärquellen stammen, sind markiert.

## Was ist Radon?
- Radon-222 ist ein **radioaktives Edelgas**, farb-, geruch- und geschmacklos. Es entsteht im Boden und Gestein aus
  **Uran-238 → … → Radium-226 → Radon-222**. Halbwertszeit **3,8 Tage**. ([BfS Einführung](https://www.bfs.de/DE/themen/ion/umwelt/radon/einfuehrung/einfuehrung.html))
- Die kurzlebigen **Folgeprodukte** sind Polonium-218 (≈ 3 min), Blei-214, Bismut-214 und Polonium-214 (≈ 0,16 ms).
  Die Alphastrahlung kommt vor allem von den **Polonium-Isotopen**. ([ICRPaedia: Radon progeny](https://icrpaedia.org/Radon_progeny), [Chemie.de: Radon-Zerfallsprodukte](https://www.chemie.de/lexikon/Radon-Zerfallsprodukte.html))
- In Österreich ist Radon der **größte Beitrag zur durchschnittlichen Strahlenbelastung** der Bevölkerung. ([radon.gv.at: Warum ist Radon gefährlich?](https://www.radon.gv.at/rund-um-radon/warum-ist-radon-gefaehrlich))

## Warum ist es gefährlich? Warum gerade die Lunge?
- Das Gas selbst wird größtenteils wieder ausgeatmet. Seine **radioaktiven Folgeprodukte (Polonium, Blei, Bismut)
  sind aber Metalle**. Sie haften an Staubteilchen und an der **feuchten Schleimhaut der Atemwege**, zerfallen dort und
  bestrahlen die Zellen der Bronchien mit **Alphastrahlung**. ([radon.gv.at](https://www.radon.gv.at/rund-um-radon/warum-ist-radon-gefaehrlich))
- Alphastrahlung hat nur eine Reichweite von Bruchteilen eines Millimeters, gibt aber auf diesem kurzen Weg sehr viel Energie
  ab. Deshalb trifft sie genau die empfindliche Zellschicht der Bronchien und kann die **DNA schädigen**. Die Lunge ist das Organ mit der
  **höchsten Strahlenbelastung aus natürlichen Quellen**. ([SSK 1985](https://ssk.de/fileadmin/documents/de/1985/Strahlenexposition_Radon.pdf))
- Die WHO stuft Radon als **nachgewiesen krebserregend** ein, in derselben Klasse wie Tabakrauch und Asbest. Nach dem Rauchen ist Radon die **zweithäufigste
  Ursache für Lungenkrebs**, bei Nichtrauchern die **häufigste**. Nach heutigem Wissen verursacht es **keine anderen Krankheiten**.
  ([radon.gv.at](https://www.radon.gv.at/rund-um-radon/warum-ist-radon-gefaehrlich))
- Das Risiko steigt um **16 % pro 100 Bq/m³** Langzeitmittel, **linear und ohne Schwelle**. Es gibt also keinen „sicheren“ Wert.
  (Darby et al. 2005, BMJ, 13 europäische Studien, 7 148 Fälle; [Paper](https://carroll.stat.tamu.edu/wp-content/uploads/2023/10/darbypaper_BMJ.pdf), [WHO 2009](https://www.who.int/news/item/21-09-2009-who-calls-for-tighter-standards-on-indoor-radon))
- **Rauchen und Radon verstärken sich gegenseitig:** Das Lungenkrebsrisiko bis zum 75. Lebensjahr beträgt bei 0 / 100 / 400 Bq/m³
  für Nichtraucher ca. **0,4 / 0,5 / 0,7 %**, für Raucher ca. **10 / 12 / 16 %**, also etwa 25-mal so viel. (Darby et al. 2005)

## 100 oder 300 Bq/m³: Was sagen die Studien?
- **Europa:** 13 Fall-Kontroll-Studien, 7 148 Erkrankte: **+16 % pro 100 Bq/m³**, linear ohne Schwelle; auch bei Wohnungen unter 200 Bq/m³ noch signifikant (Darby et al. 2005, BMJ).
- **Nordamerika:** 7 Studien, 3 662 Erkrankte, 4 966 Kontrollen: **+11 % pro 100 Bq/m³** (Krewski et al. 2005, Epidemiology; [PubMed](https://pubmed.ncbi.nlm.nih.gov/15703527/)).
- **Dosis:** Umrechnung nach UNSCEAR 2000 (7 000 h zu Hause pro Jahr, Gleichgewichtsfaktor 0,4, 9 nSv pro Bq·h/m³): 100 Bq/m³ ≈ 2,5 mSv/Jahr, 300 Bq/m³ ≈ 7,5 mSv/Jahr.
  Neuere ICRP-Faktoren ergeben höhere Werte. Durchschnittliche Gesamtdosis in Österreich ca. 4,5 mSv/Jahr (gesundheit.gv.at).
- Lungenkrebs bis 75 je 1 000 Personen (Darby): Nichtraucher 4 / 5 / 7 bei 0 / 100 / 400 Bq/m³, Raucher 101 / 116 / 160. Für 300 interpoliert: ca. 6 bzw. 145.

## Radon in Wohnungen weltweit (für die Weltkugel)
- Landesmittelwerte (arithmetisch) aus **UNSCEAR 2006, Annex E, Tabelle 1** ([PDF](https://www.unscear.org/unscear/uploads/documents/publications/UNSCEAR_2006_Annex-E-CORR.pdf)), 60 Länder, siehe `radon_laender.py`.
  Weltmittel 46 Bq/m³ (ungewichtet), 39 Bq/m³ (bevölkerungsgewichtet), UNSCEAR 2000.
- **Österreich:** ÖNRAP 1, Mittelwert 99 Bq/m³ (Friedmann 2005, Health Physics). Die neuere Erhebung ÖNRAP 2 (2013–2019, ca. 50 000 Messungen, J. Environ. Radioact. 2021) ist nicht bevölkerungsgewichtet; ihren Mittelwert konnten wir nicht prüfen.

## Wie viele Menschen sind betroffen?
- **Österreich:** etwa **10 % der Lungenkrebsfälle, rund 400 pro Jahr** (BMK, zitiert in [Salzburg Merkblatt](https://www.salzburg.gv.at/fileadmin/Dateien/Gesundheit/Strahlenschutz/Merkblatt_Radonschutz.pdf) / [forum-media](https://www.forum-media.at/news/Arbeitssicherheit-Brandschutz/Neue-Radonschutzverordnung-seit-10.11.2020-in-Kraft));
  andere Quellen nennen 5–10 % ([Land Steiermark](https://www.umwelt.steiermark.at/cms/dokumente/12567949_135844309/ec27cdad/USB-11-13-Strahlen_.pdf)). 2025 gab es eine Neuberechnung der Todesfälle, die Zahl ist auf der Seite aber nicht veröffentlicht.
- **Deutschland:** ca. **6 % der Lungenkrebstodesfälle** ([BfS](https://www.bfs.de/DE/themen/ion/umwelt/radon/einfuehrung/einfuehrung.html)).
- **USA:** ca. **21 000 Lungenkrebstote pro Jahr** ([EPA](https://epa.gov/radon/what-epas-action-level-radon-and-what-does-it-mean), [American Lung Association 2025](https://www.lung.org/media/press-releases/radon-2025-ct)).
- **Weltweit / WHO:** **3–14 %** aller Lungenkrebsfälle, je nach Land (WHO-Handbuch 2009, über Reuters; *Sekundärquelle*).

## Ergänzungen aus Lisas Recherche (geprüft am 17.11.2026)
- Radon in Innenräumen verursacht etwa **ein Drittel der durchschnittlichen Strahlenbelastung** in Österreich, mehr als die Hälfte der natürlichen.
  ([WKO Leitfaden](https://www.wko.at/oe/betriebsanlagen/leitfaden-arbeitsplaetze-radonschutzgebiete.pdf), [gesundheit.gv.at](https://www.gesundheit.gv.at/leben/umwelt/radiokativitaet/strahlenbelastung.html))
- **Förderung OÖ:** 20 % der Sanierungskosten, max. 2 000 €, Voraussetzung Langzeitmessung über 500 Bq/m³ (Land OÖ, Präsentation 2023;
  [PDF](https://www.land-oberoesterreich.gv.at/Mediendateien/Formulare/Dokumente%20UWD%20Abt_US/Radon_2023_04_UL_Leithner.pdf)). Ältere Quelle (2022) nennt 1 000 Bq/m³.
- **Rechtslage:** Strahlenschutzgesetz 2020 + Radonschutzverordnung (BGBl. II Nr. 470/2020). Schutzgebiet: Messpflicht für Arbeitsplätze. Vorsorgegebiet: bauliche Vorsorge bei Neubauten.
- **Abluftanlagen** erzeugen Unterdruck und erhöhen eher das Radon; ausgeglichene Zu-/Abluft oder Überdruck ist besser (siehe „Was kann man tun?“).

## Grenzwerte und Empfehlungen
| Stelle | Wert | Bedeutung |
|---|---|---|
| **WHO** (2009) | **100 Bq/m³** | empfohlener Referenzwert; wenn nicht umsetzbar, höchstens 300 |
| **EU** (Richtlinie 2013/59/Euratom) | ≤ 300 Bq/m³ | Obergrenze für nationale Referenzwerte |
| **Österreich** (Radonschutzverordnung 2020) | **300 Bq/m³** | Referenzwert (Jahresmittel) für Aufenthaltsräume und Arbeitsplätze |
| **USA** (EPA) | 148 Bq/m³ (4 pCi/L) | „Action Level“; zwischen 75 und 150 Bq/m³ wird empfohlen, Maßnahmen zu überlegen |

Quellen: [WHO 2009](https://www.who.int/news/item/21-09-2009-who-calls-for-tighter-standards-on-indoor-radon), [WKO Erläuterungen RnV](https://news.wko.at/oe/news/radonschutzv--erlaeuterungen.pdf), [EPA](https://epa.gov/radon/what-epas-action-level-radon-and-what-does-it-mean).
**Wichtig:** Alle Grenzwerte beziehen sich auf das **Jahresmittel**, nicht auf Einzelspitzen.

## Welche Länder und Regionen sind betroffen?
- In Europa liegen die Landesmittelwerte zwischen ca. **20 Bq/m³** (Niederlande, Großbritannien) und **120–140 Bq/m³** (Tschechien, Finnland),
  also etwa um das Zehnfache auseinander (ältere Auswertung von JRC/WHO ENHIS; [WHO-Faktenblatt](https://who-sandbox.squiz.cloud/__data/assets/pdf_file/0005/97448/4.6_WEB.pdf)).
  Aktuelle Karten gibt es im [European Indoor Radon Map / JRC](https://publications.jrc.ec.europa.eu/repository/handle/JRC144439).
- **Österreich:** hohe Werte vor allem im **Granit- und Gneis-Hochland** (Böhmische Masse: **Mühlviertel, Waldviertel**) und in Teilen
  der Steiermark und Kärntens. **104 Gemeinden (≈ 5 %)** sind Radonschutzgebiete. ([Land OÖ](https://www.land-oberoesterreich.gv.at/radon.htm), [forum-media](https://www.forum-media.at/news/Arbeitssicherheit-Brandschutz/Neue-Radonschutzverordnung-seit-10.11.2020-in-Kraft))
  Karte: [AGES Radonkarte](https://geogis.ages.at/GEOGIS_RADON.html).

### Mining (Bezirk Braunau am Inn, Innviertel) – der Standort des Hauses
- Laut Land OÖ ist **fast ganz Oberösterreich Radon-Vorsorgegebiet**, ausgenommen ist nur der Bezirk Ried im Innkreis. **37 Gemeinden** sind
  das strengere **Radonschutzgebiet**, und alle liegen im **Mühlviertel** (Bezirke Freistadt, Urfahr-Umgebung, Rohrbach, Perg).
  **Mining liegt also in einem Vorsorgegebiet** (mittlere Stufe). Dort sind bei Neubauten bauliche Vorsorgemaßnahmen vorgeschrieben.
  ([Land OÖ: Radongebiete gemäß RnV](https://www.land-oberoesterreich.gv.at/Mediendateien/Formulare/Dokumente%20UWD%20Abt_US/Radongebiete_ooe_gemaess_rnv.pdf))
- Das Innviertel gehört geologisch zur **Molassezone** des Alpenvorlands (Sand, Schotter, Ton/Mergel) und nicht zum Granit der Böhmischen Masse.
  ([GBA, Erläuterungen Blatt Ried](https://opac.geologie.ac.at/ais312/dokumente/047_Ried_im_Innkreis.pdf), [GBA OG0088](https://opac.geologie.ac.at/ais312/dokumente/OG0088_015_A.pdf))
- **Folgerung für das Projekt:** Das Haus steht in keiner Hochrisiko-Gegend. Trotzdem wurden 700 Bq/m³ gemessen, weil ein **sehr dichtes Haus**
  auch wenig Radon aus dem Boden ansammelt.

## Wie kommt Radon ins Haus?
- Radon dringt aus Poren, Spalten und Rissen im Boden über **Risse im Fundament, Fugen, Kabel- und Rohrdurchführungen, Schächte**
  vor allem in den Keller ein und sammelt sich in Innenräumen an. ([BfS](https://www.bfs.de/DE/themen/ion/umwelt/radon/einfuehrung/einfuehrung.html), [LRA Ebersberg](https://lra-ebe.de/hostedmedia/2807/sg44_radon-sanierungsmassnahmen-bei-bestehenden-gebaeuden.pdf))
- Der **Antrieb ist ein Unterdruck im Haus**. Beim **Kamineffekt** steigt warme Luft im Haus auf und entweicht oben. Unten entsteht dadurch ein kaum spürbarer
  Unterdruck, der Bodenluft ansaugt. Je größer der Unterschied zwischen innen und außen, desto stärker ist der Sog, deshalb sind die Werte **im Winter und nachts höher**.
  Auch Wind und Abluftgeräte (Dunstabzug, Kamin, Trockner) erzeugen Unterdruck. ([Gutachten Bad Kreuznach](https://www.bad-kreuznach.de/buergerservice/wirtschaft-bauen-wohnen/stadtentwicklung-und-umwelt/bauleitplanung/rechtskraeftige-bebauungsplaene/e-begruendung-anlage-3-gutachterliche-stellungnahme-zur-radonbelastung-150609.pdf?cid=3dr))
- Ist der Keller nach oben **offen** (Stiege ohne Tür, Schächte), verteilt sich das Radon leicht in die oberen Stockwerke.

## Welche Rolle spielt der Boden (z. B. Lehm)?
Zwei Dinge sind entscheidend: **wie viel Radon im Boden entsteht** (Uran-/Radiumgehalt, Granit ist hoch) und **wie leicht die Bodenluft fließen kann** (Durchlässigkeit).
- **Lehm und Ton** sind dicht und meist feucht. Die Bodenluft fließt dadurch schlecht, und Häuser auf tonreichem Boden haben **tendenziell weniger Radon**. Ton kann aber
  selbst viel Radon bilden (Bodenluft 10–120 kBq/m³ gegenüber 4–20 kBq/m³ bei Kies). **Trocknet Lehm aus, bekommt er Schwundrisse**, und dann steigt die Durchlässigkeit stark an.
  ([USGS](https://pubs.usgs.gov/publication/70209723), [emfsurvey Übersicht](https://emfsurvey.com/?p=4436))
- **Nasser oder gefrorener Boden wirkt wie ein Deckel**: Das Radon kann nicht nach oben in die Atmosphäre entweichen, sucht sich den Weg des geringsten Widerstands, also das Haus, und staut sich unter der Bodenplatte. ([USGS](https://pubs.usgs.gov/publication/70209723))
- **Kies unter der Bodenplatte** leitet die Bodenluft gut. Das kann den Radoneintritt bis zu **5-mal** erhöhen, lässt sich aber auch für eine **Radonabsaugung** nutzen. ([AIVC](https://www.aivc.org/sites/default/files/airbase_4881.pdf))
- Die Durchlässigkeit kann sich an **derselben Stelle** im Lauf der Zeit um mehr als das 2-Fache bis etwa das 90-Fache ändern, je nach Feuchte.

## Wo und wie misst man?
- **Österreich:** kostenlose Messung für Privathaushalte (BMLUK/AGES). Man bekommt zwei passive Detektoren für die **zwei meistgenutzten Räume**
  (z. B. Wohn- und Schlafzimmer). Die Messung dauert **mindestens 6 Monate** und startet im Dezember oder Juli, damit sie Tages- und Jahresschwankungen mitnimmt. Danach schickt man die Detektoren an die AGES Linz.
  Die Daten fließen anonym in die Radonkarte ein. Bestellt wird in KW 28 oder 48, der nächste Termin ist der 23.11.2026. ([radon.gv.at](https://www.radon.gv.at/rund-um-radon/wie-kann-ich-radon-messen/kostenlose-radonmessung-in-privathaushalten))
- **Elektronische Sensoren** (wie hier) messen alle paar Minuten und zeigen Verläufe. Für die Bewertung nach dem Referenzwert zählt aber das **Langzeitmittel**.
- Eine Wiederholung der Messung wird alle **10 Jahre** in Radonvorsorgegebieten und alle **5 Jahre** in Radonschutzgebieten empfohlen.

## Was kann man tun?
- **Sofortmaßnahme:** Stoß- und Querlüften. Das hilft kurzfristig, ist laut radon.gv.at **langfristig aber nicht ausreichend**. ([radon.gv.at Radonsanierung](https://www.radon.gv.at/information-fuer/buergerinnen/radonsanierung))
- **Bautechnisch:** Eintrittswege abdichten (Risse, Durchführungen), die Kellertür dicht machen, unter der Bodenplatte absaugen (Radonbrunnen bzw. Unterboden-Absaugung,
  in einem Testhaus bis **−94 %**) und eine **Lüftungsanlage mit ausgeglichenem Druck** einbauen.
  Bei Häusern mit reiner Abluftanlage (5–9 Pa Unterdruck) wurden **höhere** Radonwerte gemessen als bei balancierter Zu- und Abluft (2–3 Pa).
  ([Kanada-Studie, PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12057567/), [AIVC](https://www.aivc.org/sites/default/files/airbase_5503.pdf))
- **Kosten:** einfache Sanierungen kosten meist wenige hundert Euro, aufwendigere etwa 2 000–15 000 €. **Förderungen** gibt es in OÖ, der Steiermark und Tirol. ([radon.gv.at](https://www.radon.gv.at/information-fuer/buergerinnen/radonsanierung))
- **Neubau:** Vorsorge ist günstiger und wirksamer als eine spätere Sanierung.
