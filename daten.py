"""Einlesen und Bereinigen der Radon-Messdaten.

Die CSV-Datei hat ein „langes“ Format: Jede Zeile ist die Meldung von genau EINEM
Gerät, alle anderen Spalten sind leer. Dieses Modul macht daraus eine Zeitreihe pro
Messgröße und legt sie auf ein festes Zeitraster (10 Minuten bzw. 1 Stunde).
"""

from pathlib import Path

import pandas as pd

ORDNER = Path(__file__).resolve().parent
CSV_STANDARD = ORDNER / "radon_sample_data.csv"

# Räume mit Radon-Sensor. Reihenfolge = Reihenfolge in Diagrammen (Keller → oben).
RAEUME = ["Technikraum", "Werkstatt", "Kueche - Sockel", "Kueche", "Wohnzimmer", "Buero", "Schlafzimmer"]
KELLER = ["Technikraum", "Werkstatt"]
WOHNRAEUME = ["Kueche", "Wohnzimmer", "Buero"]

# Diese Spalten müssen vorhanden sein, sonst ist die Datei nicht die erwartete.
PFLICHTSPALTEN = ["Zeit (Europe/Vienna)"] + [f"{r} – Radon (Bq/m³)" for r in RAEUME]

# Nach einem Neustart liefert der Radon-Sensor erst Nullen und dann stark springende
# Werte, weil er noch zu wenige Zerfälle gezählt hat. Die erste Stunde wird verworfen.
ANLAUFZEIT_MIN = 60

# CO₂ kann in Innenräumen nicht unter dem Außenwert (~420 ppm) liegen. Ein Sensor, der
# selbst auf 400 kalibriert, kann knapp darunter liegen, deutlich darunter ist ein Fehler.
CO2_MINIMUM = 350


class DatenFehler(Exception):
    """Wird geworfen, wenn die CSV-Datei fehlt, leer oder falsch aufgebaut ist."""


