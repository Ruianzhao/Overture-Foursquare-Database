import pandas as pd
import os
from collections import Counter

folder_path = "/Users/magicsquirrel/Developer/workstudy/places foursquare/parquet_files"

def generateCategoryTable(df, cityName):
    # Drop missing level_2 values for consistent counting
    df_clean = df.dropna(subset=['level_2'])

    # Count level 1 categories
    level1_counts = df_clean['level_1'].value_counts().reset_index()
    level1_counts.columns = ['Category', 'Count']
    level1_counts['Percentage'] = (level1_counts['Count'] / level1_counts['Count'].sum()) * 100
    level1_counts['City'] = cityName
    level1_counts = level1_counts.sort_values(by='Count', ascending=False)

    # Count level 2 categories
    level2_counts = df_clean['level_2'].value_counts().reset_index()
    level2_counts.columns = ['Category', 'Count']
    level2_counts['Percentage'] = (level2_counts['Count'] / level2_counts['Count'].sum()) * 100
    level2_counts['City'] = cityName
    level2_counts = level2_counts.sort_values(by='Count', ascending=False)

    # Save
    os.makedirs('level1_cat_summary', exist_ok=True)
    os.makedirs('level2_cat_summary', exist_ok=True)

    output_path1 = os.path.join('level1_cat_summary', f"{cityName.lower()}_level1_category_summary.csv")
    output_path2 = os.path.join('level2_cat_summary', f"{cityName.lower()}_level2_category_summary.csv")

    level1_counts.to_csv(output_path1, index=False)
    level2_counts.to_csv(output_path2, index=False)

# Iterates through all the parquet files in the folder and generates their
# raw csv, and category summaries
for file in os.listdir(folder_path):
    if file.endswith('.parquet'):
        file_path = os.path.join(folder_path, file)
        df = pd.read_parquet(file_path, engine='auto')
        file_name = file.removesuffix('_places.parquet')
        
        output_path = os.path.join('raw_parquet_files', f"{file_name}_places.csv")
        df.to_csv(output_path, index=False)
        
        df_exploded = df.explode('fsq_category_labels')
        split_df = df_exploded['fsq_category_labels'].str.split(' > ', expand=True)
        split_df.columns = [f'level_{i+1}' for i in range(split_df.shape[1])]
        generateCategoryTable(split_df, file_name)