# 🌍 Outil d'Échantillonnage Spatial des Ménages (Sans ArcGIS)
### *Spatially Constrained Random Sampling for Epidemiological Surveys & Vaccination Campaigns*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
![Compilation Status](https://github.com/votre-compte/votre-depot/actions/workflows/build.yml/badge.svg)

> **🚀 Déploiement & Compilation Cloud :** Cet outil peut désormais être **exécuté en ligne sur le Web** (SaaS gratuit) ou être **compilé automatiquement sous forme d'exécutable Windows (.exe) portable** directement par les serveurs de GitHub Actions ! (Voir explications plus bas).

Ce projet est une solution complète, open-source et autonome en Python pour réaliser un **échantillonnage spatial aléatoire contraint** de ménages au sein des aires d'influence (catchments) des villages. 

Conçu spécifiquement pour les **épidémiologistes**, les **équipes d'enquêteurs de terrain** et les **campagnes de vaccination** dans le domaine humanitaire et médical, cet outil remplace avantageusement les anciennes boîtes à outils ArcGIS (ArcPy) gourmandes en licences. Il offre une interface cartographique interactive Leaflet moderne et génère des exports directement prêts pour les terminaux mobiles du terrain (OsmAnd, Google Earth).

---

## 🚀 Comment lancer l'application sous Windows (Trois Modes Disponibles)

Pour s'adapter aux contraintes informatiques des épidémiologistes et équipes de terrain (qui n'ont pas toujours Python installé ou qui n'ont pas les **droits d'administrateur** pour installer des logiciels), l'outil propose trois modes de fonctionnement :

