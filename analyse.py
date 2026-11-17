"""Auswertung der Radon-Daten: Zeiträume erkennen, Kennzahlen, Ursachen, Auffälligkeiten.

Aufruf:  python3 analyse.py            (nimmt radon_sample_data.csv im selben Ordner)
         python3 analyse.py andere.csv
Ergebnis: ergebnisse/ergebnisse.json  (wird von diagramme.py und webseite.py gelesen)
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

import daten

ERGEBNIS_ORDNER = daten.ORDNER / "ergebnisse"

# Physikalische Konstanten
HALBWERTSZEIT_RN_H = 3.8235 * 24                 # Radon-222, in Stunden
ZERFALL_RN = np.log(2) / HALBWERTSZEIT_RN_H      # Zerfallskonstante λ in 1/h
WHO_WERT, AT_REFERENZ = 100, 300                 # Bq/m³

# Schwellen für die automatische Erkennung (siehe DOKUMENTATION.md, Abschnitt Methoden)
CO2_ANSTIEG_ANWESEND = 15     # ppm pro 10 min: so schnell steigt CO₂ nur, wenn jemand da ist
CO2_NACHT_FENSTER_ZU = 50     # ppm: steigt CO₂ im Schlafzimmer nachts weniger, war das Fenster offen
KELLER_HOCH = 100             # Bq/m³ Tagesmittel


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def mittel(H, raeume):
    """Mittelwert mehrerer Radon-Räume pro Zeitschritt (fehlende Räume werden übersprungen)."""
    return H[[f"radon_{r}" for r in raeume]].mean(axis=1)


def runde(x, stellen=1):
    """Rundet für die JSON-Ausgabe und macht aus NaN ein None (JSON kennt kein NaN)."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return round(float(x), stellen)


def zeit_text(t):
    return pd.Timestamp(t).strftime("%Y-%m-%d %H:%M")


def laengster_lauf(maske):
    """Gibt (start, ende) des längsten zusammenhängenden True-Abschnitts einer bool-Serie zurück."""
    gruppe = (maske != maske.shift()).cumsum()
    laeufe = maske[maske].groupby(gruppe[maske])
    if laeufe.ngroups == 0:
        return None
    laengster = max(laeufe, key=lambda g: g[1].index[-1] - g[1].index[0])[1]
    return laengster.index[0], laengster.index[-1]


# ---------------------------------------------------------------------------
# 1. Zeiträume automatisch erkennen
# ---------------------------------------------------------------------------

def finde_urlaub(T):
    """Urlaub = längste Zeit, in der das CO₂ in Küche UND Schlafzimmer nie schnell ansteigt.

    Menschen atmen CO₂ aus. Ist niemand zu Hause, fällt das CO₂ nur noch langsam ab.
    """
    co2 = T[["co2_Kueche", "co2_Schlafzimmer"]].dropna(how="all")
    anstieg = (co2.diff() > CO2_ANSTIEG_ANWESEND).any(axis=1)
    lauf = laengster_lauf(~anstieg)
    if lauf is None or lauf[1] - lauf[0] < pd.Timedelta("24h"):
        return None
    return {"von": zeit_text(lauf[0]), "bis": zeit_text(lauf[1]),
            "tage": runde((lauf[1] - lauf[0]).total_seconds() / 86400, 1)}


def nacht_werte(H):
    """Kennwerte pro Nacht (22–6 Uhr): CO₂-Anstieg im Schlafzimmer, Radon, Außentemperatur."""
    wohn = mittel(H, daten.WOHNRAEUME)
    zeilen = []
    for tag in pd.date_range(H.index[0].normalize(), H.index[-1].normalize()):
        a, b = tag + pd.Timedelta("22h"), tag + pd.Timedelta("30h")
        nacht = H.loc[a:b]
        if len(nacht) < 7 or nacht["co2_Schlafzimmer"].isna().all():
            continue
        co2 = nacht["co2_Schlafzimmer"].dropna()
        w = wohn.loc[a:b].dropna()
        zeilen.append({
            "nacht": tag,
            "co2_anstieg": co2.max() - co2.iloc[0],
            "radon_wohn": w.mean(),
            "radon_anstieg": (w.iloc[-1] - w.iloc[0]) if len(w) > 1 else np.nan,
            "radon_schlaf": nacht["radon_Schlafzimmer"].mean(),
            "radon_keller": mittel(nacht, daten.KELLER).mean(),
            "aussen": nacht["temp_Wetter"].mean(),
        })
    return pd.DataFrame(zeilen).set_index("nacht")


