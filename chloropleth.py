import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def chloropleth_pcc(pcc_period):



    outline = gpd.read_file(os.path.abspath('data_files/Outline.shp')) # load the outline of UK for a backdrop
    wrz = gpd.read_file(os.path.abspath('data_files/WaterSupplyAreas_incNAVs v1_4.shp')) # Load water company data as wrz, remove unnecessary columns
    columns_to_remove = ['Disclaimer', 'Disclaim2', 'Disclaim3', 'Provenance', 'Licence', 'WARNINGS', 'Revisions'] # List of columns to be removed
    wrz = wrz.drop(columns=columns_to_remove)  # Drop the columns from the GeoDataFrame
    # wrz.head(10)
    myFig = plt.figure(figsize=(10, 10))  # create a figure of size 10x10 (representing the page size in inches)
    myCRS = ccrs.TransverseMercator(27700)  # create a Universal Transverse Mercator reference system to transform our data.
    
    print(wrz.crs == outline.crs) # test if the crs is the same 
    # Append PCC for 2019 to 2020 to the wrz geodataframe
    pr24_hist_pcc = pd.read_csv('data_files/pr24_hist_pcc.csv')     # Load the CSV file
    merged = wrz.merge(pr24_hist_pcc[['Company', pcc_period]], how='left', left_on='Acronym', right_on='Company')  # Perform the merge
    merged.drop(['Company'], axis=1, inplace=True) # Drop the unnecessary columns & rename the merged column
    merged.rename(columns={pcc_period: '2019-20_from_CSV'}, inplace=True)
    wrz[pcc_period] = merged['2019-20_from_CSV']  # Update the wrz GeoDataFrame with the merged column
    wrz.plot(column=pcc_period, cmap='viridis', linewidth=0.8, edgecolor='black', legend=True, figsize=(10, 10))     # Create the chloropleth map
    plt.suptitle('Figure x: Average per capital consumption per water company area for selected period', y=0.1, fontsize=14)     # Set plot title at the bottom of the map 
    # Add a border around the map
    for spine in plt.gca().spines.values():
        spine.set_visible(True)
        spine.set_color('black')
        spine.set_linewidth(1) 
    # Set plot title and axis labels
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    # Adjust the spacing between the title and the axis labels
    plt.subplots_adjust(bottom=0.175)
    
    return plt # Show the plot
    # plt.show()
    # Save the plot as a JPEG file
    # plt.savefig('data_files/pcc.jpg', dpi=300)  # incomment this to save a jpeg of this plot
    