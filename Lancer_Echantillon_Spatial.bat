@echo off
:: ==============================================================================
:: Lanceur portable de l'application Echantillon_Spatial (a cote de l'executable)
:: Double-cliquez sur CE fichier pour lancer l'application.
:: L'avantage par rapport a Echantillon_Spatial.exe : cette fenetre reste ouverte,
:: donc vous voyez les messages / erreurs eventuelles.
:: ==============================================================================

title Echantillonnage Spatial des Menages - Pratisig Consulting Services

echo =====================================================================
echo    OUTIL D'ECHANTILLONNAGE SPATIAL DES MENAGES (portable)
echo =====================================================================
echo.

:: Se placer dans le dossier de ce fichier .bat
cd /d "%~dp0"

if not exist "Echantillon_Spatial.exe" (
    echo [ERREUR] Echantillon_Spatial.exe introuvable dans ce dossier.
    echo Placez ce fichier .bat dans le MEME dossier que Echantillon_Spatial.exe.
    echo.
    pause
    exit /b 1
)

echo Lancement de l'application... Le navigateur va s'ouvrir.
echo NE FERMEZ PAS cette fenetre pendant l'utilisation.
echo (Fermez-la pour arreter l'application.)
echo.

"Echantillon_Spatial.exe"

echo.
echo L'application s'est arretee.
pause
