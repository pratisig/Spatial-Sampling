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
        
    # 2. Nettoyer les anciens dossiers de compilation
    print()
    print("🧹 Nettoyage des anciennes compilations...")
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"   Nettoyé : {folder}/")
            except Exception as e:
                print(f"   Impossible de nettoyer {folder} (fichier verrouillé) : {str(e)}")
                
    # 3. Lancer la commande de compilation de PyInstaller
    print()
    print("⚙️ Compilation PyInstaller en cours (cela peut prendre quelques minutes)...")
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
        "--collect-all=streamlit_folium", # CRUCIAL : Force la copie des fichiers HTML/JS/CSS statiques du composant de la carte !
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
        print("📦 Finalisation du package portable...")
        
        src_app = "app.py"
        dest_folder = os.path.join("dist", "Echantillon_Spatial")
        dest_app = os.path.join(dest_folder, "app.py")
        
        if os.path.exists(src_app):
            try:
                shutil.copy(src_app, dest_app)
                print("   ✅ app.py a été copié avec succès à la racine de l'exécutable !")
            except Exception as e:
                print(f"   ⚠️ Erreur lors de la copie de app.py : {str(e)}")
        
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
