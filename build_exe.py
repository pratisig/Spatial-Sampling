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
                
    # 3. Lancer la commande de compilation de PyInstaller
    print()
    print("[COMPILING] Compilation PyInstaller en cours (cela peut prendre quelques minutes)...")
    print()
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",             # Crée un dossier autonome contenant le .exe (recommandé pour les DLLs géospatiales)
        "--name=Echantillon_Spatial",
        "--add-data=app.py;.", # Inclut l'application streamlit dans le bundle temporaire
        "--collect-all=streamlit",
        "--collect-all=geopandas",
        "--collect-all=folium",
        "--collect-all=streamlit_folium", # Force la copie des ressources statiques du composant cartographique
        "--collect-all=pyogrio",
        "--collect-all=rtree",
        "--collect-all=branca",           # Force l'inclusion des dépendances de rendu HTML de folium
        "--copy-metadata=streamlit",       # Requis pour que Streamlit trouve sa version au démarrage
        "--copy-metadata=pyogrio",         # Requis pour le chargement correct des métadonnées du pilote de données
        "run_app.py"
    ]
    
    # Ajuster le séparateur de chemin si on compile depuis une autre plateforme pour test
    if sys.platform != "win32":
        cmd[4] = "--add-data=app.py:."
        
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
