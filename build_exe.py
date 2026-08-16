# -*- coding: utf-8 -*-
"""
Script d'automatisation de la compilation de l'application en exécutable Windows (.exe)
Utilise PyInstaller pour générer un EXE UNIQUE AUTONOME (mode --onefile).
Conception : Pratisig Consulting Services

SÉCURITÉ ENCODAGE WINDOWS / GITHUB ACTIONS :
Tous les caractères emoji spéciaux (Unicode) ont été supprimés des print() console 
pour éviter les erreurs 'UnicodeEncodeError' (cp1252/cp850) lors de la compilation
dans l'environnement cloud Windows de GitHub Actions.

NOTE MODE --onefile :
- Produit UN SEUL fichier Echantillon_Spatial.exe, facile à partager.
- Au lancement, le .exe extrait son contenu dans un dossier temporaire puis
  démarre : le premier démarrage est un peu plus lent (10-30 s selon la machine).
- Le .exe est plus volumineux qu'en mode --onedir (toutes les DLLs sont dedans).
- Si le mode --onefile posait un problème avec les DLLs géospatiales (GDAL/pyogrio),
  revenir au mode --onedir : remplacer "--onefile" par "--onedir" ci-dessous.
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
    print("[COMPILING] Compilation PyInstaller en cours (cela peut prendre plusieurs minutes)...")
    print()

    # Séparateur de chemin pour --add-data (';' sous Windows, ':' sinon)
    sep = ";" if sys.platform == "win32" else ":"

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",             # UN SEUL fichier .exe à partager
        "--name=Echantillon_Spatial",
        "--add-data=app.py%s." % sep, # Inclut l'application streamlit dans le bundle
        "--add-data=assets/folium%sassets/folium" % sep,  # Assets de carte hors-ligne (Leaflet + plugins)
        "--hidden-import=offline_folium",  # module importé par app.py -> rendu carte hors-ligne
        "--collect-all=streamlit",
        "--collect-all=geopandas",
        "--collect-all=folium",
        "--collect-all=streamlit_folium",
        "--collect-all=pyogrio",
        "--collect-all=rtree",
        "--collect-all=branca",
        "--copy-metadata=streamlit",
        "--copy-metadata=pyogrio",
        "--exclude-module=tkinter",
        "--exclude-module=IPython",
        "--exclude-module=pytest",
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "run_app.py"
    ]

    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print()
        print("[PACKAGING] Finalisation...")

        # Créer le second livrable : ZIP "source portable" avec lanceur .bat
        try:
            create_source_portable_zip()
        except Exception as e:
            print(f"   [WARNING] Impossible de creer le ZIP source portable : {str(e)}")

        print()
        print("==========================================================")
        print("   [SUCCESS] COMPILATION REUSSIE AVEC SUCCES !")
        print("==========================================================")
        print("   Votre application autonome est un SEUL fichier :")
        print("   dist\\Echantillon_Spatial.exe")
        print()
        print("   Comment la distribuer a vos collegues :")
        print("   1. Envoyez le fichier 'dist\\Echantillon_Spatial.exe' (ou son ZIP).")
        print("   2. Ils double-cliquent sur l'exe : le navigateur s'ouvre et la carte s'affiche.")
        print("   * Aucune installation requise, sans droit administrateur !")
        print("   * Au premier lancement, l'exe extrait son contenu : quelques secondes de patience.")
        print("==========================================================")
    else:
        print()
        print("   [ERROR] Erreur lors de la compilation. Veuillez verifier les logs ci-dessus.")
        
if __name__ == '__main__':
    main()
