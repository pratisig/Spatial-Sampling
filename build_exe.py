# -*- coding: utf-8 -*-
"""
Script d'automatisation de la compilation de l'application en exécutable Windows (.exe)
Utilise PyInstaller pour générer un dossier autonome portable.
Conception : Pratisig Consulting Services

SÉCURITÉ ENCODAGE WINDOWS / GITHUB ACTIONS :
Tous les caractères emoji spéciaux (Unicode) ont été supprimés des print() console 
pour éviter les erreurs 'UnicodeEncodeError' (cp1252/cp850) lors de la compilation
dans l'environnement cloud Windows de GitHub Actions.
"""

import os
import sys
import subprocess
import shutil
import zipfile


# Fichiers/dossiers à inclure dans le ZIP "source portable" (avec lanceur .bat).
SOURCE_ZIP_FILES = [
    "app.py",
    "run_app.py",
    "offline_folium.py",
    "requirements.txt",
    "Lancer_Application.bat",
    "README.md",
    "Guide_Utilisation_Echantillonnage.md",
    "Manuel_Methodologique_Echantillonnage.md",
]
SOURCE_ZIP_DIRS = [
    "assets",
    "tools",
]


def create_source_portable_zip():
    """
    Crée un second livrable : un ZIP "source portable" destiné aux machines
    QUI ONT Python installé. On le lance via Lancer_Application.bat (qui crée
    un .venv local et installe les dépendances), sans avoir besoin du .exe.
    """
    out_path = os.path.join("dist", "Echantillon_Spatial_Source_Portable.zip")
    print()
    print("[ZIP] Creation du ZIP 'source portable' avec lanceur .bat...")
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in SOURCE_ZIP_FILES:
            if os.path.isfile(fname):
                zf.write(fname, fname)
                print(f"   + {fname}")
        for d in SOURCE_ZIP_DIRS:
            if os.path.isdir(d):
                for root, _, files in os.walk(d):
                    for f in files:
                        full = os.path.join(root, f)
                        # Ignorer les éventuels caches
                        if "__pycache__" in root or f.endswith(".pyc"):
                            continue
                        zf.write(full, full)
                print(f"   + {d}/ (arborescence)")
    print(f"   [OK] {out_path}")
    return out_path