def finde_fenster_offen(naechte, urlaub):
    """„Fenster immer offen“ = längste Zeit, in der in mind. 2 von 3 Nächten (über 14 Nächte
    betrachtet) das CO₂ im Schlafzimmer nicht ansteigt. Einzelne kühle Nächte mit
    geschlossenem Fenster unterbrechen den Zeitraum so nicht."""
    offen = (naechte["co2_anstieg"] < CO2_NACHT_FENSTER_ZU).astype(float)
    if urlaub:  # Im Urlaub steigt CO₂ auch ohne offenes Fenster nicht → diese Nächte überspringen
        offen = offen.drop(offen.loc[urlaub["von"][:10]:urlaub["bis"][:10]].index)
    anteil = offen.rolling(14, center=True, min_periods=7).mean()
    lauf = laengster_lauf(anteil >= 2 / 3)
    if lauf is None:
        return None
    return {"von": lauf[0].strftime("%Y-%m-%d"), "bis": lauf[1].strftime("%Y-%m-%d"),
            "anteil_offene_naechte": runde(offen[lauf[0]:lauf[1]].mean() * 100, 0)}


def finde_lueftungsanlage(H):
    """KWL-Start = erster Tag, ab dem der Keller bis zum Datenende nie mehr über 100 Bq/m³ liegt.

    Vorher war der Keller ein eigener, kaum gelüfteter Luftraum mit oft über 200 Bq/m³.
    """
    keller = mittel(H, daten.KELLER).resample("1D").mean().dropna()
    hoch = keller[keller > KELLER_HOCH]
    if hoch.empty or hoch.index[-1] == keller.index[-1]:
        return None
    start = keller.index[keller.index > hoch.index[-1]][0]
    return {"ab": start.strftime("%Y-%m-%d")}


def phasen(T, H):
    """Erkennt alle Zeiträume und teilt die Messzeit in benannte Phasen ein."""
    urlaub = finde_urlaub(T)
    naechte = nacht_werte(H)
    fenster = finde_fenster_offen(naechte, urlaub)
    kwl = finde_lueftungsanlage(H)
    return {"urlaub": urlaub, "fenster_offen": fenster, "kwl": kwl}, naechte


def phase_von(zeitpunkte, z):
    """Ordnet jedem Zeitpunkt eine Phase zu (für Vergleiche)."""
    p = pd.Series("Frühling: morgens lüften", index=zeitpunkte)
    if z["fenster_offen"]:
        p[z["fenster_offen"]["von"]:z["fenster_offen"]["bis"]] = "Sommer: Fenster offen"
    if z["kwl"]:
        p[z["kwl"]["ab"]:] = "Lüftungsanlage"
    if z["urlaub"]:
        p[z["urlaub"]["von"]:z["urlaub"]["bis"]] = "Urlaub: alles zu"
    return p


PHASEN_REIHENFOLGE = ["Frühling: morgens lüften", "Sommer: Fenster offen",
                      "Urlaub: alles zu", "Lüftungsanlage"]


# ---------------------------------------------------------------------------
# 2. Kennzahlen
# ---------------------------------------------------------------------------

