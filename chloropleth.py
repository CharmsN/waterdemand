import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def chloropleth_pcc(pcc_period):

    """Generates a chloropleth map depicting the average per capita consumption (PCC) of water within different water company areas
    for a specific time period. 

    The function requires the following imports: 
    import os
    import pandas as pd
    import geopandas as gpd
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs

    This function is hard-coded with the following: Water company boundaries - can be downloaded from the following link: https://data.parliament.uk/resources/constituencystatistics/water/WaterSupplyAreas_incNAVsv1_4.zip. Consumption data - can be
downloaded from https://www.ofwat.gov.uk/publication/historical-performance-trends-for-pr24-v2-0/ and a shape file that defines the outline for the UK. All datasets are provided in the waterdemand Github repository. (Note: The code could also be amended to visualise total household consumption, leakage etc as this information is also available within the provided dataset. Further nhancement to this code would be to create a template that could be populated with the required data to allow visualisation a district metered area (dma) within a water company boundary. )

    The function loads geographical and statistical data, merges them based on water company acronyms, and creates a chloropleth map using the GeoDataFrame. The map shows the variation in PCC across different areas, helping to visualize the differences in water consumption patterns.

    The input for this function is a string called pcc_period: The specific time period for which the PCC data is being visualized. Options for this are in the format '2019-20', '2011-12' etc. 

    The function returns plt: The plot object representing the chloropleth map, which displays the average per capita consumption per water company area for the selected period."""

    wrz = gpd.read_file(os.path.abspath('data_files/WaterSupplyAreas_incNAVs v1_4.shp')) # Load water company data as wrz, remove unnecessary columns
    columns_to_remove = ['Disclaimer', 'Disclaim2', 'Disclaim3', 'Provenance', 'Licence', 'WARNINGS', 'Revisions'] # List of columns to be removed
    wrz = wrz.drop(columns=columns_to_remove)  # Drop the columns from the GeoDataFrame
    # wrz.head(10)
    myFig = plt.figure(figsize=(10, 10))  # create a figure of size 10x10 (representing the page size in inches)
    myCRS = ccrs.TransverseMercator(27700)  # create a Universal Transverse Mercator reference system to transform our data.

    # Append PCC for 2019 to 2020 to the wrz geodataframe
    pr24_hist_pcc = pd.read_csv('data_files/pr24_hist_pcc.csv')     # Load the CSV file
    merged = wrz.merge(pr24_hist_pcc[['Company', pcc_period]], how='left', left_on='Acronym', right_on='Company')  # Perform the merge
    merged.drop(['Company'], axis=1, inplace=True) # Drop the unnecessary columns & rename the merged column
    merged.rename(columns={pcc_period: '2019-20_from_CSV'}, inplace=True)
    wrz[pcc_period] = merged['2019-20_from_CSV']  # Update the wrz GeoDataFrame with the merged column
    wrz.plot(column=pcc_period, cmap='viridis', linewidth=0.8, edgecolor='black', legend=True, figsize=(10, 10))     # Create the chloropleth map
    plt.suptitle('Figure 4: Average per capital consumption per water company area for selected period', y=0.1, fontsize=14)     # Set plot title at the bottom of the map 
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
    
    # return plt # Show the plot
    # plt.show()
    # Save the plot as a JPEG file
    plt.savefig('data_files/2019_20pcc.jpg', dpi=300)  # uncomment this to save a jpeg of this plot
    