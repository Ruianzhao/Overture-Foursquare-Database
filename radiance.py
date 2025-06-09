import rasterio
from rasterio.transform import rowcol
import pandas as pd
import os

# Folder Path, change when you use the code
folder_path = "/Users/magicsquirrel/Developer/workstudy/radiance_tif_files"

# Dictionary of target cities with lat/lon
cities = {
    "Toronto": (43.651070, -79.347015),
    "Sydney": (-33.865143, 151.209900),
    "Beijing": (39.916668, 116.383331)
}

# List to store the data from each city in each year
results = []

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
            for city, (lat, lon) in cities.items():
                try:
                    # This transforms the lat lon into pixel coordinates
                    row, col = rowcol(src.transform, lon, lat)
                    # This gets the value stored at the pixel coordinate(Radiance value)
                    value = band1[row, col]
                    # Appends to the results a dictionary containing the city, radiance and
                    # year
                    results.append({
                        "city": city,
                        "radiance": value,
                        "year": int(year)
                    })
                # This is here just in case we go out of bounds or something
                except Exception as e:
                    results.append({
                        "city": city,
                        "radiance": None,
                        "error": str(e),
                        "year": 0
                    })


# Convert the list of dictionaries into a dataframe
df = pd.DataFrame(results)

# Pivot the dataframe so that the years are the rows, and the columns are
# The cities and their radiance values in that year
pivoted_df = df.pivot_table(index="year", columns="city", values="radiance")

# Sort by year and export
pivoted_df = pivoted_df.sort_index()
pivoted_df.to_csv("city_nightlight_1992-2023.csv")