def kennzahlen(H, z):
    """Mittelwert, Median, Maximum und Anteil über 100/300 Bq/m³ je Raum und Phase."""
    ph = phase_von(H.index, z)
    ergebnis = {}
    for raum in daten.RAEUME:
        s = H[f"radon_{raum}"]
        def werte(x):
            x = x.dropna()
            if x.empty:
                return None
            return {"mittel": runde(x.mean()), "median": runde(x.median()), "max": runde(x.max(), 0),
                    "ueber_100_proz": runde((x > WHO_WERT).mean() * 100),
                    "ueber_300_proz": runde((x > AT_REFERENZ).mean() * 100), "stunden": int(len(x))}
        ergebnis[raum] = {"gesamt": werte(s), **{p: werte(s[ph == p]) for p in PHASEN_REIHENFOLGE}}
    return ergebnis


def tagesgang(H, z):
    """Durchschnittlicher Verlauf über den Tag (0–23 Uhr) je Phase."""
    ph = phase_von(H.index, z)
    reihen = {"Wohnräume": mittel(H, daten.WOHNRAEUME), "Keller": mittel(H, daten.KELLER),
              "Schlafzimmer": H["radon_Schlafzimmer"], "CO₂ Schlafzimmer": H["co2_Schlafzimmer"]}
    ergebnis = {}
    for p in PHASEN_REIHENFOLGE:
        ergebnis[p] = {n: [runde(v) for v in s[ph == p].groupby(s[ph == p].index.hour).mean().reindex(range(24))]
                       for n, s in reihen.items()}
    return ergebnis


def monatswerte(H):
    """Monatsmittel je Raum."""
    m = H[[f"radon_{r}" for r in daten.RAEUME]].resample("MS").mean()
    return {r: {d.strftime("%Y-%m"): runde(v) for d, v in m[f"radon_{r}"].items()} for r in daten.RAEUME}


def korrelationen(H, z):
    """Wie ähnlich verlaufen die Räume? Ohne Urlaub (da steigt alles gleichzeitig)."""
    X = H[[f"radon_{r}" for r in daten.RAEUME]].copy()
    X.columns = daten.RAEUME
    if z["urlaub"]:
        X = X.drop(X.loc[z["urlaub"]["von"]:z["urlaub"]["bis"]].index)
    matrix = X.corr().round(2)
    ergebnis = {"matrix": {r: matrix[r].to_dict() for r in daten.RAEUME}}
    if z["kwl"]:
        wohn, keller = X[daten.WOHNRAEUME].mean(axis=1), X[daten.KELLER].mean(axis=1)
        vor, nach = slice(None, z["kwl"]["ab"]), slice(z["kwl"]["ab"], None)
        ergebnis["keller_wohn_vor_kwl"] = runde(wohn[vor].corr(keller[vor]), 2)
        ergebnis["keller_wohn_nach_kwl"] = runde(wohn[nach].corr(keller[nach]), 2)
    return ergebnis


# ---------------------------------------------------------------------------
# 3. Urlaub als Experiment: Wie dicht ist das Haus, wie viel Radon strömt nach?
# ---------------------------------------------------------------------------

def urlaub_physik(T, urlaub):
    """Passt physikalische Kurven an die Urlaubsdaten an.

    CO₂:   C(t) = C_außen + (C0 − C_außen) · e^(−n·t)         → Luftwechsel n
    Radon: C(t) = C_gl + (C0 − C_gl) · e^(−(n+λ)·t)           → Gleichgewicht C_gl, Luftwechsel n
    Nachströmen pro Stunde = C_gl · (n + λ)   (im Gleichgewicht gleicht Zustrom den Verlust aus)
    """
    if not urlaub:
        return None
    # 2 h Abstand zur Abreise, damit die letzten Aktivitäten im Haus die Kurve nicht stören
    t0 = pd.Timestamp(urlaub["von"]) + pd.Timedelta("2h")
    t1 = pd.Timestamp(urlaub["bis"])
    ergebnis = {"co2": {}, "radon": {}}

    def co2_kurve(t, c0, c_aussen, n):
        return c_aussen + (c0 - c_aussen) * np.exp(-n * t)

    def radon_kurve(t, c0, c_gl, k):
        return c_gl + (c0 - c_gl) * np.exp(-k * t)

    for raum in ["Kueche", "Schlafzimmer"]:
        s = T[f"co2_{raum}"][t0:t1].dropna()
        t = np.asarray((s.index - t0).total_seconds() / 3600)
        try:
            p, _ = curve_fit(co2_kurve, t, s.values, p0=[700, 400, 0.02], maxfev=20000)
        except RuntimeError:
            continue
        ergebnis["co2"][raum] = {"luftwechsel_pro_h": runde(p[2], 3), "zeitkonstante_h": runde(1 / p[2], 0)}

    for raum in daten.RAEUME:
        s = T[f"radon_{raum}"][t0:t1].dropna().rolling(6, center=True, min_periods=3).mean()
        t = np.asarray((s.index - t0).total_seconds() / 3600)
        try:
            p, _ = curve_fit(radon_kurve, t, s.values, p0=[50, 330, 0.02], maxfev=20000)
        except RuntimeError:
            continue
        ergebnis["radon"][raum] = {
            "start": runde(s.iloc[0], 0), "ende": runde(s.iloc[-1], 0),
            "gleichgewicht": runde(p[1], 0),
            "luftwechsel_pro_h": runde(p[2] - ZERFALL_RN, 3),
            "zustrom_bq_m3_h": runde(p[1] * p[2], 1),
        }
    return ergebnis


