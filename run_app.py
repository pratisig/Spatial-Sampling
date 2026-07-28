# -*- coding: utf-8 -*-
"""
Point d'entrée pour la compilation en exécutable Windows (.exe)
Lance l'application Streamlit de manière programmatique de façon autonome.

CRUCIAL : Nous importons ici explicitement TOUTES les bibliothèques tierces
utilisées dans app.py. Comme app.py est chargé dynamiquement par Streamlit 
lors de l'exécution, PyInstaller ne peut pas détecter ses imports de manière statique.
En les important ici, nous forçons PyInstaller à les inclure dans le package compilé.

Conception : Pratisig Consulting Services
"""

import os
import sys

# --- FORCER L'INCLUSION DES DÉPENDANCES DANS LE BUNDLE PYINSTALLER ---
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
import gpxpy
import folium
import streamlit_folium
import openpyxl
import pyproj
import rtree
import pyogrio
import jinja2
import geojson

# Importer Streamlit à la fin
import streamlit.web.cli as stcli

if __name__ == '__main__':
    # Déterminer si on tourne depuis l'exécutable compilé ou le script Python
    if getattr(sys, 'frozen', False):
        # Sous PyInstaller frozen, prioriser le dossier de l'exécutable (Echantillon_Spatial.exe)
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    app_path = os.path.join(base_dir, "app.py")
    
    # Sécurité : Si app.py n'est pas trouvé à côté de l'exécutable, chercher dans le dossier temporaire _MEIPASS
    if not os.path.exists(app_path):
        app_path = os.path.join(getattr(sys, '_MEIPASS', ''), "app.py")
        
    # Si toujours introuvable, afficher un message d'erreur
    if not os.path.exists(app_path):
        print(f"ERREUR : Impossible de localiser le fichier app.py dans {base_dir} ou dans le cache temporaire.")
        sys.exit(1)
    
    # Configurer les arguments système pour lancer Streamlit programmatoirement
    sys.argv = ["streamlit", "run", app_path, "--global.developmentMode=false"]
    
    # Lancer le serveur Streamlit
    sys.exit(stcli.main())
