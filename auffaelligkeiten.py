"""Alle gefundenen Auffälligkeiten als Daten (für die Website).

Jede Auffälligkeit hat einen Zeitraum (von/bis) und die Messreihen, die man dafür
ansehen soll. Die Website zeigt sie damit per Klick in der „Lupe“ an.
Zahlen, die die Analyse berechnet, werden aus den Ergebnissen eingesetzt.
"""

WOHN = ["radon_Kueche", "radon_Wohnzimmer", "radon_Buero"]
KELLER = ["radon_Technikraum", "radon_Werkstatt"]


def komma(x):
    """Zahl mit einer Nachkommastelle und deutschem Komma, z. B. 23,9."""
    return f"{x:.1f}".replace(".", ",")


def liste(e):
    """Erstellt die Liste aus den Analyse-Ergebnissen `e` (siehe analyse.analysiere)."""
    z = e["zeitraeume"]
    u, up = z["urlaub"], e["urlaub_physik"]
    fv, ko, st = e["fairer_vergleich"], e["korrelationen"], e["stockwerk"]
    k, lw = e["kennzahlen"], e["lueften_wirkung"]
    dq = e["datenqualitaet"]
    # Fehlt der 20.07. in den Daten, werden Platzhalter eingesetzt, damit die Liste trotzdem entsteht
    dz = e.get("dunstabzug") or {k: float("nan") for k in ["wohn_start", "wohn_max", "sockel_max", "zustrom_bq_m3_h",
                                                            "zustrom_urlaub", "temp_aussen_max", "temp_innen"]}
    rv, rm = e["wetter"]["vor Lüftungsanlage"]["regression"], e["wetter"]["mit Lüftungsanlage"]["regression"]
    wm = e["wetter"]["mit Lüftungsanlage"]["wind"]["wohn"]
    ev = e["lueftungsereignisse"]
    morgens = sum(1 for x in ev if 5 <= int(x["zeit"][11:13]) <= 7)
    gl = [up["radon"][r]["gleichgewicht"] for r in ["Kueche", "Wohnzimmer", "Schlafzimmer"]]

    def a(nr, kat, titel, von, bis, reihen, was, warum, **extra):
        return {"nr": nr, "kategorie": kat, "titel": titel, "von": von, "bis": bis,
                "reihen": reihen, "was": was, "warum": warum, **extra}

    V, H, D = "Verhalten", "Haus", "Daten"
    return [
        a("A1", V, "Sehr hohe Werte zu Messbeginn", "2026-03-24", "2026-04-04", ["radon_Kueche", "radon_Wohnzimmer", "radon_Kueche - Sockel"],
          "In der Küche liegt das Tagesmittel bei bis zu 433 Bq/m³, die Spitze bei 707 Bq/m³. Ab dem 31.03. sind es plötzlich nur noch 50–60.",
          "Ende der Heizzeit: draußen 0–5 °C, drinnen warm, also ein starker Kamineffekt. Gelüftet wurde schon ab dem ersten Tag jeden Morgen "
          "(siehe A2), zwischen den Lüftungen waren die Fenster aber zu. "
          "Warum es am 31.03. so plötzlich besser wird, ist noch offen (wird beim Hausbesitzer nachgefragt)."),
        a("A2", V, "Jeden Morgen gelüftet", "2026-04-01", "2026-04-15", WOHN,
          f"{len(ev)} plötzliche Radon-Abfälle wurden erkannt, {morgens} davon zwischen 5 und 8 Uhr. "
          f"Nach dem Lüften liegt das Radon 2 Stunden später bei etwa {lw['nach_2h_prozent']:.0f} % des Werts davor.",
          "Morgendliches Stoßlüften war die erste Gegenmaßnahme, laut Hausbesitzer von Anfang an (erkannt schon ab 24.03.). "
          "Es wirkt sofort, aber nachts baut sich das Radon wieder auf. "
          "Nach dem Einbau der Lüftungsanlage kommt es fast nicht mehr vor."),
        a("A3", V, "Nachts 3- bis 5-mal mehr als am Nachmittag", "2026-04-13", "2026-04-21", WOHN,
          "Im Frühling erreicht das Radon in den Wohnräumen um ca. 6 Uhr seinen Höchststand und am Nachmittag den Tiefstand.",
          "Nachts ist es draußen kalt, deshalb ist der Kamineffekt am stärksten, und die Fenster sind zu. Tagsüber ist es wärmer und es wird gelüftet."),
        a("A4", V, "Keller im Frühling fast radonfrei", "2026-04-01", "2026-05-21", KELLER + ["radon_Kueche"],
          f"Technikraum und Werkstatt liegen im Frühling im Schnitt bei nur {k['Technikraum']['Frühling: morgens lüften']['mittel']:.0f} Bq/m³, "
          "weniger als in den Wohnräumen darüber.",
          "Die Kellerfenster waren offen. Der Keller ist ein eigener Luftraum, er verläuft völlig unabhängig von den Wohnräumen (Korrelation ≈ 0)."),
        a("A5", V, "Fünf Tage Rampe im Keller", "2026-05-18", "2026-06-01", KELLER,
          "Vom 22. bis 27.05. steigt das Radon im Keller gleichmäßig von ca. 5 auf 230 Bq/m³ und fällt am 27.05. abends schlagartig.",
          "Der Keller wurde zugemacht und dann wieder geöffnet. Die gleichmäßige Rampe zeigt, wie langsam sich ein geschlossener Raum mit Radon füllt."),
        a("A6", V, "Keller bei Hitze am höchsten", "2026-06-15", "2026-07-31", KELLER + ["radon_Kueche"],
          "Vor der Lüftungsanlage steigt das Radon im Keller, wenn es draußen wärmer ist als drinnen. Physikalisch müsste es genau umgekehrt sein.",
          "Das liegt am Verhalten: An heißen Tagen bleiben die Kellerfenster zu, damit keine feuchte Luft hineinkommt. Bei kühlem Wetter wird geöffnet.",
          diagramm="kamin"),
        a("A7", V, "„Immer Fenster offen“", z["fenster_offen"]["von"], "2026-07-30", WOHN + KELLER,
          f"Vom {z['fenster_offen']['von'][8:10]}.{z['fenster_offen']['von'][5:7]}. bis Ende August steigen nachts weder CO₂ noch Radon an. "
          f"Die Wohnräume sind so niedrig wie nie (Ø ≈ {k['Kueche']['Sommer: Fenster offen']['mittel']:.0f}), der Keller aber so hoch wie nie "
          f"(Ø ≈ {k['Werkstatt']['Sommer: Fenster offen']['mittel']:.0f}).",
          "Gelüftet wurde schon vorher, aber nur kurz. Im Sommer standen die Fenster oben Tag und Nacht offen. Den Keller erreicht diese Lüftung nicht."),
        a("A8", V, "Dunstabzug am 20.07.", "2026-07-18", "2026-07-22", WOHN + ["radon_Kueche - Sockel"],
          f"Ab ca. 8:30 Uhr steigt das Radon in allen Wohnräumen gleichmäßig an, von ca. {dz['wohn_start']:.0f} am Vormittag auf {dz['wohn_max']:.0f} Bq/m³, "
          f"am Küchen-Sockel sogar auf {dz['sockel_max']:.0f}. Kurz nach Mitternacht fällt es innerhalb von 2 Stunden auf unter 50.",
          f"Hinweis des Hausbesitzers: der <b>Dunstabzug</b>. Er bläst Küchenluft nach draußen. Weil das Haus sehr dicht ist, entsteht ein Unterdruck, "
          f"und Ersatzluft wird durch Ritzen angesaugt, auch aus dem Boden. Die Daten passen dazu: Es strömen ca. {dz['zustrom_bq_m3_h']:.0f} Bq/m³ pro Stunde nach, "
          f"doppelt so viel wie im Urlaub ({dz['zustrom_urlaub']:.0f}), obwohl es draußen fast so warm war wie drinnen "
          f"(bis {komma(dz['temp_aussen_max'])} °C gegen {komma(dz['temp_innen'])} °C), also ohne Kamineffekt. Am stärksten steigt der Sensor am Boden (Sockel). "
          "In der Nacht wurde gelüftet: Temperatur und Luftfeuchte fallen gleichzeitig."),
        a("A9", V, "Urlaub: alles über 300", u["von"][:10], u["bis"][:10], WOHN + KELLER + ["radon_Schlafzimmer"],
          f"Vom {u['von'][8:10]}.{u['von'][5:7]}. (ca. {u['von'][11:13]} Uhr) bis {u['bis'][8:10]}.{u['bis'][5:7]}. (ca. 20 Uhr) steigen alle Räume, "
          f"und es stellt sich ein Gleichgewicht bei {min(gl):.0f}–{max(gl):.0f} Bq/m³ ein. "
          "Nach der Heimkehr fällt das Radon in der Küche in 3 Stunden von 330 auf 14.",
          f"Niemand war da und alles war zu. Das Haus tauscht dann nur etwa {up['co2']['Schlafzimmer']['luftwechsel_pro_h']*100:.0f}–"
          f"{up['co2']['Kueche']['luftwechsel_pro_h']*100:.0f} % der Luft pro Stunde aus. Bei der Heimkehr wurde sofort alles aufgerissen.",
          zeige_von=u["von"][:10] + " 00:00", zeige_bis="2026-08-08"),
        a("A10", V, "Luftfeuchte im Urlaub wie eingefroren", "2026-07-25", "2026-08-12", ["feuchte_Kueche", "feuchte_Schlafzimmer"],
          "Im Urlaub bleibt die Luftfeuchte in Küche und Schlafzimmer fast genau gleich. Zuerst sah das wie ein Sensorfehler aus.",
          "Geprüft: Die Werte ändern sich weiterhin ein wenig, sie bleiben also nicht auf einem Wert hängen. Es hat einfach niemand gekocht, geduscht oder gelüftet. "
          "Das ist ein weiterer Beleg für das geschlossene Haus."),
        a("A11", V, "Keller nach dem Urlaub wieder zu", "2026-08-06", "2026-08-24", KELLER + ["radon_Kueche"],
          "Vom 07. bis 22.08. liegt der Keller wieder bei bis zu 250. Am 14.08. fällt er auf einmal auf 10 und füllt sich danach über 6 Tage wieder.",
          "Die Kellerfenster blieben zu. Am 14.08. wurde einmal gelüftet, danach wieder geschlossen."),
        a("A12", V, "Start der Lüftungsanlage", "2026-08-13", "2026-09-05", KELLER + WOHN,
          f"Ab dem {z['kwl']['ab'][8:10]}.{z['kwl']['ab'][5:7]}. bleibt der Keller dauerhaft unter 100. Die Korrelation zwischen Keller und Wohnräumen steigt von "
          f"{ko['keller_wohn_vor_kwl']:.2f} auf {ko['keller_wohn_nach_kwl']:.2f}.",
          "Die Lüftungsanlage ist in Betrieb. Sie tauscht die Luft im ganzen Haus aus und verbindet dabei die Stockwerke. Der Abfall beginnt schon am 20./21.08., "
          "das ist wahrscheinlich die Zeit der Einregulierung."),
        a("A13", V, "Kurze Spitze beim Einregulieren", "2026-08-22", "2026-08-26", WOHN + KELLER + ["radon_Schlafzimmer"],
          "Am 23.08. früh steigen die Wohnräume und das Schlafzimmer kurz auf ca. 140–180, während der Keller gerade fällt.",
          "Vermutung: Beim Einstellen der Anlage wurde radonreiche Kellerluft kurz nach oben verteilt."),
        a("A14", V, "Keller folgt jetzt dem Kamineffekt", "2026-08-23", "2026-10-13", KELLER + WOHN,
          "Mit der Anlage steigt das Radon im Keller wie in den Wohnräumen an, wenn es draußen kälter wird. Vorher war es umgekehrt (A6).",
          "Der Keller wird jetzt nicht mehr über die Fenster gelüftet, sondern gehört zum gelüfteten Haus.", diagramm="kamin"),
        a("A15", V, "Herbst: Es wird langsam mehr", "2026-09-15", "2026-10-13", KELLER + WOHN + ["radon_Schlafzimmer"],
          "Ab etwa 22.09. steigt das Radon in allen Räumen langsam an, in der Werkstatt auf Tagesmittel bis 88.",
          "Es wird kälter, der Temperaturunterschied und damit der Kamineffekt nehmen zu. Mit der Anlage bleibt es trotzdem unter 100. "
          "Der Winter wird zeigen, ob das reicht."),
        a("A16", V, "Man sieht die Sommerferien", "2026-08-03", "2026-09-27", ["co2_Schlafzimmer"],
          "Das Aufstehen (wenn das CO₂ im Schlafzimmer morgens fällt) verschiebt sich an Wochentagen von ca. 8:30 im August auf ca. 7:20 im September. "
          "Am Wochenende passiert es jeweils etwa 1 Stunde später.",
          "Die Sommerferien sind vorbei, Schule bzw. Arbeit beginnen wieder. Die Sensoren zeigen also auch den Tagesablauf der Bewohner."),

        a("B1", H, "Küche und Wohnzimmer sind ein Raum", "2026-04-05", "2026-04-15", ["radon_Kueche", "radon_Wohnzimmer"],
          f"Die beiden Kurven verlaufen fast gleich (Korrelation {ko['matrix']['Kueche']['Wohnzimmer']:.2f}).",
          "Wahrscheinlich ein offener Wohn-Ess-Bereich mit gemeinsamer Luft."),
        a("B2", H, "Technikraum und Werkstatt: ein Kellerraum", "2026-06-05", "2026-06-26", KELLER,
          f"Korrelation {ko['matrix']['Technikraum']['Werkstatt']:.2f}. Auch die Messlücken treten immer gleichzeitig auf.",
          "Gemeinsamer Luftraum bzw. offene Tür. Die beiden Sensoren hängen wohl an derselben Steckdose oder demselben Netzwerk."),
        a("B3", H, "Der Sockel-Sensor findet die Eintrittsstelle", "2026-07-05", "2026-07-26", ["radon_Kueche - Sockel", "radon_Kueche"],
          f"In Bodennähe ist es meist mehr als in der Küche (Ø {k['Kueche - Sockel']['gesamt']['mittel']:.0f} gegenüber {k['Kueche']['gesamt']['mittel']:.0f}), "
          "mit vielen Einzelspitzen bis 584.",
          "Radon kommt von unten. Der Sensor steht vermutlich nahe einer Fuge oder Durchführung. Mit der Anlage ist der Unterschied verschwunden."),
        a("B4", H, "Das Schlafzimmer liegt ca. 4,8 m höher", "2026-06-01", "2026-06-10", ["druck_Kueche", "druck_Schlafzimmer"],
          f"Der Luftdruck in der Küche ist immer um {st['druckdifferenz_hpa']:.2f} hPa höher als im Schlafzimmer (Streuung nur {st['streuung_hpa']:.3f} hPa).",
          f"Nach oben wird die Luft dünner, pro Meter um ca. 0,11 hPa. Das ergibt etwa {st['hoehe_m']:.1f} m, also das Obergeschoss. "
          "Das ist eine Vermutung, weil auch ein kleiner Kalibrierunterschied der Sensoren mitspielen kann."),
        a("B5", H, "Obergeschoss, aber viel Radon", "2026-05-14", "2026-06-14", ["radon_Schlafzimmer", "radon_Kueche"],
          f"Das Schlafzimmer hat im Schnitt mehr als das Erdgeschoss (Ø {k['Schlafzimmer']['gesamt']['mittel']:.0f} gegenüber {k['Kueche']['gesamt']['mittel']:.0f}).",
          "Nachts ist die Tür zu und es gibt kaum Luftaustausch (CO₂ über 1 000 ppm). Möglich ist auch ein Messunterschied, weil das Gerät ein anderes Modell ist."),
        a("B6", H, "Wind senkt das Radon ein wenig", "2026-04-01", "2026-10-13", WOHN,
          f"Mit Lüftungsanlage sinkt das Radon von {wm[0]:.0f} (Windstille) auf ca. {min(v for v in wm if v):.0f} Bq/m³ (über 10 km/h). Vor der Anlage sieht man das "
          "im einfachen Vergleich nicht, weil die windigen Tage Ende März zugleich die radonreichsten waren.",
          f"Rechnet man den Temperaturunterschied heraus (Regression), wirkt Wind vorher und nachher gleich: ca. {rv['pro_10kmh_wind']:.1f} bzw. "
          f"{rm['pro_10kmh_wind']:.1f} Bq/m³ pro 10 km/h. Wind presst Außenluft durch Undichtigkeiten ins Haus und verdünnt so das Radon. "
          "Der Effekt ist deutlich kleiner als der Kamineffekt.", diagramm="wind"),
        a("B7", H, "Luftdruck: kein klarer Einfluss", "2026-04-01", "2026-10-13", WOHN,
          f"Vor der Anlage gibt es bei steigendem Druck etwas mehr Radon ({rv['pro_hpa_druck']:+.1f} Bq/m³ pro hPa), mit Anlage etwas weniger ({rm['pro_hpa_druck']:+.1f}).",
          "Die Richtung wechselt, deshalb ist das kein verlässlicher Zusammenhang. In der Literatur zieht fallender Druck Bodenluft heraus. "
          "Bei diesem Haus sind Temperaturunterschied und Lüften viel wichtiger.", diagramm="druck"),

        a("C1", D, "Nullen nach jedem Neustart", "2026-04-16 04:00", "2026-04-16 11:00", ["roh_Kueche"],
          f"{sum(dq['neustarts_je_raum'].values())} Neustarts. Danach meldet der Sensor zuerst 0 und dann etwa eine Stunde lang springende Werte.",
          f"Der Zähler muss erst genug Zerfälle zählen. Die erste Stunde wurde deshalb entfernt ({sum(dq['anlaufwerte_entfernt'].values())} Werte)."),
        a("C2", D, "Alle Sensoren starten gleichzeitig neu", "2026-03-24", "2026-10-13", ["radon_Kueche"],
          "Fünfmal starten alle Sensoren gleichzeitig neu: " + ", ".join(f"{x['zeit'][8:10]}.{x['zeit'][5:7]}." for x in dq["gemeinsame_neustarts"]) + ".",
          "Stromausfall oder Neustart des Routers. Drei davon kommen kurz nach dem Einbau der Lüftungsanlage, vielleicht wegen Elektroarbeiten.",
          markierungen=[x["zeit"] for x in dq["gemeinsame_neustarts"]]),
        a("C3", D, "Messlücken im Keller", "2026-06-08", "2026-06-25", KELLER,
          "Beide Kellersensoren fallen gleichzeitig aus: 11.–13.06. (39 h), 13.–14.06., 19.–20.06., 22.–23.06. und 27.–28.08. Die Wetterdaten fehlen am 15.07. 14 Stunden lang.",
          "Gemeinsamer Ausfall (Strom/WLAN im Keller). Die Lücken bleiben im Diagramm leer und werden nicht erfunden."),
        a("C4", D, "CO₂ unter Außenluft", "2026-08-05", "2026-08-07 12:00", ["co2_Kueche", "co2_Schlafzimmer"],
          "Am 06.08. um 10:03 zeigt die Küche einmal 313 ppm an. Im Urlaub sinken beide Sensoren auf 400–410 ppm, obwohl die Außenluft heute ca. 425 ppm hat.",
          "313 ppm ist ein Messfehler und wurde entfernt. Die 400 kommen von der Selbstkalibrierung der Sensoren, die ihren tiefsten Wert als 400 annehmen.",
          markierungen=["2026-08-06 10:03"]),
        a("C5", D, "Doppelte und nachgeschickte Meldungen", "2026-04-30 12:00", "2026-04-30 22:00", WOHN,
          f"{dq['doppelte_meldungen']} Meldungen kommen doppelt. Manchmal springt die Betriebszeit um ca. 30 Minuten zurück.",
          "Die Sensoren schicken ältere Werte nach. Das ist kein Neustart (Schwelle: Rücksprung > 100 min)."),
        a("C6", D, "Ein Sensor ist anders", "2026-05-13", "2026-06-13", ["radon_Schlafzimmer"],
          "Nur das Schlafzimmer-Radon hat Kommazahlen, keine Betriebszeit und kommt in der gleichen Zeile wie die Raumklima-Werte.",
          "Es ist ein anderes Gerätemodell (Kombi-Gerät mit CO₂, Temperatur und Feuchte). Die Werte sind darum nur eingeschränkt mit den anderen vergleichbar."),
        a("C7", D, "Innendruck höher als der Wetterdruck", "2026-06-01", "2026-06-15", ["druck_Kueche", "druck_Wetter"],
          "Der Druck in der Küche liegt immer ca. 1 hPa über dem Luftdruck aus den Wetterdaten.",
          "Die Wetterdaten gelten für eine andere Höhe (ca. 8 m Unterschied). Für den Kamineffekt wird deshalb die Temperatur verwendet, nicht der Druck."),
        a("C8", D, "Sensoren kamen nach und nach dazu", "2026-03-24", "2026-07-15", ["radon_Kueche", "radon_Wohnzimmer", "radon_Kueche - Sockel", "radon_Werkstatt", "radon_Schlafzimmer"],
          "Küche ab 24.03., Büro und Wohnzimmer ab 27.03., Sockel ab 30.03., Keller ab 01.04., Raumklima ab 08./13.05., Luftfeuchte ab 10.07.",
          "Das Messsystem ist gewachsen. Vergleiche zwischen Räumen nutzen deshalb nur Zeiten, in denen beide messen."),
    ]