def lade_rohdaten(pfad=CSV_STANDARD):
    """Liest die CSV-Datei ein und prüft, ob sie brauchbar ist."""
    pfad = Path(pfad)
    if not pfad.exists():
        raise DatenFehler(f"Datei nicht gefunden: {pfad.name}")
    try:
        df = pd.read_csv(pfad)
    except pd.errors.EmptyDataError:
        raise DatenFehler(f"Die Datei {pfad.name} ist leer.")
    except (pd.errors.ParserError, UnicodeDecodeError) as fehler:
        raise DatenFehler(f"Die Datei {pfad.name} ist keine gültige CSV-Datei ({fehler}).")

    fehlend = [s for s in PFLICHTSPALTEN if s not in df.columns]
    if fehlend:
        raise DatenFehler("Es fehlen Spalten: " + ", ".join(fehlend))
    if df.empty:
        raise DatenFehler(f"Die Datei {pfad.name} enthält keine Messwerte.")

    # Wir rechnen in Ortszeit, weil Tagesabläufe (Lüften, Schlafen) an der Uhr hängen.
    df["zeit"] = pd.to_datetime(df["Zeit (Europe/Vienna)"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    ungueltig = df["zeit"].isna().sum()
    df = df.dropna(subset=["zeit"]).sort_values("zeit")
    if df.empty:
        raise DatenFehler("Keine Zeile hat einen gültigen Zeitstempel.")
    df.attrs["ungueltige_zeiten"] = int(ungueltig)

    # Alle Messspalten in Zahlen umwandeln; kaputte Einträge werden zu „fehlt“ (NaN).
    for spalte in df.columns:
        if spalte not in ("Zeit (UTC)", "Zeit (Europe/Vienna)", "zeit"):
            df[spalte] = pd.to_numeric(df[spalte], errors="coerce")
    return df


def kurzname(spalte):
    """Macht aus 'Kueche (Luft) – CO₂ (ppm)' einen kurzen Schlüssel wie 'co2_Kueche'."""
    geraet, groesse = spalte.split(" – ", 1)
    geraet = geraet.replace(" (Luft)", "")
    kuerzel = {
        "Radon": "radon", "Betriebszeit": "betrieb", "Luftdruck innen": "druck",
        "Temperatur innen": "temp", "CO₂": "co2", "rel. Luftfeuchte": "feuchte",
        "Temperatur 2 m": "temp", "Luftdruck": "druck", "Wind 10 m": "wind",
        "Bodentemperatur 0 cm": "boden0", "Bodentemperatur 6 cm": "boden6",
        "Bodentemperatur 54 cm": "boden54",
    }
    name = groesse.rsplit(" (", 1)[0]
    return f"{kuerzel.get(name, name)}_{geraet}"


def bereinige(df):
    """Erstellt pro Messgröße eine saubere Zeitreihe und zählt, was entfernt wurde.

    Rückgabe: (serien, bericht). serien ist ein dict {kurzname: pd.Series},
    bericht zählt die entfernten Werte je Grund.
    """
    serien, bericht = {}, {"anlauf": {}, "co2_fehler": 0, "doppelt": 0}
    for spalte in df.columns:
        if " – " not in spalte or "Betriebszeit" in spalte:
            continue
        name = kurzname(spalte)
        teil = df.loc[df[spalte].notna(), ["zeit", spalte]]
        if spalte.endswith("Radon (Bq/m³)"):
            raum = spalte.split(" – ")[0]
            betrieb = df.loc[teil.index].get(f"{raum} – Betriebszeit (min)")
            if betrieb is not None:
                # Schlafzimmer-Gerät hat keine Betriebszeit (NaN) → bleibt drin.
                anlauf = betrieb < ANLAUFZEIT_MIN
                bericht["anlauf"][raum] = int(anlauf.sum())
                teil = teil[~anlauf]
        if name.startswith("co2_"):
            zu_tief = teil[spalte] < CO2_MINIMUM
            bericht["co2_fehler"] += int(zu_tief.sum())
            teil = teil[~zu_tief]
        s = teil.set_index("zeit")[spalte].rename(name)
        # Manche Meldungen kommen doppelt (gleicher Zeitpunkt) → nur die erste behalten.
        doppelt = s.index.duplicated()
        bericht["doppelt"] += int(doppelt.sum())
        serien[name] = s[~doppelt]
    return serien, bericht


def raster(serien, takt="1h"):
    """Mittelt alle Zeitreihen auf ein gemeinsames Zeitraster (z. B. '10min' oder '1h')."""
    return pd.DataFrame({name: s.resample(takt).mean() for name, s in serien.items()})


def neustarts(df):
    """Findet Sensor-Neustarts: Die Betriebszeit springt deutlich nach unten.

    Kleine Rücksprünge (< 100 min) sind nur nachgeschickte alte Meldungen, keine Neustarts.
    """
    zeilen = []
    for raum in RAEUME:
        spalte = f"{raum} – Betriebszeit (min)"
        if spalte not in df.columns:
            continue
        b = df.loc[df[spalte].notna(), ["zeit", spalte]].reset_index(drop=True)
        sprung = b[spalte].diff() < -100
        for i in b.index[sprung]:
            zeilen.append({"raum": raum, "zeit": b.at[i, "zeit"],
                           "lief_tage": round(b.at[i - 1, spalte] / 1440, 1)})
    return pd.DataFrame(zeilen, columns=["raum", "zeit", "lief_tage"])


def luecken(serien, mindestens="3h"):
    """Listet alle Messlücken, die länger als `mindestens` sind."""
    zeilen = []
    for name, s in serien.items():
        abstand = s.index.to_series().diff()
        for ende, dauer in abstand[abstand > pd.Timedelta(mindestens)].items():
            zeilen.append({"reihe": name, "von": ende - dauer, "bis": ende,
                           "stunden": round(dauer.total_seconds() / 3600, 1)})
    return pd.DataFrame(zeilen, columns=["reihe", "von", "bis", "stunden"])
