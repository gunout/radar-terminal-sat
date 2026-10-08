#!/usr/bin/env python3
# dashboard_live.py - Dashboard temps réel avec recalcul SGP4

import json
import math
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from sgp4.api import Satrec, jday
from sgp4 import omm

BASE = Path(__file__).parent
CELESTRAK = BASE / "all_active.json"

MU = 398600.4418
R_EARTH = 6371.0
INTERVALLE = 10
W = 68


# =========================================================
# Utilitaires
# =========================================================
def strip_ansi(s):
    return re.sub(r'\033\[[0-9;]*m', '', s)


def vlen(s):
    return len(strip_ansi(s))


def pad(s, largeur, align="left"):
    manque = max(0, largeur - vlen(s))
    if align == "left":
        return s + " " * manque
    if align == "right":
        return " " * manque + s
    g = manque // 2
    return " " * g + s + " " * (manque - g)


def ligne(contenu=""):
    """Ligne ║ ... ║ avec contenu paddé à W."""
    return "║" + pad(contenu, W) + "║"


# =========================================================
# Chargement
# =========================================================
print("Chargement du catalogue...")
with open(CELESTRAK) as f:
    catalogue = json.load(f)

print(f"Pré-calcul de {len(catalogue)} orbites...")
satrecs = {}
for sat in catalogue:
    try:
        satrec = Satrec()
        omm.initialize(satrec, sat)
        satrecs[sat["NORAD_CAT_ID"]] = {
            "satrec": satrec,
            "nom": sat["OBJECT_NAME"],
            "norad": sat["NORAD_CAT_ID"],
        }
    except Exception:
        continue
print(f"{len(satrecs)} orbites prêtes")
time.sleep(1)


# =========================================================
# Calcul des positions
# =========================================================
def eci_vers_geo(r, jd, fr):
    x, y, z = r
    gmst = (280.46061837 + 360.98564736629 * (jd + fr - 2451545.0)) % 360
    g = math.radians(gmst)
    xr = x * math.cos(g) + y * math.sin(g)
    yr = -x * math.sin(g) + y * math.cos(g)
    lon = math.degrees(math.atan2(yr, xr))
    lat = math.degrees(math.atan2(z, math.sqrt(xr**2 + yr**2)))
    alt = math.sqrt(xr**2 + yr**2 + z**2) - R_EARTH
    return lat, lon, alt


def calculer_positions():
    now = datetime.now(timezone.utc)
    jd, fr = jday(now.year, now.month, now.day,
                  now.hour, now.minute, now.second)
    
    positions = []
    for norad, info in satrecs.items():
        try:
            e, r, v = info["satrec"].sgp4(jd, fr)
            if e != 0 or any(math.isnan(x) for x in r):
                continue
            lat, lon, alt = eci_vers_geo(r, jd, fr)
            if math.isnan(lat) or math.isnan(lon) or math.isnan(alt):
                continue
            positions.append({
                "norad": norad,
                "nom": info["nom"],
                "lat": lat,
                "lon": lon,
                "alt": alt,
                "vitesse": math.sqrt(sum(vv*vv for vv in v)),
            })
        except Exception:
            continue
    return positions


# =========================================================
# Statistiques
# =========================================================
def type_orbite(alt):
    if alt < 500:
        return "LEO bas"
    elif alt < 1000:
        return "LEO moyen"
    elif alt < 2000:
        return "LEO haut"
    elif alt < 10000:
        return "MEO bas"
    elif alt < 30000:
        return "MEO haut"
    else:
        return "GEO"


def top_operateurs(positions, n=10):
    ops = Counter()
    for p in positions:
        nom = p["nom"]
        op = nom.split()[0]
        op = re.sub(r'[-\d]+$', '', op).strip()
        if not op:
            op = nom.split()[0]
        ops[op] += 1
    return ops.most_common(n)


def barre(count, total, largeur, char="█"):
    if total == 0:
        return ""
    n = int(count / total * largeur)
    return char * n


# =========================================================
# Tableau — largeurs fixes
# =========================================================
# Somme des largeurs : 2 + 7 + 1 + 25 + 1 + 10 + 1 + 10 + 1 + 9 = 67
# Puis pad à W = 68 → 1 espace final automatique
W_ID  = 7
W_NOM = 25
W_LAT = 10
W_LON = 10
W_ALT = 9