# Zeitfenster des auffälligen Tages (Hinweis des Hausbesitzers: Dunstabzug)
DUNSTABZUG_VON, DUNSTABZUG_BIS = "2026-07-20 09:00", "2026-07-20 23:00"


def dunstabzug_tag(H, physik):
    """Rechnet den 20.07. so nach wie den Urlaub und vergleicht den Radon-Zustrom.

    Idee: Ohne Kamineffekt (draußen etwa so warm wie drinnen) dürfte kaum Radon
    nachströmen. Strömt trotzdem mehr nach als im Urlaub, muss ein anderer Sog
    wirken, z. B. ein Dunstabzug, der Luft aus dem dichten Haus hinausbläst.

    Luftwechsel n aus dem CO₂-Abfall (log-linear), Zustrom = Anstieg + n · C.
    """
    w = H[DUNSTABZUG_VON:DUNSTABZUG_BIS]
    if len(w) < 10 or "co2_Kueche" not in w or w["co2_Kueche"].isna().all():
        return None
    t = np.arange(len(w))
    wohn = mittel(w, daten.WOHNRAEUME)
    co2 = (w["co2_Kueche"] - 420).clip(lower=1)
    gut = co2.notna() & wohn.notna()
    n = -np.polyfit(t[gut], np.log(co2[gut]), 1)[0]
    anstieg = np.polyfit(t[gut], wohn[gut], 1)[0]
    zustrom = anstieg + n * wohn.mean()
    urlaub = None
    if physik and physik["radon"]:
        urlaub = np.mean([physik["radon"][r]["zustrom_bq_m3_h"] for r in ["Kueche", "Wohnzimmer"] if r in physik["radon"]])
    return {
        "von": DUNSTABZUG_VON, "bis": DUNSTABZUG_BIS,
        "wohn_start": runde(wohn.iloc[:2].mean(), 0), "wohn_max": runde(wohn.max(), 0),
        "sockel_max": runde(w["radon_Kueche - Sockel"].max(), 0),
        "luftwechsel_pro_h": runde(n, 3), "anstieg_bq_m3_h": runde(anstieg, 1),
        "zustrom_bq_m3_h": runde(zustrom, 1),
        "zustrom_urlaub": runde(urlaub, 1) if urlaub is not None else None,
        "temp_innen": runde(w["temp_Kueche"].mean(), 1),
        "temp_aussen_max": runde(w["temp_Wetter"].max(), 1),
        "temp_aussen_mittel": runde(w["temp_Wetter"].mean(), 1),
    }


# ---------------------------------------------------------------------------
# 4. Lüften: einzelne Lüftungsereignisse finden
# ---------------------------------------------------------------------------

