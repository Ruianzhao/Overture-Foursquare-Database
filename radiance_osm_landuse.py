import os
import osmnx as ox
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import pandas as pd
import numpy as np

# Folder containing your GeoTIFF files
folder_path = "/Users/magicsquirrel/Developer/workstudy/radiance_tif_files"

# Dictionary for each city, and what the OSM query will be
city_queries = {
    "Toronto": "Toronto, Canada",
    "Sydney": "Sydney, Australia",
    "Beijing": "Beijing, China"
}

for city_name, query in city_queries.items():
    
    # Get polygon for the city
    city_poly = ox.geocode_to_gdf(query)

    # Query industrial and commercial land use areas from OSM
    tags = {'landuse': ['industrial', 'commercial']}
    landuse_gdf = ox.features_from_place(query, tags=tags)

    if landuse_gdf.empty or landuse_gdf.geometry.is_empty.all():
        print(f" No landuse polygons found for {city_name}. Skipping.")
        continue

    # Clean invalid geometries
    landuse_gdf = landuse_gdf[~landuse_gdf.geometry.is_empty]
    landuse_gdf = landuse_gdf[landuse_gdf.is_valid]

    # Clip landuse by city polygon to remove outliers
    landuse_gdf = gpd.clip(landuse_gdf, city_poly)

    if landuse_gdf.empty:
        print(f" All landuse geometries were removed after clipping for {city_name}.")
        continue

    # Merge geometries and buffer slightly (0.001 deg or roughly 100m)
    landuse_union = landuse_gdf.geometry.unary_union.buffer(0.001)
    landuse_gdf = gpd.GeoDataFrame(geometry=[landuse_union], crs=landuse_gdf.crs)

    city_results = []

    for file in os.listdir(folder_path):
        if not file.endswith(".tif"):
            continue

        # Extract year
        year =  file.split('_')[-1].removesuffix('.tif')
        file_path = os.path.join(folder_path, file)

        try:
            with rasterio.open(file_path) as src:
                # Reproject landuse polygon to match raster CRS
                landuse_proj = landuse_gdf.to_crs(src.crs)

                # Mask raster using reprojected landuse
                out_image, _ = mask(src, landuse_proj.geometry, crop=True)
                data = out_image[0]

                # Drop radiance ≤ 3.5
                masked = np.ma.masked_where(data <= 3.5, data)

                stats = {
                    "year": year,
                    "sum": float(masked.sum()),
                    "mean": float(masked.mean()),
                    "median": float(np.ma.median(masked)),
                    "min": float(masked.min()),
                    "max": float(masked.max()),
                    "count": int(masked.count())
                }

        except Exception as e:
            stats = {
                "year": year,
                "sum": None, "mean": None, "median": None,
                "min": None, "max": None, "count": None,
                "error": str(e)
            }

        city_results.append(stats)

    # Save results to CSV
    df = pd.DataFrame(city_results).sort_values("year")
    df.set_index("year", inplace=True)
    df.to_csv(f"{city_name.lower()}_ntl_summary_osm_landuse_1992-2020.csv")
