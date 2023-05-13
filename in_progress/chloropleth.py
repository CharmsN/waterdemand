import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def read_water_resource_zones(water_areas_file):
    """
    Read water resource zones shapefile and remove unnecessary columns.

    Args:
        water_areas_file (str): The file path of the water areas shapefile.

    Returns:
        gpd.GeoDataFrame: The geodataframe containing water resource zone data.
    """
    water_resource_zones = gpd.read_file(os.path.abspath(water_areas_file))
    columns_to_remove = ['Disclaimer', 'Disclaim2', 'Disclaim3', 'Provenance', 'Licence', 'WARNINGS', 'Revisions']
    water_resource_zones = water_resource_zones.drop(columns=columns_to_remove)
    return water_resource_zones

def merge_pcc_data(water_resource_zones, history_file, pcc_period):
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
    merged_data = water_resource_zones.merge(pcc_data[['Company', pcc_period]], how='left', left_on='Acronym', right_on='Company')
    merged_data.drop(['Company'], axis=1, inplace=True)
    merged_data.rename(columns={pcc_period: f'{pcc_period}_from_CSV'}, inplace=True)
    water_resource_zones[f'{pcc_period}'] = merged_data[f'{pcc_period}_from_CSV']
    return water_resource_zones

def plot_chloropleth_map(water_resource_zones, pcc_period):
    """
    Generate a chloropleth map depicting the average per capita consumption (PCC) of water within different water company areas.

    Args:
        water_resource_zones (gpd.GeoDataFrame): The geodataframe containing water resource zone data.
        pcc_period (str): The specific time period for which the PCC data is being visualized.

    Returns:
        None
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title(f'Average per capita consumption per water company area for {pcc_period}', fontsize=14)
    water_resource_zones.plot(column=pcc_period, cmap='viridis', linewidth=0.8, edgecolor='black', legend=True, ax=ax)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.spines['top'].set_visible(True)
    plt.show()

# Example usage
water_areas_file = 'data_files/WaterSupplyAreas_incNAVs v1_4.shp'
history_file = 'data_files/pr24_hist_pcc.csv'
pcc_period = '2019-20'

water_resource_zones = read_water_resource_zones(water_areas_file)
water_resource_zones = merge_pcc_data(water_resource_zones, history_file, pcc_period)
plot_chloropleth_map(water_resource_zones, pcc_period)


