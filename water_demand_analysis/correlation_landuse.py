import os
import pandas as pd
import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from shapely.ops import unary_union

"""
This script processes water company data and land use data to analyze correlations between different variables.

Inputs:
- 'data_files/WaterSupplyAreas_incNAVs v1_4.shp': Shapefile containing water company data.
- 'data_files/correlation_data.csv': CSV file containing correlation data.
- 'data_files/clc2018_uk.shp': Shapefile containing land use data.
- 'data_files/legend.csv': CSV file containing land use category labels.

Outputs:
- 'data_files_correlate.shp': Shapefile containing merged water company data with correlation information.

Process:
1. Loads water company data from the shapefile and removes unnecessary columns.
2. Filters the data to select features with specific area types.
3. Fixes an issue with a specific record in the 'COMPANY' column.
4. Performs a union operation on the geometries based on the 'COMPANY' column.
5. Creates a new GeoDataFrame with the unioned geometries for each company.
6. Loads correlation data from a CSV file and merges it with the water company data.
7. Converts specific columns to numeric values and filters out NaN values.
8. Calculates the Pearson correlation coefficient between household population and household consumption.
9. Loads land use data from a shapefile and merges it with a CSV file containing labels.
10. Drops unnecessary columns from the merged land use data.
11. Performs a spatial join between the water company data and merged land use data.
12. Groups the data by company and land use label, summing the 'Area_Ha' column.
13. Creates a new GeoDataFrame with the grouped data, setting the geometry as the centroid of each land use label.
14. Filters the rows where the land use label includes 'urban'.
15. Groups the rows by company and calculates the sum of the 'Area_Ha' column for each group.
16. Rounds the values in the 'Area_Ha' column to 2 significant digits.
17. Merges the water company data with the area by company data.
18. Calculates the Pearson correlation coefficient between household consumption and area of urban land use.
19. Calculates household consumption per hectare in liters per day for land classified as 'urban use'.
20. Adds a new column to the data containing household consumption per hectare in liters per day.
21. Returns the updated water company data with the additional column.

Note: The code includes references to Amiya Rout's contributions on geeksforgeeks.org for the Pearson correlation calculation.

Author: [Charmaine Newmarch]
Date: [11 May 2023]
"""


# Load water company data as wrz, remove unnecessary columns
wrz = gpd.read_file(os.path.abspath('data_files/WaterSupplyAreas_incNAVs v1_4.shp'))
# List of columns to be removed
columns_to_remove = ['Disclaimer', 'Disclaim2', 'Disclaim3', 'Provenance', 'Licence', 'WARNINGS', 'Revisions', 'AreaServed']

# Drop the columns from the GeoDataFrame
wrz = wrz.drop(columns=columns_to_remove)

included_area_types = ['regional water and sewerage company', 'regional water only company'] # Filter the GeoDataFrame to select the features with "Northumbrian Water"

wrz['COMPANY'] = wrz['COMPANY'].replace('Northumbrian Water Limited', 'Northumbrian Water') # fix issue with NES record

# Filter out features with the specified area types
wrz_ref = wrz[wrz['CoType'].isin(included_area_types)]
 # len(wrz_ref) # uncomment this to check that all 43 water company areas are included 
wrz_ref
# Group the data by the 'Company' column
grouped_wrz = wrz.groupby('COMPANY')

# Create an empty GeoSeries to store the unioned geometries
merged_geometries = gpd.GeoSeries()
acronyms = []

# Iterate over each group and perform the union operation
for group_name, group_data in grouped_wrz:
    unioned_geometry = group_data['geometry'].unary_union
    merged_geometries[group_name] = unioned_geometry
    acronyms.append(group_data['Acronym'].iloc[0])
# Create a new GeoDataFrame with the unioned geometries for each company
merged_wrz_companies = gpd.GeoDataFrame(geometry=merged_geometries.values, index=merged_geometries.index)
merged_wrz_companies['COMPANY'] = merged_geometries.index
merged_wrz_companies['Acronym'] = acronyms