def entete_tableau():
    contenu = (f"  {'ID':<{W_ID}} {'NOM':<{W_NOM}} "
               f"{'LAT':>{W_LAT}} {'LON':>{W_LON}} {'ALT km':>{W_ALT}}")
    return ligne(contenu)


def separateur_tableau():
    """Ligne ╠──┼──┼...╣ alignée sur les colonnes."""
    positions = []
    p = 2 + W_ID
    positions.append(p)
    p += 1 + W_NOM
    positions.append(p)
    p += 1 + W_LAT
    positions.append(p)
    p += 1 + W_LON
    positions.append(p)
    
    parts = []
    prev = 0
    for pos in positions:
        parts.append("─" * (pos - prev))
        parts.append("┼")
        prev = pos + 1
    parts.append("─" * max(0, W - prev))
    return "╠" + "".join(parts) + "╣"


def ligne_tableau(p):
    lat = f"{p['lat']:>+8.2f}"
    lon = f"{p['lon']:>+8.2f}"
    alt = f"{p['alt']:>7.0f}"
    nom = p["nom"][:W_NOM]
    contenu = (f"  {str(p['norad']):<{W_ID}} {nom:<{W_NOM}} "
               f"{lat:>{W_LAT}} {lon:>{W_LON}} {alt:>{W_ALT}}")
    return ligne(contenu)


# =========================================================
# Affichage
# =========================================================
def afficher(positions):
    os.system("clear")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    total = len(positions)
    
    par_type = {}
    for p in positions:
        t = type_orbite(p["alt"])
        par_type[t] = par_type.get(t, 0) + 1
    
    alt_min = min(p["alt"] for p in positions) if positions else 0
    alt_max = max(p["alt"] for p in positions) if positions else 0
    alt_moy = sum(p["alt"] for p in positions) / total if total else 0
    
    # Bandeau
    print("╔" + "═" * W + "╗")
    print(ligne(" DASHBOARD SATELLITES — TEMPS RÉEL".center(W)))
    print(ligne(" (positions recalculées SGP4)".center(W)))
    print("╠" + "═" * W + "╣")
    print(ligne(f" Mise à jour : {now}"))
    print(ligne(f" Total       : {total} satellites"))
    print(ligne(f" Intervalle  : {INTERVALLE}s"))
    print("╠" + "═" * W + "╣")
    
    # Répartition
    print(ligne(" RÉPARTITION PAR TYPE D'ORBITE"))
    print("╠" + "═" * W + "╣")
    for nom, count in sorted(par_type.items(), key=lambda x: -x[1]):
        b = barre(count, total, 40)
        print(ligne(f"   {nom:<12} {count:>5}  {b}"))
    print("╠" + "═" * W + "╣")
    
    # Stats
    print(ligne(" STATISTIQUES"))
    print("╠" + "═" * W + "╣")
    print(ligne(f"   Altitude min     : {alt_min:>10.0f} km"))
    print(ligne(f"   Altitude max     : {alt_max:>10.0f} km"))
    print(ligne(f"   Altitude moyenne : {alt_moy:>10.0f} km"))
    print("╠" + "═" * W + "╣")
    
    # Top opérateurs
    print(ligne(" TOP 10 OPÉRATEURS"))
    print("╠" + "═" * W + "╣")
    top = top_operateurs(positions, 10)
    max_count = top[0][1] if top else 1
    for op, count in top:
        b = barre(count, max_count, 30)
        print(ligne(f"   {op:<15} {count:>5}  {b}"))
    print("╠" + "═" * W + "╣")
    
    # Tableau
    print(ligne(" SATELLITES LES PLUS BAS (top 15 temps réel)"))
    print("╠" + "═" * W + "╣")
    print(entete_tableau())
    print(separateur_tableau())
    
    for p in sorted(positions, key=lambda x: x["alt"])[:15]:
        print(ligne_tableau(p))
    
    print("╚" + "═" * W + "╝")
    print(f"  Rafraîchissement dans {INTERVALLE}s... (Ctrl+C pour quitter)")


# =========================================================
# Boucle principale
# =========================================================
if __name__ == "__main__":
    try:
        while True:
            positions = calculer_positions()
            afficher(positions)
            time.sleep(INTERVALLE)
    except KeyboardInterrupt:
        print("\n  Dashboard arrêté.")