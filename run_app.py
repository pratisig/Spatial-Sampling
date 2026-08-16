# -*- coding: utf-8 -*-
"""
Point d'entrée pour la compilation en exécutable Windows (.exe)
Lance l'application Streamlit de manière programmatique de façon autonome.
Priorise la recherche de app.py à côté de l'exécutable.

SÉCURITÉ PARE-FEU / DROITS ADMIN :
Pour éviter l'alerte du Pare-feu Windows (qui exige les droits d'administrateur),
nous forçons Streamlit à s'exécuter uniquement sur l'adresse de boucle locale 
127.0.0.1 (localhost) au lieu de l'adresse réseau publique 0.0.0.0.

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
    
    # Configurer les arguments système pour lancer Streamlit uniquement en local (localhost)
    # L'argument '--server.address=127.0.0.1' indique à Streamlit de ne pas s'ouvrir sur le réseau public,
    # ce qui contourne de fait l'alerte de sécurité du Pare-feu Windows et évite de demander les droits d'admin !
    sys.argv = [
        "streamlit", "run", app_path, 
        "--global.developmentMode=false",
        "--browser.gatherUsageStats=false",  # Désactive la question d'e-mail de bienvenue
        "--server.address=127.0.0.1",
        "--server.port=8501",
        "--server.headless=false"  # Ouvre AUTOMATIQUEMENT le navigateur au lancement
    ]
    
    # Lancer le serveur Streamlit
    sys.exit(stcli.main())
