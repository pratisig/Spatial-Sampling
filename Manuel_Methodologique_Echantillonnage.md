# 📓 Manuel Méthodologique et Technique : Échantillonnage Spatial Constraint
### *Pratisig Consulting Services*
*Auteur : Youssoupha Mbodji (pratisig.consulting@gmail.com)*

---

## Table des Matières
1. **Contexte Épidémiologique et Statistiques Spatiales**
2. **Algorithmes Géospatiaux Détaillés**
   * *A. Délimitation des Aires d'Influence (Diagrammes de Voronoi & Tampons)*
   * *B. Algorithme d'Inhibition Spatiale (Distance Minimale Adaptative)*
   * *C. Méthodes d'Allocation d'Échantillon (PPS)*
3. **Précision Cartographique et Reprojections (UTM)**
4. **Références Documentaires et Académiques**

---

## 1. Contexte Épidémiologique et Statistiques Spatiales

Dans les pays à ressources limitées, la planification d'enquêtes représentatives (couverture vaccinale, prévalence du paludisme, malnutrition, choléra) se heurte souvent à l'absence de registres nominatifs ou de bases de sondage exhaustives de la population. 

Historiquement, les épidémiologistes utilisaient la méthode révisée de l'OMS (méthode de la "bouteille tournée" ou échantillonnage par grappes de type spinning-pen). Bien que simple, cette approche souffre de **biais de sélection majeurs** (les enquêteurs ont tendance à choisir les maisons les plus proches du centre ou des routes principales, excluant les ménages isolés).

L'**échantillonnage spatial aléatoire contraint** sur des concessions numérisées (par satellite ou IA) résout ce problème. En s'appuyant sur la position géographique réelle des toits de bâtiments, il garantit que **chaque ménage de la zone d'étude possède une probabilité connue et non nulle d'être sélectionné**, respectant ainsi les principes fondamentaux de la statistique probabiliste.

### Le Concept d'Inhibition Spatiale (Espacement Minimum)
Pour éviter un biais de regroupement spatial (clustering), où l'algorithme sélectionne par hasard plusieurs concessions adjacentes dans un même quartier dense, l'outil met en œuvre un processus d'**inhibition spatiale** (dérivé du modèle de processus ponctuel de Strauss ou d'inhibition de type Hard-Core). En imposant une distance minimale de sécurité $d_{min}$ en mètres entre les points sélectionnés, l'outil force l'échantillon à se disperser de manière homogène sur l'ensemble de la grappe, optimisant la représentativité épidémiologique et évitant de sur-représenter un seul sous-groupe familial ou de voisinage.

---

## 2. Algorithmes Géospatiaux Détaillés

### A. Délimitation des Aires d'Influence (Voronoi & Tampons)
Lorsque l'utilisateur ne dispose pas de limites de polygones officiels pour les villages mais uniquement de coordonnées de centres (centroids), l'outil génère automatiquement des polygones d'influence géographiquement cohérents et non chevauchants.

#### 1. Diagramme de Voronoi (Thiessen)
Mathématiquement, pour un ensemble de points de villages $S = \{p_1, p_2, ..., p_n\}$ dans un plan, la cellule de Voronoi $V(p_i)$ associée au village $p_i$ est le lieu géométrique des points du plan dont la distance à $p_i$ est inférieure ou égale à la distance à tout autre point $p_j$ de $S$ :

$$V(p_i) = \{x \in \mathbb{R}^2 \ | \ ||x - p_i|| \le ||x - p_j||, \ \forall j \neq i\}$$

Cette partition de l'espace garantit qu'aucun espace n'est laissé vide et qu'aucun chevauchement n'est possible.

#### 2. Tampon de Recherche (Buffer)
Une cellule de Voronoi peut s'étendre théoriquement jusqu'à l'infini sur les bordures de la zone d'étude. Pour éviter d'attribuer à un village des concessions situées à plusieurs kilomètres, l'outil calcule un tampon circulaire $B(p_i, R)$ de rayon de recherche $R$ (en mètres) défini par l'utilisateur autour de chaque centre de village :

$$B(p_i, R) = \{x \in \mathbb{R}^2 \ | \ ||x - p_i|| \le R\}$$

#### 3. Intersection et Dissolution
L'aire d'influence finale $A_i$ de chaque village est calculée par l'intersection géométrique de sa cellule de Voronoi et de son tampon circulaire :

$$A_i = V(p_i) \cap B(p_i, R)$$

Cette aire d'influence $A_i$ est ensuite dissoute et rattachée à l'identifiant du village. Elle définit la **zone de responsabilité exclusive du village**. Tout bâtiment tombant dans cette zone est attribué à ce village et à aucun autre.

