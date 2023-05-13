import rasterio
from rasterio.mask import mask
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
# Define the paths to the image and shapefile
image_path = 'data_files/R10m/T30UWB_20230121T111351.tif'
shapefile_path = 'data_files/WaterSupplyAreas_incNAVs v1_4.shp'
reprojected_image ='data_files/R10m/T30UWB_20230121_reproj.tif'
output_path ='data_files/R10m/T30UWB_20230121_cropped.tif'
# Define the attribute and value to select the desired area
attribute_field = 'AreaServed'
attribute_value = 'Bournemouth'

# Read the shapefile using geopandas
gdf = gpd.read_file(shapefile_path)

# Filter the shapefile to select the desired area
filtered_gdf = gdf[gdf[attribute_field] == attribute_value]
# Read the shapefile and raster image
gdf = gpd.read_file(shapefile_path)
with rasterio.open(image_path) as src:
    pass  # We only need to open the raster to access its CRS
# Check the coordinate reference systems (CRS)
print("Shapefile CRS:", gdf.crs)
print("Raster CRS:", src.crs)
# Open the raster image
with rasterio.open(image_path) as src:
    # Define the target CRS
    target_crs = 'EPSG:27700'

    # Calculate the transformation parameters for reprojection
    transform, width, height = calculate_default_transform(
        src.crs, target_crs, src.width, src.height, *src.bounds
    )

    # Create the reprojected image
    reprojected_image_path = reprojected_image
    reprojected_image_meta = src.meta.copy()
    reprojected_image_meta.update({
        'crs': target_crs,
        'transform': transform,
        'width': width,
        'height': height
    })

    with rasterio.open(reprojected_image_path, 'w', **reprojected_image_meta) as dst:
        for i in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, i),
                destination=rasterio.band(dst, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=target_crs,
                resampling=Resampling.nearest
            )
# Read the raster image
with rasterio.open(reprojected_image) as src:
    # Crop the image using the shapefile
    cropped_image, cropped_transform = mask(src, filtered_gdf.geometry, crop=True)
    cropped_meta = src.meta.copy()

# Update the metadata of the cropped image
cropped_meta.update({
    "height": cropped_image.shape[1],
    "width": cropped_image.shape[2],
    "transform": cropped_transform
})
# Save the cropped image

with rasterio.open(output_path, 'w', **cropped_meta) as dest:
    dest.write(cropped_image)

# Display the cropped image (optional)
plt.imshow(cropped_image[0, :, :])  # Assuming the image is single-band
plt.axis('off')
plt.show()