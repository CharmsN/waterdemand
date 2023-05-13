import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import folium

def read_water_resource_zones(water_areas_file):
    """
    Read water resource zones shapefile and remove unnecessary columns.

    Args:
        water_areas_file (str): The file path of the water areas shapefile.

    Returns:
        gpd.GeoDataFrame: The geodataframe containing water resource zone data.
    """
    wrz = gpd.read_file(os.path.abspath(water_areas_file))
    columns_to_remove = ['Disclaimer', 'Disclaim2', 'Disclaim3', 'Provenance', 'Licence', 'WARNINGS', 'Revisions']
    wrz = wrz.drop(columns=columns_to_remove)
    return wrz

def merge_pcc_data(wrz, history_file, pcc_period):
    """
    Merge per capita consumption (PCC) data with water resource zones based on company identifiers.

    Args:
        water_resource_zones (gpd.GeoDataFrame): The geodataframe containing water resource zone data.
        history_file (str): The file path of the history file.
        pcc_period (str): The specific time period for which the PCC data is being visualized.

    Returns:
        gpd.GeoDataFrame: The geodataframe with merged PCC data.
    """
    pcc_data = pd.read_csv(history_file)
    merged_data = wrz.merge(pcc_data[['Company', pcc_period]], how='left', left_on='Acronym', right_on='Company')
    merged_data.drop(['Company'], axis=1, inplace=True)
    merged_data.rename(columns={pcc_period: f'{pcc_period}_from_CSV'}, inplace=True)
    wrz[f'{pcc_period}'] = merged_data[f'{pcc_period}_from_CSV']
    return wrz

def plot_chloropleth_map(wrz, pcc_period):
    """
    Generate a chloropleth map depicting the average per capita consumption (PCC) of water within different water company areas.

    Inputs:
        water_resource_zones (gpd.GeoDataFrame): The geodataframe containing water resource zone data.
        pcc_period (str): The specific time period for which the PCC data is being visualized.

    Outputs:
        None
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title(f'Average per capita consumption per water company area for {pcc_period}', fontsize=14)
    wrz.plot(column=pcc_period, cmap='viridis', linewidth=0.8, edgecolor='black', legend=True, ax=ax)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.spines['top'].set_visible(True)
    plt.show()
    
def plot_folium_map(wrz, history_file, pcc_period):
    """
    Create a Folium map displaying the per capita consumption (PCC) data on a geographic map.

    Args:
        water_resource_zones (gpd.GeoDataFrame): The geodataframe containing water resource zone data.
        history_file (str): The file path of the history file.
        pcc_period (str): The specific time period for which the PCC data is being visualized.

    Returns:
        folium.Map: The Folium map object displaying the PCC data.

    """
     # Create a Folium map using the existing GeoDataFrame
    m = folium.Map()

    # Add the PCC data to the map
    m = wrz.explore(pcc_period, # show the PCC for this period column
                cmap='YlOrRd', # use the 'plasma' colormap from matplotlib
                legend_kwds={'caption': 'PCC Period Selected'} # set the caption to a longer explanation
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
