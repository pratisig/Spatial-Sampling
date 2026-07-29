# 📘 Guide d'Utilisation Complet : Outil d'Échantillonnage Spatial des Ménages
### *Pratisig Consulting Services*
*Assistance & Support : Youssoupha Mbodji (pratisig.consulting@gmail.com)*

---

## Table des Matières
1. **Présentation de l'Outil**
2. **Installation et Lancement**
3. **Préparation des Données d'Entrée**
4. **Configuration des Paramètres d'Échantillonnage**
5. **Visualisation et Contrôle Qualité de Bureau**
6. **Outil d'Édition et Repositionnement de Points**
7. **Exportation et Intégration Terrain (OsmAnd & Google Earth)**
8. **Interprétation du Rapport de Synthèse**

---

## 1. Présentation de l'Outil

Cet outil d'échantillonnage spatial a été développé pour automatiser et fiabiliser la sélection de ménages (bâtiments) lors d'enquêtes épidémiologiques, d'évaluations de couverture vaccinale ou d'enquêtes socio-économiques de terrain. 

Il élimine le besoin de licences coûteuses (ArcGIS) en s'appuyant entièrement sur des technologies open-source réactives, offrant aux équipes de planification une interface cartographique interactive haute définition et des exports directement utilisables hors-ligne par les équipes d'enquêteurs sur leurs téléphones portables.

---

## 2. Installation et Lancement

L'outil propose **trois modes d'installation** pour s'adapter à toutes les infrastructures informatiques, y compris les ordinateurs sans connexion internet ou sans droits d'administrateur système.

### Mode A : Lancement via l'Exécutable Portable (Recommandé pour les non-techniciens)
1. Téléchargez l'archive zip `Echantillon_Spatial_Windows.zip` (générée automatiquement par GitHub ou compilée localement).
2. Décompressez le dossier sur votre disque dur (ex: sur votre Bureau).
3. Ouvrez le dossier extrait et double-cliquez sur le fichier **`Echantillon_Spatial.exe`**.
4. Une fenêtre noire d'initialisation s'ouvre, puis votre navigateur internet par défaut s'ouvre automatiquement à l'adresse `http://localhost:8501`. **Aucun droit d'administrateur n'est requis.**

### Mode B : Lancement Universel (Si Python portable est configuré)
1. Double-cliquez sur le fichier **`Lancer_Application.bat`**.
2. Si vous avez copié un dossier de Python portable nommé `python` à la racine, le script l'utilisera. Sinon, il recherchera le Python système et configurera automatiquement un environnement virtuel `.venv`.

### Mode C : Exécution en Ligne (SaaS Cloud)
* Si votre administrateur a déployé l'application sur **Streamlit Community Cloud** ou **Hugging Face**, ouvrez simplement l'URL fournie (ex: `https://pratisig-sampling.streamlit.app/`) sur votre PC, tablette ou smartphone.

---

## 3. Préparation des Données d'Entrée

L'outil accepte une large gamme de formats géographiques et tabulaires. Avant de commencer, préparez vos deux couches de données :

### Couche A : Les Bâtiments / Ménages (Points de départ)
Cette couche représente l'intégralité des concessions ou bâtiments éligibles pour l'échantillonnage dans votre zone d'étude.
* **Formats acceptés** : 
  * Fichiers vectoriels : `.geojson`, `.gpkg` ou Shapefile compressé en `.zip` (contenant les fichiers `.shp`, `.dbf`, `.shx`, `.prj`).
  * Fichiers tabulaires : `.csv` ou `.xlsx` (Excel).
* **Si format tabulaire (Excel/CSV)** : Assurez-vous que votre fichier contient deux colonnes pour les coordonnées géographiques (ex: `latitude` et `longitude` en degrés décimaux WGS84). L'outil vous demandera de sélectionner ces colonnes dans la barre latérale.

### Couche B : Les Villages / Localités (Limites ou Points)
Cette couche définit les grappes d'échantillonnage (les villages).
* **Cas 1 : Vous disposez des polygones de limites de villages** : Chargez le fichier vectoriel (`.geojson`, `.gpkg`, ou `.zip` de Shapefile). L'outil utilisera directement ces limites officielles.
* **Cas 2 : Vous ne disposez que des coordonnées des centres de villages (centroids)** : Chargez un fichier de points (WGS84). L'outil va générer automatiquement des aires d'influence non chevauchantes autour de chaque point.
* **Attribut requis** : Votre fichier de villages doit contenir une colonne de texte représentant le **nom unique** ou l'identifiant de chaque village (ex : `nom_vill`, `village_name`, `site_id`). Vous devrez sélectionner ce champ dans la barre latérale sous l'onglet *"Attributs"*.

