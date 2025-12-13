import pandas as pd
import os
from collections import Counter

def generateCategoryTable(df1, df2, cityName):
    # Drop missing level_2 values for consistent counting
    df_clean = df1.dropna(subset=['level_2'])
    df_3 = df1.dropna(subset=['level_3'])

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
    
    # Count level 3 categories
    level3_counts = df_3['level_3'].value_counts().reset_index()
    level3_counts.columns = ['Category', 'Count']
    level3_counts['Percentage'] = (level3_counts['Count'] / level3_counts['Count'].sum()) * 100
    level3_counts['City'] = cityName
    level3_counts = level3_counts.sort_values(by='Count', ascending=False)
    
    df2_counts = df2['truncated_category'].value_counts().reset_index()
    df2_counts.columns = ['Category', 'Count']
    df2_counts['Percentage'] = (df2_counts['Count'] / df2_counts['Count'].sum()) * 100
    df2_counts['City'] = cityName
    df2_counts = df2_counts.sort_values(by='Count', ascending=False)

    # Save
    os.makedirs('places foursquare/Canadian/level1_cat_summary', exist_ok=True)
    os.makedirs('places foursquare/Canadian/level2_cat_summary', exist_ok=True)
    os.makedirs('places foursquare/Canadian/level3_cat_summary', exist_ok=True)
    os.makedirs('places foursquare/Canadian/truncated_cat_summary', exist_ok=True)

    output_path1 = os.path.join('places foursquare/Canadian/level1_cat_summary', f"{cityName.lower()}_category_summary.csv")
    output_path2 = os.path.join('places foursquare/Canadian/level2_cat_summary', f"{cityName.lower()}_category_summary.csv")
    output_path3 = os.path.join('places foursquare/Canadian/level3_cat_summary', f"{cityName.lower()}_category_summary.csv")
    output_path4 = os.path.join('places foursquare/Canadian/truncated_cat_summary', f"{cityName.lower()}_truncated_category_summary.csv")

    level1_counts.to_csv(output_path1, index=False)
    level2_counts.to_csv(output_path2, index=False)
    level3_counts.to_csv(output_path3, index=False)
    df2_counts.to_csv(output_path4, index=False)

folder_path = ""

# Iterates through all the parquet files in the folder and generates their
# raw csv, and category summaries
for file in os.listdir(folder_path):
    if file.endswith('.parquet'):
        file_path = os.path.join(folder_path, file)
        df = pd.read_parquet(file_path, engine='auto')
        file_name = file.removesuffix('_places.parquet')
        
        output_path = os.path.join('places foursquare/Canadian/raw_csv_files', f"{file_name}_places.csv")
        df.to_csv(output_path, index=False)
        
        df_exploded = df.explode('fsq_category_labels')
        split_df1 = df_exploded['fsq_category_labels'].str.split(' > ', expand=True)
        split_df1.columns = [f'level_{i+1}' for i in range(split_df1.shape[1])]
        df_exploded = df_exploded.dropna(subset=['fsq_category_labels'])
        df_exploded['truncated_category'] = df_exploded['fsq_category_labels'].apply(
            lambda x: ' > '.join(x.split(' > ')[:3])
        )
        generateCategoryTable(split_df1, df_exploded, file_name)
