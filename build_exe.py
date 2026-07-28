# -*- coding: utf-8 -*-
"""
Script d'automatisation de la compilation de l'application en exécutable Windows (.exe)
Utilise PyInstaller pour générer un dossier autonome portable.
Conception : Pratisig Consulting Services
"""

import os
import sys
import subprocess
import shutil

def main():
    print("==========================================================")
    print("   🔨 SCRIPT DE COMPILATION EN EXECUTABLE WINDOWS (.EXE)   ")
    print("==========================================================")
    print()
    
    # 1. Installer PyInstaller si non disponible
    try:
        import PyInstaller
        print("✅ PyInstaller est déjà installé sur ce système.")
    except ImportError:
        print("📥 PyInstaller non détecté. Installation en cours...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    # 2. Lancer la commande de compilation de PyInstaller
    # --onedir est fortement recommandé pour Streamlit car il évite les latences d'extraction à chaque démarrage
    # et prévient les conflits de chargement de DLLs (particulièrement pour geopandas, shapely et pyogrio).
    
    print()
    print("⚙️ Compilation en cours, veuillez patienter (cela peut prendre quelques minutes)...")
    print()
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",             # Crée un dossier autonome contenant le .exe (recommandé pour les DLLs géospatiales)
        "--name=Echantillon_Spatial",
        "--add-data=app.py;.", # Inclut l'application streamlit
        "--collect-all=streamlit",
        "--collect-all=geopandas",
        "--collect-all=folium",
        "--collect-all=pyogrio",
        "--collect-all=rtree",
        "run_app.py"
    ]
    
    # Ajuster le séparateur de chemin si on compile depuis une autre plateforme pour test
    if sys.platform != "win32":
        cmd[4] = "--add-data=app.py:."
        
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print()
        print("==========================================================")
        print("🎉 COMPILATION REUSSIE AVEC SUCCES !")
        print("==========================================================")
        print("👉 Votre application autonome est disponible dans le dossier :")
        print("   dist\\Echantillon_Spatial\\")
        print()
        print("🔧 Comment la distribuer à vos collègues :")
        print("   1. Allez dans le dossier 'dist'.")
        print("   2. Compressez le dossier 'Echantillon_Spatial' en fichier .zip (clic droit -> Envoyer vers -> Dossier compressé).")
        print("   3. Envoyez ce fichier .zip à vos collègues.")
        print("   4. Ils n'auront qu'à le décompresser sur n'importe quel PC Windows et double-cliquer sur 'Echantillon_Spatial.exe' pour lancer la carte !")
        print("   * Aucune installation requise, fonctionne sans aucun droit administrateur !")
        print("==========================================================")
    else:
        print()
        print("❌ Erreur lors de la compilation. Veuillez vérifier les logs ci-dessus.")
        
if __name__ == '__main__':
    main()
