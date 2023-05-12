import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def wrz_geo(water_areas):
    """This function creates a geodataframe of water resource zone data with a Universal Transverse Mercator reference system (TransverseMercator(27700)).

    Args:
        water_areas (str): The file path of the water areas shapefile.

    Returns:
        gpd.GeoDataFrame: The geodataframe containing water resource zone data.
    """
    wrz = gpd.read_file(os.path.abspath(water_areas))
    columns_to_remove = ['Disclaimer', 'Disclaim2', 'Disclaim3', 'Provenance', 'Licence', 'WARNINGS', 'Revisions']
    wrz = wrz.drop(columns=columns_to_remove)
    return wrz

def chloropleth_pcc(water_areas, pcc_period):
    """Generates a chloropleth map depicting the average per capita consumption (PCC) of water within different water company areas for a specific time period.

    Args:
        water_areas (str): The file path of the water areas shapefile.
        pcc_period (str): The specific time period for which the PCC data is being visualized.

    Returns:
        None
    """
    wrz = wrz_geo(water_areas)

    pr24_hist_pcc = pd.read_csv('data_files/pr24_hist_pcc.csv')
    merged = wrz.merge(pr24_hist_pcc[['Company', pcc_period]], how='left', left_on='Acronym', right_on='Company')
    merged.drop(['Company'], axis=1, inplace=True)
    merged.rename(columns={pcc_period: '2019-20_from_CSV'}, inplace=True)
    wrz[pcc_period] = merged['2019-20_from_CSV']

    myFig = plt.figure(figsize=(10, 10))
    myCRS = ccrs.TransverseMercator(27700)

    wrz.plot(column=pcc_period, cmap='viridis', linewidth=0.8, edgecolor='black', legend=True, figsize=(10, 10))
    plt.suptitle('Figure 4: Average per capita consumption per water company area for selected period', y=0.1, fontsize=14)
    for spine in plt.gca().spines.values():
        spine.set_visible(True)
        spine.set_color('black')
        spine.set_linewidth(1)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.subplots_adjust(bottom=0.175)

    plt.savefig('data_files/2019_20pcc.jpg', dpi=300)

# Example usage
water_areas_file = 'data_files/WaterSupplyAreas_incNAVs v1_4.shp'
pcc_period = '2019-20'
chloropleth_pcc(water_areas_file, pcc_period)
