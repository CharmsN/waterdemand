import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import Counter
import os

'''This module requires cv2, numpy, sklearn, collections, PIL, imageio, os and math to be installed. It defines three functions: find_vector_set, find_FVS, and clustering, which are used for various steps in the change detection process.

The find_PCAKmeans function is the main function that takes two image paths as inputs and performs change detection using PCA and K-means. It reads the images, resizes them, calculates the difference image, performs PCA on the difference image, and prepares the feature vector space (FVS).

The find_vector_set function divides the difference image into smaller blocks, extracts feature vectors from each block, and calculates the mean vector from all the feature vectors.

The find_FVS function extracts blocks from the difference image, flattens them into feature vectors, combines them into a feature vector space, and transforms the feature vector space using PCA by multiplying it with the eigenvectors and subtracting the mean vector.

The clustering function performs K-means clustering on the feature vector space. It assigns each feature vector to a cluster, identifies the least common cluster as a reference for change detection, reshapes the cluster assignments into a change map, and returns the least common cluster index and the change map.

The module also includes some additional code to save the change map and clean change map as image files.

Finally, it provides the image paths and call them in the find_PCAKmeans function.

This code is an adaptation of the code provided in GitHub by Abhujeet Kumar on 25 November 2017. (Change-Detection-In-Satellite_Imagery)'''

def find_PCAKmeans(imagepath1, imagepath2):   # Function to find changes using PCA and K-means
    print('Operating')
    """
   Further information can be found by calling the help function for PCSKmeans_updatedCN module.    
    """ 
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
    cv2.imwrite("data_files/changemap.jpg", change_map)
    cv2.imwrite("data_files/cleanchangemap.jpg", cleanChangeMap)


def find_vector_set(diff_image, new_size):   # Function to find the vector set and mean vector from the difference image)    
    """
      Further information can be found by calling the help function for PCSKmeans_updatedCN module.    
    """   
    block_size = 5  
    num_blocks = (new_size[0] // block_size) * (new_size[1] // block_size)

    vector_set = np.empty((num_blocks, block_size * block_size), dtype=np.int16)
    idx = 0

    for i in range(new_size[0] // block_size):    # Divide the difference image into blocks and extract features from each block
        for j in range(new_size[1] // block_size):
            block = diff_image[i * block_size:(i + 1) * block_size, j * block_size:(j + 1) * block_size]
            feature = block.flatten()
            vector_set[idx, :] = feature[:vector_set.shape[1]]
            idx += 1

    mean_vec = np.mean(vector_set, axis=0)
    return vector_set, mean_vec


def find_FVS(EVS, diff_image, mean_vec, new):   # Function to find the feature vector space (FVS) from the EVS, difference image, mean vector, and new size 
    """
      Further information can be found by calling the help function for PCSKmeans_updatedCN module. 
    """ 
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
    """
    Further information can be found by calling the help function for PCSKmeans_updatedCN module.
    """
    kmeans = KMeans(n_clusters=components, n_init=10, verbose=0)  # Set n_init parameter explicitly
    kmeans.fit(FVS)
    output = kmeans.predict(FVS)
    count = Counter(output)

    least_index = min(count, key=count.get)
    print(new[0], new[1])
    change_map = np.reshape(output, (new[0] - 4, new[1] - 4, -1))  # this has been changed and should be checked
    return least_index, change_map

directory = os.path.abspath('data_files/test_data')   # Get the absolute path to the directory containing the image files

if __name__ == "__main__":
    imagepath1 = os.path.join(directory, '20200327.jpeg')  # Construct the absolute paths to the image files
    imagepath2 = os.path.join(directory, '20230208.jpeg')  # Construct the absolute paths to the image files
    find_PCAKmeans(imagepath1, imagepath2)
    
print("Code execution complete.")
