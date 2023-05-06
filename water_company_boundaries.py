import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import seaborn as sns

def wrz_boundaries(company_data):
    # Set Seaborn style and color palette 
    sns.set_style("darkgrid")
    sns.set_palette("husl")

    # Load water company data
    wrz = gpd.read_file(os.path.abspath(company_data))

    myFig = plt.figure(figsize=(10, 10))
    myCRS = ccrs.TransverseMercator(27700)

    wrz.plot(column='COMPANY', cmap='viridis', linewidth=0.8, edgecolor='black', legend=True, label='COMPANY', figsize=(20,20))
    plt.suptitle('Figure x: Boundaries for Water companies in England and Wales', y=0.1, fontsize=14)
    # Add a border around the map
    for spine in plt.gca().spines.values():
        spine.set_visible(True)
        spine.set_color('black')
        spine.set_linewidth(1) 

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.subplots_adjust(bottom=0.15)
 
    return plt