def lueftungsereignisse(T):
    """Findet plötzliche Radon-Abfälle in Küche/Wohnzimmer (≥ 40 % in 90 min, von ≥ 50 Bq/m³).

    So schnell kann Radon nur fallen, wenn frische Außenluft hereinkommt, also beim Lüften.
    """
    wohn = T[["radon_Kueche", "radon_Wohnzimmer"]].mean(axis=1).rolling(3, center=True, min_periods=2).mean()
    vorher = wohn.rolling(4).max().shift(1)
    nachher = wohn.rolling(9).min().shift(-8)
    treffer = wohn.index[(vorher >= 50) & (nachher <= 0.6 * vorher)]
    ereignisse, letzter = [], None
    for t in treffer:
        if letzter is None or t - letzter > pd.Timedelta("6h"):
            ereignisse.append({"zeit": zeit_text(t), "von": runde(vorher[t], 0), "auf": runde(nachher[t], 0)})
        letzter = t
    return ereignisse


def lueften_wirkung(T, ereignisse):
    """Wie schnell kommt das Radon nach dem Morgenlüften (5–9 Uhr) zurück?"""
    wohn = T[["radon_Kueche", "radon_Wohnzimmer"]].mean(axis=1)
    kurven = []
    for e in ereignisse:
        t = pd.Timestamp(e["zeit"])
        if not 5 <= t.hour <= 9:
            continue
        stueck = wohn[t - pd.Timedelta("3h"):t + pd.Timedelta("12h")]
        if len(stueck) < 80:
            continue
        rel = (stueck.index - t).total_seconds() / 3600
        kurven.append(pd.Series(stueck.values / e["von"] * 100, index=np.round(rel * 6) / 6))
    if not kurven:
        return None
    mittelkurve = pd.concat(kurven, axis=1).mean(axis=1).groupby(level=0).mean()
    # Nach dem Lüften bleibt es tagsüber niedrig; erst nachts baut sich das Radon wieder auf.
    return {"anzahl": len(kurven),
            "kurve_stunden": [runde(x, 2) for x in mittelkurve.index],
            "kurve_prozent": [runde(v) for v in mittelkurve.values],
            "nach_2h_prozent": runde(mittelkurve.loc[2.0], 0),
            "nach_12h_prozent": runde(mittelkurve.loc[12.0], 0)}


# ---------------------------------------------------------------------------
# 5. Ursachen: Wetter und Kamineffekt
# ---------------------------------------------------------------------------

def wetter_einfluss(H, z):
    """Radon in Abhängigkeit von Temperaturdifferenz innen−außen, Wind und Luftdruckänderung."""
    d = pd.DataFrame({
        "wohn": mittel(H, daten.WOHNRAEUME), "keller": mittel(H, daten.KELLER),
        "dT": H["temp_Kueche"] - H["temp_Wetter"],
        "wind": H["wind_Wetter"],
        "dp12": H["druck_Wetter"] - H["druck_Wetter"].shift(12),
    })
    if z["urlaub"]:
        d = d.drop(d.loc[z["urlaub"]["von"]:z["urlaub"]["bis"]].index)
    teile = {"vor Lüftungsanlage": d, "mit Lüftungsanlage": d.iloc[0:0]}
    if z["kwl"]:
        teile = {"vor Lüftungsanlage": d[:z["kwl"]["ab"]], "mit Lüftungsanlage": d[z["kwl"]["ab"]:]}
    klassen = {"dT": [-15, -5, 0, 5, 10, 15, 25], "wind": [0, 3, 6, 10, 15, 60], "dp12": [-12, -3, -1, 1, 3, 12]}
    ergebnis = {}
    for name, teil in teile.items():
        ergebnis[name] = {}
        for gross, grenzen in klassen.items():
            g = teil.groupby(pd.cut(teil[gross], grenzen), observed=False)
            ergebnis[name][gross] = {
                "klassen": [f"{a} bis {b}" for a, b in zip(grenzen[:-1], grenzen[1:])],
                "wohn": [runde(v) for v in g["wohn"].mean()], "keller": [runde(v) for v in g["keller"].mean()],
                "stunden": [int(v) for v in g.size()],
            }
        # Mehrfache lineare Regression: Wie stark wirkt jede Größe, wenn die anderen gleich bleiben?
        # (Nötig, weil z. B. windige Tage oft auch kalte Tage sind.)
        r = teil.dropna(subset=["wohn", "dT", "wind", "dp12"])
        if len(r) > 100:
            X = np.column_stack([np.ones(len(r)), r["dT"], r["wind"], r["dp12"]])
            k = np.linalg.lstsq(X, r["wohn"].to_numpy(), rcond=None)[0]
            ergebnis[name]["regression"] = {"pro_grad_dT": runde(k[1], 2), "pro_10kmh_wind": runde(k[2] * 10, 1),
                                            "pro_hpa_druck": runde(k[3], 2), "stunden": int(len(r))}
        ergebnis[name]["korrelation"] = {
            gross: {"wohn": runde(teil["wohn"].corr(teil[gross]), 2), "keller": runde(teil["keller"].corr(teil[gross]), 2)}
            for gross in klassen}
    return ergebnis


