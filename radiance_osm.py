import os
import osmnx as ox
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import mapping

# Folder containing your GeoTIFF files
folder_path = "/Users/magicsquirrel/Developer/workstudy/radiance_harmony_files"

# Dictionary for each city, and what the OSM query will be
city_queries = {
    "Toronto": "Toronto, Canada",
    "Sydney": "Sydney, Australia",
    "Beijing": "Beijing, China"
}

for city_name, query in city_queries.items():
    city_poly = ox.geocode_to_gdf(query)
    
    city_results = []

    for file in os.listdir(folder_path):
        if file.endswith(".tif"):
            #year = file.split('_')[-1].replace(".tif", "")
            year = file.split('_')[3]
            file_path = os.path.join(folder_path, file)

            try:
                with rasterio.open(file_path) as src:
                    # Reproject city boundary to match raster coordinate system
                    city_poly_proj = city_poly.to_crs(src.crs)

                    # Use the mask function to crop the raster to the city polygon
                    out_image, _ = mask(src, city_poly_proj.geometry, crop=True)
                    data = out_image[0]
                    # Drop any data points where the radiance is below 0
                    masked = np.ma.masked_where(data <= 0, data)

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
    df.to_csv(f"{city_name.lower()}_ntl_summary_osm_harmony_1992-2020.csv")