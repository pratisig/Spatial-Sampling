# -*- coding: utf-8 -*-
"""
Rendu OFFLINE des cartes Folium.

Folium génère du HTML qui charge Leaflet et tous ses plugins depuis des CDN
(cdn.jsdelivr.net, cdnjs.cloudflare.com, code.jquery.com, ...). Quand la machine
n'a pas accès à Internet (ou que ces CDN sont bloqués/lents — fréquent sur le
terrain), la carte s'affiche en blanc.

Ce module remplace ces ressources distantes par des `data:` URI construites à
partir des fichiers locaux vendored dans `assets/folium/`
(voir tools/vendor_folium_assets.py), ce qui rend la carte 100% autonome.

Il suffit d'appeler `patch_folium_offline()` une fois au démarrage, avant de
créer une carte : cela corrige à la fois `st_folium` (mode script) et
`folium_static` (mode exécutable compilé).

Les tuiles de fond (OpenStreetMap / Esri) restent chargées depuis Internet :
hors connexion, la carte, les points et les contrôles s'affichent quand même
(fond gris), et le fond de carte apparaît dès qu'une connexion est disponible.
"""
import base64
import os
import sys

# URL CDN -> nom de fichier local dans assets/folium/
# (doit rester synchronisé avec tools/vendor_folium_assets.py, Folium 0.20.0)
CDN_TO_FILE = {
    # JS
    "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js": "leaflet.js",
    "https://code.jquery.com/jquery-3.7.1.min.js": "jquery.min.js",
    "https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js": "bootstrap.bundle.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js": "leaflet.awesome-markers.js",
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/leaflet.markercluster.js": "leaflet.markercluster.js",
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/leaflet.draw.js": "leaflet.draw.js",
    # CSS
    "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css": "leaflet.css",
    "https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css": "bootstrap.min.css",
    "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css": "all.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css": "leaflet.awesome-markers.css",
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/MarkerCluster.css": "MarkerCluster.css",
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/MarkerCluster.Default.css": "MarkerCluster.Default.css",
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/leaflet.draw.css": "leaflet.draw.css",
}

# URL non nécessaires pour cette application -> on les retire simplement.
DROP_URLS = {
    # Icônes glyphicons (Bootstrap 3) : l'app utilise FontAwesome (prefix="fa").
    "https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap-glyphicons.css",
    # Rotation d'icônes : non utilisée.
    "https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css",
}


def _assets_dir():
    # 1) À côté de ce fichier offline_folium.py (dossier du repo, ou dossier
    #    de l'exécutable quand il y est copié par build_exe.py).
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "folium")
    if os.path.isdir(local):
        return local
    # 2) Dans le bundle PyInstaller (_MEIPASS), en secours.
    base = getattr(sys, "_MEIPASS", None)
    if base:
        bundled = os.path.join(base, "assets", "folium")
        if os.path.isdir(bundled):
            return bundled
    return local


def _to_data_uri(fname):
    with open(os.path.join(_assets_dir(), fname), "rb") as f:
        data = f.read()
    mime = "text/css" if fname.endswith(".css") else "application/javascript"
    return "data:%s;base64,%s" % (mime, base64.b64encode(data).decode())


def _patch_link_list(links):
    """Transforme une liste [(name, url), ...] de folium en version hors-ligne."""
    out = []
    for name, url in links:
        if url in DROP_URLS:
            continue
        if url in CDN_TO_FILE:
            try:
                out.append((name, _to_data_uri(CDN_TO_FILE[url])))
                continue
            except OSError:
                # Asset manquant : on garde l'URL CDN d'origine (repli).
                pass
        out.append((name, url))
    return out


_PATCHED = False


def patch_folium_offline():
    """Remplace les ressources CDN de Folium par des data: URI locales.

    À appeler une fois au démarrage, avant de créer les cartes. Idempotente :
    Streamlit relance le script à chaque interaction, mais cette fonction ne
    refait le travail (lecture + base64 des assets) que la première fois.
    """
    global _PATCHED
    if _PATCHED:
        return

    import folium.folium as _fm
    from folium.plugins import MarkerCluster as _MarkerCluster
    from folium.plugins import Draw as _Draw

    # Carte de base (folium.Map)
    _fm._default_js[:] = _patch_link_list(_fm._default_js)
    _fm._default_css[:] = _patch_link_list(_fm._default_css)

    # Plugin MarkerCluster (regroupement des bâtiments)
    _MarkerCluster.default_js[:] = _patch_link_list(_MarkerCluster.default_js)
    _MarkerCluster.default_css[:] = _patch_link_list(_MarkerCluster.default_css)

    # Plugin Draw (outil de dessin / repositionnement)
    _Draw.default_js[:] = _patch_link_list(_Draw.default_js)
    _Draw.default_css[:] = _patch_link_list(_Draw.default_css)

    _PATCHED = True
