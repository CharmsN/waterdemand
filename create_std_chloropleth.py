"""this module creates a standard chloropleth map using a Seaborn colour palette. Inputs are data field = the data colum to map; data_file = the geodataframe data source and title = the figure capture to include in the map. The map is created using TransverseMNercator (27700) and changes the crs of the gdf to that of the outline to ensure they are the same."""

import os
import pandas as pd
import numpy as np
import geopandas as gpd
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import seaborn as sns

def create_chloropleth(data_field, data_file,title):

    # Set Seaborn style and color palette
    sns.set_style("darkgrid")
    sns.set_palette("husl")

    outline = gpd.read_file(os.path.abspath('data_files/Outline.shp')) # load the outline of UK for a backdrop
    gdf = gpd.read_file(os.path.abspath('data_file')) # Load data as gdf
    myFig = plt.figure(figsize=(10, 10))  # create a figure of size 10x10 (representing the page size in inches)
    myCRS = ccrs.TransverseMercator(27700)  # create a Universal Transverse Mercator reference system to transform our data.
    gdf = gdf.to_crs(outline.crs) # changes the gdf to the same crs as the outline
    # print(gdf.crs == outline.crs) # test if the crs is the same, this is commented out but can be uncommented if required
    wrz.plot(column=data_field, cmap='viridis', linewidth=0.8, edgecolor='black', legend=True, figsize=(10, 10))     # Create the chloropleth map
    plt.suptitle('title', y=0.1, fontsize=14)     # Set plot title at the bottom of the map 
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
    # Save the plot as a JPEG file
    # plt.savefig('data_files/img_chloropleth.jpg', dpi=300)
    