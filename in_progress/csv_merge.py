def merge_csv_to_wrz(csv_file_path, column_name):
    import pandas as pd
    import geopandas as gpd
    import os

    # Load the CSV file
    pr24_hist_pcc = pd.read_csv(csv_file_path)
    wrz = gpd.read_file(os.path.abspath('data_files/WaterSupplyAreas_incNAVs v1_4.shp'))

    # Perform the merge
    merged = wrz.merge(pr24_hist_pcc[['Company', column_name]], how='left', left_on='Acronym', right_on='Company')

    # Drop the 'Acronym' and 'Company' columns from merged
    merged.drop(['Acronym', 'Company'], axis=1, inplace=True)

    # Rename the merged column
    merged.rename(columns={column_name: f'{column_name}_from_CSV'}, inplace=True)

    # Assign the merged column back to the wrz GeoDataFrame
    wrz[f'{column_name}_from_CSV'] = merged[f'{column_name}_from_CSV']

 

