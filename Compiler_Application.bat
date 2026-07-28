@echo off
:: ==============================================================================
:: Script de Compilation Automatique en Exécutable Windows (.exe)
:: Utilise le Python de l'environnement virtuel local (.venv) pour s'assurer
:: que toutes les dépendances géospatiales sont incluses correctement.
:: Ne nécessite AUCUN droit d'administrateur !
:: ==============================================================================

title Compilateur Echantillon_Spatial - Pratisig Consulting Services

echo =====================================================================
echo    🔨 COMPILATION DE L'APPLICATION EN EXECUTABLE AUTONOME (.EXE) 🔨
echo =====================================================================
echo.

:: Vérifier si l'environnement virtuel local existe
if not exist "%~dp0.venv" (
    echo [ERREUR] L'environnement virtuel local ".venv" n'existe pas.
    echo S'il vous plait, lancez d'abord "Lancer_Application.bat" au moins une fois
    echo pour initialiser l'environnement et installer les bibliothèques.
    echo.
    pause
    exit /b
)

echo [1/3] Activation de l'environnement virtuel local (.venv)...
call "%~dp0.venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel.
    pause
    exit /b
)

echo [2/3] Verification et mise a jour du compilateur PyInstaller...
python -m pip install --upgrade pip
pip install pyinstaller

echo.
echo [3/3] Lancement du processus de compilation PyInstaller...
echo Cela va prendre quelques minutes, veuillez patienter...
echo.

python "%~dp0build_exe.py"

:: Désactiver l'environnement virtuel à la fin
call deactivate

echo.
echo Processus de compilation termine !
pause
