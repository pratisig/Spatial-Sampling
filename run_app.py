# -*- coding: utf-8 -*-
"""
Point d'entrée pour la compilation en exécutable Windows (.exe)
Lance l'application Streamlit de manière programmatique de façon autonome.
Conception : Pratisig Consulting Services
"""

import os
import sys
import streamlit.web.cli as stcli

if __name__ == '__main__':
    # Déterminer si on tourne depuis l'exécutable compilé ou le script Python
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    app_path = os.path.join(base_dir, "app.py")
    
    # Configurer les arguments système pour lancer Streamlit programmatoirement
    sys.argv = ["streamlit", "run", app_path, "--global.developmentMode=false"]
    
    # Lancer le serveur Streamlit
    sys.exit(stcli.main())
