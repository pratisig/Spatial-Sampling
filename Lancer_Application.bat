@echo off
:: ==============================================================================
:: Script de Lancement Universel pour l'Outil d'Echantillonnage Spatial (Windows)
:: ==============================================================================
:: Ce script est conçu pour s'exécuter dans TOUTES les situations :
:: 1. Mode Portable (SANS PYTHON INSTALLE) : Si vous copiez une version de Python
::    portable dans un dossier nommé "python" à côté de ce fichier.
:: 2. Mode Standard : Utilise le Python installé sur le système de manière sécurisée
::    en créant un environnement virtuel (.venv) local pour éviter les conflits.
:: Ne nécessite AUCUN droit d'administrateur !
:: ==============================================================================

title Echantillonnage Spatial des Menages - Pratisig Consulting Services

echo =====================================================================
echo    🌍 OUTIL D'ECHANTILLONNAGE SPATIAL DES MENAGES (SANS ARCGIS) 🌍
echo =====================================================================
echo.

:: ------------------------------------------------------------------------------
:: CAS 1 : VERIFICATION DE LA PRESENCE D'UN PYTHON PORTABLE LOCAL
:: ------------------------------------------------------------------------------
if exist "%~dp0python\python.exe" (
    echo [MODE PORTABLE] Python portable local detecte !
    echo Utilisation de la version autonome et portable du dossier "python".
    echo.
    set "PYTHON_CMD=%~dp0python\python.exe"
    set "PIP_CMD=%~dp0python\python.exe -m pip"
    set "STREAMLIT_CMD=%~dp0python\Scripts\streamlit.exe"
    goto install_dependencies
)

:: ------------------------------------------------------------------------------
:: CAS 2 : UTILISATION DU PYTHON SYSTEME AVEC ENVIRONNEMENT VIRTUEL
:: ------------------------------------------------------------------------------
echo [MODE SYSTEME] Verification de l'installation de Python sur l'ordinateur...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] Aucun Python detecte !
    echo.
    echo Pour utiliser cet outil sur ce PC, vous avez deux choix :
    echo.
    echo CHOIX A (Le plus simple, 100%% Portable, Sans installation, Sans droit Admin) :
    echo   1. Telechargez l'archive zip de Python Portable (ex: WinPython Justin ou Embeddable).
    echo   2. Extrayez-la dans ce dossier de projet et renommez le dossier extrait en "python".
    echo   3. Relancez ce fichier "Lancer_Application.bat".
    echo.
    echo CHOIX B (Installation standard) :
    echo   1. Telechargez et installez Python : https://www.python.org/downloads/
    echo   2. Cochez ABSOLUMENT la case "Add Python to PATH" lors de l'installation.
    echo   3. Une fois l'installation terminee, relancez ce fichier.
    echo.
    pause
    exit /b
)

echo Python systeme detecte avec succes.
echo Configuration de l'environnement virtuel local (.venv)...

:: Créer l'environnement virtuel s'il n'existe pas
if not exist "%~dp0.venv" (
    echo Creation de l'environnement virtuel .venv en cours...
    python -m venv "%~dp0.venv"
    if %errorlevel% neq 0 (
        echo [ERREUR] Impossible de creer l'environnement virtuel local.
        pause
        exit /b
    )
    echo Environnement virtuel cree !
)

set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
set "PIP_CMD=%~dp0.venv\Scripts\python.exe -m pip"
set "STREAMLIT_CMD=%~dp0.venv\Scripts\streamlit.exe"

:install_dependencies
echo.
echo [Etape 2/3] Verification et installation des dependances (requirements.txt)...
echo Cela peut prendre 1 a 2 minutes lors de la premiere initialisation...
echo.

%PIP_CMD% install --upgrade pip

%PIP_CMD% install -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] L'installation des dependances a echoue.
    echo Verifiez votre connexion internet pour la premiere installation et relancez.
    pause
    exit /b
)

echo.
echo [Etape 3/3] Lancement de l'application dans votre navigateur...
echo.

:: Lancer Streamlit uniquement en local (127.0.0.1) pour contourner l'alerte du Pare-feu Windows
:: et s'exécuter sans aucun droit d'administration !
%PYTHON_CMD% -m streamlit run "%~dp0app.py" --server.address=127.0.0.1 --server.port=8501 --server.headless=true

echo.
echo L'application s'est arretee normalement.
pause
