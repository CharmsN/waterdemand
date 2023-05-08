import os
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def wrz_boundaries(company_data):

    """
    Generates a plot displaying the boundaries of water companies in England and Wales based on the provided company data.

    The function reads the company data from a file, creates a GeoDataFrame using GeoPandas, and plots the boundaries of the water
    companies on a map. Each company is represented by a different color. The resulting plot provides a visual representation of the
    geographic distribution of water companies.
    
    The column to plot is hardcoded to COMPANY. A refinement to this code would be to create a variable for the volumn to plot.

    Input:
        company_data (str): The file path or name of the company data file. The file should contain the necessary information to
        define the boundaries of water companies. Example is given in waterdemand Github repository 
        (WaterSupplyAreas_incNAVs v1_4.shp)

    Output:
        plt: The plot object representing the boundaries of water companies in England and Wales.

    Example:
        company_data = 'path/to/company_data.shp'
        wrz_boundaries(company_data)
    """

    # Load water company data
    wrz = gpd.read_file(os.path.abspath(company_data))

    myFig = plt.figure(figsize=(10, 10))
    myCRS = ccrs.TransverseMercator(27700)

    wrz.plot(column='COMPANY', cmap='viridis', linewidth=0.8, edgecolor='black', legend=True, label='COMPANY', figsize=(20,20))
    plt.suptitle('Figure 2: Boundaries for Water companies in England and Wales', y=0.1, fontsize=14)
    # Add a border around the map
    for spine in plt.gca().spines.values():
        spine.set_visible(True)
        spine.set_color('black')
        spine.set_linewidth(1) 

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.subplots_adjust(bottom=0.15)
    
    # Save the plot as an image file
    output_file = 'data_files/wrz.png'  # Specify the desired file path and name
    plt.savefig(output_file)
 
    return plt
