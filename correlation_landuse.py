import os
import geopandas as gpd
import pandas as pd
from scipy.stats import pearsonr
from functions import read_water_resource_zones

"""
This code performs data processing and analysis on water company data and land use data.

1. Load water company data and filter it based on specific area types.
2. Perform union operation on the geometries of water company groups.
3. Create a new GeoDataFrame with the unioned geometries for each company.
4. Append correlation data to the water company GeoDataFrame.
5. Convert certain columns to numeric and filter out NaN values.
6. Calculate the Pearson correlation coefficient between household population and consumption.
7. Load land use data and merge it with the water company GeoDataFrame.
8. Perform a spatial join between water companies and land use data.
9. Group the data by company and land use label, and sum the area column.
10. Create a new GeoDataFrame with the grouped data and centroid geometry.
11. Filter the rows with 'urban' land use.
12. Calculate the total area of urban land use for each company.
13. Calculate the Pearson correlation coefficient between household consumption and urban land use area.

The Pearson's Correlation Coefficient code is contributed by Amiya Rout (ref: https://www.geeksforgeeks.org/python-pearson-correlation-test-between-two-variables/)
"""

water_area_file = 'data_files/WaterSupplyAreas_incNAVs v1_4.shp'

# Load water company data as wrz, remove unnecessary columns
wrz = read_water_resource_zones(water_area_file)

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


