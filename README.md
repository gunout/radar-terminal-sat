<div align="center">

# 🛰️ Radar Terminal Satellites

**Suivi en temps réel des satellites en orbite terrestre, directement dans votre terminal.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![SGP4](https://img.shields.io/badge/Propagation-SGP4-ff6b6b?style=for-the-badge)](https://github.com/brandon-rhodes/python-sgp4)
[![Data](https://img.shields.io/badge/Data-CelesTrak-0ea5e9?style=for-the-badge)](https://celestrak.org/)
[![Terminal](https://img.shields.io/badge/Terminal-ASCII-000000?style=for-the-badge&logo=gnubash&logoColor=white)](https://github.com/gunout/radar-terminal-sat)

<img src="https://img.shields.io/badge/status-active-22c55e?style=flat-square" alt="Status">
<img src="https://img.shields.io/badge/version-3.0-blue?style=flat-square" alt="Version">
<img src="https://img.shields.io/badge/satellites-16,682-orange?style=flat-square" alt="Satellites">

Un radar ASCII haute définition qui calcule en temps réel la position des satellites visibles depuis votre position, avec azimut, élévation, distance et altitude.

</div>

---

## SCREENSHOTS 

<img width="1920" height="1080" alt="735_Sat" src="https://github.com/user-attachments/assets/ec440323-a6e7-4a10-854f-22739b803d53" />

---

## 📖 À propos

Ce projet permet de **visualiser en temps réel** les satellites en orbite autour de la Terre, directement depuis un terminal. Il utilise :

- **CelesTrak** pour le catalogue orbital (16 682 satellites actifs)
- **SGP4** pour la propagation orbitale
- **Natural Earth** pour la carte du monde (radar)
- **ASCII art** pour un rendu universel

Idéal pour les passionnés de spatial, les radioamateurs, ou toute personne curieuse de voir ce qui passe au-dessus de sa tête.

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| 🎯 **Radar temps réel** | Vue de dessus avec azimut et élévation |
| 📊 **Dashboard** | Statistiques, top opérateurs, histogramme |
| 🎨 **Design ESA** | Logo et palette de l'Agence spatiale européenne |
| 🌍 **Carte du monde** | Natural Earth 110m, projection équirectangulaire |
| 🔍 **Filtres** | Starlink, OneWeb, Kuiper, navigation, stations... |
| 💻 **100% terminal** | Compatible SSH, aucune interface graphique |
| ⚡ **Calcul local** | SGP4 exécuté sur votre machine, pas d'API externe |
| 🌐 **Multi-sites** | Fonctionne partout (Paris, La Réunion, Kourou, etc.) |

---

## 🚀 Installation

### Prérequis

- Python 3.12+
- Terminal 256 couleurs (XFCE4, GNOME, Kitty, Alacritty...)
- ~10 Mo d'espace disque

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/gunout/radar-terminal-sat.git
cd radar-terminal-sat

# 2. Créer un environnement virtuel
python3 -m venv nasa-env
source nasa-env/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Télécharger le catalogue orbital
curl -o all_active.json "https://celestrak.org/NORAD/elements/gp.php?GROUP=ACTIVE&FORMAT=JSON"
```

---

## 🎮 Utilisation

### Radar temps réel

```bash
# Radar depuis Paris
python3 radar.py starlink

# Radar depuis La Réunion
python3 radar.py --lat -20.88 --lon 55.45 starlink
```

### Dashboard

```bash
# Dashboard depuis Paris
python3 dashboard.py

# Dashboard depuis La Réunion
python3 dashboard.py --lat -20.88 --lon 55.45
```

### Filtres disponibles

| Filtre | Description |
|--------|-------------|
| `all` | Tous les satellites |
| `leo` | Orbite basse (< 2000 km) |
| `meo` | Orbite moyenne (2000-30000 km) |
| `geo` | Orbite géostationnaire (> 30000 km) |
| `starlink` | SpaceX Starlink (~11 000) |
| `oneweb` | OneWeb (~650) |
| `kuiper` | Amazon Kuiper (~390) |
| `nav` | Navigation (GPS, Galileo, GLONASS, BeiDou) |
| `stations` | ISS, CSS, Tiangong |
| `insat` | INSAT / GSAT / IRNSS (Inde) |

---

## 📸 Aperçu

### Radar

```
+==============================================================================+
|                                                                              |
|  ███████ ███████ ███████                             EUROPEAN SPACE AGENCY  |
|  ██      ██      ██   ██                           ORBITAL TRACKING SYSTEM  |
|  █████   ███████ ███████                            GROUND STATION : PARIS  |
|  ██           ██ ██   ██                                 FILTER : STARLINK  |
|  ███████ ███████ ██   ██                         UTC : 2026-10-08 21:41:44  |
|  ★ ★ ★ ★  ★ ★ ★ ★  ★ ★ ★ ★                                                  |
|                                                                              |
+==============================================================================+

                         +-- N --+
                         |   0   |
                         +---+---+
                            .                        |                        .
                             .                       .                       . 
                              .                .     .     .                .  
                               .               . *  o.     .               .   
                                .        .     *  *  .     .     .        .    
                                 .       .    o*. ....... .     .        .     
                                  .       . * ...    .*   ...   .       .      
                                   .     ** .   .    .  * .   . .      .       
                                    .     o.    .    .    .    ..     .        
                                     . **. ..*   .   .   .    *  .  *.         
                                      . .   . *  .   .   .    .  o. .          
                                       . *   .   .........   .     . o         
                                    * . .    * ....  .  .....     . . *        
                                ..   .   . * .. *o.  .  .** ..*  .   .   ..    
                                  *..*    . . .   . *.**.   . .*. *   ...      
                                    .***** .. o.  .  .  . ..  ..    **.*       
                                  ***.*  *. *  *.  . . .  .   . . **..****     
                                 **. * .  .  .  .  .....  .  .* . *. *** *     
                                * *     ...* *.* ... . ...  .   ..*  *  . *    
                              ..**.*    .  .   ... . . .. ..   *  .    *.*...  
                               * ..*.  *.  ... .. . .*. * .. ..   . * ..*.     
                                 .   ....*    .* .. ... .. ..    *....   . *   
                                ****   ..... ..............*.. .....    **     
                                       .    ....  .......  ....    .      *    
                                *.*   *.o    .  .....|....o  .     .*    . *   
W 270 --------------------...o...*......*....*...-O-...............o...*...-------------------- 90 E
                               **.     .     .  .....|.....  .     .     .*    
                                *    * .    ....  .......  ....    . *     *   
                                 .   * ..... ...*............. ...*. *   .     
                                 .  *....     .  .. .** ..  .     ...*   .     
                                *....*  *  ... .. . ... . .. ... *.   ....*    
                              ...**  ** *  .   .. *. . .. ..   .  .  *  .**..  
                                 *. *   ...   .  ... . ...  o   ...    ****    
                                 **** *.  .  .  .  .....  .  .  .  .   .       
                                 *** ..   . .   .  . . . *.   . . * .. **      
                                   *.* *   ..  .. .  .  . .. *..   * **        
                                 .**.*    . .* .  *  .  .   . . .  *  ***.     
                                .  **.  *.   ..   .  .  .   ..   ** **    .    
                                   *  **.***  .....  .  *....     . * **       
                                    ** .*    .*  ...*.....*  .* *  . *         
                                     *. . * *.   .   . * . * *.* *. .*         
                                     .* **  .    **  .   .* * .  * **.         
                                    .   ***** * *  * . *  .o*  *.*    .        
                                   .    ***.o*  .  * .*   *   .** *    .       
                                  .       . * ..**   .    *.. **.       .      
                                 .        . *  ***.....*. *  ** .        .     
                                .        .    *.  * **  ** * *   .        .    
                               .               .  ***.*  * .               .   
                              .                .     .     .                .  
                             .                       .                       . 
                            .                        |                        .
                         +---+---+
                         |  180  |
                         +-- S --+

  LEGEND :  * LEO LOW   o LEO HIGH   O MEO   # GEO

+==============================================================================+
|  TRACKING STATISTICS                                             // ESA-OPS  |
+------------------------------------------------------------------------------+
|  TOTAL VISIBLE    332   LEO   332   MEO    0   GEO    0                     |
|  MAX ELEVATION   72.5 deg   MIN ALT     298 km   SHOWING  15                |
+==============================================================================+

+========+============================+=========+===================+============+===========+
|   ID   | OBJECT NAME                |   AZ    |     ELEVATION     |  DIST km   |  ALT km   |
+========+============================+=========+===================+============+===========+
| 46045  | STARLINK-1591              |  158.0  | ########---  72.5 |       491  |      470  |
| 68514  | STARLINK-37251             |  185.8  | ########---  71.9 |       485  |      463  |
| 65529  | STARLINK-35077             |    2.1  | ########---  70.9 |       493  |      467  |
+========+============================+=========+===================+============+===========+
| CTRL+C to quit   |   REFRESH 5s   |   SOURCE CelesTrak ACTIVE               |
+==============================================================================+
  ★ ESA -- EUROPEAN SPACE AGENCY -- ORBITAL OPERATIONS
```

### Dashboard

```
╔════════════════════════════════════════════════════════════════════╗
║                  DASHBOARD SATELLITES — PARIS                      ║
║                    (positions recalculées SGP4)                    ║
╠════════════════════════════════════════════════════════════════════╣
║ Mise à jour : 2026-10-08 21:41:44 UTC                              ║
║ Total       : 16682 satellites                                     ║
║ Visibles    : 736 (el > 5°)                                        ║
║ Intervalle  : 10s                                                  ║
╠════════════════════════════════════════════════════════════════════╣
║ RÉPARTITION PAR TYPE D'ORBITE                                      ║
╠════════════════════════════════════════════════════════════════════╣
║   LEO bas      11459  ███████████████████████████                  ║
║   LEO moyen     3177  ███████                                      ║
║   LEO haut      1234  ██                                           ║
║   GEO            617  █                                            ║
╠════════════════════════════════════════════════════════════════════╣
║ TOP 10 OPÉRATEURS                                                  ║
╠════════════════════════════════════════════════════════════════════╣
║   STARLINK        11132  ██████████████████████████████            ║
║   ONEWEB            651  █                                         ║
║   KUIPER            391  █                                         ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 🗂️ Structure du projet

```
radar-terminal-sat/
├── radar.py              # Radar temps réel
├── dashboard.py          # Dashboard statistiques
├── positions.py          # Calcul SGP4 → positions.json
├── requirements.txt      # Dépendances Python
├── .gitignore            # Fichiers exclus
├── README.md             # Ce fichier
└── LICENSE               # MIT
```

---

## 🔧 Configuration

### Changer de site d'observation

Modifiez les coordonnées dans `radar.py` et `dashboard.py` :

```python
# Paris
OBS_LAT = 48.85
OBS_LON = 2.35

# La Réunion (Saint-Denis)
OBS_LAT = -20.88
OBS_LON = 55.45

# Ou passez-les en argument
python3 radar.py --lat 48.85 --lon 2.35 starlink
```

### Sites prédéfinis

| Site | Latitude | Longitude |
|------|----------|-----------|
| Paris | 48.85 | 2.35 |
| La Réunion | -20.88 | 55.45 |
| Kourou (CSG) | 5.23 | -52.77 |
| Toulouse (CNES) | 43.60 | 1.44 |
| Cologne (ESA) | 50.94 | 6.96 |

---

## 📦 Dépendances

```txt
sgp4>=2.27        # Propagation orbitale SGP4
pyshp>=2.3        # Lecture des shapefiles Natural Earth
```

---

## 🧪 Tests

```bash
# Vérifier que SGP4 fonctionne
python3 -c "from sgp4.api import Satrec; print('OK')"

# Vérifier le catalogue
python3 -c "import json; print(len(json.load(open('all_active.json'))), 'satellites')"

# Lancer le radar
python3 radar.py stations
```

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

1. **Fork** le projet
2. **Créer** une branche (`git checkout -b feature/ma-feature`)
3. **Commit** (`git commit -m 'Ajout de ma feature'`)
4. **Push** (`git push origin feature/ma-feature`)
5. **Ouvrir** une Pull Request

---

## 📜 Licence

Ce projet est sous licence **MIT** — voir [LICENSE](LICENSE).

---

## 🙏 Remerciements

- **[CelesTrak](https://celestrak.org/)** — Catalogue orbital public
- **[Python SGP4](https://github.com/brandon-rhodes/python-sgp4)** — Propagation orbitale
- **[Natural Earth](https://www.naturalearthdata.com/)** — Données cartographiques
- **[ESA](https://www.esa.int/)** — Inspiration du design
- **[NASA](https://www.nasa.gov/)** — Données orbitales publiques

---

<div align="center">

**⭐ Si ce projet vous plaît, n'hésitez pas à lui donner une étoile !**

Fait avec ❤️ pour la communauté spatiale francophone

</div>