def main():
    print("==========================================================")
    print("   [BUILD] SCRIPT DE COMPILATION EN EXECUTABLE WINDOWS     ")
    print("==========================================================")
    print()
    
    # 1. Installer PyInstaller si non disponible
    try:
        import PyInstaller
        print("[INFO] PyInstaller est deja installe sur ce systeme.")
    except ImportError:
        print("[INFO] PyInstaller non detecte. Installation en cours...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    # 2. Nettoyer les anciens dossiers de compilation
    print()
    print("[CLEAN] Nettoyage des anciennes compilations...")
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"   Nettoye : {folder}/")
            except Exception as e:
                print(f"   Impossible de nettoyer {folder} (fichier verrouille) : {str(e)}")
                
    # 2bis. Vendor les assets Folium (Leaflet + plugins) pour un rendu carte HORS-LIGNE.
    # Ces fichiers (assets/folium/) sont nécessaires pour que la carte s'affiche
    # sans connexion internet ni accès aux CDN. On les télécharge avant la
    # compilation si le dossier est absent ou vide.
    print()
    print("[ASSETS] Preparation des assets de carte hors-ligne (Leaflet)...")
    assets_dir = os.path.join("assets", "folium")
    assets_ready = os.path.isdir(assets_dir) and any(
        f.endswith((".js", ".css")) for f in os.listdir(assets_dir)
    )
    if not assets_ready:
        vendor_script = os.path.join("tools", "vendor_folium_assets.py")
        if os.path.exists(vendor_script):
            print("   Telechargement des assets Folium (npm) en cours...")
            r = subprocess.run([sys.executable, vendor_script])
            if r.returncode != 0:
                print("   [WARNING] Impossible de telecharger les assets : la carte utilisera les CDN.")
        else:
            print("   [WARNING] tools/vendor_folium_assets.py introuvable : la carte utilisera les CDN.")
    else:
        print("   Assets deja presents, rien a telecharger.")

    # 3. Lancer la commande de compilation de PyInstaller
    print()
    print("[COMPILING] Compilation PyInstaller en cours (cela peut prendre quelques minutes)...")
    print()

    # Séparateur de chemin pour --add-data (';' sous Windows, ':' sinon)
    sep = ";" if sys.platform == "win32" else ":"

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",             # Crée un dossier autonome contenant le .exe (recommandé pour les DLLs géospatiales)
        "--name=Echantillon_Spatial",
        "--add-data=app.py%s." % sep, # Inclut l'application streamlit dans le bundle temporaire
        "--add-data=assets/folium%sassets/folium" % sep,  # Assets de carte hors-ligne (Leaflet + plugins)
        "--collect-all=streamlit",
        "--collect-all=geopandas",
        "--collect-all=folium",
        "--collect-all=streamlit_folium", # Force la copie des ressources statiques du composant cartographique
        "--collect-all=pyogrio",
        "--collect-all=rtree",
        "--collect-all=branca",           # Force l'inclusion des dépendances de rendu HTML de folium
        "--copy-metadata=streamlit",       # Requis pour que Streamlit trouve sa version au démarrage
        "--copy-metadata=pyogrio",         # Requis pour le chargement correct des métadonnées du pilote de données
        # --- REDUCTION DE LA TAILLE DU BUNDLE (le quota GitHub Actions est de 500 Mo) ---
        # Ces modules ne sont pas utilisés par l'application : on les exclut
        # pour alléger fortement le dossier portable et le ZIP final.
        "--exclude-module=tkinter",        # Non utilisé (application web, pas d'UI desktop)
        "--exclude-module=IPython",        # Non utilisé
        "--exclude-module=pytest",         # Non utilisé (outil de test uniquement)
        "--exclude-module=matplotlib",     # Retiré de requirements.txt (jamais importé)
        "--exclude-module=scipy",          # Retiré de requirements.txt (jamais importé)
        "run_app.py"
    ]

    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        # --- SOLUTION MAJEURE DE ROBUSTESSE ---
        # Copier manuellement les fichiers nécessaires À LA RACINE du dossier de
        # sortie 'dist/Echantillon_Spatial/' (à côté de l'exécutable) :
        #   - app.py (exécuté par Streamlit)
        #   - offline_folium.py (importé par app.py -> rendu carte hors-ligne)
        #   - assets/folium/ (Leaflet + plugins, utilisés par offline_folium)
        #   - Lancer_Echantillon_Spatial.bat (lanceur qui garde la console ouverte)
        print()
        print("[PACKAGING] Finalisation du package portable...")

        dest_folder = os.path.join("dist", "Echantillon_Spatial")
        os.makedirs(dest_folder, exist_ok=True)

        extra_files = [
            "app.py",
            "offline_folium.py",
            "Lancer_Echantillon_Spatial.bat",
        ]
        for fname in extra_files:
            if os.path.exists(fname):
                try:
                    shutil.copy(fname, os.path.join(dest_folder, fname))
                    print(f"   [OK] {fname} copie a cote de l'executable.")
                except Exception as e:
                    print(f"   [WARNING] Impossible de copier {fname} : {str(e)}")
            else:
                print(f"   [WARNING] {fname} introuvable, ignore.")

        # Copier les assets de carte hors-ligne (Leaflet + plugins)
        src_assets = os.path.join("assets", "folium")
        if os.path.isdir(src_assets):
            dest_assets = os.path.join(dest_folder, "assets", "folium")
            try:
                if os.path.isdir(dest_assets):
                    shutil.rmtree(dest_assets)
                shutil.copytree(src_assets, dest_assets)
                print("   [OK] assets/folium copie a cote de l'executable.")
            except Exception as e:
                print(f"   [WARNING] Impossible de copier assets/folium : {str(e)}")

        # Créer le second livrable : ZIP "source portable" avec lanceur .bat
        try:
            create_source_portable_zip()
        except Exception as e:
            print(f"   [WARNING] Impossible de creer le ZIP source portable : {str(e)}")

        print()
        print("==========================================================")
        print("   [SUCCESS] COMPILATION REUSSIE AVEC SUCCES !")
        print("==========================================================")
        print("   Votre application autonome est disponible dans le dossier :")
        print("   dist\\Echantillon_Spatial\\")
        print()
        print("   Comment la distribuer a vos collegues :")
        print("   1. Allez dans le dossier 'dist'.")
        print("   2. Compressez le dossier 'Echantillon_Spatial' en fichier .zip (clic droit -> Envoyer vers -> Dossier compresse).")
        print("   3. Envoyez ce fichier .zip a vos collegues.")
        print("   4. Ils n'auront qu'a le decompresser sur n'importe quel PC Windows et double-cliquer sur 'Echantillon_Spatial.exe' pour lancer la carte !")
        print("   * Aucune installation requise, fonctionne sans aucun droit administrateur !")
        print("==========================================================")
    else:
        print()
        print("   [ERROR] Erreur lors de la compilation. Veuillez verifier les logs ci-dessus.")
        
if __name__ == '__main__':
    main()
