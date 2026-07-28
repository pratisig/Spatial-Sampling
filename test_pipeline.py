import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
from shapely.ops import voronoi_diagram

# 1. Generate Simulated Data
villages = [
    ('Ngor', -17.51, 14.75),
    ('Yoff', -17.47, 14.76),
    ('Fann', -17.47, 14.69),
    ('Medina', -17.44, 14.70)
]

vill_points = [Point(lon, lat) for _, lon, lat in villages]
vill_names = [name for name, _, _ in villages]
vill_gdf = gpd.GeoDataFrame({'nom_vill': vill_names}, geometry=vill_points, crs='EPSG:4326')

bld_points = []
for name, lon, lat in villages:
    # Generate 30 buildings per village with some noise
    np.random.seed(42)
    lons = np.random.normal(lon, 0.003, 30)
    lats = np.random.normal(lat, 0.003, 30)
    for lo, la in zip(lons, lats):
        bld_points.append(Point(lo, la))
        
bld_gdf = gpd.GeoDataFrame({'bld_id': range(len(bld_points))}, geometry=bld_points, crs='EPSG:4326')

# 2. Determine UTM
centroid = vill_gdf.geometry.union_all().centroid
lon, lat = centroid.x, centroid.y
utm_zone = int(np.floor((lon + 180) / 6) + 1)
utm_epsg = 32600 + utm_zone if lat >= 0 else 32700 + utm_zone
print(f"Centroid: {lon:.4f}, {lat:.4f} -> UTM EPSG: {utm_epsg}")

# 3. Project to UTM
vill_utm = vill_gdf.to_crs(epsg=utm_epsg)
bld_utm = bld_gdf.to_crs(epsg=utm_epsg)

# 4. Create Catchment Areas
search_radius_m = 1000.0
buffers = vill_utm.geometry.buffer(search_radius_m)

multipoint = MultiPoint(vill_utm.geometry.tolist())
vor = voronoi_diagram(multipoint)

catchments = []
for idx, row in vill_utm.iterrows():
    p = row.geometry
    buf = buffers.iloc[idx]
    matched_cell = None
    for cell in vor.geoms:
        if cell.contains(p) or cell.distance(p) < 1e-9:
            matched_cell = cell
            break
    if matched_cell is not None:
        catchment = buf.intersection(matched_cell)
        catchments.append(catchment)
    else:
        catchments.append(buf)

catchments_utm = gpd.GeoDataFrame(vill_utm.copy(), geometry=catchments, crs=f"EPSG:{utm_epsg}")
print(f"Catchment polygons created: {len(catchments_utm)}")

# 5. Spatial Join
bld_with_village = gpd.sjoin(bld_utm, catchments_utm, how="inner", predicate="intersects")
print(f"Buildings assigned to villages: {len(bld_with_village)}")

# 6. Sample with distance constraint
def sample_village(group_df, sample_size, min_dist_m, name_field):
    points = list(group_df.geometry)
    v_name = group_df[name_field].iloc[0]
    
    if len(points) <= sample_size:
        res = group_df.copy()
        res['actual_dist'] = 0.0
        res['status'] = 'All Selected'
        return res
        
    np.random.seed()
    shuffled_indices = np.random.permutation(len(points))
    shuffled_points = [points[i] for i in shuffled_indices]
    shuffled_rows = group_df.iloc[shuffled_indices].copy()
    
    current_min_dist = min_dist_m
    attempts = 0
    max_attempts = 10
    
    while current_min_dist >= 2.0 and attempts < max_attempts:
        selected_indices = []
        selected_geoms = []
        
        for i, geom in enumerate(shuffled_points):
            is_valid = True
            for sel_geom in selected_geoms:
                if geom.distance(sel_geom) < current_min_dist:
                    is_valid = False
                    break
            if is_valid:
                selected_indices.append(i)
                selected_geoms.append(geom)
            if len(selected_geoms) == sample_size:
                break
                
        if len(selected_geoms) == sample_size:
            break
            
        current_min_dist *= 0.85
        attempts += 1
        
    selected_df = shuffled_rows.iloc[selected_indices].copy()
    selected_df['actual_dist'] = current_min_dist
    selected_df['status'] = 'Sampled' if len(selected_geoms) == sample_size else 'Partial'
    return selected_df

sampled_list = []
for name, group in bld_with_village.groupby('nom_vill'):
    sampled_group = sample_village(group, 10, 50.0, 'nom_vill')
    sampled_list.append(sampled_group)
    print(f"Village {name}: desired=10, selected={len(sampled_group)}, status={sampled_group['status'].iloc[0]}, min_dist={sampled_group['actual_dist'].iloc[0]:.1f}m")

sampled_all = gpd.GeoDataFrame(pd.concat(sampled_list, ignore_index=True), crs=f"EPSG:{utm_epsg}")
print(f"Total sampled points: {len(sampled_all)}")

