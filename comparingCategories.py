# This program goes through a folder selected by the user and creates different
# Analysis files, such as the categories present in only one city, the max deviation
# per category, a binary coverage matrix, a spearman correlation matrix and a jaccard matrix
# make sure to change the summaries_directory, and output_path when you use this program

import pandas as pd
import os
import csv

#This is the folder where the category summaries are located, make sure you
#change this 
summaries_directory = "/Users/magicsquirrel/Developer/workstudy/places foursquare/Canadian/truncated_cat_summary"

#This creates a list of all the names of the summary.csv files
summary_files = [
    file for file in os.listdir(summaries_directory)
    if file.endswith('_category_summary.csv')
]

city_data = {}
city_sets = {}

#This goes through the whole folder and adds each summary csv file into 2 dictionaries
#one that contains all the dataframes, and one that contains all the category data as a set
for file in summary_files:
    city = file.removesuffix('truncated_category_summary.csv').capitalize()
    df = pd.read_csv(os.path.join(summaries_directory, file))
    city_data[city] = df
    city_sets[city] = set(df['Category'])

#Creates a list of the city names
city_names = list(city_data.keys())

#This iterates through every city in the list of cities and finds their unique categories
for city in city_names:
    #This finds the union of the categories from cities that isn't the current city
    other_categories = set().union(*(city_sets[c] for c in city_names if c != city))
    #This finds the categories that are unique to this city
    unique_categories = sorted(city_sets[city] - other_categories)
    output_path = os.path.join('places foursquare/Canadian/unique_categories', f"{city.lower()}_unique_categories.csv")
    os.makedirs('places foursquare/Canadian/unique_categories', exist_ok=True)
    pd.DataFrame({'Unique_category': unique_categories}).to_csv(output_path, index=False, quoting=1)

#Combines all the tables together
combinedTable = pd.concat(city_data.values(), ignore_index=True)

#Changes the table so that the categories are used to index the table and the columns
#display the count and percentage of each category for each city
pivotTable1 = combinedTable.pivot_table(index='Category', columns='City', values='Percentage')
pivotTable2 = combinedTable.pivot_table(index='Category', columns='City', values='Count')

#This removes any categories that are present in one city which can mess with the 
#comparison
filteredTable = pivotTable1[pivotTable1.notna().sum(axis=1)>=2]

#Creates a new column called Max Deviation, which compares the percentages
#in each row and determines the max deviation between the cities for each category
filteredTable = filteredTable.copy()
filteredTable['Max Deviation'] = filteredTable.max(axis=1) - filteredTable.min(axis=1)

#Sorts the table based on descending order
filteredTable = filteredTable.sort_values(by='Max Deviation', ascending=False)

output_path = os.path.join('places foursquare/Canadian/city_comparison', "max_deviation_category_comparison.csv")
os.makedirs('places foursquare/Canadian/city_comparison', exist_ok=True)

filteredTable.to_csv(output_path, index=True)
    
    
    
#This makes it so if a category is present it will get a value of 1 and if it isnt
#present it will get a value of 0
binaryCoverageMatrix = pivotTable1.notna().astype(int)
binaryCoverageMatrix = binaryCoverageMatrix.copy()

binaryCoverageMatrix['Cities Present'] = binaryCoverageMatrix.sum(axis=1)
binaryCoverageMatrix = binaryCoverageMatrix.sort_values(
    by=['Cities Present', binaryCoverageMatrix.index.name],
    ascending=[False, True]
)

grouped = binaryCoverageMatrix.groupby('Cities Present')

group1 = grouped.get_group(1)
group2 = grouped.get_group(2)
group3 = grouped.get_group(3)
group4 = grouped.get_group(4)

output_path = os.path.join('places foursquare/Canadian/city_comparison', "binary_coverage_matrix_of_categories.csv")
os.makedirs('places foursquare/Canadian/city_comparison', exist_ok=True)

binaryCoverageMatrix.to_csv(output_path, index=True)

output_path = os.path.join('places foursquare/Canadian/city_comparison', "categories_in_1_country.csv")

group1.to_csv(output_path, index=True)

output_path = os.path.join('places foursquare/Canadian/city_comparison', "categories_in_2_country.csv")

group2.to_csv(output_path, index=True)

output_path = os.path.join('places foursquare/Canadian/city_comparison', "categories_in_3_country.csv")

group3.to_csv(output_path, index=True)

output_path = os.path.join('places foursquare/Canadian/city_comparison', "categories_in_4_country.csv")

group4.to_csv(output_path, index=True)


#This creates a Spearman ranked correlation table based on the data
#This removes any rows that arent presnent in all 
pivotTable2Clean = pivotTable2.dropna()
rankedTable2 = pivotTable2.rank(ascending=False)
spearmanCorrelation = rankedTable2.corr(method='spearman')

output_path = os.path.join('places foursquare/Canadian/city_comparison', "spearman_correlation_common_categories.csv")

spearmanCorrelation.to_csv(output_path, index=True)

#This section creates a jaccard matrix out of the data
def jaccard(city1, city2):
    return len(city1 & city2)/len(city1 | city2)


#Creates an empty dataframe for the jaccard matrix which figures out the percentage
#of categories that are shared between the cities
jaccardMatrix = pd.DataFrame(index=city_names, columns=city_names)

for city1 in city_names:
    for city2 in city_names:
        jaccardMatrix.loc[city1, city2] = jaccard(city_sets[city1], city_sets[city2])

output_path = os.path.join('places foursquare/Canadian/city_comparison', "jaccard_matrix.csv")
jaccardMatrix.to_csv(output_path, index=True)