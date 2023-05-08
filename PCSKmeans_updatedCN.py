PyCharm
Community
edition
supports
Jupyter
notebooks in read - only
mode, to
get
full
support
for local notebooks download and try PyCharm Professional now!

Try
DataSpell — a
dedicated
IDE
for data science,
    with full support for local and remote notebooks

Try
Datalore — an
online
environment
for Jupyter notebooks in the browser

Also
read
more
about
JetBrains
Data
Solutions
on
our
website

import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import Counter
from PIL import Image
import imageio.v2 as imageio
import os
import math


def find_PCAKmeans(imagepath1, imagepath2):
    print('Operating')

    image1 = cv2.imread(imagepath1)
    image2 = cv2.imread(imagepath2)
    print(image1.shape, image2.shape)

    new_size = np.ceil(np.asarray(image1.shape) / 5) * 5  # Round up to the nearest multiple of 5
    new_size = new_size.astype(int)
    image1 = cv2.resize(image1, (new_size[1], new_size[0])).astype(np.int16)
    image2 = cv2.resize(image2, (new_size[1], new_size[0])).astype(np.int16)

    diff_image = np.abs(image1 - image2)
    cv2.imwrite('diff.jpg', diff_image)
    print('\nBoth images resized to', new_size)

    vector_set, mean_vec = find_vector_set(diff_image, new_size)

    pca = PCA()
    pca.fit(vector_set)
    EVS = pca.components_

    FVS = find_FVS(EVS, diff_image, mean_vec, new_size)

    print('\ncomputing k means')

    components = 3
    least_index, change_map = clustering(FVS, components, new_size)

    change_map[change_map == least_index] = 255
    change_map[change_map != 255] = 0

    change_map = change_map.astype(np.uint8)
    kernel = np.asarray(((0, 0, 1, 0, 0),
                         (0, 1, 1, 1, 0),
                         (1, 1, 1, 1, 1),
                         (0, 1, 1, 1, 0),
                         (0, 0, 1, 0, 0)), dtype=np.uint8)
    cleanChangeMap = cv2.erode(change_map, kernel)
    cv2.imwrite("data_files/test_data/changemap.jpg", change_map)
    cv2.imwrite("data_files/test_data/cleanchangemap.jpg", cleanChangeMap)


def find_vector_set(diff_image, new_size):
    block_size = 5
    num_blocks = (new_size[0] // block_size) * (new_size[1] // block_size)

    vector_set = np.empty((num_blocks, block_size * block_size), dtype=np.int16)
    idx = 0

    for i in range(new_size[0] // block_size):
        for j in range(new_size[1] // block_size):
            block = diff_image[i * block_size:(i + 1) * block_size, j * block_size:(j + 1) * block_size]
            feature = block.flatten()
            vector_set[idx, :] = feature[:vector_set.shape[1]]
            idx += 1

    mean_vec = np.mean(vector_set, axis=0)
    return vector_set, mean_vec


def find_FVS(EVS, diff_image, mean_vec, new):
    i = 2
    feature_vector_set = []

    while i < new[0] - 2:
        j = 2
        while j < new[1] - 2:
            block = diff_image[i - 2:i + 3, j - 2:j + 3]
            feature = block.flatten()
            feature_vector_set.append(feature)
            j = j + 1
        i = i + 1

    feature_vector_set = np.array(feature_vector_set)
    feature_vector_set = feature_vector_set.reshape((-1, 25))
    FVS = np.dot(feature_vector_set, EVS)
    FVS = FVS - mean_vec
    print("\nfeature vector space size", FVS.shape)
    return FVS


def clustering(FVS, components, new):
    kmeans = KMeans(components, verbose=0)
    kmeans.fit(FVS)
    output = kmeans.predict(FVS)
    count = Counter(output)

    least_index = min(count, key=count.get)
    print(new[0], new[1])
    change_map = np.reshape(output, (new[0] - 4, new[1] - 4, -1))  # this has been changed and should be checked

    return least_index, change_map


# Get the absolute path to the directory containing the image files
directory = os.path.abspath('data_files/test_data')

if __name__ == "__main__":
    imagepath1 = os.path.join(directory, '20200327.jpeg')  # Construct the absolute paths to the image files
    imagepath2 = os.path.join(directory, '20230208.jpeg')  # Construct the absolute paths to the image files
    find_PCAKmeans(imagepath1, imagepath2)
Stacking
Bands
from stack_bands import band_stacking_three_bands

band_files = (
'data_files/R10m/T30UWB_20221207T111339_B03_10m.jp2', 'data_files/R10m/T30UWB_20221207T111339_B04_10m.jp2',
'data_files/R10m/T30UWB_20221207T111339_B08_10m.jp2')
output_tiff = 'data_files/R10m/T30UWB_20221207T111339.tif'
output_jpg = 'data_files/test_data/Img2a.jpg'

band_stacking_three_bands(band_files, output_tiff, output_jpg)
# this works and also converts the tiff to a jpeg
import rasterio
import numpy as np

band_files = (
'data_files/R10m/T30UWB_20221207T111339_B03_10m.jp2', 'data_files/R10m/T30UWB_20221207T111339_B04_10m.jp2',
'data_files/R10m/T30UWB_20221207T111339_B08_10m.jp2')
output_tiff = 'data_files/test_data/Img2a.tif'
output_jpg = 'data_files/test_data/Img2a.jpg'

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

# Convert the GeoTIFF to JPEG
with rasterio.open(output_tiff) as src:
    profile = src.profile
    # Read the data from the GeoTIFF
    data = src.read()

# Convert the data to the 0-255 range
data = (data * 255 / data.max()).astype(np.uint8)

# Write the data to the JPEG file
with rasterio.open(output_jpg, 'w', driver='JPEG', width=profile['width'], height=profile['height'],
                   count=profile['count'], dtype='uint8') as dst:
    dst.write(data)
