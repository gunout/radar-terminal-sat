#!/usr/bin/env python3
# radar_reunion.py - Radar ESA temps réel depuis La Réunion

import json
import math
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from sgp4.api import Satrec, jday
from sgp4 import omm

BASE = Path(__file__).parent
CELESTRAK = BASE / "all_active.json"

# Coordonnées : La Réunion (Saint-Denis)
OBS_LAT = -20.88
OBS_LON = 55.45
OBS_ALT = 0.035
R_EARTH = 6371.0
INTERVAL = 5
MIN_ELEV = 5.0

ESA_BLUE = "\033[38;5;33m"
ESA_GOLD = "\033[38;5;220m"
ESA_CYAN = "\033[38;5;51m"
ESA_WHITE = "\033[38;5;255m"
ESA_GREY = "\033[38;5;245m"
ESA_GREEN = "\033[38;5;46m"
ESA_AMBER = "\033[38;5;214m"
ESA_RED = "\033[38;5;196m"
BOLD = "\033[1m"
RESET = "\033[0m"

FILTRES = {
    "all":       ("TOUS",       lambda s, n: True),
    "leo":       ("LEO",        lambda s, n: s < 2000),
    "meo":       ("MEO",        lambda s, n: 2000 <= s < 30000),
    "geo":       ("GEO",        lambda s, n: s >= 30000),
    "starlink":  ("STARLINK",   lambda s, n: "STARLINK" in n),
    "oneweb":    ("ONEWEB",     lambda s, n: "ONEWEB" in n),
    "kuiper":    ("KUIPER",     lambda s, n: "KUIPER" in n),
    "nav":       ("NAVIGATION", lambda s, n: any(x in n for x in ["GPS","GALILEO","GLONASS","BEIDOU","NAVSTAR","GSAT","IRNSS"])),
    "stations":  ("STATIONS",   lambda s, n: any(x in n for x in ["ISS","CSS","TIANHE","ZARYA"])),
    "insat":     ("INSAT/GSAT", lambda s, n: any(x in n for x in ["INSAT","GSAT","IRNSS"])),
}

W = 78


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


def load_catalogue():
    print(f"{ESA_CYAN}+-- ESA ORBITAL TRACKING SYSTEM -- INIT --+{RESET}")
    with open(CELESTRAK) as f:
        cat = json.load(f)
    print(f"{ESA_CYAN}|{RESET} {len(cat)} objets charges                    {ESA_CYAN}|{RESET}")
    return cat


def prepare_orbits(catalogue, filtre_func):
    satrecs = {}
    for sat in catalogue:
        try:
            nom = sat["OBJECT_NAME"]
            mm = float(sat["MEAN_MOTION"])
            T_s = 86400 / mm
            alt_est = (398600.4418 * (T_s / (2 * math.pi)) ** 2) ** (1/3) - 6371
            if not filtre_func(alt_est, nom):
                continue
            satrec = Satrec()
            omm.initialize(satrec, sat)
            satrecs[sat["NORAD_CAT_ID"]] = (satrec, nom)
        except Exception:
            continue
    print(f"{ESA_CYAN}|{RESET} {len(satrecs)} orbites pretes                   {ESA_CYAN}|{RESET}")
    print(f"{ESA_CYAN}+{'-' * 47}+{RESET}")
    return satrecs


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


def az_el(lat_s, lon_s, alt_s):
    lat_r = math.radians(OBS_LAT)
    lon_r = math.radians(OBS_LON)
    lat_ss = math.radians(lat_s)
    lon_ss = math.radians(lon_s)
    ox = (R_EARTH + OBS_ALT) * math.cos(lat_r) * math.cos(lon_r)
    oy = (R_EARTH + OBS_ALT) * math.cos(lat_r) * math.sin(lon_r)
    oz = (R_EARTH + OBS_ALT) * math.sin(lat_r)
    sx = (R_EARTH + alt_s) * math.cos(lat_ss) * math.cos(lon_ss)
    sy = (R_EARTH + alt_s) * math.cos(lat_ss) * math.sin(lon_ss)
    sz = (R_EARTH + alt_s) * math.sin(lat_ss)
    dx, dy, dz = sx - ox, sy - oy, sz - oz
    sl, cl = math.sin(lat_r), math.cos(lat_r)
    so, co = math.sin(lon_r), math.cos(lon_r)
    s = sl * co * dx + sl * so * dy - cl * dz
    e = -so * dx + co * dy
    z = cl * co * dx + cl * so * dy + sl * dz
    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
    az = math.degrees(math.atan2(e, -s)) % 360
    el = math.degrees(math.asin(z / dist))
    return az, el, dist


