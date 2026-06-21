# -*- coding: utf-8 -*-
"""
fix_geojson_gaps.py
Repara topologia del GeoJSON de comunas:
- Rellena gaps entre comunas adyacentes
- Clipea para que NO se sobrepongan
Resultado: sin gaps NI solapas.
"""
import json
import shapely
import geopandas as gpd
from shapely.validation import make_valid

SRC = "Datos/comunas.geojson"
MAX_GAP_DEG = 0.012

with open(SRC, encoding="utf-8") as f:
    data = json.load(f)

rows = []
for feat in data["features"]:
    if feat["geometry"]:
        geom = make_valid(shapely.from_geojson(json.dumps(feat["geometry"])))
        row = feat["properties"].copy()
        row["geometry"] = geom
        rows.append(row)

gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")
mask5 = (gdf["codregion"] == 5) & (~gdf["Comuna"].isin(["Isla de Pascua", "Juan Fernandez"]))

reg5 = gdf[mask5].copy()
comunas = list(reg5.itertuples())
gaps = []
for i, a in enumerate(comunas):
    for b in comunas[i+1:]:
        d = a.geometry.distance(b.geometry)
        if 0 < d < MAX_GAP_DEG:
            gaps.append((d, a.Index, b.Index, a.Comuna, b.Comuna))
gaps.sort(reverse=True)
print(f"Pares con gap: {len(gaps)}")
for d, ia, ib, ca, cb in gaps:
    print(f"  {d:.6f} ({d*111000:.0f} m)  {ca} -- {cb}")

repaired = 0
for d, idx_a, idx_b, name_a, name_b in gaps:
    geom_a = gdf.at[idx_a, "geometry"]
    geom_b = gdf.at[idx_b, "geometry"]

    half = d / 2 + 0.0002
    exp_a = geom_a.buffer(half)
    exp_b = geom_b.buffer(half)
    corridor = exp_a.intersection(exp_b)

    if corridor.is_empty:
        print(f"  SKIP: corredor vacio {name_a} -- {name_b}")
        continue

    # A toma el corredor completo
    new_a = make_valid(geom_a.union(corridor))
    # B toma solo la parte del corredor que no quedo en A, y se clipea con A
    gap_for_b = corridor.difference(new_a)
    new_b = make_valid(geom_b.union(gap_for_b)) if not gap_for_b.is_empty else geom_b
    new_b = make_valid(new_b.difference(new_a))

    gdf.at[idx_a, "geometry"] = new_a
    gdf.at[idx_b, "geometry"] = new_b
    repaired += 1
    print(f"  OK: {name_a} -- {name_b}")

print(f"\nReparados: {repaired}/{len(gaps)}")
print(f"Invalidas: {(~gdf.geometry.is_valid).sum()}")

reg5_new = gdf[mask5].copy()
remaining = []
for i, a in enumerate(list(reg5_new.itertuples())):
    for b in list(reg5_new.itertuples())[i+1:]:
        d = a.geometry.distance(b.geometry)
        if 0 < d < MAX_GAP_DEG:
            remaining.append((d, a.Comuna, b.Comuna))

if remaining:
    print(f"\nGaps restantes ({len(remaining)}):")
    for d, ca, cb in sorted(remaining, reverse=True):
        print(f"  {d:.6f} ({d*111000:.0f} m)  {ca} -- {cb}")
else:
    print("\nTodos los gaps cerrados sin solapas.")

gdf.to_file(SRC, driver="GeoJSON")
print(f"Guardado: {SRC}")
