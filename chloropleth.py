import os
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import folium
import scipy
import seaborn as sns
from sentinelsat import SentinelAPI, make_path_filter
from IPython import display
import shapely
from shapely.geometry import MultiPolygon
#import add_axis_scalebar as add_axis_elements
from csv_merge import merge_csv_to_wrz
import download_sat_image_company
from IPython.display import Image

def chloropleth_pcc(pcc_period):

    # Set Seaborn style and color palette
    sns.set_style("darkgrid")
    sns.set_palette("husl")

    outline = gpd.read_file(os.path.abspath('data_files/Outline.shp')) # load the outline of UK for a backdrop
    wrz = gpd.read_file(os.path.abspath('data_files/WaterSupplyAreas_incNAVs v1_4.shp')) # Load water company data as wrz, remove unnecessary columns
    columns_to_remove = ['Disclaimer', 'Disclaim2', 'Disclaim3', 'Provenance', 'Licence', 'WARNINGS', 'Revisions'] # List of columns to be removed
    wrz = wrz.drop(columns=columns_to_remove)  # Drop the columns from the GeoDataFrame
    # wrz.head(10)
    myFig = plt.figure(figsize=(10, 10))  # create a figure of size 10x10 (representing the page size in inches)
    myCRS = ccrs.TransverseMercator(27700)  # create a Universal Transverse Mercator reference system to transform our data.
   
    # Uncomment and remove indent from this section this to see plot of water company boundaries
        # ax = plt.axes(projection=myCRS)  # finally, create an axes object in the figure, using a UTM projection,
        #outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', facecolor='w') # first, we just add the outline using cartopy's ShapelyFeature
        #xmin, ymin, xmax, ymax = outline.total_bounds
        #ax.add_feature(outline_feature) # add the features we've created to the map. 
       # ax.set_extent([xmin-5000, xmax+5000, ymin-5000, ymax+5000], crs=myCRS) 
        #myFig ## re-draw the figure
        #num_wrz = len(wrz.COMPANY.unique())  # get the number of unique water companies we have in the dataset
        # print('Number of unique features: {}'.format(num_wrz))
       # num_colours = num_wrz  # pick colours for the individual water companies- generate random RGB colors# Number of colours to generate
       # company_colours = sns.color_palette("husl", n_colors=num_colours)  # Use Seaborn color palette
       # company_names = list(wrz.COMPANY.unique())  # get a list of unique names for the company boundaries
      #  company_names.sort() # sort the companies alphabetically by name
        # next, add the company outlines to the map using the colours that we've picked.
      #  for ii, name in enumerate(company_names):
      #      feat = ShapelyFeature(wrz.loc[wrz['COMPANY'] == name, 'geometry'], # first argument is the geometry
       #                           myCRS, # second argument is the CRS
       #                           edgecolor='k', # outline the feature in black
       #                           facecolor=company_colours[ii], # set the face color to the corresponding color from the list
       #                           linewidth=1, # set the outline width to be 1 pt
       #                           alpha=0.25) # set the alpha (transparency) to be 0.25 (out of 1)
       #     ax.add_feature(feat) # once we have created the feature, we have to add it to the map using ax.add_feature()
        #fig, ax = plt.subplots() # ... code to create the plot ...
        #add_axis_elements.add_axis_elements(ax)
        # plt.show()
    
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
    # Show the plot
    # plt.show()
    # Save the plot as a JPEG file
    plt.savefig('data_files/pcc.jpg', dpi=300)
    