def radar_ascii(satellites):
    size = 51
    c = size // 2
    grid = [[" " for _ in range(size)] for _ in range(size)]

    for r in [20, 14, 8, 3]:
        for a_deg in range(0, 360, 4):
            a = math.radians(a_deg)
            x = int(round(c + r * math.cos(a)))
            y = int(round(c + r * math.sin(a)))
            if 0 <= x < size and 0 <= y < size and grid[y][x] == " ":
                grid[y][x] = "."

    for a_deg in range(0, 360, 15):
        a = math.radians(a_deg)
        for r in range(2, c):
            x = int(round(c + r * math.cos(a)))
            y = int(round(c + r * math.sin(a)))
            if 0 <= x < size and 0 <= y < size and grid[y][x] == " ":
                grid[y][x] = "."

    for i in range(size):
        if grid[c][i] == " ":
            grid[c][i] = "-"
        if grid[i][c] == " ":
            grid[i][c] = "|"

    for d in range(-c, c + 1):
        for x, y in [(c + d, c + d), (c + d, c - d)]:
            if 0 <= x < size and 0 <= y < size and grid[y][x] == " ":
                grid[y][x] = "."

    grid[c][c] = f"{ESA_CYAN}O{RESET}"

    for sat in satellites:
        az = sat["az"]
        el = sat["el"]
        r = int((90 - el) / 90 * (c - 1))
        r = max(1, min(c - 1, r))
        a = math.radians(90 - az)
        x = int(round(c + r * math.cos(a)))
        y = int(round(c - r * math.sin(a)))
        if 0 <= x < size and 0 <= y < size:
            alt = sat["alt"]
            if alt < 500:
                grid[y][x] = f"{ESA_GREEN}*{RESET}"
            elif alt < 2000:
                grid[y][x] = f"{ESA_AMBER}o{RESET}"
            elif alt < 30000:
                grid[y][x] = f"{ESA_GOLD}O{RESET}"
            else:
                grid[y][x] = f"{ESA_RED}#{RESET}"

    print(f"{ESA_CYAN}                         +-- N --+{RESET}")
    print(f"{ESA_CYAN}                         |   0   |{RESET}")
    print(f"{ESA_CYAN}                         +---+---+{RESET}")
    for i, row in enumerate(grid):
        line = "".join(row)
        if i == c:
            print(f"{ESA_CYAN}W 270 -------------------{RESET}{line}{ESA_CYAN}------------------- 90 E{RESET}")
        else:
            print(f"                            {line}")
    print(f"{ESA_CYAN}                         +---+---+{RESET}")
    print(f"{ESA_CYAN}                         |  180  |{RESET}")
    print(f"{ESA_CYAN}                         +-- S --+{RESET}")


COLS = [
    ("ID",          6,  "center"),
    ("OBJECT NAME", 26, "left"),
    ("AZ",          7,  "center"),
    ("ELEVATION",   17, "center"),
    ("DIST km",     10, "center"),
    ("ALT km",      9,  "center"),
]


def border(char="="):
    parts = [char * (w + 2) for _, w, _ in COLS]
    return f"{ESA_BLUE}+" + "+".join(parts) + f"+{RESET}"


def row(cells, colors=None):
    parts = []
    for i, (_, w, align) in enumerate(COLS):
        cell = cells[i]
        if colors and colors[i]:
            cell = f"{colors[i]}{cell}{RESET}"
        parts.append(f" {pad(cell, w, align)} ")
    return f"{ESA_BLUE}|{RESET}" + f"{ESA_BLUE}|{RESET}".join(parts) + f"{ESA_BLUE}|{RESET}"