---

## 4. Configuration des Paramètres d'Échantillonnage

Une fois les données chargées, réglez vos paramètres dans la barre latérale gauche :

1. **Rayon de recherche (mètres)** *(Uniquement si vos villages sont sous forme de points)* :
   * Détermine la distance maximale (tampon) autour du centre d'un village pour rechercher des concessions éligibles. Par exemple, si vous réglez sur `1000m`, l'outil ne sélectionnera aucun ménage situé à plus de 1 km du centre du village.
2. **Distance minimale entre les ménages (mètres)** :
   * C'est le paramètre d'espacement de sécurité (inhibition). Il évite que l'échantillon choisisse des maisons voisines, assurant ainsi une bonne répartition géographique. Pour les enquêtes de couverture vaccinale, un espacement de `20m` à `50m` est standard.
3. **Méthode d'allocation de l'échantillon** :
   * **Nombre fixe par village** : Sélectionne exactement la même quantité de ménages (ex : `15`) dans chaque village.
   * **Pourcentage des bâtiments** : Sélectionne une fraction constante de la population de toits de chaque village (ex : `10%`).
   * **Allocation Proportionnelle Globale (PPS)** : Vous donnez une taille d'échantillon globale pour toute l'enquête (ex : `200` ménages), et l'application la répartit automatiquement entre les villages au prorata de leur nombre total de bâtiments (les villages plus grands auront plus de points échantillonnés).
4. **Relâcher la contrainte de distance si nécessaire** :
   * **Laissez cette case cochée**. Si un village est très dense ou compte peu de bâtiments, il peut être géométriquement impossible de trouver le nombre requis de ménages espacés de la distance demandée. Ce mode permet à l'outil de réduire progressivement et automatiquement l'espacement requis par paliers de 15% pour ce village spécifique afin d'atteindre votre cible d'échantillon, tout en conservant le maximum d'écart possible.

---

## 5. Visualisation et Contrôle Qualité de Bureau

Dès que vos paramètres sont configurés, cliquez sur le bouton rouge **`🚀 Lancer l'Échantillonnage Spatial`**.