def fairer_vergleich(naechte, z):
    """Vorher/Nachher nur für Nächte mit GESCHLOSSENEM Fenster und ähnlicher Außentemperatur."""
    if not z["kwl"]:
        return None
    n = naechte[naechte["co2_anstieg"] >= 100].copy()      # Fenster sicher zu
    if z["urlaub"]:
        n = n.drop(n.loc[z["urlaub"]["von"][:10]:z["urlaub"]["bis"][:10]].index, errors="ignore")
    n["gruppe"] = np.where(n.index >= z["kwl"]["ab"], "mit Anlage", "ohne Anlage")
    n = n.dropna(subset=["radon_wohn", "aussen"])
    grenzen = [0, 8, 12, 16, 25]
    n["temp"] = pd.cut(n["aussen"], grenzen)
    zeilen = []
    for (temp, gruppe), g in n.groupby(["temp", "gruppe"], observed=True):
        zeilen.append({"aussen": f"{temp.left:.0f}–{temp.right:.0f} °C", "gruppe": gruppe, "naechte": len(g),
                       "radon_wohn": runde(g["radon_wohn"].mean()), "anstieg_nacht": runde(g["radon_anstieg"].mean()),
                       "radon_schlaf": runde(g["radon_schlaf"].mean())})
    ohne, mit = n[n.gruppe == "ohne Anlage"], n[n.gruppe == "mit Anlage"]
    # Gesamteffekt: Temperaturklassen gleich gewichten, damit kalte Nächte nicht überwiegen
    paare = [(a, b) for a in zeilen for b in zeilen if a["aussen"] == b["aussen"]
             and a["gruppe"] == "ohne Anlage" and b["gruppe"] == "mit Anlage"]
    senkung = np.mean([1 - b["radon_wohn"] / a["radon_wohn"] for a, b in paare]) * 100 if paare else None
    return {"tabelle": zeilen, "naechte_ohne": len(ohne), "naechte_mit": len(mit), "senkung_proz": runde(senkung, 0)}


def kamin_druck_pa(hoehe_m, innen_c, aussen_c, luftdruck_hpa=970):
    """Unterdruck durch den Kamineffekt in Pascal.

    Kalte Außenluft ist schwerer als warme Innenluft. Über die Höhe h ergibt das den
    Druckunterschied Δp = g · h · (ρ_außen − ρ_innen), mit ρ = p / (R · T).
    """
    r_luft, g = 287.05, 9.81
    rho_aussen = 100 * luftdruck_hpa / (r_luft * (273.15 + aussen_c))
    rho_innen = 100 * luftdruck_hpa / (r_luft * (273.15 + innen_c))
    return g * hoehe_m * (rho_aussen - rho_innen)


# Annahmen für den Winter (keine Messdaten): Jänner-Mittel im Innviertel ≈ 0 °C, innen 21 °C
WINTER_AUSSEN_C, WINTER_INNEN_C = 0, 21
# Empfohlener Luftwechsel in Wohnungen (Richtwert, Anteil der Luft pro Stunde)
LUFTWECHSEL_EMPFOHLEN = (0.3, 0.5)