---

### B. Algorithme d'Inhibition Spatiale (Distance Minimale Adaptative)
Pour sélectionner $k_i$ ménages dans le village $i$ parmi l'ensemble des bâtiments $B_i$ situés dans l'aire $A_i$, l'outil utilise un algorithme d'inhibition de type Poisson-Disk ou Hard-Core adapté aux ensembles de points discrets :

1. **Cas Limite** : Si le nombre total de bâtiments disponibles est inférieur ou égal à la cible ($|B_i| \le k_i$), l'algorithme sélectionne automatiquement l'intégralité des bâtiments ($100\%$ de réussite) et désactive la contrainte de distance pour ce village.
2. **Cas Nominal** : Si $|B_i| > k_i$, l'algorithme effectue une permutation aléatoire des bâtiments de $B_i$ pour garantir l'équiprobabilité du tirage. Il initialise un ensemble vide de ménages sélectionnés $S_i = \emptyset$.
3. **Itération de Sélection** : Pour chaque bâtiment candidat $b \in B_i$ (dans l'ordre du mélange aléatoire) :
   * Il calcule la distance euclidienne plane $d(b, s)$ vers tous les ménages déjà sélectionnés dans $S_i$.
   * Si $\forall s \in S_i, \ d(b, s) \ge d_{min}$ (où $d_{min}$ est la distance minimale requise), alors le bâtiment $b$ est accepté et ajouté à $S_i$.
   * Le processus s'arrête dès que $|S_i| = k_i$.
4. **Algorithme de Relaxation Adaptative** :
   Si l'algorithme parcourt l'intégralité des bâtiments candidats de $B_i$ sans parvenir à atteindre la taille cible $k_i$ (parce que les maisons sont trop denses ou la zone trop petite pour respecter $d_{min}$), et si l'option de relaxation est activée :
   * L'algorithme réduit la contrainte de distance minimale : $d_{min} \leftarrow d_{min} \times 0.85$.
   * Il réinitialise $S_i = \emptyset$ et relance la sélection sur les mêmes points mélangés.
   * Il répète cette réduction de manière itérative jusqu'à ce que la cible de taille $k_i$ soit atteinte ou que la distance minimale tombe en dessous d'un seuil de sécurité biologique/spatial absolu fixé à **$1.5$ mètres** (la taille d'une concession).
   * La distance minimale finale appliquée est enregistrée dans les attributs du point (`dist_m`) pour assurer une transparence méthodologique totale.

---

### C. Méthodes d'Allocation de la Taille d'Échantillon
L'outil propose trois méthodes d'allocation pour répondre aux différents designs d'études épidémiologiques :

#### 1. Taille Fixe
Chaque grappe (village) reçoit une cible d'échantillonnage identique :

$$k_i = K \quad (\forall i)$$

*Utilité* : Utilisé pour les enquêtes par grappes classiques de type OMS (ex : 30 grappes de 7 ou 15 ménages) où l'on cherche à simplifier la logistique des équipes de terrain.

#### 2. Pourcentage Constant
La cible est proportionnelle au nombre de concessions disponibles $N_i$ dans le village $i$, avec un minimum de sécurité de 1 ménage :

$$k_i = \max\left(1, \ \text{round}\left(N_i \times \frac{P}{100}\right)\right)$$

*Utilité* : Utilisé pour les enquêtes de couverture systématique ou de prévalence où l'on souhaite maintenir une fraction de sondage constante sur l'ensemble du territoire.

#### 3. Échantillonnage Proportionnel à la Taille (PPS - Probability Proportional to Size)
Pour un échantillon total désiré de $T$ ménages sur l'ensemble de la zone d'étude, la répartition de la cible $k_i$ pour chaque village est proportionnelle à sa population de toits par rapport à la population totale $N_{total}$ de la zone d'étude :

$$k_i = \max\left(1, \ \text{round}\left(T \times \frac{N_i}{N_{total}}\right)\right) \quad \text{où} \quad N_{total} = \sum_{j=1}^{M} N_j$$

*Utilité* : C'est le design de sondage de référence pour les enquêtes épidémiologiques stratifiées multi-étapes. Il garantit une auto-pondération de l'échantillon, simplifiant grandement l'analyse statistique ultérieure (pas besoin de calculer des poids de sondage complexes lors de l'estimation de la prévalence).

---

## 3. Précision Cartographique et Reprojections (UTM)

Pour assurer une précision métrique rigoureuse lors du calcul des tampons circulaires et de l'espacement entre ménages, l'outil effectue des reprojections géospatiales dynamiques.

### WGS84 vs UTM
* **Coordonnées Géographiques (WGS84 - EPSG:4326)** : Exprimées en degrés décimaux. C'est le système universel utilisé par les récepteurs GPS de terrain et les téléphones mobiles (OsmAnd). Cependant, un degré de longitude ne représente pas la même distance en mètres selon la latitude de l'équateur vers les pôles (distorsion de projection). Il est donc impossible de calculer précisément des tampons ou des distances métriques directement en WGS84.
* **Système de Projection UTM (Universal Transverse Mercator)** : Système de projection plane conforme qui divise la Terre en 60 fuseaux de 6 degrés de longitude. Dans chaque fuseau, les coordonnées sont exprimées en mètres (Nord et Est), ce qui permet d'effectuer des calculs de géométrie euclidienne plane d'une précision centimétrique.

### Algorithme d'Auto-Détection du Fuseau UTM Optimal
Pour libérer l'utilisateur de la sélection manuelle complexe du code de projection (EPSG), l'outil calcule dynamiquement le centre géographique de vos données d'entrée :

1. Il détermine le centre de gravité (centroïde) $(\lambda_{center}, \phi_{center})$ de la zone d'étude (Longitude, Latitude) en WGS84 :

$$\lambda_{center} = \frac{1}{n}\sum_{i=1}^n \lambda_i, \quad \phi_{center} = \frac{1}{n}\sum_{i=1}^n \phi_i$$

2. Il calcule le numéro du fuseau UTM correspondant :

$$\text{Zone UTM} = \lfloor \frac{\lambda_{center} + 180}{6} \rfloor + 1$$

3. Il détermine l'hémisphère pour obtenir le code EPSG officiel de l'EPSG registry :
   * Si $\phi_{center} \ge 0$ (Hémisphère Nord) : $\text{EPSG} = 32600 + \text{Zone UTM}$
   * Si $\phi_{center} < 0$ (Hémisphère Sud) : $\text{EPSG} = 32700 + \text{Zone UTM}$

*Exemple* : Pour des données situées à Dakar (Sénégal) à une longitude de $-17.47^\circ$ et une latitude de $+14.72^\circ$, l'outil calcule automatiquement :
$$\text{Zone UTM} = \lfloor \frac{-17.47 + 180}{6} \rfloor + 1 = \lfloor 27.08 \rfloor + 1 = 28$$
Le centre étant au Nord de l'équateur, le code EPSG appliqué est **`EPSG:32628` (WGS 84 / UTM zone 28N)**. 

Toutes les opérations géospatiales (création de tampons, spatial join, espacement minimal) sont réalisées dans ce repère métrique projeté, garantissant une **précision spatiale absolue au millimètre près**. À la fin du processus, les coordonnées des points échantillonnés sont re-projetées en WGS84 (`EPSG:4326`) pour être lisibles sur le terrain par les smartphones (OsmAnd) et Google Earth.

---

## 4. Références Documentaires et Académiques

Les méthodologies et algorithmes implémentés dans cet outil s'appuient sur les guides de référence internationaux et travaux académiques suivants :

1. **Organisation Mondiale de la Santé (OMS/WHO)** :
   * *Vaccination Coverage Cluster Survey Reference Manual* (WHO/IVB/18.09, 2018). Ce manuel recommande l'utilisation de bases de sondage spatiales basées sur la numérisation des concessions par satellite et l'exclusion des sélections non probabilistes de terrain.
2. **Médecins Sans Frontières (MSF) & Epicentre** :
   * *Méthodes de sondage spatial pour les enquêtes de mortalité et de couverture vaccinale en situation d'urgence*. Travaux de référence sur l'utilisation du SIG et du GPS hors-ligne pour la réduction des biais de sélection d'enquêteurs.
3. **Centers for Disease Control and Prevention (CDC)** :
   * *Multi-Indicator Cluster Surveys (MICS) & Demographic and Health Surveys (DHS) Sampling Manuals*. Guides méthodologiques sur la stratification géographique et l'échantillonnage systématique de concessions géoréférencées.
4. **Statistiques Spatiales (Inhibition de Strauss)** :
   * Diggle, P. J. (2013). *Statistical Analysis of Spatial and Spatio-Temporal Point Patterns*. CRC Press. Établit les fondations mathématiques des modèles de processus ponctuels contraints (Strauss et Hard-Core) utilisés pour modéliser la répulsion spatiale entre concessions.
   * Ripley, B. D. (1981). *Spatial Statistics*. John Wiley & Sons. Travaux pionniers sur l'analyse de dispersion ponctuelle et de représentativité spatiale.

---
*Document rédigé par **Pratisig Consulting Services**.*
*Pour toute question d'ordre théorique ou méthodologique, contactez **Youssoupha Mbodji** (pratisig.consulting@gmail.com)*
