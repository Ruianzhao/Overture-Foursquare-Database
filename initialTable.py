# This program allows you to chose a folder on your computer, and it will scan the 
# folder for parquet files, convert it into a .csv file, then it creates a table with
# the different categories and the amount they show up and exports it as a .csv file.
# Make sure you change the input folder, and output folder locations in the code
# before using it

#Use pandas to read parquet files
import pandas as pd

from collections import Counter

import os


#Function that will create a table with the number and percentage that each
#category shows up, and exports it as a .csv file
def generateCategoryTable(df, cityName):
    categories = []
    #Goes through ever place in the parquet and determines what category they are
    for curr in df['categories']:
        #If the dictionary isnt empty, and the primary tag exists, then add the category
        # into the categories list
        if isinstance(curr, dict) and 'primary' in curr:
            categories.append(curr['primary'])
    
    #Counts and creates a dictionary with each category and the amount they show up
    categoriesAndCount = Counter(categories)
    
    #Creates a new dataframe with the different categories and their respective counts
    outputTable = pd.DataFrame.from_dict(categoriesAndCount, orient='index', columns=['Count'])
    outputTable.index.name = 'Category'
    outputTable = outputTable.reset_index()
    outputTable = outputTable.assign(Percentage= lambda counts: (counts['Count']/sum(categoriesAndCount.values()) * 100))
    outputTable = outputTable.assign(City= cityName)
    
    #Orders the tables so the categories with the highest counts are at the top
    outputTable = outputTable.sort_values(by='Count', ascending=False)
    
    #Ensures the output path is the category_summaries folder make sure you change
    #this if you have a different folder
    output_path = os.path.join('category_summaries', f"{cityName.lower()}_category_summary.csv")
    #Export to .csv
    outputTable.to_csv(output_path, index=False)

#The path where all the parquet files are kept, remember to change this if you are
#using this code
folder_path = ""

#Iterates through all the parquet files in the folder and generates their
#raw csv, and category summaries
for file in os.listdir(folder_path):
    if file.endswith('.parquet'):
        file_path = os.path.join(folder_path, file)
         # gets 'toronto' from 'toronto_places.parquet' only works if file name is
         # in the form city_places.parquet
        city_name = file.split('_')[0].lower() 
        df = pd.read_parquet(file_path, engine='auto')
        
        #Ensures that the output path is the raw_city_files folder, remember to change
        #this if you have a different folder
        output_path = os.path.join('raw_city_files', f"{city_name}_places.csv")
        df.to_csv(output_path, index=False)
        generateCategoryTable(df, city_name)