def afficher_dashboard(satellites, filtre_desc):
    now = datetime.now(timezone.utc)

    E = ["███████", "██     ", "█████  ", "██     ", "███████"]
    S = ["███████", "██     ", "███████", "     ██", "███████"]
    A = ["███████", "██   ██", "███████", "██   ██", "██   ██"]

    LOGO_W = 7 + 1 + 7 + 1 + 7
    INFO_W = 38
    PAD_L = 2
    PAD_R = 1
    GAP = W - 2 - PAD_L - LOGO_W - INFO_W - PAD_R

    infos = [
        f"{ESA_GREY}EUROPEAN SPACE AGENCY{RESET}",
        f"{ESA_GREY}ORBITAL TRACKING SYSTEM{RESET}",
        f"{ESA_GREY}GROUND STATION : LA REUNION{RESET}",
        f"{ESA_GREY}FILTER :{RESET} {ESA_GOLD}{filtre_desc}{RESET}",
        f"{ESA_GREY}UTC :{RESET} {ESA_WHITE}{now.strftime('%Y-%m-%d %H:%M:%S')}{RESET}",
    ]

    print(f"{ESA_BLUE}+{'=' * W}+{RESET}")
    print(f"{ESA_BLUE}|{RESET}{' ' * W}{ESA_BLUE}|{RESET}")

    for i in range(5):
        logo = (f"{ESA_GOLD}{BOLD}{E[i]}{RESET} "
                f"{ESA_GOLD}{BOLD}{S[i]}{RESET} "
                f"{ESA_GOLD}{BOLD}{A[i]}{RESET}")
        print(f"{ESA_BLUE}|{RESET}"
              f"{' ' * PAD_L}"
              f"{logo}"
              f"{' ' * GAP}"
              f"{pad(infos[i], INFO_W, 'right')}"
              f"{' ' * PAD_R}"
              f"{ESA_BLUE}|{RESET}")

    etoiles = f"{ESA_GOLD}★ ★ ★ ★  ★ ★ ★ ★  ★ ★ ★ ★{RESET}"
    print(f"{ESA_BLUE}|{RESET}"
          f"{' ' * PAD_L}"
          f"{etoiles}"
          f"{' ' * (W - PAD_L - vlen(etoiles) - PAD_R)}"
          f"{ESA_BLUE}|{RESET}")
    print(f"{ESA_BLUE}|{RESET}{' ' * W}{ESA_BLUE}|{RESET}")
    print(f"{ESA_BLUE}+{'=' * W}+{RESET}")
    print()

    radar_ascii(satellites)
    print()

    print(f"  {ESA_GREY}LEGEND :{RESET}  "
          f"{ESA_GREEN}*{RESET} {ESA_GREY}LEO LOW{RESET}   "
          f"{ESA_AMBER}o{RESET} {ESA_GREY}LEO HIGH{RESET}   "
          f"{ESA_GOLD}O{RESET} {ESA_GREY}MEO{RESET}   "
          f"{ESA_RED}#{RESET} {ESA_GREY}GEO{RESET}")
    print()

    n_leo = sum(1 for s in satellites if s["alt"] < 2000)
    n_meo = sum(1 for s in satellites if 2000 <= s["alt"] < 30000)
    n_geo = sum(1 for s in satellites if s["alt"] >= 30000)
    el_max = max((s["el"] for s in satellites), default=0)
    alt_min = min((s["alt"] for s in satellites), default=0)

    print(f"{ESA_BLUE}+{'=' * W}+{RESET}")
    titre = f"  {ESA_WHITE}{BOLD}TRACKING STATISTICS{RESET}"
    tag = f"{ESA_GREY}// ESA-OPS{RESET}"
    manque = W - vlen(titre) - vlen(tag) - 2
    print(f"{ESA_BLUE}|{RESET}{titre}{' ' * max(0, manque)}{tag}  {ESA_BLUE}|{RESET}")
    print(f"{ESA_BLUE}+{'-' * W}+{RESET}")

    s1 = (f"  {ESA_GREY}TOTAL VISIBLE{RESET}  {ESA_WHITE}{len(satellites):>5}{RESET}   "
          f"{ESA_GREY}LEO{RESET} {ESA_GREEN}{n_leo:>5}{RESET}   "
          f"{ESA_GREY}MEO{RESET} {ESA_GOLD}{n_meo:>4}{RESET}   "
          f"{ESA_GREY}GEO{RESET} {ESA_RED}{n_geo:>4}{RESET}")
    print(f"{ESA_BLUE}|{RESET}{s1}{' ' * max(0, W - vlen(s1) - 1)}{ESA_BLUE}|{RESET}")

    s2 = (f"  {ESA_GREY}MAX ELEVATION{RESET}  {ESA_WHITE}{el_max:>5.1f} deg{RESET}   "
          f"{ESA_GREY}MIN ALT{RESET} {ESA_WHITE}{alt_min:>7.0f} km{RESET}   "
          f"{ESA_GREY}SHOWING{RESET} {ESA_WHITE}{min(len(satellites),15):>3}{RESET}")
    print(f"{ESA_BLUE}|{RESET}{s2}{' ' * max(0, W - vlen(s2) - 1)}{ESA_BLUE}|{RESET}")

    print(f"{ESA_BLUE}+{'=' * W}+{RESET}")
    print()

    print(border("="))
    header_cells = [f"{ESA_WHITE}{BOLD}{nom}{RESET}" for nom, _, _ in COLS]
    print(row(header_cells))
    print(border("="))

    for sat in satellites[:15]:
        alt = sat["alt"]
        if alt < 500:
            color = ESA_GREEN
        elif alt < 2000:
            color = ESA_AMBER
        elif alt < 30000:
            color = ESA_GOLD
        else:
            color = ESA_RED

        el_bar = int(sat["el"] / 90 * 11)
        el_viz = "#" * el_bar + "-" * (11 - el_bar)
        el_str = f"{el_viz} {sat['el']:>5.1f}"

        cells = [
            str(sat["norad"])[:5],
            sat["nom"][:24],
            f"{sat['az']:>5.1f}",
            el_str,
            f"{sat['dist']:>8.0f}",
            f"{sat['alt']:>7.0f}",
        ]
        colors = [color, ESA_WHITE, None, color, None, color]
        print(row(cells, colors))

    print(border("="))

    footer = (f" {ESA_GREY}CTRL+C to quit{RESET}   {ESA_BLUE}|{RESET}   "
              f"{ESA_GREY}REFRESH{RESET} {ESA_WHITE}{INTERVAL}s{RESET}   {ESA_BLUE}|{RESET}   "
              f"{ESA_GREY}SOURCE{RESET} {ESA_WHITE}CelesTrak ACTIVE{RESET}")
    print(f"{ESA_BLUE}|{RESET}{footer}{' ' * max(0, W - vlen(footer) - 1)}{ESA_BLUE}|{RESET}")
    print(f"{ESA_BLUE}+{'=' * W}+{RESET}")
    print(f"{ESA_GOLD}  ★ ESA -- EUROPEAN SPACE AGENCY -- LA REUNION{RESET}")


