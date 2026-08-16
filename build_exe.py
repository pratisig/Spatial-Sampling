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
        # Copier manuellement app.py directement à la racine du dossier de sortie 'dist/Echantillon_Spatial/'
        # Cela garantit que le serveur web Streamlit le trouve immédiatement à côté de l'exécutable !
        print()
        print("[PACKAGING] Finalisation du package portable...")
        
        src_app = "app.py"
        dest_folder = os.path.join("dist", "Echantillon_Spatial")
        dest_app = os.path.join(dest_folder, "app.py")
        
        if os.path.exists(src_app):
            try:
                shutil.copy(src_app, dest_app)
                print("   [OK] app.py a ete copie avec succes a la racine de l'executable !")
            except Exception as e:
                print(f"   [WARNING] Erreur lors de la copie de app.py : {str(e)}")
        
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