def fazit_zahlen(H, z, physik, wetter, stockwerk):
    """Kennzahlen für das Fazit: Winter gegen Sommer, Druck durch den Kamineffekt, Dichtheit."""
    ph = phase_von(H.index, z)
    wohn = mittel(H, daten.WOHNRAEUME)
    # „Heizzeit“ = Messbeginn bis vor dem ungeklärten Abfall am 31.03. (draußen 0–5 °C)
    heiz = H[:"2026-03-30 23:59"]
    sommer = ph == "Sommer: Fenster offen"
    ergebnis = {
        "heizzeit": {"wohn": runde(wohn[:"2026-03-30 23:59"].mean(), 0), "aussen": runde(heiz["temp_Wetter"].mean(), 1)},
        "sommer": {"wohn": runde(wohn[sommer].mean(), 0), "aussen": runde(H["temp_Wetter"][sommer].mean(), 1),
                   "innen": runde(H["temp_Kueche"][sommer].mean(), 1)},
    }
    ergebnis["faktor_gemessen"] = runde(ergebnis["heizzeit"]["wohn"] / ergebnis["sommer"]["wohn"], 1)
    # Mit Anlage: kalte Stunden (15–25 °C Unterschied) gegen warme (0–5 °C), aus dem Kamineffekt-Vergleich
    if wetter.get("mit Lüftungsanlage"):
        d = wetter["mit Lüftungsanlage"]["dT"]
        kalt, warm = d["wohn"][d["klassen"].index("15 bis 25")], d["wohn"][d["klassen"].index("0 bis 5")]
        ergebnis["anlage"] = {"kalt": kalt, "warm": warm, "faktor": runde(kalt / warm, 1)}
    # Druck: Höhe = gemessener Abstand Küche ↔ Schlafzimmer (aus dem Luftdruck)
    h = stockwerk["hoehe_m"] if stockwerk else 5.0
    s = ergebnis["sommer"]
    ergebnis["druck"] = {
        "hoehe_m": h,
        "sommer_pa": runde(kamin_druck_pa(h, s["innen"], s["aussen"]), 1),
        "heizzeit_pa": runde(kamin_druck_pa(h, WINTER_INNEN_C, ergebnis["heizzeit"]["aussen"]), 1),
        "winter_pa": runde(kamin_druck_pa(h, WINTER_INNEN_C, WINTER_AUSSEN_C), 1),
        "sensor_streuung_pa": runde(stockwerk["streuung_hpa"] * 100, 1) if stockwerk else None,
    }
    if physik and physik["co2"]:
        n = [v["luftwechsel_pro_h"] for v in physik["co2"].values()]
        ergebnis["dichtheit"] = {"luftwechsel_min": min(n), "luftwechsel_max": max(n),
                                 "empfohlen": LUFTWECHSEL_EMPFOHLEN,
                                 "faktor_zu_wenig": [runde(LUFTWECHSEL_EMPFOHLEN[0] / max(n), 0), runde(LUFTWECHSEL_EMPFOHLEN[1] / min(n), 0)]}
    return ergebnis


def stockwerk_aus_druck(H):
    """Höhenunterschied Küche ↔ Schlafzimmer aus dem Luftdruck (Luft wird nach oben dünner)."""
    dp = (H["druck_Kueche"] - H["druck_Schlafzimmer"]).dropna()
    if dp.empty:
        return None
    dichte = 100 * H["druck_Kueche"].mean() / (287.05 * (273.15 + H["temp_Kueche"].mean()))  # kg/m³
    return {"druckdifferenz_hpa": runde(dp.mean(), 2), "streuung_hpa": runde(dp.std(), 3),
            "hoehe_m": runde(dp.mean() * 100 / (dichte * 9.81), 1)}


# ---------------------------------------------------------------------------
# 6. Datenqualität
# ---------------------------------------------------------------------------

