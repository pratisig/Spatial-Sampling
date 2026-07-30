# -*- coding: utf-8 -*-
"""
Constrained Random Spatial Sampling Tool
Designed for Epidemiologists and Field Teams (Vaccination & Health Surveys)
Author: Arena.ai Agent
Date: 2026-07-28
"""

import os
import sys
import io
import zipfile
import tempfile
import datetime
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
from shapely.geometry import Point, MultiPoint, Polygon
from shapely.ops import voronoi_diagram
import gpxpy
import gpxpy.gpx
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# Set Page Config
st.set_page_config(
    page_title="🌍 Échantillonnage Spatial des Ménages / Spatial Sampling",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Translations Dictionary
TRANSLATIONS = {
    'fr': {
        'title': "🌍 Échantillonnage Spatial des Ménages",
        'subtitle': "Outil d'échantillonnage aléatoire spatial contraint pour les enquêtes épidémiologiques et de vaccination",
        'lang_selector': "Langue / Language",
        'mode_selector': "Source des données",
        'real_data': "Importer mes propres données (Shapefile, GeoJSON, GPKG, CSV, Excel)",
        'sim_data': "Générer des données de simulation (Dakar, Sénégal)",
        'load_bld': "Couche des Bâtiments / Ménages",
        'load_bld_help': "Fichier de points représentant tous les bâtiments éligibles de la zone.",
        'load_vil': "Couche des Villages / Localités",
        'load_vil_help': "Fichier de points (centroids des villages) ou polygones (limites officielles).",
        'bld_lat_col': "Colonne Latitude (Bâtiments)",
        'bld_lon_col': "Colonne Longitude (Bâtiments)",
        'vil_lat_col': "Colonne Latitude (Villages)",
        'vil_lon_col': "Colonne Longitude (Villages)",
        'vil_name_field': "Champ du nom du village / de la localité",
        'params_header': "⚙️ Paramètres d'Échantillonnage",
        'radius_lbl': "Rayon de recherche (mètres) - si villages sous forme de points",
        'radius_help': "Rayon du tampon autour des points de village pour délimiter les zones d'influence.",
        'dist_lbl': "Distance minimale entre ménages sélectionnés (mètres)",
        'dist_help': "Évite la concentration spatiale des ménages (effet de grappe trop prononcé).",
        'method_lbl': "Méthode de calcul du nombre de ménages",
        'fixed_method': "Nombre fixe de ménages par village",
        'percent_method': "Pourcentage de bâtiments par village",
        'total_method': "Allocation d'un échantillon total (proportionnel au nombre de bâtiments)",
        'sample_val_lbl': "Valeur de l'échantillon",
        'sample_val_help': "Nombre de ménages à sélectionner, pourcentage, ou taille globale de l'échantillon.",
        'relax_lbl': "Relâcher la contrainte de distance si nécessaire",
        'relax_help': "Si activé, l'algorithme réduira progressivement la distance minimale si le nombre cible de ménages ne peut pas être atteint dans un village.",
        'run_btn': "🚀 Lancer l'Échantillonnage Spatial",
        'out_path_lbl': "Dossier de sauvegarde local (sur votre ordinateur)",
        'export_gpx_lbl': "Exporter les fichiers GPX par village (pour OsmAnd)",
        'export_kml_lbl': "Exporter les fichiers KML par village (pour Google Earth)",
        'export_report_lbl': "Générer le rapport de synthèse HTML/PDF",
        'summary_hdr': "📊 Rapport de Synthèse",
        'metric_villages': "Villages traités",
        'metric_buildings': "Bâtiments totaux",
        'metric_sampled': "Ménages échantillonnés",
        'metric_success': "Taux de réussite",
        'metric_avg_dist': "Distance moyenne réelle",
        'map_title': "🗺️ Carte Interactive des Échantillons",
        'map_help': "Utilisez le menu en haut à droite de la carte pour changer le fond de carte (OSM ou Image Sat) ou afficher/masquer les couches.",
        'download_hdr': "📥 Téléchargement des Résultats",
        'download_btn': "Télécharger le pack complet de résultats (ZIP)",
        'save_success': "✅ Fichiers sauvegardés localement avec succès dans le dossier :",
        'no_bld_in_vil': "⚠️ Le village '{vil}' n'a aucun bâtiment dans son aire d'influence.",
        'sampling_details': "Détails d'échantillonnage par village",
        'table_vil': "Village",
        'table_bld': "Bâtiments dispo",
        'table_target': "Cible",
        'table_sampled': "Échantillon",
        'table_dist': "Distance finale",
        'table_status': "Statut",
        'osmand_guide': "📱 Guide d'intégration OsmAnd (Navigation Offline)",
        'osmand_steps': """
1. **Copier les fichiers GPX** : Transférez les fichiers GPX du dossier `gpx_exports` vers votre téléphone Android/iOS (via câble USB, email, WhatsApp, ou Google Drive).
2. **Importer dans OsmAnd** :
   - Ouvrez OsmAnd.
   - Allez dans le menu principal ☰ ➔ **Mes lieux** (My Places) ➔ **Traces** (Tracks).
   - Cliquez sur le bouton d'import **+** en bas, et sélectionnez le ou les fichiers GPX.
3. **Naviguer sur le terrain** :
   - Les ménages sélectionnés apparaîtront sous forme d'étoiles ou de points de couleur sur votre carte offline.
   - En cliquant sur un point, vous verrez son identifiant unique (ex: `Yoff_05`) et sa description.
   - Utilisez le guidage GPS piéton ou voiture de OsmAnd pour vous rendre exactement sur le toit du bâtiment sélectionné.
""",
        'google_earth_guide': "💻 Guide d'intégration Google Earth (KML)",
        'google_earth_steps': """
1. **Ouvrir dans Google Earth** : Double-cliquez sur n'importe quel fichier KML du dossier `kml_exports` pour l'ouvrir dans Google Earth Pro (sur PC) ou l'application mobile Google Earth.
2. **Visualiser en 3D** : Observez la position exacte des ménages sélectionnés directement sur l'imagerie satellite haute résolution en 3D pour valider la faisabilité du terrain avant le départ des équipes de vaccination.
""",
        'intro_desc': """
Cet outil réalise un **échantillonnage spatial aléatoire contraint** de ménages (bâtiments) au sein des zones de responsabilité (catchments) de chaque village.
Il est conçu spécifiquement pour les enquêtes de couverture vaccinale, les études épidémiologiques et la planification des équipes humanitaires sur le terrain.

**Améliorations majeures incluses :**
* 🧩 **Détourage automatique par polygone de Voronoi (Thiessen) et Tampon** si vous ne disposez que des coordonnées ponctuelles des villages. Cela garantit des zones de responsabilité non chevauchantes et géographiquement cohérentes.
* 📏 **Contrainte de distance minimale adaptative** : Évite les biais de regroupement spatial (clusters) en maintenant les ménages espacés. Si un village est trop petit ou dense, l'outil réduit intelligemment la contrainte pour atteindre la taille cible tout en maintenant le maximum d'espacement possible !
* 🎒 **Export direct OsmAnd (GPX) et Google Earth (KML)** : Permet de guider les équipes directement sur les toits ciblés sans réseau mobile.
""",
        'sel_village_warning': "Veuillez sélectionner le champ contenant le nom des villages dans la barre latérale."
    },
    'en': {
        'title': "🌍 Household Spatial Sampling Tool",
        'subtitle': "Constrained random spatial sampling tool for epidemiological surveys and vaccination campaigns",
        'lang_selector': "Language / Langue",
        'mode_selector': "Data Source",
        'real_data': "Upload my own data (Shapefile, GeoJSON, GPKG, CSV, Excel)",
        'sim_data': "Generate simulated data (Dakar, Senegal)",
        'load_bld': "Buildings / Households Layer",
        'load_bld_help': "Point file representing all eligible buildings in the zone.",
        'load_vil': "Villages / Localities Layer",
        'load_vil_help': "Point file (village centroids) or polygon file (official boundaries).",
        'bld_lat_col': "Latitude Column (Buildings)",
        'bld_lon_col': "Longitude Column (Buildings)",
        'vil_lat_col': "Latitude Column (Villages)",
        'vil_lon_col': "Longitude Column (Villages)",
        'vil_name_field': "Village / Locality Name Field",
        'params_header': "⚙️ Sampling Parameters",
        'radius_lbl': "Search Radius (meters) - if villages are points",
        'radius_help': "Buffer distance around village points to delineate catchment areas.",
        'dist_lbl': "Minimum distance between selected households (meters)",
        'dist_help': "Avoids spatial clustering of selected households (prevents cluster effect).",
        'method_lbl': "Sample Size Allocation Method",
        'fixed_method': "Fixed number of households per village",
        'percent_method': "Percentage of buildings in each village",
        'total_method': "Proportional allocation of a total sample size (based on building count)",
        'sample_val_lbl': "Sample Value",
        'sample_val_help': "Number of households to select, percentage, or overall target sample size.",
        'relax_lbl': "Relax distance constraint if necessary",
        'relax_help': "If enabled, the algorithm will progressively reduce the minimum distance if the target sample size cannot be met in a village.",
        'run_btn': "🚀 Run Spatial Sampling",
        'out_path_lbl': "Local save folder (on your computer)",
        'export_gpx_lbl': "Export GPX files by village (for OsmAnd)",
        'export_kml_lbl': "Export KML files by village (for Google Earth)",
        'export_report_lbl': "Generate summary HTML/PDF report",
        'summary_hdr': "📊 Sampling Report Summary",
        'metric_villages': "Villages processed",
        'metric_buildings': "Total buildings",
        'metric_sampled': "Sampled households",
        'metric_success': "Success rate",
        'metric_avg_dist': "Actual average distance",
        'map_title': "🗺️ Interactive Sample Map",
        'map_help': "Use the layer control menu in the upper-right corner of the map to switch to Satellite imagery or toggle layers.",
        'download_hdr': "📥 Download Results",
        'download_btn': "Download Complete Results Pack (ZIP)",
        'save_success': "✅ Files successfully saved locally in the folder:",
        'no_bld_in_vil': "⚠️ Village '{vil}' has 0 buildings in its catchment area.",
        'sampling_details': "Sampling details by village",
        'table_vil': "Village",
        'table_bld': "Available buildings",
        'table_target': "Target",
        'table_sampled': "Sampled",
        'table_dist': "Final distance",
        'table_status': "Status",
        'osmand_guide': "📱 OsmAnd Integration Guide (Offline Navigation)",
        'osmand_steps': """
1. **Copy GPX Files**: Transfer the GPX files from the `gpx_exports` folder to your Android/iOS phone (via USB, email, WhatsApp, or Google Drive).
2. **Import into OsmAnd**:
   - Open OsmAnd.
   - Go to main menu ☰ ➔ **My Places** ➔ **Tracks**.
   - Click the **+** (Import) button at the bottom and choose your GPX file(s).
3. **Field Navigation**:
   - The selected households will appear as star icons or colored markers on your offline map.
   - Tap on any point to see its unique identifier (e.g. `Yoff_05`) and details.
   - Use OsmAnd's offline navigation (car or walking mode) to guide you directly to the roof of the selected household!
""",
        'google_earth_guide': "💻 Google Earth & KML Integration Guide",
        'google_earth_steps': """
1. **Open in Google Earth**: Double-click any KML file in the `kml_exports` folder to open it in Google Earth Pro (desktop) or the Google Earth mobile app.
2. **3D Visualization**: Inspect the precise location of the selected households on high-resolution 3D satellite imagery to evaluate terrain accessibility before deploying field teams.
""",
        'intro_desc': """
This tool performs **constrained random spatial sampling** of households (buildings) within village catchment zones.
It is specifically designed for vaccine coverage surveys, epidemiological studies, and field team planning in humanitarian and resource-limited settings.

**Key Features Included:**
* 🧩 **Automatic Catchment Delineation (Voronoi/Thiessen + Buffer)** if you only have point coordinates of villages. This guarantees non-overlapping, geographically continuous catchment zones.
* 📏 **Adaptive Minimum Distance Constraint**: Prevents spatial clustering of samples by keeping points spaced apart. If a village is too small or dense, the tool safely relaxes the constraint to meet the target sample size while maintaining optimal spatial spacing.
* 🎒 **OsmAnd (GPX) and Google Earth (KML) Export**: Allows direct navigation to targeted rooftops in the field without any cellular connection.
""",
        'sel_village_warning': "Please select the field containing village names in the sidebar."
    }
}

# --- HELPER FUNCTIONS ---

def get_utm_epsg(gdf):
    """
    Automatically detects the optimal UTM zone EPSG code for a GeoDataFrame based on its centroid.
    """
    centroid = gdf.geometry.union_all().centroid
    lon, lat = centroid.x, centroid.y
    utm_zone = int(np.floor((lon + 180) / 6) + 1)
    epsg = 32600 + utm_zone if lat >= 0 else 32700 + utm_zone
    return epsg

def detect_lat_lon_cols(columns):
    """
    Tries to auto-detect latitude and longitude columns in a pandas DataFrame.
    """
    lat_candidates = ['lat', 'latitude', 'y', 'lat_wgs84', 'latitude_dec', 'latitude_degrees', 'coord_y']
    lon_candidates = ['lon', 'longitude', 'x', 'lon_wgs84', 'longitude_dec', 'longitude_degrees', 'lng', 'coord_x']
    
    detected_lat = None
    detected_lon = None
    
    cols_lower = [c.lower() for c in columns]
    for cand in lat_candidates:
        if cand in cols_lower:
            detected_lat = columns[cols_lower.index(cand)]
            break
            
    for cand in lon_candidates:
        if cand in cols_lower:
            detected_lon = columns[cols_lower.index(cand)]
            break
            
    return detected_lat, detected_lon

def load_spatial_data(uploaded_file, file_name, is_village=False):
    """
    Loads spatial files (Shapefile, GeoJSON, GPKG, CSV, Excel) and returns a WGS84 GeoDataFrame.
    """
    if file_name.endswith('.zip'):
        # Save zip to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        try:
            gdf = gpd.read_file(tmp_path, engine="pyogrio")
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            else:
                gdf = gdf.to_crs(epsg=4326)
            return gdf, None
        except Exception as e:
            return None, f"Error reading zipped shapefile: {str(e)}"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    elif file_name.endswith(('.geojson', '.gpkg', '.json')):
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        try:
            gdf = gpd.read_file(tmp_path, engine="pyogrio")
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            else:
                gdf = gdf.to_crs(epsg=4326)
            return gdf, None
        except Exception as e:
            return None, f"Error reading file: {str(e)}"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    elif file_name.endswith(('.csv', '.xlsx', '.xls')):
        try:
            if file_name.endswith('.csv'):
                # Try reading with utf-8 first, fallback to latin-1
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
            else:
                df = pd.read_excel(uploaded_file)
                
            lat_col, lon_col = detect_lat_lon_cols(df.columns)
            
            # Put in session state so user can modify if necessary
            suffix = "_vil" if is_village else "_bld"
            if f"lat_col{suffix}" not in st.session_state:
                st.session_state[f"lat_col{suffix}"] = lat_col
            if f"lon_col{suffix}" not in st.session_state:
                st.session_state[f"lon_col{suffix}"] = lon_col
                
            return df, None
        except Exception as e:
            return None, f"Error reading tabular file: {str(e)}"
    else:
        return None, "Unsupported file format."

def generate_simulated_data():
    """
    Generates high-quality simulation datasets centered around Dakar, Senegal.
    Returns (villages_gdf, buildings_gdf)
    """
    # 4 villages in Dakar
    villages = [
        ('Ngor', -17.5122, 14.7505),
        ('Yoff', -17.4715, 14.7602),
        ('Fann', -17.4754, 14.6888),
        ('Medina', -17.4422, 14.7011)
    ]
    
    vill_points = [Point(lon, lat) for _, lon, lat in villages]
    vill_names = [name for name, _, _ in villages]
    vill_gdf = gpd.GeoDataFrame({'nom_vill': vill_names}, geometry=vill_points, crs='EPSG:4326')
    
    # Generate buildings clustered around these villages
    bld_points = []
    bld_villages = []
    
    # Define building densities
    np.random.seed(101) # Set seed for consistent and realistic simulation
    densities = [120, 80, 150, 200] # Number of buildings per village
    spreads = [0.004, 0.005, 0.003, 0.004] # Gaussian spread of buildings around village center
    
    bld_idx = 1
    for (name, lon, lat), density, spread in zip(villages, densities, spreads):
        lons = np.random.normal(lon, spread, density)
        lats = np.random.normal(lat, spread, density)
        for lo, la in zip(lons, lats):
            bld_points.append(Point(lo, la))
            bld_villages.append(f"Ménage_SIM_{bld_idx:04d}")
            bld_idx += 1
            
    bld_gdf = gpd.GeoDataFrame({'id_bat': bld_villages}, geometry=bld_points, crs='EPSG:4326')
    
    return vill_gdf, bld_gdf


# --- GEOPROCESSING PIPELINE ---

def create_catchment_polygons(villages_gdf, search_radius_m, name_field, utm_epsg):
    """
    Generates bounded, non-overlapping catchment polygons for villages.
    If villages are already Polygons/MultiPolygons, uses them directly.
    If they are Points, uses buffer + Voronoi intersection.
    """
    # Project to metric coordinate system
    villages_utm = villages_gdf.to_crs(epsg=utm_epsg)
    
    # Check if geometries are polygons
    geom_types = villages_utm.geometry.geom_type.unique()
    is_polygon = any('Polygon' in t for t in geom_types)
    
    if is_polygon:
        # Already polygon, return it directly
        # But make sure name_field is present and geometries are clean
        villages_utm['geometry'] = villages_utm.geometry.make_valid()
        return villages_utm
        
    # If point geometries, perform Buffer + Voronoi intersection
    # 1. Circular buffers
    buffers = villages_utm.geometry.buffer(search_radius_m)
    
    # 2. Voronoi partition
    if len(villages_utm) >= 2:
        multipoint = MultiPoint(villages_utm.geometry.tolist())
        vor = voronoi_diagram(multipoint)
        
        catchments = []
        for idx, row in villages_utm.iterrows():
            p = row.geometry
            buf = buffers.iloc[idx]
            
            # Find the Voronoi cell containing the village point
            matched_cell = None
            for cell in vor.geoms:
                if cell.contains(p) or cell.distance(p) < 1e-9:
                    matched_cell = cell
                    break
            
            if matched_cell is not None:
                # Intersect buffer with Voronoi cell
                catchment = buf.intersection(matched_cell)
                # Keep valid polygons only
                if not catchment.is_valid:
                    catchment = catchment.make_valid()
                catchments.append(catchment)
            else:
                catchments.append(buf) # Fallback to buffer only
    else:
        # If 1 village point, catchment is just the circular buffer
        catchments = list(buffers)
        
    catchments_utm = gpd.GeoDataFrame(villages_utm.copy(), geometry=catchments, crs=f"EPSG:{utm_epsg}")
    return catchments_utm


def sample_village_buildings(group_df, sample_size, min_dist_m, name_field, relax_constraint=True):
    """
    Core sampling logic with adaptive distance constraint relaxation.
    """
    points = list(group_df.geometry)
    v_name = group_df[name_field].iloc[0]
    
    # If building count is less than or equal to requested sample size, select all buildings
    if len(points) <= sample_size:
        res = group_df.copy()
        res['actual_dist_constraint'] = 0.0
        res['sampling_status'] = 'All Buildings Selected'
        return res
        
    # Shuffle buildings randomly to ensure equal probability of selection
    np.random.seed() # ensures true randomness on each run
    shuffled_indices = np.random.permutation(len(points))
    shuffled_points = [points[i] for i in shuffled_indices]
    shuffled_rows = group_df.iloc[shuffled_indices].copy()
    
    current_min_dist = min_dist_m
    attempts = 0
    max_attempts = 15
    
    selected_indices = []
    selected_geoms = []
    
    while current_min_dist >= 1.5 and attempts < max_attempts:
        selected_indices = []
        selected_geoms = []
        
        for i, geom in enumerate(shuffled_points):
            is_valid = True
            for sel_geom in selected_geoms:
                if geom.distance(sel_geom) < current_min_dist:
                    is_valid = False
                    break
            if is_valid:
                selected_indices.append(i)
                selected_geoms.append(geom)
            if len(selected_geoms) == sample_size:
                break
                
        # If target size is met, or relaxation is disabled, exit
        if len(selected_geoms) == sample_size or not relax_constraint:
            break
            
        # Relax constraint: reduce minimum distance by 15% on each try
        current_min_dist *= 0.85
        attempts += 1
        
    selected_df = shuffled_rows.iloc[selected_indices].copy()
    selected_df['actual_dist_constraint'] = current_min_dist
    
    if len(selected_geoms) == sample_size:
        selected_df['sampling_status'] = 'Target Achieved'
    else:
        selected_df['sampling_status'] = 'Partial Sample (Insufficient points with spacing)'
        
    return selected_df


# --- FILE FORMAT GENERATORS ---

def save_gpx_by_village(gdf_wgs84, name_field, output_folder):
    """
    Saves individual GPX files for OsmAnd, grouped and named by village.
    """
    gpx_dir = os.path.join(output_folder, "gpx_exports")
    os.makedirs(gpx_dir, exist_ok=True)
    
    grouped = gdf_wgs84.groupby(name_field)
    generated_files = []
    
    for village_name, group in grouped:
        safe_name = "".join([c if c.isalnum() or c in "._-" else "_" for c in str(village_name)])
        filename = f"{safe_name}_echantillon.gpx"
        filepath = os.path.join(gpx_dir, filename)
        
        gpx = gpxpy.gpx.GPX()
        gpx.name = f"Echantillon - {village_name}"
        gpx.description = f"Points d'echantillonnage pour le village {village_name}"
        
        for idx, (_, row) in enumerate(group.iterrows()):
            p = row.geometry
            wpt_name = f"{safe_name}_{idx+1:02d}"
            desc = f"Village: {village_name}"
            if 'dist_m' in row:
                desc += f" | Spacing: {row['dist_m']:.1f}m"
            if 'lat' in row and 'lon' in row:
                desc += f" | Lat/Lon: {row['lat']:.5f}, {row['lon']:.5f}"
                
            waypoint = gpxpy.gpx.GPXWaypoint(
                latitude=p.y,
                longitude=p.x,
                name=wpt_name,
                description=desc
            )
            gpx.waypoints.append(waypoint)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(gpx.to_xml())
            
        generated_files.append((filename, filepath))
        
    return generated_files


def save_kml_by_village(gdf_wgs84, name_field, output_folder):
    """
    Saves individual KML files for Google Earth, grouped and named by village.
    """
    kml_dir = os.path.join(output_folder, "kml_exports")
    os.makedirs(kml_dir, exist_ok=True)
    
    grouped = gdf_wgs84.groupby(name_field)
    generated_files = []
    
    for village_name, group in grouped:
        safe_name = "".join([c if c.isalnum() or c in "._-" else "_" for c in str(village_name)])
        filename = f"{safe_name}_echantillon.kml"
        filepath = os.path.join(kml_dir, filename)
        
        kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Echantillon - {village_name}</name>
    <description>Points d'echantillonnage pour le village {village_name}</description>
    <Style id="redPin">
      <IconStyle>
        <scale>1.1</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>
        </Icon>
        <hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>
      </IconStyle>
    </Style>
    <Folder>
      <name>{village_name}</name>
"""
        for idx, (_, row) in enumerate(group.iterrows()):
            p = row.geometry
            wpt_name = f"{safe_name}_{idx+1:02d}"
            desc = f"Village: {village_name}"
            if 'dist_m' in row:
                desc += f" | Distance minimum de securite : {row['dist_m']:.1f}m"
            if 'lat' in row and 'lon' in row:
                desc += f" | Coordonnees : {row['lat']:.5f}, {row['lon']:.5f}"
                
            kml_content += f"""      <Placemark>
        <name>{wpt_name}</name>
        <description>{desc}</description>
        <styleUrl>#redPin</styleUrl>
        <Point>
          <coordinates>{p.x},{p.y},0</coordinates>
        </Point>
      </Placemark>
"""
        kml_content += """    </Folder>
  </Document>
</kml>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(kml_content)
            
        generated_files.append((filename, filepath))
        
    return generated_files


def generate_html_report(summary_stats, village_details, lang):
    """
    Generates a beautifully designed HTML summary report that is printer-friendly (PDF ready).
    """
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    title = "Rapport de Synthèse d'Échantillonnage Spatial" if lang == 'fr' else "Spatial Sampling Summary Report"
    date_lbl = "Généré le" if lang == 'fr' else "Generated on"
    methodology_title = "Méthodologie d'Échantillonnage" if lang == 'fr' else "Sampling Methodology"
    summary_title = "Statistiques Globales" if lang == 'fr' else "Global Statistics"
    details_title = "Détails par Village / Grappe" if lang == 'fr' else "Details by Village / Cluster"
    instructions_title = "Guide d'Utilisation Terrain" if lang == 'fr' else "Field Operations Guide"
    
    # Methodology description
    if lang == 'fr':
        methodology_desc = """
        Cet échantillonnage a été réalisé à l'aide d'algorithmes spatiaux avancés. 
        Pour chaque village, une aire d'influence (catchment) a été délimitée (soit par des limites de polygones fournies, 
        soit automatiquement via l'intersection de tampons de recherche et de polygones de Voronoi/Thiessen). 
        Ensuite, un processus spatial aléatoire contraint par une distance minimale a sélectionné des bâtiments uniques (ménages) 
        afin d'éviter les biais de regroupement spatial (clustering), assurant une représentativité épidémiologique optimale.
        """
        osmand_guide_html = """
        <h4>📱 Importation dans OsmAnd (Navigation Hors-ligne)</h4>
        <ol>
            <li>Transférez les fichiers GPX du dossier <code>gpx_exports</code> vers les téléphones des enquêteurs (par USB, e-mail, WhatsApp, ou Google Drive).</li>
            <li>Ouvrez OsmAnd sur le téléphone.</li>
            <li>Allez dans <strong>Menu ☰ ➔ Mes lieux ➔ Traces</strong>.</li>
            <li>Cliquez sur le bouton d'import <strong>+</strong> et sélectionnez les fichiers GPX copiés.</li>
            <li>Les ménages ciblés s'affichent sous forme d'étoiles sur la carte offline. Sélectionnez un point et cliquez sur <strong>Naviguer</strong> pour vous y rendre directement.</li>
        </ol>
        """
        ge_guide_html = """
        <h4>💻 Importation dans Google Earth (KML)</h4>
        <ol>
            <li>Double-cliquez sur les fichiers KML du dossier <code>kml_exports</code>.</li>
            <li>Google Earth s'ouvrira automatiquement et affichera les points de ménages sur l'imagerie satellite en 3D.</li>
            <li>Cette étape permet de valider visuellement si le point tombe bien sur un bâtiment réel et d'en évaluer l'accessibilité.</li>
        </ol>
        """
    else:
        methodology_desc = """
        This sampling was conducted using advanced spatial geoprocessing. 
        For each village, a zone of influence (catchment area) was delineated (either using user-provided boundaries, 
        or automatically generated via the intersection of circular buffers and Voronoi/Thiessen polygons). 
        Then, a spatially constrained random process with a minimum distance threshold selected unique rooftops (households). 
        This prevents clustering and spatial bias, ensuring optimal epidemiological representation.
        """
        osmand_guide_html = """
        <h4>📱 Import to OsmAnd (Offline Navigation)</h4>
        <ol>
            <li>Transfer the GPX files from the <code>gpx_exports</code> folder to the surveyors' phones (via USB, email, WhatsApp, or Google Drive).</li>
            <li>Open OsmAnd on the phone.</li>
            <li>Navigate to <strong>Menu ☰ ➔ My Places ➔ Tracks</strong>.</li>
            <li>Click the import button <strong>+</strong> and select the copied GPX files.</li>
            <li>The selected target households will appear as star icons on your offline map. Select any point and click <strong>Navigate</strong> to walk or drive directly to it.</li>
        </ol>
        """
        ge_guide_html = """
        <h4>💻 Import to Google Earth (KML)</h4>
        <ol>
            <li>Double-click on any KML file in the <code>kml_exports</code> folder.</li>
            <li>Google Earth will open and overlay the sampled households directly onto high-resolution 3D satellite imagery.</li>
            <li>This enables office-based validation of whether the selected point lands on a real building and assesses physical accessibility.</li>
        </ol>
        """

    # Generate table rows
    table_rows_html = ""
    for idx, row in village_details.iterrows():
        status_color = "#2ecc71" if row['Status'] == 'Target Achieved' or row['Status'] == 'Target Achieved' or 'Achieved' in row['Status'] or 'succ' in row['Status'].lower() else "#f1c40f"
        if row['Status'] == 'All Buildings Selected':
            status_color = "#3498db"
            
        table_rows_html += f"""
        <tr>
            <td><strong>{row['Village']}</strong></td>
            <td>{row['Available Buildings']}</td>
            <td>{row['Target']}</td>
            <td>{row['Sampled']}</td>
            <td>{row['Final Distance (m)']:.1f} m</td>
            <td><span style="background-color: {status_color}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.85em; font-weight: bold;">{row['Status']}</span></td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #2c3e50;
                line-height: 1.6;
                margin: 0;
                padding: 40px;
                background-color: #fcfcfc;
            }}
            .header {{
                border-bottom: 3px solid #1abc9c;
                padding-bottom: 20px;
                margin-bottom: 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .header h1 {{
                color: #1a5276;
                margin: 0 0 10px 0;
                font-size: 2.2em;
            }}
            .header .meta {{
                font-size: 0.9em;
                color: #7f8c8d;
            }}
            .section-title {{
                color: #1a5276;
                border-bottom: 1.5px solid #d5dbdb;
                padding-bottom: 8px;
                margin-top: 40px;
                margin-bottom: 20px;
                font-size: 1.4em;
            }}
            .card-container {{
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .card {{
                flex: 1;
                background: white;
                border: 1px solid #e5e8e8;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            }}
            .card .value {{
                font-size: 2.2em;
                font-weight: bold;
                color: #1abc9c;
                margin-top: 10px;
            }}
            .card .label {{
                font-size: 0.9em;
                color: #7f8c8d;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            }}
            th, td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #e5e8e8;
            }}
            th {{
                background-color: #1a5276;
                color: white;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 0.85em;
                letter-spacing: 0.5px;
            }}
            tr:hover {{
                background-color: #f8f9f9;
            }}
            .methodology-box {{
                background-color: #ebf5fb;
                border-left: 5px solid #3498db;
                padding: 15px 20px;
                border-radius: 4px;
                font-style: italic;
                margin-bottom: 30px;
            }}
            .guide-container {{
                display: flex;
                gap: 30px;
                margin-top: 20px;
            }}
            .guide-block {{
                flex: 1;
                background-color: #f4f6f7;
                padding: 20px;
                border-radius: 8px;
                border-top: 4px solid #1abc9c;
            }}
            .guide-block h4 {{
                margin-top: 0;
                color: #1a5276;
                font-size: 1.1em;
            }}
            .footer {{
                margin-top: 60px;
                text-align: center;
                font-size: 0.85em;
                color: #95a5a6;
                border-top: 1px solid #e5e8e8;
                padding-top: 20px;
            }}
            @media print {{
                body {{
                    background: white;
                    padding: 0;
                }}
                .guide-block {{
                    page-break-inside: avoid;
                }}
                tr {{
                    page-break-inside: avoid;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>{title}</h1>
                <div class="meta">{date_lbl} : {now_str} | Outil d'Échantillonnage Spatial Constraint</div>
            </div>
            <div style="font-size: 2.5em; color: #1abc9c;">🌍</div>
        </div>

        <div class="section-title">{methodology_title}</div>
        <div class="methodology-box">
            {methodology_desc}
        </div>

        <div class="section-title">{summary_title}</div>
        <div class="card-container">
            <div class="card">
                <div class="label">{summary_stats['label_vil']}</div>
                <div class="value" style="color: #1a5276;">{summary_stats['villages']}</div>
            </div>
            <div class="card">
                <div class="label">{summary_stats['label_bld']}</div>
                <div class="value" style="color: #7f8c8d;">{summary_stats['buildings']}</div>
            </div>
            <div class="card">
                <div class="label">{summary_stats['label_sampled']}</div>
                <div class="value" style="color: #1abc9c;">{summary_stats['sampled']}</div>
            </div>
            <div class="card">
                <div class="label">{summary_stats['label_success']}</div>
                <div class="value" style="color: #2ecc71;">{summary_stats['success_rate']:.1f}%</div>
            </div>
        </div>

        <div class="section-title">{details_title}</div>
        <table>
            <thead>
                <tr>
                    <th>{summary_stats['table_header_vil']}</th>
                    <th>{summary_stats['table_header_bld']}</th>
                    <th>{summary_stats['table_header_target']}</th>
                    <th>{summary_stats['table_header_sampled']}</th>
                    <th>{summary_stats['table_header_dist']}</th>
                    <th>{summary_stats['table_header_status']}</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
        </table>

        <div class="section-title">{instructions_title}</div>
        <div class="guide-container">
            <div class="guide-block">
                {osmand_guide_html}
            </div>
            <div class="guide-block">
                {ge_guide_html}
            </div>
        </div>

        <div class="footer">
            Conception : Pratisig Consulting Services • Assistance / Contact : Youssoupha Mbodji (pratisig.consulting@gmail.com) • Destiné aux équipes d'épidémiologie, d'enquête et de vaccination de terrain.
        </div>
    </body>
    </html>
    """
    return html_content


def create_results_zip(export_gdf, name_field, output_folder, summary_stats, village_details, lang):
    """
    Packs all outputs (Shapefile, GeoJSON, GPX exports, KML exports, Excel table, HTML report) into a single ZIP file in memory.
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        # 1. GeoJSON
        geojson_str = export_gdf.to_json()
        zip_file.writestr("geojson/echantillon_spatial.geojson", geojson_str)
        
        # 2. Shapefile (Temporary write and add to ZIP)
        with tempfile.TemporaryDirectory() as tmpdir:
            shp_path = os.path.join(tmpdir, "echantillon_spatial.shp")
            # Convert any object columns to string to prevent fiona errors
            gdf_shp = export_gdf.copy()
            for col in gdf_shp.columns:
                if col != 'geometry' and gdf_shp[col].dtype == 'object':
                    gdf_shp[col] = gdf_shp[col].astype(str)
            gdf_shp.to_file(shp_path, driver="ESRI Shapefile", engine="pyogrio")
            
            for file_name in os.listdir(tmpdir):
                file_path = os.path.join(tmpdir, file_name)
                zip_file.write(file_path, f"shapefile/{file_name}")
                
        # 3. GPX Folder
        gpx_files = save_gpx_by_village(export_gdf, name_field, output_folder)
        for fname, fpath in gpx_files:
            zip_file.write(fpath, f"gpx_exports/{fname}")
            
        # 4. KML Folder
        kml_files = save_kml_by_village(export_gdf, name_field, output_folder)
        for fname, fpath in kml_files:
            zip_file.write(fpath, f"kml_exports/{fname}")
            
        # 5. Excel Coordinate List
        excel_df = pd.DataFrame(export_gdf.drop(columns='geometry'))
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            excel_df.to_excel(writer, index=False, sheet_name="Echantillon")
        zip_file.writestr("coordonnees_echantillon.xlsx", excel_buffer.getvalue())
        
        # 6. HTML Summary Report
        html_report_content = generate_html_report(summary_stats, village_details, lang)
        zip_file.writestr("rapport_echantillonnage.html", html_report_content)
        
    return zip_buffer.getvalue()


# --- STREAMLIT MAIN APPLICATION ---

def main():
    # Detect language choice
    if 'lang' not in st.session_state:
        st.session_state.lang = 'fr' # Default to French
        
    # Language Toggle in Sidebar
    lang_sel = st.sidebar.selectbox(
        TRANSLATIONS[st.session_state.lang]['lang_selector'],
        options=["Français", "English"],
        index=0 if st.session_state.lang == 'fr' else 1
    )
    
    # Update Language in state
    new_lang = 'fr' if lang_sel == "Français" else 'en'
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
        
    lang = st.session_state.lang
    texts = TRANSLATIONS[lang]
    
    # Main Header
    st.title(texts['title'])
    st.caption(f"**{texts['subtitle']}**")
    
    # Intro/Description
    st.info(texts['intro_desc'])
    
    # Sidebar - Data source selection
    st.sidebar.header(f"📂 {texts['mode_selector']}")
    data_mode = st.sidebar.radio(
        "",
        options=[texts['real_data'], texts['sim_data']],
        index=0
    )
    
    # Initialize variables
    villages_df = None
    buildings_df = None
    is_simulation = data_mode == texts['sim_data']
    
    if is_simulation:
        st.sidebar.success("💡 Données de simulation activées.")
        villages_df, buildings_df = generate_simulated_data()
        st.sidebar.info(f"📍 Villages : {len(villages_df)} | Toîts : {len(buildings_df)}")
    else:
        # File uploaders for user's own data
        st.sidebar.subheader(f"🏠 {texts['load_bld']}")
        bld_file = st.sidebar.file_opener = st.sidebar.file_uploader(
            texts['load_bld'],
            type=['zip', 'geojson', 'gpkg', 'csv', 'xlsx', 'xls'],
            help=texts['load_bld_help']
        )
        
        st.sidebar.subheader(f"📍 {texts['load_vil']}")
        vil_file = st.sidebar.file_uploader(
            texts['load_vil'],
            type=['zip', 'geojson', 'gpkg', 'csv', 'xlsx', 'xls'],
            help=texts['load_vil_help']
        )
        
        if bld_file:
            buildings_df, bld_err = load_spatial_data(bld_file, bld_file.name, is_village=False)
            if bld_err:
                st.sidebar.error(bld_err)
            elif isinstance(buildings_df, pd.DataFrame) and not isinstance(buildings_df, gpd.GeoDataFrame):
                # Tabular file, need lat/lon mapping
                st.sidebar.warning("📊 Bâtiments : Fichier tabulaire détecté.")
                lat_col_bld = st.sidebar.selectbox(texts['bld_col_lat'], options=buildings_df.columns, key="lat_col_bld")
                lon_col_bld = st.sidebar.selectbox(texts['bld_col_lon'], options=buildings_df.columns, key="lon_col_bld")
                if lat_col_bld and lon_col_bld:
                    buildings_df = gpd.GeoDataFrame(
                        buildings_df,
                        geometry=gpd.points_from_xy(buildings_df[lon_col_bld], buildings_df[lat_col_bld]),
                        crs="EPSG:4326"
                    )
            elif isinstance(buildings_df, gpd.GeoDataFrame):
                st.sidebar.success(f"✅ Bâtiments chargés : {len(buildings_df)} points")
                
        if vil_file:
            villages_df, vil_err = load_spatial_data(vil_file, vil_file.name, is_village=True)
            if vil_err:
                st.sidebar.error(vil_err)
            elif isinstance(villages_df, pd.DataFrame) and not isinstance(villages_df, gpd.GeoDataFrame):
                st.sidebar.warning("📊 Villages : Fichier tabulaire détecté.")
                lat_col_vil = st.sidebar.selectbox(texts['vil_col_lat'], options=villages_df.columns, key="lat_col_vil")
                lon_col_vil = st.sidebar.selectbox(texts['vil_col_lon'], options=villages_df.columns, key="lon_col_vil")
                if lat_col_vil and lon_col_vil:
                    villages_df = gpd.GeoDataFrame(
                        villages_df,
                        geometry=gpd.points_from_xy(villages_df[lon_col_vil], villages_df[lat_col_vil]),
                        crs="EPSG:4326"
                    )
            elif isinstance(villages_df, gpd.GeoDataFrame):
                st.sidebar.success(f"✅ Villages chargés : {len(villages_df)} entités")
                
    # Proceed only if both datasets are successfully loaded
    if villages_df is not None and buildings_df is not None:
        
        # Select Village Name Field dynamically from loaded columns
        st.sidebar.subheader("🏷️ Attributs")
        name_fields = list(villages_df.columns)
        if 'geometry' in name_fields:
            name_fields.remove('geometry')
            
        # Try to pre-select a logical name column
        default_idx = 0
        name_candidates = ['nom_vill', 'nom', 'name', 'village', 'locality', 'localite', 'village_name', 'nom_village', 'site']
        for cand in name_candidates:
            cols_lower = [c.lower() for c in name_fields]
            if cand in cols_lower:
                default_idx = cols_lower.index(cand)
                break
                
        name_field = st.sidebar.selectbox(
            texts['vil_name_field'],
            options=name_fields,
            index=default_idx
        )
        
        # Sampling Parameters Section
        st.sidebar.header(f"🎯 {texts['params_header']}")
        
        # Check village geometry type
        geom_types = villages_df.geometry.geom_type.unique()
        is_polygon = any('Polygon' in t for t in geom_types)
        
        if not is_polygon:
            search_radius_m = st.sidebar.slider(
                texts['radius_lbl'],
                min_value=100,
                max_value=5000,
                value=1000,
                step=100,
                help=texts['radius_help']
            )
        else:
            search_radius_m = 1000.0 # Not used for polygons
            st.sidebar.info("💡 Polygones de village détectés. Les limites officielles seront utilisées à la place du rayon tampon.")
            
        min_dist_m = st.sidebar.slider(
            texts['dist_lbl'],
            min_value=0,
            max_value=300,
            value=25,
            step=5,
            help=texts['dist_help']
        )
        
        sampling_method = st.sidebar.selectbox(
            texts['method_lbl'],
            options=[texts['fixed_method'], texts['percent_method'], texts['total_method']]
        )
        
        # Configure sample value input based on selected method
        if sampling_method == texts['fixed_method']:
            sample_val = st.sidebar.number_input(texts['sample_val_lbl'], min_value=1, max_value=500, value=15, step=1)
        elif sampling_method == texts['percent_method']:
            sample_val = st.sidebar.slider(texts['sample_val_lbl'] + " (%)", min_value=1, max_value=100, value=10, step=1)
        else:
            sample_val = st.sidebar.number_input(texts['sample_val_lbl'] + " (Total Global)", min_value=10, max_value=10000, value=100, step=10)
            
        relax_constraint = st.sidebar.checkbox(
            texts['relax_lbl'],
            value=True,
            help=texts['relax_help']
        )
        
        # Target Map Display Config (Performance Optimization)
        st.sidebar.subheader("🎨 Affichage de la Carte")
        show_bld_on_map = st.sidebar.checkbox("Afficher les bâtiments de fond / Show buildings", value=True, help="Décochez cette case pour rendre les cartes extrêmement rapides si vos fichiers contiennent des milliers de points.")
        if show_bld_on_map:
            max_bld_display = st.sidebar.slider(
                "Max bâtiments de fond à afficher",
                min_value=100,
                max_value=5000,
                value=1000,
                step=100,
                help="Limite le nombre de points affichés en arrière-plan pour maintenir la fluidité de la carte."
            )
        else:
            max_bld_display = 0

        # Target Output Folder Config
        st.sidebar.subheader("💾 Options d'enregistrement")
        output_folder_path = st.sidebar.text_input(
            texts['out_path_lbl'],
            value="./outputs"
        )
        
        # Section À Propos & Assistance dans la barre latérale
        st.sidebar.write("---")
        with st.sidebar.expander("ℹ️ À propos & Assistance / Help & Support", expanded=False):
            st.markdown("""
            **Outil d'Échantillonnage Spatial des Ménages**
            
            * **Conception** : Pratisig Consulting Services
            * **Assistance & Support** : Youssoupha Mbodji
            * **Email** : [pratisig.consulting@gmail.com](mailto:pratisig.consulting@gmail.com)
            
            *Développé pour appuyer les équipes d'épidémiologie et de santé publique sur le terrain sans dépendances ArcGIS.*
            """)
            
        # Run Calculation Trigger
        run_sampling = st.sidebar.button(
            texts['run_btn'],
            use_container_width=True,
            type="primary"
        )
        
        if run_sampling or 'last_results' in st.session_state:
            # Check if calculation needs to be run
            if run_sampling:
                with st.spinner("Traitement spatial en cours... / Processing spatial data..."):
                    # 1. Determine optimal metric projection
                    utm_epsg = get_utm_epsg(villages_df)
                    
                    # 2. Delineate Catchment Areas
                    catchments_utm = create_catchment_polygons(
                        villages_df,
                        search_radius_m,
                        name_field,
                        utm_epsg
                    )
                    
                    # 3. Project buildings to UTM
                    buildings_utm = buildings_df.to_crs(epsg=utm_epsg)
                    
                    # 4. Spatial Join to associate each building with its corresponding village catchment
                    bld_with_village_utm = gpd.sjoin(
                        buildings_utm,
                        catchments_utm[[name_field, 'geometry']],
                        how="inner",
                        predicate="intersects"
                    )
                    
                    # Remove spatial join index columns to avoid confusion
                    if 'index_right' in bld_with_village_utm.columns:
                        bld_with_village_utm = bld_with_village_utm.drop(columns='index_right')
                        
                    # Calculate buildings per village
                    building_counts = bld_with_village_utm.groupby(name_field).size().to_dict()
                    
                    # 5. Determine Sample Sizes per Village
                    village_targets = {}
                    all_villages = list(catchments_utm[name_field].unique())
                    
                    if sampling_method == texts['fixed_method']:
                        for v in all_villages:
                            village_targets[v] = int(sample_val)
                    elif sampling_method == texts['percent_method']:
                        for v in all_villages:
                            n_bld = building_counts.get(v, 0)
                            village_targets[v] = max(1, int(round(n_bld * sample_val / 100.0)))
                    else: # Proportional Allocation
                        total_buildings_in_catchments = sum(building_counts.values())
                        if total_buildings_in_catchments > 0:
                            for v in all_villages:
                                n_bld = building_counts.get(v, 0)
                                proportional_val = sample_val * (n_bld / total_buildings_in_catchments)
                                village_targets[v] = max(1, int(round(proportional_val)))
                        else:
                            for v in all_villages:
                                village_targets[v] = 1
                                
                    # 6. Perform Spatial Constrained Sampling
                    sampled_subsets = []
                    village_sampling_details = []
                    
                    for v_name, group in bld_with_village_utm.groupby(name_field):
                        target_size = village_targets.get(v_name, 10)
                        n_avail = len(group)
                        
                        sampled_group = sample_village_buildings(
                            group,
                            target_size,
                            min_dist_m,
                            name_field,
                            relax_constraint
                        )
                        
                        if len(sampled_group) > 0:
                            sampled_subsets.append(sampled_group)
                            final_dist = sampled_group['actual_dist_constraint'].iloc[0]
                            status = sampled_group['sampling_status'].iloc[0]
                            n_sampled = len(sampled_group)
                        else:
                            final_dist = 0.0
                            status = 'No Buildings Sampled'
                            n_sampled = 0
                            
                        village_sampling_details.append({
                            'Village': v_name,
                            'Available Buildings': n_avail,
                            'Target': target_size,
                            'Sampled': n_sampled,
                            'Final Distance (m)': final_dist,
                            'Status': status
                        })
                        
                    # Handle villages with 0 buildings inside catchment
                    for v_name in all_villages:
                        if v_name not in building_counts:
                            st.warning(texts['no_bld_in_vil'].format(vil=v_name))
                            village_sampling_details.append({
                                'Village': v_name,
                                'Available Buildings': 0,
                                'Target': village_targets.get(v_name, 10),
                                'Sampled': 0,
                                'Final Distance (m)': 0.0,
                                'Status': '0 buildings in area'
                            })
                            
                    # Combine all sampled subsets
                    if sampled_subsets:
                        sampled_all_utm = gpd.GeoDataFrame(
                            pd.concat(sampled_subsets, ignore_index=True),
                            crs=f"EPSG:{utm_epsg}"
                        )
                        
                        # Project back to WGS84 for display and GPX/KML
                        sampled_all_wgs84 = sampled_all_utm.to_crs(epsg=4326)
                        catchments_wgs84 = catchments_utm.to_crs(epsg=4326)
                        
                        # Prepare attributes for final Shapefile / GeoJSON export (truncation protection)
                        export_gdf = gpd.GeoDataFrame(sampled_all_wgs84.copy())
                        export_gdf['lat'] = export_gdf.geometry.y
                        export_gdf['lon'] = export_gdf.geometry.x
                        
                        # Standardize columns to under 10 chars
                        if name_field != 'vil_name':
                            export_gdf['vil_name'] = export_gdf[name_field].astype(str)
                        if 'actual_dist_constraint' in export_gdf.columns:
                            export_gdf['dist_m'] = export_gdf['actual_dist_constraint']
                            
                        # Unique point ID generator per village
                        point_ids = []
                        village_counts = {}
                        for idx, row in export_gdf.iterrows():
                            v_name = str(row[name_field])
                            safe_v = "".join([c if c.isalnum() else "_" for c in v_name])[:5].upper()
                            village_counts[v_name] = village_counts.get(v_name, 0) + 1
                            point_ids.append(f"{safe_v}_{village_counts[v_name]:02d}")
                        export_gdf['pt_id'] = point_ids
                        
                        # Filter to essential export fields
                        cols_to_keep = ['geometry', 'pt_id', 'vil_name', 'lat', 'lon', 'dist_m', 'sampling_status']
                        # Keep any short original attributes
                        for col in export_gdf.columns:
                            if col not in cols_to_keep and len(col) <= 10 and col != 'geometry':
                                cols_to_keep.append(col)
                        export_gdf = export_gdf[cols_to_keep]
                        
                        # Save to session state to prevent lost calculations on reruns
                        st.session_state.last_results = {
                            'sampled_wgs84': sampled_all_wgs84,
                            'catchments_wgs84': catchments_wgs84,
                            'export_gdf': export_gdf,
                            'village_details': pd.DataFrame(village_sampling_details),
                            'utm_epsg': utm_epsg,
                            'building_counts': building_counts
                        }
                    else:
                        st.error("❌ Aucun point n'a pu être échantillonné. Vérifiez vos contraintes de distance ou vos couches.")
                        return
            
            # Retrieve processed results from session state
            results = st.session_state.last_results
            sampled_all_wgs84 = results['sampled_wgs84']
            catchments_wgs84 = results['catchments_wgs84']
            export_gdf = results['export_gdf']
            vil_details_df = results['village_details']
            building_counts = results['building_counts']
            
            # Calculate summary metrics
            tot_villages = len(vil_details_df)
            tot_bld = sum(building_counts.values())
            tot_sampled = len(export_gdf)
            achieved_targets = len(vil_details_df[vil_details_df['Status'] == 'Target Achieved'])
            success_rate = (achieved_targets / tot_villages) * 100 if tot_villages > 0 else 0
            
            # Calc actual average spacing
            avg_spacing = export_gdf['dist_m'].mean() if 'dist_m' in export_gdf.columns else min_dist_m
            
            # Write files to LOCAL directory (as requested)
            os.makedirs(output_folder_path, exist_ok=True)
            
            # Save Shapefile folder
            shp_folder = os.path.join(output_folder_path, "shapefile")
            os.makedirs(shp_folder, exist_ok=True)
            shp_out_path = os.path.join(shp_folder, "echantillon_spatial.shp")
            # Convert object columns to str to satisfy fiona
            gdf_shp = export_gdf.copy()
            for col in gdf_shp.columns:
                if col != 'geometry' and gdf_shp[col].dtype == 'object':
                    gdf_shp[col] = gdf_shp[col].astype(str)
            gdf_shp.to_file(shp_out_path, driver="ESRI Shapefile", engine="pyogrio")
            
            # Save GeoJSON
            geojson_folder = os.path.join(output_folder_path, "geojson")
            os.makedirs(geojson_folder, exist_ok=True)
            export_gdf.to_file(os.path.join(geojson_folder, "echantillon_spatial.geojson"), driver="GeoJSON", engine="pyogrio")
            
            # Save GPX and KML folders
            save_gpx_by_village(export_gdf, 'vil_name', output_folder_path)
            save_kml_by_village(export_gdf, 'vil_name', output_folder_path)
            
            # Save Excel List
            excel_path = os.path.join(output_folder_path, "coordonnees_echantillon.xlsx")
            excel_df = pd.DataFrame(export_gdf.drop(columns='geometry'))
            excel_df.to_excel(excel_path, index=False, engine='openpyxl')
            
            # Save HTML Report
            summary_stats = {
                'villages': tot_villages,
                'buildings': tot_bld,
                'sampled': tot_sampled,
                'success_rate': success_rate,
                'label_vil': texts['metric_villages'],
                'label_bld': texts['metric_buildings'],
                'label_sampled': texts['metric_sampled'],
                'label_success': texts['metric_success'],
                'table_header_vil': texts['table_vil'],
                'table_header_bld': texts['table_bld'],
                'table_header_target': texts['table_target'],
                'table_header_sampled': texts['table_sampled'],
                'table_header_dist': texts['table_dist'],
                'table_header_status': texts['table_status']
            }
            html_content = generate_html_report(summary_stats, vil_details_df, lang)
            report_path = os.path.join(output_folder_path, "rapport_echantillonnage.html")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            # Local Save Confirmation Alert
            st.sidebar.success(f"{texts['save_success']} `{os.path.abspath(output_folder_path)}`")
            
            # Summary Metrics Display Row
            st.subheader(texts['summary_hdr'])
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric(texts['metric_villages'], f"{tot_villages}")
            with col2:
                st.metric(texts['metric_buildings'], f"{tot_bld:,}")
            with col3:
                st.metric(texts['metric_sampled'], f"{tot_sampled}")
            with col4:
                st.metric(texts['metric_success'], f"{success_rate:.1f}%")
            with col5:
                st.metric(texts['metric_avg_dist'], f"{avg_spacing:.1f} m")
                    
            # Split Layout: Left for Details Table, Right for Map
            left_col, right_col = st.columns([2, 3])
            
            with left_col:
                st.subheader(f"📋 {texts['sampling_details']}")
                st.dataframe(
                    vil_details_df.style.map(
                        lambda val: "background-color: #d4efdf; color: #196f3d;" if "Achieved" in str(val) or "Selected" in str(val) else "background-color: #fcf3cf; color: #7d6608;",
                        subset=['Status']
                    ),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download ZIP Button for Browser Users
                st.subheader(texts['download_hdr'])
                zip_bytes = create_results_zip(
                    export_gdf,
                    'vil_name',
                    output_folder_path,
                    summary_stats,
                    vil_details_df,
                    lang
                )
                st.download_button(
                    label=f"📥 {texts['download_btn']}",
                    data=zip_bytes,
                    file_name="echantillon_spatial_complet.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
            with right_col:
                st.subheader(texts['map_title'])
                st.caption(texts['map_help'])
                
                # Calculate geographical center of selected households
                center_lat = export_gdf['lat'].mean()
                center_lon = export_gdf['lon'].mean()
                
                # Initialize Folium Map (or load from session state to persist zoom/pan)
                if 'map_center' not in st.session_state:
                    st.session_state['map_center'] = [center_lat, center_lon]
                if 'map_zoom' not in st.session_state:
                    st.session_state['map_zoom'] = 12
                    
                m = folium.Map(location=st.session_state['map_center'], zoom_start=st.session_state['map_zoom'])
                
                # Add Alternative Tile Layers (Basemaps)
                folium.TileLayer(
                    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                    attr="Esri World Imagery (Satellite)",
                    name="Image Satellite (Esri Sat)",
                    overlay=False
                ).add_to(m)
                
                folium.TileLayer(
                    tiles="OpenStreetMap",
                    name="Plan de Ville (OSM)",
                    overlay=False
                ).add_to(m)
                
                # Add Catchment Areas Layer
                catchments_layer = folium.FeatureGroup(name="Zones d'Influence (Catchments)", show=True)
                colors = ['#16a085', '#2980b9', '#8e44ad', '#d35400', '#c0392b', '#27ae60']
                
                for idx, row in catchments_wgs84.iterrows():
                    v_name = row[name_field]
                    color = colors[idx % len(colors)]
                    
                    # Highlight boundary style
                    style_fn = lambda x, col=color: {
                        'fillColor': col,
                        'color': col,
                        'fillOpacity': 0.18,
                        'weight': 2.5,
                        'dashArray': '4, 4'
                    }
                    
                    folium.GeoJson(
                        row.geometry,
                        style_function=style_fn,
                        tooltip=f"Village : {v_name}"
                    ).add_to(catchments_layer)
                catchments_layer.add_to(m)
                
                # Add All Buildings Layer (Clustered or circle markers for speed)
                bld_layer = folium.FeatureGroup(name="Tous les Bâtiments", show=False)
                marker_cluster = MarkerCluster(options={'maxClusterRadius': 40}).add_to(bld_layer)
                
                # Optimisation de la performance en fonction des choix utilisateur
                if show_bld_on_map and max_bld_display > 0:
                    buildings_wgs84 = buildings_df.to_crs(epsg=4326)
                    display_bld = buildings_wgs84.sample(min(max_bld_display, len(buildings_wgs84)))
                    
                    for _, row in display_bld.iterrows():
                        p = row.geometry
                        folium.CircleMarker(
                            location=[p.y, p.x],
                            radius=2,
                            color="#7f8c8d",
                            fill=True,
                            fill_color="#7f8c8d",
                            fill_opacity=0.6,
                            popup="Bâtiment"
                        ).add_to(marker_cluster)
                bld_layer.add_to(m)
                
                # Add Sampled Households (Red custom pins)
                sampled_layer = folium.FeatureGroup(name="Ménages Échantillonnés (Grappes)", show=True)
                for _, row in export_gdf.iterrows():
                    p = row.geometry
                    folium.Marker(
                        location=[p.y, p.x],
                        popup=folium.Popup(f"""
                        <div style='font-family: Arial, sans-serif; font-size: 13px; line-height: 1.4;'>
                            <b style='color: #1a5276; font-size: 14px;'>📍 {row['pt_id']}</b><br>
                            <b>Village :</b> {row['vil_name']}<br>
                            <b>Coordonnées :</b> {row['lat']:.6f}, {row['lon']:.6f}<br>
                            <b>Distance Spacing :</b> {row['dist_m']:.1f} m<br>
                            <span style='color: #27ae60; font-weight: bold;'>{row['sampling_status']}</span>
                        </div>
                        """, max_width=250),
                        icon=folium.Icon(color="red", icon="home", prefix="fa"),
                        tooltip=f"{row['pt_id']} ({row['vil_name']})"
                    ).add_to(sampled_layer)
                sampled_layer.add_to(m)
                
                # Add Controls
                folium.LayerControl(collapsed=False).add_to(m)
                
                # Ajout des outils de sélection et d'édition (Leaflet Draw) directement sur la carte !
                from folium.plugins import Draw
                draw_tool = Draw(
                    export=False,
                    position='topleft',
                    draw_options={
                        'polyline': False,
                        'polygon': False,
                        'circle': False,
                        'rectangle': False,
                        'circlemarker': False,
                        'marker': True # Permet de placer un nouveau point cible sur la carte
                    },
                    edit_options={
                        'edit': False,
                        'remove': True # Permet d'effacer les dessins
                    }
                )
                draw_tool.add_to(m)
                
                # Render Map in Streamlit
                # Gestion robuste de l'affichage de la carte sous forme d'exécutable compilé
                if getattr(sys, 'frozen', False):
                    from streamlit_folium import folium_static
                    folium_static(m, height=550)
                    st.info("💡 **Mode Exécutable Portable** : Pour déplacer un point de l'échantillon, saisissez ses coordonnées directement dans l'Option 2 de l'outil d'édition ci-dessous. En mode standard (script .bat), le clic direct sur la carte satellite est activé.")
                else:
                    # Rendu ultra-fluide avec conservation dynamique du centrage et du zoom !
                    map_data = st_folium(m, use_container_width=True, height=550, key="sampling_map", returned_objects=["last_clicked", "all_drawings"])
                    
# Zoom and center state is managed dynamically based on selection and click events
                    
                    # Initialisation sécurisée du mode de clic
                    if 'map_click_mode' not in st.session_state:
                        st.session_state['map_click_mode'] = 'select'
                    
                    # 1. Détecter si l'utilisateur a dessiné un point cible sur la carte avec l'outil de dessin Leaflet
                    if map_data and map_data.get('all_drawings'):
                        drawings = map_data['all_drawings']
                        if drawings:
                            last_drawing = drawings[-1]
                            if last_drawing.get('geometry') and last_drawing['geometry'].get('type') == 'Point':
                                draw_lon, draw_lat = last_drawing['geometry']['coordinates']
                                # Si cette coordonnée de dessin est différente de la dernière gérée, on l'applique
                                if st.session_state.get('last_handled_drawing_coords') != (draw_lat, draw_lon):
                                    st.session_state['last_handled_drawing_coords'] = (draw_lat, draw_lon)
                                    st.session_state['map_click'] = (draw_lat, draw_lon)
                                    st.session_state['map_center'] = [draw_lat, draw_lon]
                                    st.session_state['map_zoom'] = 18
                                    st.toast(f"🎯 Cible de repositionnement définie par l'outil de dessin sur la carte !", icon="🎯")
                                    st.rerun()
                    
                    # 2. Gestionnaire de clic unifié (Sélection et Repositionnement guidé par clic simple)
                    if map_data and map_data.get('last_clicked'):
                        click_coords = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
                        if st.session_state.get('last_handled_click') != click_coords:
                            st.session_state['last_handled_click'] = click_coords
                            
                            lat_clicked, lon_clicked = click_coords
                            
                            if st.session_state.get('map_click_mode') == 'select':
                                # Mode Sélection : Trouver le point le plus proche (rayon d'attraction de 250m)
                                dists_m = np.sqrt(
                                    ((export_gdf['lat'] - lat_clicked) * 111000)**2 + 
                                    ((export_gdf['lon'] - lon_clicked) * 111000 * np.cos(np.radians(lat_clicked)))**2
                                )
                                min_idx = dists_m.idxmin()
                                min_dist = dists_m[min_idx]
                                
                                if min_dist < 250.0:
                                    clicked_pt_id = export_gdf.loc[min_idx, 'pt_id']
                                    st.session_state['selected_pt_id'] = clicked_pt_id
                                    # Centrer automatiquement la carte sur le point sélectionné
                                    st.session_state['map_center'] = [lat_clicked, lon_clicked]
                                    st.session_state['map_zoom'] = 18
                                    # Basculer automatiquement en mode repositionnement !
                                    st.session_state['map_click_mode'] = 'move'
                                    st.toast(f"📍 Point `{clicked_pt_id}` sélectionné ! Vous pouvez cliquer sur la carte ou utiliser l'outil de dessin (icône repère) pour définir sa cible.", icon="📍")
                                    st.rerun()
                                else:
                                    st.toast("💡 Aucun point à proximité. Cliquez plus près d'un point rouge, ou utilisez la boîte de sélection ci-dessous.", icon="ℹ️")
                            else:
                                # Mode Repositionnement : Aucune contrainte de distance, définit la position exacte
                                st.session_state['map_click'] = click_coords
                                # Conserver le cadrage de carte sur la cible
                                st.session_state['map_center'] = [lat_clicked, lon_clicked]
                                st.session_state['map_zoom'] = 18
                                st.toast(f"🎯 Position cible définie pour `{st.session_state.get('selected_pt_id')}` !", icon="🎯")
                                st.rerun()
            
                        # Outil d'Édition et de Repositionnement Manuel
            st.write("---")
            with st.expander("✍️ Outil d'Édition : Repositionnement Manuel des Points / Point Repositioning Tool", expanded=False):
                st.markdown("""
                **Cet outil vous permet d'ajuster manuellement la position des points échantillonnés si certains ne tombent pas sur de vrais toits de bâtiments (visibles sur l'imagerie satellite d'Esri).**
                
                **Instructions :**
                1. Sélectionnez dans le menu déroulant ci-dessous le point que vous souhaitez déplacer (ex: `YOFF_01`).
                2. Cliquez n'importe où sur la carte satellite ci-dessus à l'endroit exact où vous souhaitez placer ce point.
                3. Les coordonnées cliquées s'afficheront ci-dessous. Cliquez sur le bouton vert **"Déplacer le point ici"** pour appliquer le déplacement.
                """)
                
                # Sélecteur de mode de clic interactif et visuel
                if 'map_click_mode' not in st.session_state:
                    st.session_state['map_click_mode'] = 'select'
                
                st.write("👉 **Mode d'interaction actuel sur la carte :**")
                click_mode = st.radio(
                    "Mode d'interaction",
                    options=["Selection", "Deplacement"],
                    format_func=lambda x: "📍 Sélectionner un point (cliquez près d'un point rouge sur la carte)" if x == "Selection" else "🎯 Définir la position cible (cliquez sur le toit réel du bâtiment)",
                    index=0 if st.session_state['map_click_mode'] == 'select' else 1,
                    horizontal=True,
                    label_visibility="collapsed"
                )
                mapped_mode = 'select' if click_mode == "Selection" else 'move'
                if mapped_mode != st.session_state['map_click_mode']:
                    st.session_state['map_click_mode'] = mapped_mode
                    st.rerun()
                
                pt_ids = list(export_gdf['pt_id'].unique())
                
                # Initialiser selected_pt_id dans l'état de session si manquant
                if 'selected_pt_id' not in st.session_state or st.session_state['selected_pt_id'] not in pt_ids:
                    st.session_state['selected_pt_id'] = pt_ids[0] if pt_ids else None
                    
                # Déterminer l'index correspondant
                default_idx = pt_ids.index(st.session_state['selected_pt_id']) if st.session_state['selected_pt_id'] in pt_ids else 0
                
                selected_pt = st.selectbox(
                    "Sélectionnez le point à déplacer / Select point to move", 
                    options=pt_ids,
                    index=default_idx
                )
                
                # Mettre à jour l'état de session en cas de changement manuel de la boîte de sélection (et centrer la carte au zoom 18)
                if selected_pt != st.session_state['selected_pt_id']:
                    st.session_state['selected_pt_id'] = selected_pt
                    pt_row = export_gdf[export_gdf['pt_id'] == selected_pt].iloc[0]
                    st.session_state['map_center'] = [pt_row['lat'], pt_row['lon']]
                    st.session_state['map_zoom'] = 18
                    st.session_state['map_click_mode'] = 'move' # Basculer directement en mode repositionnement !
                    st.rerun()
                
                # Find current row
                pt_row = export_gdf[export_gdf['pt_id'] == selected_pt].iloc[0]
                current_lat = pt_row['lat']
                current_lon = pt_row['lon']
                
                st.write(f"📍 **Position actuelle de `{selected_pt}`** : Latitude `{current_lat:.6f}` | Longitude `{current_lon:.6f}`")
                
                col_edit1, col_edit2 = st.columns(2)
                
                with col_edit1:
                    st.markdown("#### Option 1 : Repositionner par clic sur la carte")
                    if 'map_click' in st.session_state and st.session_state['map_click'] is not None:
                        clicked_lat, clicked_lon = st.session_state['map_click']
                        st.success(f"🎯 **Coordonnées cliquées sur la carte** : Latitude `{clicked_lat:.6f}` | Longitude `{clicked_lon:.6f}`")
                        
                        if st.button(f"👉 Déplacer `{selected_pt}` ici", type="primary", key="btn_move_click"):
                            idx_to_update = export_gdf[export_gdf['pt_id'] == selected_pt].index[0]
                            
                            # Update export_gdf
                            export_gdf.at[idx_to_update, 'geometry'] = Point(clicked_lon, clicked_lat)
                            export_gdf.at[idx_to_update, 'lat'] = clicked_lat
                            export_gdf.at[idx_to_update, 'lon'] = clicked_lon
                            export_gdf.at[idx_to_update, 'sampling_status'] = 'Repositionné manuellement / Manually repositioned'
                            
                            # Update sampled_wgs84
                            sampled_all_wgs84.at[idx_to_update, 'geometry'] = Point(clicked_lon, clicked_lat)
                            
                            # Save back to session state
                            st.session_state.last_results['export_gdf'] = export_gdf
                            st.session_state.last_results['sampled_wgs84'] = sampled_all_wgs84
                            
                            st.toast(f"Point {selected_pt} déplacé avec succès !", icon="✅")
                            # Centrer la carte sur la nouvelle position et repasser en mode Sélection
                            st.session_state['map_center'] = [clicked_lat, clicked_lon]
                            st.session_state['map_zoom'] = 18
                            st.session_state['map_click_mode'] = 'select'
                            # Clear map click
                            st.session_state['map_click'] = None
                            st.rerun()
                    else:
                        st.info("💡 Cliquez n'importe où sur la carte ci-dessus pour sélectionner un nouvel emplacement pour ce point.")
                        
                with col_edit2:
                    st.markdown("#### Option 2 : Repositionner par saisie manuelle")
                    manual_lat = st.number_input("Nouvelle Latitude", value=float(current_lat), format="%.6f", key="man_lat")
                    manual_lon = st.number_input("Nouvelle Longitude", value=float(current_lon), format="%.6f", key="man_lon")
                    
                    if st.button("💾 Enregistrer la saisie manuelle", key="btn_move_manual"):
                        idx_to_update = export_gdf[export_gdf['pt_id'] == selected_pt].index[0]
                        
                        # Update export_gdf
                        export_gdf.at[idx_to_update, 'geometry'] = Point(manual_lon, manual_lat)
                        export_gdf.at[idx_to_update, 'lat'] = manual_lat
                        export_gdf.at[idx_to_update, 'lon'] = manual_lon
                        export_gdf.at[idx_to_update, 'sampling_status'] = 'Repositionné manuellement / Manually repositioned'
                        
                        # Update sampled_wgs84
                        sampled_all_wgs84.at[idx_to_update, 'geometry'] = Point(manual_lon, manual_lat)
                        
                        st.session_state.last_results['export_gdf'] = export_gdf
                        st.session_state.last_results['sampled_wgs84'] = sampled_all_wgs84
                        
                        st.toast(f"Point {selected_pt} mis à jour !", icon="💾")
                        # Centrer la carte sur la position saisie et repasser en mode Sélection
                        st.session_state['map_center'] = [manual_lat, manual_lon]
                        st.session_state['map_zoom'] = 18
                        st.session_state['map_click_mode'] = 'select'
                        st.rerun()

            # Deployment & User Instructions at the Bottom
            st.write("---")
            instr_col1, instr_col2 = st.columns(2)
            with instr_col1:
                st.subheader(texts['osmand_guide'])
                st.markdown(texts['osmand_steps'])
            with instr_col2:
                st.subheader(texts['google_earth_guide'])
                st.markdown(texts['google_earth_steps'])
                
            # Bas de page officiel Pratisig
            st.write("---")
            st.markdown(
                "<div style='text-align: center; color: #7f8c8d; font-size: 0.9em; padding: 20px 10px 10px 10px;'>"
                "Conception : <b>Pratisig Consulting Services</b> &nbsp;•&nbsp; Assistance / Contact : "
                "<b>Youssoupha Mbodji</b> (<a href='mailto:pratisig.consulting@gmail.com'>pratisig.consulting@gmail.com</a>)"
                "</div>",
                unsafe_allow_html=True
            )
                
        else:
            # Preview map when data is loaded but sampling has not run yet
            left_p, right_p = st.columns([2, 3])
            
            with left_p:
                st.subheader("👉 Prêt pour l'échantillonnage !")
                st.markdown(f"""
                ### Données chargées avec succès :
                * **Couche des Villages / Localités** : `{len(villages_df)}` entités chargées.
                * **Couche des Bâtiments / Toîts** : `{len(buildings_df)}` points chargés.
                
                ---
                
                ### Instructions :
                1. **Vérifiez vos données** de départ sur la carte de droite. Les points de village et les bâtiments y sont représentés.
                2. **Sélectionnez le champ de nom** des villages dans la barre latérale gauche (sous "Attributs").
                3. **Réglez vos paramètres** (rayon de recherche, distance minimale de sécurité, méthode d'allocation).
                4. **Cliquez sur le bouton rouge 'Lancer l'Échantillonnage Spatial'** dans la barre latérale pour générer votre échantillon.
                """)
                
            with right_p:
                st.subheader("🗺️ Carte de Prévisualisation des Données Brutes")
                st.caption("Cette carte affiche la position réelle de vos villages et bâtiments d'origine pour vérifier leur superposition.")
                
                # Center map on villages centroid
                v_centroid = villages_df.geometry.union_all().centroid
                m_preview = folium.Map(location=[v_centroid.y, v_centroid.x], zoom_start=12)
                
                # Add Satellite and OSM
                folium.TileLayer(
                    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                    attr="Esri World Imagery (Satellite)",
                    name="Image Satellite (Esri Sat)",
                    overlay=False
                ).add_to(m_preview)
                
                folium.TileLayer(
                    tiles="OpenStreetMap",
                    name="Plan de Ville (OSM)",
                    overlay=False
                ).add_to(m_preview)
                
                # Show villages
                vil_layer = folium.FeatureGroup(name="Villages d'Origine", show=True)
                for idx, row in villages_df.iterrows():
                    p = row.geometry
                    if p is not None:
                        v_name = str(row[name_field]) if name_field in villages_df.columns else f"Village {idx+1}"
                        if p.geom_type == 'Point' and hasattr(p, 'y') and hasattr(p, 'x'):
                            folium.Marker(
                                location=[p.y, p.x],
                                tooltip=v_name,
                                icon=folium.Icon(color="blue", icon="info-sign")
                            ).add_to(vil_layer)
                    else: # Polygon
                        folium.GeoJson(
                            p,
                            tooltip=v_name,
                            style_function=lambda x: {'fillColor': '#3498db', 'color': '#2980b9', 'weight': 2, 'fillOpacity': 0.2}
                        ).add_to(vil_layer)
                vil_layer.add_to(m_preview)
                
                # Show buildings in a cluster for speed
                bld_layer = folium.FeatureGroup(name="Tous les Bâtiments", show=True)
                marker_cluster_preview = MarkerCluster(options={'maxClusterRadius': 45}).add_to(bld_layer)
                
                # Optimisation de la performance de prévisualisation (Sécurisée contre les géométries nulles)
                if show_bld_on_map and max_bld_display > 0:
                    display_bld_prev = buildings_df.sample(min(max_bld_display, len(buildings_df)))
                    for _, row in display_bld_prev.iterrows():
                        p = row.geometry
                        if p is not None and hasattr(p, 'y') and hasattr(p, 'x'):
                            folium.CircleMarker(
                                location=[p.y, p.x],
                                radius=2,
                                color="#7f8c8d",
                                fill=True,
                                fill_color="#7f8c8d",
                                fill_opacity=0.6,
                                popup="Bâtiment"
                            ).add_to(marker_cluster_preview)
                bld_layer.add_to(m_preview)
                
                folium.LayerControl(collapsed=False).add_to(m_preview)
                
                # Render preview map
                if getattr(sys, 'frozen', False):
                    from streamlit_folium import folium_static
                    folium_static(m_preview, height=500)
                else:
                    st_folium(m_preview, use_container_width=True, height=500, key="preview_map", returned_objects=[])

    else:
        # Prompt user to load datasets in sidebar
        st.warning(f"👈 {texts['sel_village_warning']}")
        
        # Display sample dashboard image or simulated map info as a placeholder
        st.info("💡 **Astuce / Tip** : Pour tester l'outil immédiatement sans données, cochez l'option **'Générer des données de simulation'** dans la barre latérale gauche !")

if __name__ == '__main__':
    main()