### 🌟 MODE A : 100% PORTABLE (Recommandé - Sans installation & Sans droits Administrateur)
Si l'ordinateur cible **ne dispose pas de Python** et que vous n'avez pas les droits d'admin pour l'installer :
1. Téléchargez une version autonome (portable) de **WinPython** ou de **Python Embedded** pour Windows (ex: [WinPython Justin / Portable 64-bit](https://winpython.github.io/)).
2. Décompressez l'archive et copiez le dossier Python obtenu directement dans votre dossier de projet.
3. **Renommez** ce dossier contenant `python.exe` simplement en **`python`**.
4. Double-cliquez sur **`Lancer_Application.bat`**. 
   * *Le script détectera automatiquement le dossier `python` local, y installera les dépendances isolées, et démarrera le serveur web de la carte en moins d'une minute, sans toucher au système Windows de l'ordinateur !*

### 🔨 MODE B : Compilation en Exécutable Windows Autonome (`.exe` Direct)
Si vous souhaitez compiler l'application en un **vrai fichier `.exe` exécutable d'un simple double-clic** pour le distribuer à vos collègues :
1. Ouvrez une console de commande dans votre environnement de travail (contenant Python) et exécutez la commande :
   ```bash
   python build_exe.py
   ```
2. Ce script va utiliser **PyInstaller** pour assembler Python, Streamlit, Folium, GeoPandas et toutes les dépendances dans un dossier autonome disponible sous :
   `dist\Echantillon_Spatial\`
3. **Comment le distribuer** : Compressez le dossier `Echantillon_Spatial` en un fichier **`Echantillon_Spatial.zip`** (Clic droit ➔ Envoyer vers ➔ Dossier compressé).
4. Vos collaborateurs n'auront qu'à décompresser ce zip sur n'importe quel ordinateur Windows et double-cliquer sur le fichier **`Echantillon_Spatial.exe`** pour lancer l'application ! **Cela fonctionne sur 100% des ordinateurs, sans Python installé et sans aucun droit d'administration !**

### 💻 MODE C : Standard (Utilise le Python installé sur le système)
Si Python est installé sur l'ordinateur (ou si vous pouvez l'installer facilement) :
1. Assurez-vous d'avoir **Python 3.9 ou supérieur** installé.
   * *Important* : Cochez impérativement la case **"Add Python.exe to PATH"** (Ajouter Python au PATH) lors de l'installation.
2. Double-cliquez sur le fichier **`Lancer_Application.bat`**.
3. Le script va créer un environnement de travail virtuel sécurisé (`.venv`), installer les bibliothèques requises et ouvrir l'application.

### ☁️ MODE D : Déploiement Cloud (SaaS Gratuit sur Internet)
Puisque le projet est hébergé sur GitHub, vous pouvez le déployer gratuitement sur le Web en 1 clic :
1. Créez un compte gratuit sur **[Streamlit Community Cloud](https://share.streamlit.io/)**.
2. Cliquez sur **"New App"**, liez votre compte GitHub, et sélectionnez votre dépôt.
3. Écrivez **`app.py`** dans le champ *Main file path*, puis cliquez sur **"Deploy!"**.
4. L'application est en ligne sur une URL publique sécurisée (ex: `https://votre-site.streamlit.app/`), prête pour vos clients ou équipes distantes !

---

## 🤖 Compilation Automatique sous Windows (.exe) via GitHub Actions (CI/CD)

Pour rendre l'outil encore plus professionnel et vous faire gagner du temps, j'ai configuré un outil d'intégration continue **GitHub Actions** (`.github/workflows/build.yml`) :

* **Comment ça marche ?** : 
  Chaque fois que vous publiez une mise à jour (un `git push`) de votre code sur GitHub, les serveurs cloud de GitHub démarrent automatiquement un ordinateur virtuel Windows temporaire pour vous !
* **Ce qu'il fait** :
  1. Il récupère votre code.
  2. Il installe Python 3.11 et toutes les dépendances de `requirements.txt`.
  3. Il lance la compilation de l'exécutable à l'aide de notre script de compilation `build_exe.py`.
  4. Il compresse le dossier final en un fichier **`Echantillon_Spatial_Windows.zip`**.
  5. Il l'enregistre en tant qu'**Artifact de build** téléchargeable sur votre page GitHub !
* **Comment télécharger votre exécutable (.exe) prêt à l'emploi depuis GitHub** :
  1. Allez sur la page de votre dépôt sur GitHub.
  2. Cliquez sur l'onglet **"Actions"** en haut de la page.
  3. Cliquez sur le dernier flux de compilation réussi (marqué d'une coche verte `Compile Windows Executable`).
  4. Descendez tout en bas de la page dans la section **"Artifacts"**.
  5. Cliquez sur **`Echantillon_Spatial_Windows_Portable`** pour télécharger votre fichier ZIP compilé ! Vous n'avez plus besoin de compiler l'application sur votre propre ordinateur !

---

## 🎨 Fonctionnalités Clés & Améliorations de l'Outil

L'outil intègre plusieurs améliorations majeures par rapport aux anciennes solutions cartographiques :

### 1. 🧩 Délimitation Automatique des Zones d'Influence (Catchments)
* Si vous disposez de polygones pour les limites de vos villages, l'application les utilise directement pour découper l'espace de chaque village.
* **Si vous n'avez que des points GPS pour les centres des villages**, l'outil génère automatiquement un **tampon (Buffer)** de recherche autour de chaque point intersecté avec un **diagramme de Voronoi (Thiessen)**. Cela garantit que les zones d'influence créées autour de chaque village ne se chevauchent jamais, résolvant ainsi mathématiquement les conflits d'attribution des ménages situés à mi-chemin.

### 2. 📏 Algorithme de Distance Minimale Adaptatif (Inhibition Spatiale)
Pour éviter qu'une sélection aléatoire regroupe tous les ménages échantillonnés dans un même quartier dense (effet de grappe spatial biaisé), l'outil impose une distance minimale en mètres entre les ménages sélectionnés.
* **Innovation** : Si un village est petit ou très dense et qu'il est géométriquement impossible d'extraire le nombre cible de ménages avec la distance minimale spécifiée, **l'algorithme réduit progressivement la contrainte de distance de 15% à chaque tentative** (jusqu'à une limite sécuritaire de 1.5 mètres). Cela garantit d'atteindre la taille d'échantillon souhaitée tout en assurant l'espacement spatial maximal possible !

### 3. ✍️ Sélection et Repositionnement Visuel "en 2 clics" sur la Carte (Click-to-Select & Click-to-Move)
C'est l'atout majeur pour l'ergonomie de planification ! Si un point sélectionné au hasard tombe sous un arbre, dans un champ vide ou sur un bâtiment détruit :
* **Sélection Directe (1er Clic)** : Cliquez simplement **sur le point rouge** (ou juste à côté, tolérance de 80 mètres) directement sur la carte satellite. L'application identifie immédiatement de quel point il s'agit (ex : `NGOR_02`), l'affiche en surbrillance avec un message de notification : *"📍 Point NGOR_02 sélectionné !"* et met à jour automatiquement la sélection d'édition.
* **Déplacement Intuitif (2e Clic)** : Cliquez n'importe où sur l'image satellite à l'emplacement exact (le vrai toit) où vous souhaitez déplacer ce point. L'application affiche les coordonnées cliquées. Cliquez sur le bouton vert **"Déplacer le point ici"**.
* Le point se déplace, la carte se met à jour, et **tous les fichiers d'exports (Shapefile, Excel, GPX, KML, rapports) sont réécrits sur le disque à jour en moins d'une seconde, tout en conservant votre zoom et votre cadrage de carte !**

### 4. 📊 Trois Méthodes d'Allocation de la Taille d'Échantillon
* **Nombre fixe par village** : Exemple, 10 ménages sont sélectionnés aléatoirement dans chaque village traité.
* **Pourcentage des bâtiments** : Sélectionne une proportion constante (ex: 5% des toits) dans chaque village.
* **Allocation Proportionnelle d'un échantillon Global (PPS)** : Vous spécifiez une taille d'échantillon totale pour l'enquête (ex: 300 ménages), et l'outil la répartit automatiquement entre les villages au prorata de leur nombre total de bâtiments.

### 5. 🗺️ Double Carte : Prévisualisation et Résultats
* **Carte de Prévisualisation (Avant tirage)** : Dès le chargement des fichiers d'entrée, une carte à droite affiche vos polygones officiels et tous vos bâtiments sous forme de grappes fluides. Elle est **100% passive et optimisée (aucun rechargement "Running..." intempestif)** pour vous permettre d'explorer et vérifier la validité de vos données d'entrée.
* **Carte des Résultats (Après tirage)** : Affiche les zones découpées par village, les bâtiments de fond et les ménages finaux sélectionnés. Elle intègre l'écouteur de clic pour le repositionnement interactif.

### 6. 📥 Export Multi-format Complet pour le Terrain
Lors de l'exécution, les fichiers sont sauvegardés **automatiquement dans votre dossier local choisi (par défaut `./outputs`)** et un bouton de téléchargement d'un dossier compressé `.zip` est proposé dans le navigateur. Le pack de résultats contient :
* **Dossier `shapefile/`** : L'échantillon complet sous forme de fichier Shapefile ESRI avec des colonnes d'attributs standardisées et protégées contre la troncature de caractères (limite de 10 caractères du format SHP respectée : `pt_id`, `vil_name`, `lat`, `lon`, `dist_m`). *Écrit de façon ultra-rapide avec le moteur `pyogrio`.*
* **Dossier `geojson/`** : L'échantillon au format géo-standardisé GeoJSON pour intégration dans QGIS, ArcGIS Pro ou applications web.
* **Dossier `gpx_exports/`** : Fichiers GPX individuels nommés par village (ex: `Yoff_echantillon.gpx`). Chaque point y est rattaché avec un identifiant clair (ex: `YOFF_01`, `YOFF_02`) et sa description. **C'est le format de navigation offline idéal pour OsmAnd !**
* **Dossier `kml_exports/`** : Fichiers KML individuels nommés par village pour une visualisation 3D interactive immédiate dans Google Earth.
* **`coordonnees_echantillon.xlsx`** : Un classeur Excel élégant listant l'ensemble des points d'échantillonnage avec leurs coordonnées géographiques décimales WGS84, pour impression ou intégration dans des bases de données de suivi (ODK, KoboToolbox).
* **`rapport_echantillonnage.html`** : Un rapport de synthèse au design épuré, prêt pour impression ou sauvegarde PDF, contenant l'ensemble des statistiques de réussite, de densité et de distance par grappe.

---

## 📱 Guide Pratique d'Intégration sur le Terrain (OsmAnd & Google Earth)

### 1. Utilisation Hors-ligne sur Mobile avec OsmAnd (Android & iOS)
OsmAnd est l'outil de navigation de référence pour les équipes d'enquête terrain en zones reculées ou sans réseau cellulaire.
1. **Copie des fichiers** : Transférez les fichiers `.gpx` du dossier `gpx_exports` vers les téléphones des équipes terrain (via câble USB, partage Bluetooth, e-mail, WhatsApp, ou Google Drive).
2. **Importation** :
   * Ouvrez l'application **OsmAnd** sur le téléphone.
   * Ouvrez le menu principal (☰) en bas à gauche, puis allez sur **"Mes lieux"** (My Places) ➔ **"Traces"** (Tracks).
   * Appuyez sur le bouton d'importation **`+`** (ou cliquez sur le fichier GPX directement depuis le gestionnaire de fichiers du téléphone et choisissez "Ouvrir avec OsmAnd").
3. **Collecte et Navigation** :
   * Les points de l'échantillon s'affichent sur votre carte offline sous forme d'étoiles colorées.
   * L'enquêteur sélectionne le point cible (ex: `NGOR_03`), clique sur **"Naviguer"** (Navigation), et choisit le mode **"Piéton"**.
   * Le GPS du téléphone le guide alors avec précision jusqu'à l'habitation échantillonnée.

### 2. Validation Visuelle de Bureau avec Google Earth
Avant le départ des équipes sur le terrain, il is fortement recommandé de procéder à une validation visuelle rapide de bureau.
1. Ouvrez le dossier `kml_exports` sur votre ordinateur.
2. Double-cliquez sur le fichier KML du village à inspecter.
3. **Google Earth** se lance automatiquement et effectue un zoom sur la grappe échantillonnée.
4. L'utilisateur peut ainsi vérifier en 3D haute définition si certains points tombent sur des obstacles inaccessibles (zones inondées, casernes militaires, falaises) ou des bâtiments détruits, et adapter l'échantillon si nécessaire.

---

## 🛠️ Structure des Fichiers du Projet

```bash
├── app.py                      # Code source principal de l'application Streamlit (GUI & Geoprocessing)
├── run_app.py                  # Script d'entrée pour la compilation sous forme d'exécutable .exe
├── build_exe.py                # Script de compilation automatisée de l'exécutable à l'aide de PyInstaller
├── Lancer_Application.bat      # Script batch Windows d'lancement universel (Auto / Portable / Standard)
├── requirements.txt            # Liste des dépendances géospatiales Python requises
├── test_pipeline.py            # Script d'intégration de test unitaire pour la logique géospatiale
└── README.md                   # Documentation complète et guide d'utilisation (ce fichier)
```

---

*Conception : **Pratisig Consulting Services** • Assistance & Support : **Youssoupha Mbodji** (pratisig.consulting@gmail.com)*