def datenqualitaet(df, serien, bericht):
    """Fasst Neustarts, Lücken und entfernte Werte zusammen."""
    ns = daten.neustarts(df)
    # Neustarts, die bei fast allen Sensoren gleichzeitig passieren → Stromausfall / Router
    gemeinsam = []
    if not ns.empty:
        ns = ns.sort_values("zeit")
        gruppe = (ns["zeit"].diff() > pd.Timedelta("30min")).cumsum()
        for _, g in ns.groupby(gruppe):
            if g["raum"].nunique() >= 4:
                gemeinsam.append({"zeit": zeit_text(g["zeit"].min()), "sensoren": int(g["raum"].nunique())})
    lu = daten.luecken(serien, "3h")
    beginn = {name: zeit_text(s.index.min()) for name, s in serien.items()}
    return {
        "zeilen": int(len(df)), "von": zeit_text(df["zeit"].min()), "bis": zeit_text(df["zeit"].max()),
        "neustarts_je_raum": ns.groupby("raum").size().to_dict() if not ns.empty else {},
        "gemeinsame_neustarts": gemeinsam,
        "anlaufwerte_entfernt": bericht["anlauf"], "co2_fehlwerte": bericht["co2_fehler"],
        "doppelte_meldungen": bericht["doppelt"], "ungueltige_zeiten": df.attrs.get("ungueltige_zeiten", 0),
        "luecken": [{"reihe": r.reihe, "von": zeit_text(r.von), "bis": zeit_text(r.bis), "stunden": r.stunden}
                    for r in lu.sort_values("stunden", ascending=False).itertuples()][:15],
        "messbeginn": beginn,
    }


# ---------------------------------------------------------------------------
# Hauptprogramm
# ---------------------------------------------------------------------------

def analysiere(pfad=daten.CSV_STANDARD):
    """Führt die komplette Auswertung aus und gibt alle Ergebnisse als dict zurück."""
    df = daten.lade_rohdaten(pfad)
    serien, bericht = daten.bereinige(df)
    fehlend = [n for n in ["co2_Kueche", "co2_Schlafzimmer", "temp_Kueche", "temp_Wetter"] if n not in serien]
    if fehlend:
        raise daten.DatenFehler("Für die Auswertung fehlen Messreihen: " + ", ".join(fehlend))
    T, H = daten.raster(serien, "10min"), daten.raster(serien, "1h")

    z, naechte = phasen(T, H)
    ereignisse = lueftungsereignisse(T)
    physik = urlaub_physik(T, z["urlaub"])
    wetter, stockwerk = wetter_einfluss(H, z), stockwerk_aus_druck(H)
    return {
        "zeitraeume": z,
        "datenqualitaet": datenqualitaet(df, serien, bericht),
        "kennzahlen": kennzahlen(H, z),
        "monatswerte": monatswerte(H),
        "tagesgang": tagesgang(H, z),
        "korrelationen": korrelationen(H, z),
        "urlaub_physik": physik,
        "dunstabzug": dunstabzug_tag(H, physik),
        "lueftungsereignisse": ereignisse,
        "lueften_wirkung": lueften_wirkung(T, ereignisse),
        "wetter": wetter,
        "fairer_vergleich": fairer_vergleich(naechte, z),
        "stockwerk": stockwerk,
        "fazit": fazit_zahlen(H, z, physik, wetter, stockwerk),
    }


def main():
    pfad = Path(sys.argv[1]) if len(sys.argv) > 1 else daten.CSV_STANDARD
    try:
        ergebnis = analysiere(pfad)
    except daten.DatenFehler as fehler:
        print(f"Fehler: {fehler}")
        sys.exit(1)
    ERGEBNIS_ORDNER.mkdir(exist_ok=True)
    ziel = ERGEBNIS_ORDNER / "ergebnisse.json"
    ziel.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    z = ergebnis["zeitraeume"]
    print("Gefundene Zeiträume:")
    for name, wert in z.items():
        print(f"  {name:14s} {wert}")
    print(f"Ergebnisse gespeichert: {ziel.relative_to(daten.ORDNER)}")


if __name__ == "__main__":
    main()