def afficher(filtre_desc, satrecs):
    while True:
        now = datetime.now(timezone.utc)
        jd, fr = jday(now.year, now.month, now.day,
                      now.hour, now.minute, now.second)

        visibles = []
        for norad, (satrec, nom) in satrecs.items():
            try:
                e, r, v = satrec.sgp4(jd, fr)
                if e != 0 or any(math.isnan(x) for x in r):
                    continue
                lat, lon, alt = eci_vers_geo(r, jd, fr)
                az, el, dist = az_el(lat, lon, alt)
                if el >= MIN_ELEV:
                    visibles.append({
                        "norad": norad, "nom": nom,
                        "az": az, "el": el,
                        "dist": dist, "alt": alt,
                    })
            except Exception:
                continue

        visibles.sort(key=lambda s: -s["el"])
        os.system("clear")
        afficher_dashboard(visibles, filtre_desc)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    catalogue = load_catalogue()
    filtre_nom = sys.argv[1] if len(sys.argv) > 1 else "all"
    if filtre_nom not in FILTRES:
        print(f"Filtres : {', '.join(FILTRES.keys())}")
        sys.exit(1)

    filtre_desc, filtre_func = FILTRES[filtre_nom]
    satrecs = prepare_orbits(catalogue, filtre_func)
    time.sleep(1)

    try:
        afficher(filtre_desc, satrecs)
    except KeyboardInterrupt:
        print(f"\n{ESA_GOLD}★ ESA Radar stopped.{RESET}")