### Rapport de Synthèse
En haut de l'écran s'affiche un tableau de bord récapitulant :
* Le nombre de villages traités.
* Le nombre total de bâtiments analysés.
* Le nombre de ménages échantillonnés.
* Le **Taux de réussite** (le pourcentage de villages où la cible d'échantillonnage a été atteinte).
* La **Distance moyenne réelle** d'espacement mesurée sur le terrain.

### Carte Interactive des Échantillons
La carte Leaflet à droite est votre outil principal de contrôle qualité :
* **Changement de fond de carte (Crucial)** : Cliquez sur l'icône de couches en haut à droite de la carte et sélectionnez **`Image Satellite (Esri Sat)`**. Zoomer sur vos points d'échantillon (repères rouges) : l'imagerie haute résolution vous permet de valider visuellement si chaque point tombe bien sur le toit d'une vraie habitation.
* **Affichage des couches** : Vous pouvez cocher/décocher les polygones d'influence des villages (en couleur) ou l'ensemble des bâtiments d'origine (grappes grises) pour vérifier la cohérence du tirage.

---

## 6. Outil d'Édition et Repositionnement de Points

Si vous observez qu'un point sélectionné tombe dans un espace vide, sur un bâtiment public, ou dans une zone d'accès dangereuse (marécage, falaise), vous pouvez le déplacer manuellement en 2 clics :

1. Déroulez le panneau **`✍️ Outil d'Édition : Repositionnement Manuel des Points`** situé sous la carte.
2. **Sélectionnez le point à déplacer** :
   * *Méthode rapide* : Cliquez simplement sur le **repère rouge** du point sur la carte satellite. Un message s'affiche : *"📍 Point [ID] sélectionné !"* et le point est automatiquement sélectionné dans l'outil d'édition.
   * *Méthode manuelle* : Choisissez l'identifiant du point (ex: `YOFF_03`) dans le menu déroulant de l'outil d'édition.
3. **Choisissez le nouvel emplacement** :
   * Zoomer sur l'image satellite à l'endroit exact où se trouve la maison de remplacement.
   * Cliquez sur le toit de cette maison sur la carte.
   * L'outil d'édition affiche les coordonnées de votre clic sous *Option 1*.
4. **Appliquez le déplacement** :
   * Cliquez sur le bouton vert **`👉 Déplacer [ID] ici`**.
   * Le point se déplace instantanément sur la carte, son statut d'attribut devient *"Repositionné manuellement"*, et tous vos fichiers d'exports (Shapefile, Excel, GPX, KML, rapport HTML) sont réécrits à jour sur votre ordinateur en moins d'une seconde !

---

## 7. Exportation et Intégration Terrain (OsmAnd & Google Earth)

Une fois l'échantillon validé et corrigé, allez dans la section **`📥 Téléchargement des Résultats`** et cliquez sur le bouton **`Télécharger le pack complet de résultats (ZIP)`**.

Les résultats sont également sauvegardés automatiquement dans votre dossier local choisi (par défaut `./outputs/`).

### Dossier Shapefile (`shapefile/`)
* Contient votre échantillon complet au format standard SIG (.shp, .dbf, .shx, .prj, .cpg).
* Les noms de colonnes respectent strictement la limite de 10 caractères des Shapefiles pour éviter toute corruption de données :
  * `pt_id` : Identifiant unique du point (ex: `FANN_01`).
  * `vil_name` : Nom du village d'appartenance.
  * `lat` / `lon` : Coordonnées géographiques en degrés décimaux WGS84.
  * `dist_m` : Distance de sécurité appliquée pour ce point.
  * `sampl_stat` : Statut du point (Target Achieved, Repositionné manuellement, etc.).

### Dossier GPX par Village (`gpx_exports/`)
* Contient des fichiers GPX individuels nommés par village (ex: `Ngor_echantillon.gpx`).
* **C'est le format idéal pour la navigation hors-ligne sur le terrain avec l'application mobile gratuite OsmAnd !**

#### 📱 Guide d'importation dans OsmAnd (Android & iOS) :
1. **Copie des fichiers** : Envoyez les fichiers `.gpx` sur les téléphones des enquêteurs (par câble USB, e-mail, WhatsApp, ou Google Drive).
2. **Importation** :
   * Ouvrez l'application **OsmAnd** sur le téléphone.
   * Allez dans le menu principal (☰) en bas à gauche ➔ **Mes lieux** (My Places) ➔ **Traces** (Tracks).
   * Appuyez sur le bouton d'importation **`+`** en bas, et sélectionnez le fichier GPX importé.
3. **Navigation terrain** :
   * Les points de l'échantillon apparaissent sous forme d'étoiles colorées sur la carte offline d'OsmAnd.
   * L'enquêteur clique sur un point (ex: `NGOR_02`), appuie sur **"Naviguer"**, choisit le mode **"Piéton"**, et se laisse guider par le GPS du téléphone pas-à-pas jusqu'à la concession ciblée, sans besoin de réseau internet !

### Dossier KML par Village (`kml_exports/`)
* Contient des fichiers KML individuels pour **Google Earth**.
* Idéal pour une inspection rapide en 3D haute définition depuis votre ordinateur de bureau avant le départ des équipes. Double-cliquez simplement sur le fichier KML pour ouvrir Google Earth et survoler vos concessions échantillonnées.

### Tableau Excel (`coordonnees_echantillon.xlsx`)
* Un tableur élégant listant l'ensemble de vos points avec leurs coordonnées exactes. Idéal pour être imprimé ou importé dans vos outils de collecte de données mobiles comme **ODK** ou **KoboToolbox** !

---

## 8. Interprétation du Rapport de Synthèse

Le fichier **`rapport_echantillonnage.html`** inclus dans le ZIP est un rapport officiel prêt à être imprimé ou sauvegardé au format PDF :
* **Statistiques Globales** : Résume le succès de votre planification pour vos bailleurs ou coordinateurs médicaux.
* **Tableau de Détail par Village** : Liste pour chaque village le nombre de concessions disponibles, la cible demandée, le nombre réellement échantillonné, et surtout, la **distance minimale finale appliquée**. Si la distance finale est inférieure à votre paramètre d'origine, cela signifie que la contrainte a été automatiquement desserrée (relaxée) pour pouvoir atteindre votre taille d'échantillon, preuve de la densité ou de l'exiguïté du village concerné.

---
*Outil d'Échantillonnage Spatial des Ménages — Conçu et développé par **Pratisig Consulting Services**.*
*Assistance & Support technique : **Youssoupha Mbodji** (pratisig.consulting@gmail.com)*
