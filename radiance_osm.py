import os
import osmnx as ox
import rasterio
import rasterio.mask
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import mapping

# Folder containing your GeoTIFF files
folder_path = "/Users/magicsquirrel/Developer/workstudy/radiance_tif_files"

# Dictionary for each city, and what the OSM query will be
city_queries = {
    "Toronto": "Financial District, Toronto, Ontario, Canada",
    "Sydney": "Sydney CBD, New South Wales, Australia",
    "Beijing": "Dongcheng, Beijing, China"
}

# Dictionary to store the data from each city in each year
results = {city: [] for city in city_queries}

for file in os.listdir(folder_path):
    if file.endswith(".tif"):
        year = file.split('_')[-1].replace(".tif", "")
        file_path = os.path.join(folder_path, file)

        with rasterio.open(file_path) as src:
            raster_crs = src.crs

            # Loops through all the cities and tries to use OSM queries
            # To find the bounding polygon
            for city, query in city_queries.items():
                try:
                    # Query OSM and retrieve the polygon boundary of each cities 
                    # specified region
                    gdf = ox.geocode_to_gdf(query)
                    
                    # Reproject the polygon to the rasters image's coordinate system
                    gdf = gdf.to_crs(raster_crs)
                    
                    # Convert the polygon geometry to a GeoJSON format for masking
                    geom = [mapping(gdf.geometry.iloc[0])]

                    # Crop the raster to the city polygon
                    masked, _ = rasterio.mask.mask(src, geom, crop=True)
                    
                    #Extract the radiance values, and remove radiance values of 0
                    data = masked[0]
                    data = np.ma.masked_where(data <= 0, data)

                    stats = {
                        "year": int(year),
                        "sum": float(data.sum()),
                        "mean": float(data.mean()),
                        "min": float(data.min()),
                        "max": float(data.max()),
                        "count": int(data.count())
                    }
                except Exception as e:
                    stats = {
                        "year": int(year),
                        "sum": None,
                        "mean": None,
                        "min": None,
                        "max": None,
                        "count": 0,
                        "error": str(e)
                    }

                results[city].append(stats)

# Export CSVs per city
for city, data in results.items():
    df = pd.DataFrame(data).sort_values("year")
    df.set_index("year", inplace=True)
    df.to_csv(f"{city.lower()}_downtown_ntl_summary.csv")
