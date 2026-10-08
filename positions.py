#!/usr/bin/env python3
# positions_v3.py - Calcul SGP4 via omm.initialize

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from sgp4.api import Satrec, jday, WGS72
from sgp4 import omm

BASE = Path(__file__).parent
CELESTRAK = BASE / "all_active.json"
SORTIE = BASE / "positions.json"

R_EARTH = 6371.0

print("Chargement du catalogue...")
with open(CELESTRAK) as f:
    catalogue = json.load(f)
print(f"{len(catalogue)} satellites chargés")

now = datetime.now(timezone.utc)
jd, fr = jday(now.year, now.month, now.day,
              now.hour, now.minute, now.second)


def omm_vers_satrec(sat):
    """Crée un Satrec depuis un objet OMM via omm.initialize."""
    satrec = Satrec()
    # omm.initialize attend un dictionnaire avec les clés OMM
    # Vérifier le nom exact des clés requises
    omm.initialize(satrec, sat)
    return satrec


def eci_vers_geo(r, jd, fr):
    x, y, z = r
    gmst = (280.46061837 + 360.98564736629 * (jd + fr - 2451545.0)) % 360
    gmst_rad = math.radians(gmst)
    x_rot = x * math.cos(gmst_rad) + y * math.sin(gmst_rad)
    y_rot = -x * math.sin(gmst_rad) + y * math.cos(gmst_rad)
    z_rot = z
    lon = math.degrees(math.atan2(y_rot, x_rot))
    lat = math.degrees(math.atan2(z_rot, math.sqrt(x_rot**2 + y_rot**2)))
    alt = math.sqrt(x_rot**2 + y_rot**2 + z_rot**2) - R_EARTH
    return lat, lon, alt


resultats = []
erreurs = []

for sat in catalogue:
    try:
        satrec = omm_vers_satrec(sat)
        e, r, v = satrec.sgp4(jd, fr)
        
        if e != 0:
            erreurs.append(sat["NORAD_CAT_ID"])
            continue
        
        if any(math.isnan(x) for x in r):
            erreurs.append(sat["NORAD_CAT_ID"])
            continue
        
        lat, lon, alt = eci_vers_geo(r, jd, fr)
        
        if math.isnan(lat) or math.isnan(lon) or math.isnan(alt):
            erreurs.append(sat["NORAD_CAT_ID"])
            continue
        
        resultats.append({
            "norad_id": sat["NORAD_CAT_ID"],
            "nom": sat["OBJECT_NAME"],
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "altitude_km": round(alt, 2),
            "vitesse_km_s": round(math.sqrt(sum(vv*vv for vv in v)), 3)
        })
    except Exception as ex:
        erreurs.append(sat["NORAD_CAT_ID"])
        continue

with open(SORTIE, "w") as f:
    json.dump({
        "timestamp": now.isoformat(),
        "total": len(resultats),
        "erreurs": len(erreurs),
        "positions": resultats
    }, f, indent=2)

print(f"✅ {len(resultats)} positions calculées")
print(f"❌ {len(erreurs)} erreurs")
print(f"📄 {SORTIE}")