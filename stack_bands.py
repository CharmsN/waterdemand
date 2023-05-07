import rasterio
import numpy as np


def band_stacking_three_bands(band_files,output_tiff):
    
    # Create an empty array to store the band data
    stacked_data = []

    # Read each band file and stack the data
    for i, band_file in enumerate(band_files):
        with rasterio.open(band_file) as band_src:
            band_data = band_src.read(1)  # Read the band data
            stacked_data.append(band_data)

    # Open one of the band files to get the metadata
    with rasterio.open(band_files[0]) as src:
        # Read the metadata
        meta = src.meta

    # Update the metadata for the output TIFF file
    meta.update(count=len(stacked_data))

    # Write the stacked data to the output TIFF file
    with rasterio.open(output_tiff, 'w', **meta) as dst:
        dst.write(np.array(stacked_data))

