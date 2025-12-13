#This program allows you to easily combine csv files between different cities into one 
#csv file

import pandas as pd
import os

#This is the folder with all the category summaries, make sure to change this
folderPath = ""

#This creates a list with all the category summary files
summary_files = [
    file for file in os.listdir(folderPath)
        if file.endswith("_category_summary.csv")
]

city_data = {}

#This iterates through the summary files list and creates a dictionary with all the 
#city names and their corresponding csv files, and it also removes the city and percentage
#columns as we will recalculate the percentage after combining
for file in summary_files:
    city = file.removesuffix("_category_summary.csv")
    df = pd.read_csv(os.path.join(folderPath, file))
    city_data[city] = df.drop(['City', 'Percentage'], axis=1)
    
#This combines all the csv files of the different cities into one csv, and sums
#all of the common categories
combinedTable = pd.concat(city_data.values(), ignore_index=True)
combinedTable = combinedTable.groupby('Category', as_index=False).sum()

# Calculate total count across all categories
total_count = combinedTable['Count'].sum()

# Add a new Percentage column
combinedTable['Percentage'] = (combinedTable['Count'] / total_count) * 100

#Sort the table and reindex them
combinedTable = combinedTable.sort_values(by='Count', ascending=False)
combinedTable = combinedTable.reset_index(drop=True)

countryname = folderPath.split("/")[-1]

#Add a new country column that contains the country name which is helpful when we compare
#different tables
combinedTable = combinedTable.assign(Country= countryname)

outputPath = os.path.join('combined_csv', f"{countryname}_category_summary.csv")
combinedTable.to_csv(outputPath, index=True)

#This removes any categories with a count less than 5
changedTable = combinedTable[combinedTable['Count'] > 5]

outputPath = os.path.join('combined_altered_csv', f"{countryname}_category_summary.csv")
changedTable.to_csv(outputPath, index=True)


