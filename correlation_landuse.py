import os
import pandas as pd
import geopandas as gpd
import pandas as pd
from scipy.stats import pearsonr

# Load water company data as wrz, remove unnecessary columns
wrz = gpd.read_file(os.path.abspath('data_files/WaterSupplyAreas_incNAVs v1_4.shp'))
# List of columns to be removed
columns_to_remove = ['Disclaimer', 'Disclaim2', 'Disclaim3', 'Provenance', 'Licence', 'WARNINGS', 'Revisions']

# Drop the columns from the GeoDataFrame
wrz = wrz.drop(columns=columns_to_remove)

# Append Correlation data to the wrz geodataframe
# Load the CSV file
correlation_data = pd.read_csv('data_files/correlation_data.csv')

# Perform the merge
correlate = wrz.merge(correlation_data[['Company', 'hh_cons', 'hh_pop']], how='left', left_on='Acronym', right_on='Company')

# Drop the unnecessary columns & rename the merged column
correlate.drop(['Company'], axis=1, inplace=True)

# Convert the hh_pop and hh_cons columns to numeric
correlate['hh_pop'] = pd.to_numeric(correlate['hh_pop'], errors='coerce')
correlate['hh_cons'] = pd.to_numeric(correlate['hh_cons'], errors='coerce')

# Filter out NaN values
correlate = correlate.dropna()

# Convert dataframe into series
list1 = correlate['hh_pop']
list2 = correlate['hh_cons']

# Apply the pearsonr()
corr, _ = pearsonr(list1, list2)
# print('Pearsons correlation: %.3f' % corr)

# Convert dataframe into series
list1 = correlate['hh_pop']
list2 = correlate['hh_cons']

# Apply the pearsonr()   # This code is contributed by Amiya Rout (ref: https://www.geeksforgeeks.org/python-pearson-correlation-test-between-two-variables/)
corr, _ = pearsonr(list1, list2)
# print('Pearsons correlation: %.3f' % corr)

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
print(merged_landuse.crs == wrz.crs) # test if the crs is the same 
# Perform spatial join between wrz and merged_landuse
join = gpd.sjoin(wrz, merged_landuse, how='inner', predicate='intersects')
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

# Perform the merge
correlate_landuse = correlate.merge(area_by_company[['COMPANY', 'Area_Ha']], how='left', left_on='COMPANY', right_on='COMPANY')

# Convert dataframe into series
list2 = correlate_landuse['hh_cons']
list3 = correlate_landuse['Area_Ha']

# Apply the pearsonr()  # This code is contributed by Amiya Rout (ref: https://www.geeksforgeeks.org/python-pearson-correlation-test-between-two-variables/)
corr, _ = pearsonr(list2, list3)
print('Pearsons correlation for Household Water Consumption (Ml/d) and Urban Landuse (Ha): %.3f' % corr)

# Convert dataframe into series
list2 = correlate_landuse['hh_pop']
list3 = correlate_landuse['Area_Ha']

# Apply the pearsonr()
corr, _ = pearsonr(list2, list3)
print('Pearsons correlation for Household Population (000s) and Urban Landuse (Ha) (: %.3f' % corr)

# household consumption (megalitres per day) divided by Area (Hectares) and converted to Litres per Hectare to give Household consumption per Hectare in Litres per day for land classed as 'urban use'
correlate_landuse['hh_cons_per_Area_Ha'] = correlate_landuse['hh_cons'] * 10**6 / 86400 / correlate_landuse['Area_Ha'] * 10000
print('Household Water Consumption (Litres per day) per Hectare of Land Classified under Urban Landuse :', correlate_landuse)
# average household property size in the UK is around 120m 


