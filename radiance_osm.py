import os
import osmnx as ox
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import mapping

# Folder containing your GeoTIFF files
folder_path = "/Users/magicsquirrel/Developer/workstudy/radiance_tif_files"

output_folder = "/Users/magicsquirrel/Developer/workstudy/radiance_OSM/Bounding Poly"

# Dictionary for each city, and what the OSM query will be
city_queries = {
    "Beijing": "Beijing, China",
    "Tianjin": "Tianjin, China",
    "Shanghai": "Shanghai, China",
    "Chengdu": "Chengdu, China"
}

for city_name, query in city_queries.items():
    city_poly = ox.geocode_to_gdf(query)
    
    city_results = []

    for file in os.listdir(folder_path):
        if file.endswith(".tif"):
            year = file.split('_')[-1].replace(".tif", "")
            file_path = os.path.join(folder_path, file)

            try:
                with rasterio.open(file_path) as src:
                    # Reproject city boundary to match raster coordinate system
                    city_poly_proj = city_poly.to_crs(src.crs)

                    # Use the mask function to crop the raster to the city polygon
                    out_image, _ = mask(src, city_poly_proj.geometry, crop=True)
                    data = out_image[0]
                    # Clean up invalid fill values first (from old DMSP)
                    data = np.where(data <= -1e38, np.nan, data)

                    # Apply a unified mask that filters both invalid and low radiance
                    masked = np.ma.masked_where((data <= 3.5) | np.isnan(data), data)

                    valid_data = masked.compressed()

                    if len(valid_data) > 0:
                        lower = np.percentile(valid_data, 0.5)
                        upper = np.percentile(valid_data, 99.93)

                        trimmed = np.ma.masked_outside(masked, lower, upper)

                        stats = {
                            "year": year,
                            "sum": float(trimmed.sum()),
                            "mean": float(trimmed.mean()),
                            "median": float(np.ma.median(trimmed)),
                            "min": float(trimmed.min()),
                            "max": float(trimmed.max()),
                            "count": int(trimmed.count())
                        }
                    else:
                        stats = {
                            "year": year,
                            "sum": None, "mean": None, "median": None,
                            "min": None, "max": None, "count": None,
                            "error": f"No valid data in {city_name} for year {year}"
                        }

            except Exception as e:
                stats = {
                    "year": year,
                    "sum": None,
                    "mean": None,
                    "median": None,
                    "min": None,
                    "max": None,
                    "count": None,
                    "error": str(e)
                }

            city_results.append(stats)

    # Save CSV
    df = pd.DataFrame(city_results).sort_values("year")
    df.set_index("year", inplace=True)
    df.to_csv(f"{output_folder}/{city_name.lower()}_ntl_summary_osm_polygon_1992-2023.csv")