merged_wrz_companies
# Append Correlation data to the wrz geodataframe
# Load the CSV file
correlation_data = pd.read_csv('data_files/correlation_data.csv', thousands=',')  
correlation_data
# Perform the merge
correlate = merged_wrz_companies.merge(correlation_data[['Company', 'hh_cons', 'hh_pop']], how='left', left_on='Acronym', right_on='Company')

correlate.to_file('data_files_correlate.shp')
correlate
# Convert the hh_pop and hh_cons columns to numeric
correlate['hh_pop'] = pd.to_numeric(correlate['hh_pop'], errors='coerce')
correlate['hh_cons'] = pd.to_numeric(correlate['hh_cons'], errors='coerce')

# Filter out NaN values
correlate = correlate.dropna()
correlate
# Convert dataframe into series
list1 = correlate['hh_pop']
list2 = correlate['hh_cons']

# Apply the pearsonr()
corr, _ = pearsonr(list1, list2)
print('Pearsons correlation for household population and household consumption: %.3f' % corr)

# This code is contributed by Amiya Rout (ref: https://www.geeksforgeeks.org/python-pearson-correlation-test-between-two-variables/)

# Load landuse data
landuse = gpd.read_file(os.path.abspath('data_files/clc2018_uk.shp'))
# Load the CSV file
landuse_categories = pd.read_csv('data_files/legend.csv')
# print(landuse_categories.head())  #show a sample of the CSV file 
# merge the csv file with the geodataframe to include the labels for the landuse in the geodataframe
landuse_categories['CODE'] = landuse_categories['CODE'].astype(str)
merged_landuse = pd.merge(landuse, landuse_categories, left_on='CODE_18', right_on='CODE')

# Drop unnecessary columns - this cleans the dataset to make it easier to work with
merged_landuse = merged_landuse.drop(['CODE_18', 'CODE', 'Unnamed: 4', 'Unnamed: 5'], axis=1)
merged_landuse
# Access the 'LABEL' column in the merged DataFrame - LABEL gives the actual landuse description
label_column = merged_landuse['LABEL']
merged_wrz_companies = merged_wrz_companies.set_crs(wrz.crs)
# print(merged_landuse.crs == merged_wrz_companies.crs) # test if the crs is the same 
# Perform spatial join between wrz and merged_landuse
join = gpd.sjoin(merged_wrz_companies, merged_landuse, how='inner', predicate='intersects')
# Group by COMPANY and LABEL, and sum the Area_Ha column
grouped = join.groupby(['COMPANY', 'LABEL'])['Area_Ha'].sum().reset_index()

# Create a new GeoDataFrame from the grouped data
company_landuse = gpd.GeoDataFrame(grouped, geometry=gpd.GeoSeries(), crs=wrz.crs)

# Set the geometry of the new GeoDataFrame to the centroid of each LABEL
company_landuse.geometry = company_landuse.apply(lambda x: wrz[wrz['COMPANY'] == x['COMPANY']].geometry.centroid.iloc[0], axis=1)
# Filter the rows where LABEL includes 'urban'
urban_company_landuse = company_landuse[company_landuse['LABEL'].str.contains('urban')]
urban_company_landuse
# Group the rows by the COMPANY column and get the sum of the Area_Ha column for each group
area_by_company = urban_company_landuse.groupby("COMPANY")["Area_Ha"].sum()

# Round the values in the "Area_Ha" column to 2 significant digits
area_by_company = area_by_company.round(2)

# Convert the result to a new GeoDataFrame with a "COMPANY" column and an "AreaHa" column
area_by_company = area_by_company.reset_index()
area_by_company.columns = ["COMPANY", "Area_Ha"]
area_by_company
correlate
# Perform the merge
correlate_landuse = correlate.merge(area_by_company[['COMPANY', 'Area_Ha']], how='left', left_on='COMPANY', right_on='COMPANY')

correlate_landuse
# Convert dataframe into series
list2 = correlate_landuse['hh_cons']
list3 = correlate_landuse['Area_Ha']

# Apply the pearsonr()
corr, _ = pearsonr(list2, list3)
print('Pearsons correlation for household population and area urban landuse: %.3f' % corr)

# The Pearson's Correlation Coefficient code is contributed by Amiya Rout (ref: https://www.geeksforgeeks.org/python-pearson-correlation-test-between-two-variables/)
