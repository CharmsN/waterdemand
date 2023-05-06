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

def folium_pcc_map(): 
    
    # Set Seaborn style and color palette
    sns.set_style("darkgrid")
    sns.set_palette("husl")

    # Load water company data as wrz, remove unnecessary columns
    wrz = gpd.read_file(os.path.abspath('data_files/WaterSupplyAreas_incNAVs v1_4.shp'))

    # List of columns to be removed
    columns_to_remove = ['Disclaimer', 'Disclaim2', 'Disclaim3', 'Provenance', 'Licence', 'WARNINGS', 'Revisions']

    # Drop the columns from the GeoDataFrame
    wrz = wrz.drop(columns=columns_to_remove)

    # Append PCC for 2019 to 2020 to the wrz geodataframe
    # Load the CSV file
    pr24_hist_pcc = pd.read_csv('data_files/pr24_hist_pcc.csv')

    # Perform the merge
    merged = wrz.merge(pr24_hist_pcc[['Company', '2019-20']], how='left', left_on='Acronym', right_on='Company')

    # Drop the unnecessary columns & rename the merged column
    merged.drop(['Company'], axis=1, inplace=True)
    merged.rename(columns={'2019-20': '2019-20_from_CSV'}, inplace=True)

    # Update the wrz GeoDataFrame with the merged column
    wrz['2019-20'] = merged['2019-20_from_CSV']

    # Create a Folium map using the existing GeoDataFrame
    m = folium.Map()

    # Add the PCC data to the map
    m = wrz.explore('2019-20', # show the PCC for this period column
                cmap='YlOrRd', # use the 'plasma' colormap from matplotlib
                legend_kwds={'caption': 'PCC for 2019-20'} # set the caption to a longer explanation
                )

    # Add a red marker to each water company
    pcc_args = {
        'm': m, # add the markers to the same map we just created
        'marker_type': 'marker', # use a marker for the points, instead of a circle
        'popup': True, # show the information as a popup when we click on the marker
        'legend': False, # don't show a separate legend for the point layer
        'marker_kwds': {'icon': folium.Icon(color='red', icon='dot', prefix='fa')}# make the markers red with a dot icon from FA
    }

    return(m)
