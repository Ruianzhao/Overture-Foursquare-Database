import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import pandas as pd
import numpy as np

# Path to the GHSL Urban Centre GPKG file and its correct layer
ghsl_path = ""
ghsl_layer = "GHS_UCDB_THEME_GENERAL_CHARACTERISTICS_GLOBE_R2024A"

# Load the GHSL Urban Centres GeoDataFrame
ghs = gpd.read_file(ghsl_path, layer=ghsl_layer)

# Define target cities and the matching values in the GHSL file
target_cities = {
    "Edmonton": "Edmonton",
    "Montreal": "Montreal",
    "Ottawa": "Ottawa"
}

# Path to folder containing GeoTIFF files
tif_folder = ""

output_folder = ""

# Container for city-wise results
results = {city: [] for city in target_cities}

# Loop through all GeoTIFF files
for file in os.listdir(tif_folder):
    if not file.endswith(".tif"):
        continue
    
    year = file.split('_')[-1].replace(".tif", "")
    file_path = os.path.join(tif_folder, file)

    # Open raster
    with rasterio.open(file_path) as src:
        raster_crs = src.crs

        for city_name, ghsl_name in target_cities.items():
            # Select the city polygon by name
            poly = ghs[ghs["GC_UCN_MAI_2025"] == ghsl_name]

            if poly.empty:
                print(f"Warning: {city_name} not found in GHSL shapefile.")
                continue

            # Reproject to raster CRS
            poly_proj = poly.to_crs(raster_crs)

            try:
                # Mask raster using polygon
                out_image, _ = mask(src, poly_proj.geometry, crop=True)
                data = out_image[0]
                
                # Mask out nonpositive values (e.g., ocean, no data, etc.)
                masked = np.ma.masked_where(data <= 0.1, data)

                stats = {
                    "year": int(year),
                    "sum": float(masked.sum()),
                    "mean": float(masked.mean()),
                    "median": float(np.ma.median(masked)),
                    "min": float(masked.min()),
                    "max": float(masked.max()),
                    "count": int(masked.count())
                }
            except Exception as e:
                stats = {
                    "year": int(year),
                    "sum": None, "mean": None, "median": None,
                    "min": None, "max": None, "count": None,
                    "error": str(e)
                }

            results[city_name].append(stats)

# Save output CSVs
for city, records in results.items():
    df = pd.DataFrame(records).sort_values("year")
    df.set_index("year", inplace=True)
    df.to_csv(f"{output_folder}/{city.lower()}_ntl_summary_ghsl_1992-2023.csv")
