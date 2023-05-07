import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import Counter
import imageio

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

    image1 = imageio.imread('data_files/S2A_MSIL2A_20201212T111451_N0214_R137_T30UWB_20201212T140141.jpeg')
    image2 = imageio.imread('data_files/S2B_MSIL2A_20221207T111339_N0509_R137_T30UWB_20221207T125110.jpeg')
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

   