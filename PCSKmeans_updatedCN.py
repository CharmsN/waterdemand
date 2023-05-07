import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import Counter
import imageio
import geopandas as gps
import cartopy.crs as ccrs
import rasterio
from rasterio.mask import mask

wrz = gpd.read_file(os.path.abspath('data_files/WaterSupplyAreas_incNAVs v1_4.shp'))
    
    # select water company to review in further detail:
    selected_company_gdf = wrz[wrz['AreaServed'] == company_detail]

    # get the outline of the selected water company:
    company_outline = selected_company_gdf['geometry']

    # create a new GeoDataFrame with the outline of the selected water company:
    outline_gdf = gpd.GeoDataFrame(geometry=company_outline)

    # print the GeoDataFrame
    print(outline_gdf)

    # ensure that the crs for the the gdf of the water company selected is set to epsg 4326
    outline_gdf = outline_gdf.to_crs(epsg=4326)

    # convert the MULTIPOLYGON to a valid POLYGON
    polygon = outline_gdf['geometry'].unary_union
    #polygon # to visualise polygon

    # get the minimum rotated angle 
    boundary_box = polygon.minimum_rotated_rectangle
    
image__1='data_files/S2A_MSIL2A_20201212T111451_N0214_R137_T30UWB_20201212T140141.jpeg'
image__2='data_files/S2B_MSIL2A_20221207T111339_N0509_R137_T30UWB_20221207T125110.jpeg'

# Open the image file
image_1 = rasterio.open(image__1)
image_2 = rasterio.open(image__2)

# Create a image_1 = rasterio.open(image__1)polygon geometry from the boundary box
boundary_polygon = {
    'type': 'Polygon',
    'coordinates': [boundary_box]
}

# Clip the image using the boundary polygon
clipped_image1, clipped_transform = mask(image1, [boundary_polygon], crop=True)

# Update the metadata of the clipped image to match the new dimensions
clipped_meta1 = image1.meta.copy()
clipped_meta1.update({
    'height': clipped_image1.shape[1],
    'width': clipped_image1.shape[2],
    'transform': clipped_transform1
})

# Save the clipped image to a new file
clipped_filename1 = 'clipped_image1.jpeg'
with rasterio.open(clipped_filename1, 'w', **clipped_meta) as dst:
    dst.write(clipped_image1)

print("Image clipped and saved as", clipped_filename1)

# Clip the image using the boundary polygon
clipped_image2, clipped_transform = mask(image2, [boundary_polygon], crop=True)

# Update the metadata of the clipped image to match the new dimensions
clipped_meta2 = image2.meta.copy()
clipped_meta2.update({
    'height': clipped_image2.shape[1],
    'width': clipped_image2.shape[2],
    'transform': clipped_transform2
})

# Save the clipped image to a new file
clipped_filename2 = 'clipped_image1.jpeg'
with rasterio.open(clipped_filename2, 'w', **clipped_meta) as dst:
    dst.write(clipped_image2)

print("Image clipped and saved as", clipped_filename2)

def find_vector_set(diff_image, new_size):
    i = 0
    j = 0
    vector_set = np.zeros((int(new_size[0] * new_size[1] / 25), 25))
    print('\nvector_set shape', vector_set.shape)

    while i < vector_set.shape[0]:
        while j < new_size[0]:
            k = 0
            while k < new_size[1]:
                block = diff_image[j:j+5, k:k+5]
                feature = block.ravel()
                vector_set[i, :] = feature
                k = k + 5
            j = j + 5
        i = i + 1

    mean_vec = np.mean(vector_set, axis=0)
    vector_set = vector_set - mean_vec

    return vector_set, mean_vec


def find_FVS(EVS, diff_image, mean_vec, new):
    i = 2
    feature_vector_set = []

    while i < new[0] - 2:
        j = 2
        while j < new[1] - 2:
            block = diff_image[i-2:i+3, j-2:j+3]
            feature = block.flatten()
            feature_vector_set.append(feature)
            j = j + 1
        i = i + 1

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
    change_map = np.reshape(output, (new[0] - 4, new[1] - 4))

    return least_index, change_map


def find_PCAKmeans(imagepath1, imagepath2):
    print('Operating')

    image1 = imageio.imread(clipped_filename1)
    image2 = imageio.imread(clipped_filename2)
    print(image1.shape, image2.shape)
    new_size = np.asarray(image1.shape) // 5 * 5
    image1 = imageio.imresize(image1, new_size).astype(np.int16)
    image2 = imageio.imresize(image2, new_size).astype(np.int16)

    diff_image = np.abs(image1 - image2)
    imageio.imsave('diff.jpg', diff_image)
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

   
