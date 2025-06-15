import rasterio
from rasterio.transform import rowcol
import pandas as pd
import os
import numpy as np

# Folder Path, change when you use the code
folder_path = "/Users/magicsquirrel/Developer/workstudy/radiance_tif_files"

# Dictionary of target cities with lat/lon
cities = {
    "Toronto": (-79.639283, 43.579608, -79.113219, 43.855443),
    "Sydney": (150.2608, -34.1732, 151.3439, -33.3642),
    "Beijing": (115.4172, 39.1707, 117.7371, 41.0596)
}

# List to store the data from each city in each year
results = {city: [] for city in cities}

# This loops through all the files in the folder containing the .tif files
for file in os.listdir(folder_path):
    if file.endswith('.tif'):
        year = file.split('_')[-1].removesuffix('.tif')
        file_path = os.path.join(folder_path, file)
        
        # Open the raster file
        with rasterio.open(file_path) as src:
            # Read the first band which contains radiance data
            band1 = src.read(1) 
            
            # This loops tries to find the radiance values for each city
            for city, (west, south, east, north) in cities.items():
                row_min, col_min = rowcol(src.transform, west, north)
                row_max, col_max = rowcol(src.transform, east, south)
                rmin, rmax = sorted([row_min, row_max])
                cmin, cmax = sorted([col_min, col_max])
                
                window = band1[rmin:rmax, cmin:cmax]
                masked = np.ma.masked_where(window <= 0, window)
                
                stats = {
                    "year": year,
                    "sum": float(masked.sum()),
                    "mean": float(masked.mean()),
                    "min": float(masked.min()),
                    "max": float(masked.max()),
                    "count": int(masked.count())
                }
                results[city].append(stats)


for city, records in results.items():
    df = pd.DataFrame(records).sort_values("year")
    df.set_index("year", inplace=True)
    df.to_csv(f"{city.lower()}_ntl_summary_1992-2023.csv")
