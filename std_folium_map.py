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


def folium_map(data_field,data_file): 
    
    # Load water company data as wrz, remove unnecessary columns
    gdf = data_file

    # Create a Folium map using the existing GeoDataFrame
    m = folium.Map()

    # Add the data to the map
    m = gdf.explore(data_field, # show the PCC for this period column
                cmap='YlOrRd', # use the 'plasma' colormap from matplotlib
                legend_kwds={'caption': 'landuse'} # set the caption to a longer explanation
                )

    # Add a red marker to each water company
    landuse_args = {
        'm': m, # add the markers to the same map we just created
        'marker_type': 'marker', # use a marker for the points, instead of a circle
        'popup': True, # show the information as a popup when we click on the marker
        'legend': False, # don't show a separate legend for the point layer
        'marker_kwds': {'icon': folium.Icon(color='red', icon='dot', prefix='fa')}# make the markers red with a dot icon from FA
    }

    return(m)
