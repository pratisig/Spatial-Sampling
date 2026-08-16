#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vendors all the CDN assets that Folium 0.20.0 references so the map can be
rendered fully OFFLINE (no internet / no CDN needed at runtime).

The assets are pulled from the public npm registry (registry.npmjs.org) as
version-pinned tarballs, then written to `assets/folium/`:
  - JS files are copied verbatim.
  - CSS files have every url(...) reference rewritten to a base64 data: URI
    (images and webfonts are inlined), so no external request is ever made.

Run from the repo root:  python tools/vendor_folium_assets.py
This runs on the CI build machine (which has internet) before PyInstaller,
and can also be run manually before a local build.
"""
import base64
import io
import os
import posixpath
import re
import shutil
import tarfile
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO_ROOT, "assets", "folium")

HEADERS = {"User-Agent": "Mozilla/5.0 (folio-asset-vendor)"}

# folium CDN URL  ->  (npm package, version, path inside the npm tarball)
ENTRIES = [
    # --- JS ---
    ("https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js",
     "leaflet", "1.9.3", "dist/leaflet.js"),
    ("https://code.jquery.com/jquery-3.7.1.min.js",
     "jquery", "3.7.1", "dist/jquery.min.js"),
    ("https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js",
     "bootstrap", "5.2.2", "dist/js/bootstrap.bundle.min.js"),
    ("https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js",
     "leaflet.awesome-markers", "2.0.4", "dist/leaflet.awesome-markers.js"),
    ("https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/leaflet.markercluster.js",
     "leaflet.markercluster", "1.1.0", "dist/leaflet.markercluster.js"),
    ("https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/leaflet.draw.js",
     "leaflet-draw", "1.0.2", "dist/leaflet.draw.js"),
    # --- CSS ---
    ("https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css",
     "leaflet", "1.9.3", "dist/leaflet.css"),
    ("https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css",
     "bootstrap", "5.2.2", "dist/css/bootstrap.min.css"),
    ("https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css",
     "@fortawesome/fontawesome-free", "6.2.0", "css/all.min.css"),
    ("https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css",
     "leaflet.awesome-markers", "2.0.4", "dist/leaflet.awesome-markers.css"),
    ("https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/MarkerCluster.css",
     "leaflet.markercluster", "1.1.0", "dist/MarkerCluster.css"),
    ("https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/MarkerCluster.Default.css",
     "leaflet.markercluster", "1.1.0", "dist/MarkerCluster.Default.css"),
    ("https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/leaflet.draw.css",
     "leaflet-draw", "1.0.2", "dist/leaflet.draw.css"),
]

# Local output filename for each CDN URL (stable, human readable).
def out_name(path_in_tarball):
    base = posixpath.basename(path_in_tarball)
    return base


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def npm_tarball_url(pkg: str, version: str) -> str:
    if pkg.startswith("@"):
        # @fortawesome/fontawesome-free -> fontawesome-free-6.2.0.tgz
        name = pkg.split("/", 1)[1]
        return "https://registry.npmjs.org/%s/-/%s-%s.tgz" % (pkg, name, version)
    return "https://registry.npmjs.org/%s/-/%s-%s.tgz" % (pkg, pkg, version)


def mime_from_name(name: str) -> str:
    n = name.lower()
    if n.endswith(".png"):
        return "image/png"
    if n.endswith(".woff2"):
        return "font/woff2"
    if n.endswith(".woff"):
        return "font/woff"
    if n.endswith(".ttf"):
        return "font/ttf"
    if n.endswith(".eot"):
        return "application/vnd.ms-fontobject"
    if n.endswith(".svg"):
        return "image/svg+xml"
    if n.endswith(".gif"):
        return "image/gif"
    return "application/octet-stream"


def rewrite_css_urls(css_text: str, files: dict, css_path: str) -> str:
    """Rewrite url(...) in a CSS string to base64 data: URIs, resolving
    relative paths against `css_path` inside the `files` dict."""
    def repl(match):
        raw = match.group(1).strip().strip("'\"")
        if raw.startswith(("data:", "http://", "https://", "//")):
            return match.group(0)
        # strip any query/fragment
        raw = raw.split("?")[0].split("#")[0]
        target = posixpath.normpath(posixpath.join(posixpath.dirname(css_path), raw))
        if target in files:
            data = files[target]
            mime = mime_from_name(target)
            return "url(data:%s;base64,%s)" % (mime, base64.b64encode(data).decode())
        return match.group(0)

    return re.sub(r"url\(\s*([^)]+?)\s*\)", repl, css_text)


def extract_package(pkg: str, version: str, cache_dir: str) -> dict:
    """Download and extract an npm tarball, return {path_in_tarball: bytes}."""
    url = npm_tarball_url(pkg, version)
    print("  fetching %s" % url)
    tgz = fetch(url)
    files = {}
    with tarfile.open(fileobj=io.BytesIO(tgz), mode="r:gz") as tf:
        for member in tf.getmembers():
            if not member.isfile():
                continue
            # npm tarballs have a single top-level "package/" dir
            path = member.name
            if path.startswith("package/"):
                path = path[len("package/"):]
            f = tf.extractfile(member)
            if f is not None:
                files[path] = f.read()
    return files


def main():
    if os.path.isdir(ASSETS):
        shutil.rmtree(ASSETS)
    os.makedirs(ASSETS, exist_ok=True)

    cache_dir = os.path.join(ASSETS, ".cache")
    os.makedirs(cache_dir, exist_ok=True)

    pkg_cache = {}

    for url, pkg, version, path_in_tarball in ENTRIES:
        if (pkg, version) not in pkg_cache:
            print("[pkg] %s@%s" % (pkg, version))
            pkg_cache[(pkg, version)] = extract_package(pkg, version, cache_dir)
        files = pkg_cache[(pkg, version)]

        if path_in_tarball not in files:
            raise SystemExit("ERROR: %s not found in %s@%s" % (path_in_tarball, pkg, version))

        data = files[path_in_tarball]
        fname = out_name(path_in_tarball)

        if fname.endswith(".css"):
            text = data.decode("utf-8", "ignore")
            text = rewrite_css_urls(text, files, path_in_tarball)
            data = text.encode("utf-8")

        dest = os.path.join(ASSETS, fname)
        with open(dest, "wb") as f:
            f.write(data)
        print("  -> %s (%d bytes)" % (fname, len(data)))

    shutil.rmtree(cache_dir, ignore_errors=True)

    total = sum(os.path.getsize(os.path.join(ASSETS, n)) for n in os.listdir(ASSETS) if n.endswith((".js", ".css")))
    print("\nDone. JS/CSS assets in %s (~%d KB)" % (ASSETS, total // 1024))


if __name__ == "__main__":
    main()
