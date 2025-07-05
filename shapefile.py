import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import pandas as pd
import numpy as np


# Path to the GHSL Urban Centre GPKG file and the appropriate theme layer
ghsl_path = "/Users/magicsquirrel/Developer/workstudy/city_shapefiles/GHS_UCDB_GLOBE_R2024A.gpkg"
ghsl_layer = "GHS_UCDB_THEME_GENERAL_CHARACTERISTICS_GLOBE_R2024A"

# Directory containing your .tif nighttime light rasters
tif_folder = "/Users/magicsquirrel/Developer/workstudy/radiance_tif_files"

# City names mapped to their GHSL "GC_UCN_MAI_2025" field
target_cities = {
    "Toronto": "Toronto",
    "Sydney": "Sydney",
    "Beijing": "Beijing"
}

# Load the GHSL vector data

# Load the specified GHSL theme layer
ghs = gpd.read_file(ghsl_path, layer=ghsl_layer)

# Ensure the GeoDataFrame has a valid CRS
if ghs.crs is None:
    ghs.set_crs("EPSG:4326", inplace=True)


results = {city: [] for city in target_cities}

for filename in os.listdir(tif_folder):
    if not filename.endswith(".tif"):
        continue

    file_path = os.path.join(tif_folder, filename)

    # Extract year using digits from filename
    year =  filename.split('_')[-1].removesuffix('.tif')

    with rasterio.open(file_path) as src:
        raster_crs = src.crs

        for city_name, ghsl_match_name in target_cities.items():
            # Filter GHSL data for city match
            city_poly = ghs[ghs["GC_UCN_MAI_2025"].str.lower() == ghsl_match_name.lower()]

            if city_poly.empty:
                print(f"Warning: No match found in GHSL for {city_name} using '{ghsl_match_name}'")
                continue

            # Reproject city polygon to match raster CRS
            city_poly_proj = city_poly.to_crs(raster_crs)

            try:
                # Apply mask and crop raster to city polygon
                out_image, _ = mask(src, city_poly_proj.geometry, crop=True)
                data = out_image[0]

                # Mask low or invalid values (typically ocean/empty areas)
                masked = np.ma.masked_where(data <= 0.1, data)

                # Collect stats
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
                # Handle errors during masking or stats calculation
                stats = {
                    "year": year,
                    "sum": None, "mean": None, "median": None,
                    "min": None, "max": None, "count": None,
                    "error": str(e)
                }

            results[city_name].append(stats)

for city, records in results.items():
    df = pd.DataFrame(records).sort_values("year")
    df.set_index("year", inplace=True)
    df.to_csv(f"{city.lower()}_ntl_summary_ghsl_1992-2023.csv")

