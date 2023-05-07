import geopandas as gpd
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
from sentinelsat import SentinelAPI, make_path_filter
from IPython import display
import shapely
import os
from PIL import Image

def download_best_overlap_image(company_detail,date_start,date_end,img_name):
    # Load water company data as wrz, remove unnecessary columns
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
    search_area = polygon.minimum_rotated_rectangle

    #search_area # to visual rotated rectangle

    #connect to SentinelAPI
    api = SentinelAPI(None, None, api_url='https://scihub.copernicus.eu/dhus') # connect to the SentinelAPi using sign on details on .netrc file

    #retrieve images for 10% cloud cover, date range 1 April 2019 to 31 March 2020 
    products = api.query(search_area.wkt, # use the WKT representation of our search area
                     date=(date_start,date_end), # all images from February 2023
                     platformname='Sentinel-2', # the platform name is Sentinel-2
                     producttype='S2MSI2A', # surface reflectance product (L2A)
                     cloudcoverpercentage=(0, 10)) # limit to 10% cloud cover
    # Determine the number of images retrieved
    nresults = len(products) # get the number of results found
    print('Found {} results'.format(nresults)) # show the number of results found 
    if nresults == 0:
        print('No images in this range')

    results = next(iter(products)) # gets the second item from the dict
    products[results] # show the metadata for the second item

    qlook = api.download_quicklook(results) # download the quicklook image for this first result 
    display.Image(qlook['path']) # display the image 

    product_geo = SentinelAPI.to_geodataframe(products) # convert the search results to a geodataframe
    product_geo.head() # show the first 5 rows of the geodataframe

    # calculate the % overlay of the image and the rectangle for selection
    for ind, row in product_geo.iterrows():
        intersection = search_area.intersection(row['geometry']) # find the intersection of the two polygons
        product_geo.loc[ind, 'overlap'] = intersection.area / search_area.area # get the fractional overlap
    
    # print(product_geo.overlap) # show the fractional overlap for each index

    # work out the max overlap and return the index
    max_index = product_geo.overlap.argmax() # get the integer location of the largest overlap value
    # print(max_index) 

    best_overlap = product_geo.inbest_overlap = product_geo.index[max_index] # get the actual index (image name) with the largest overlap
    # download the quicklook image for the best overlap
    # qlook = api.download_quicklook(best_overlap)

    # create an Image object from the downloaded image file
    # img = Image.open(qlook['path'])

    # save the Image object as PNG with the desired file name and location
    # img.save('data_files/img.png')
    
    # download best image
    api.download(best_overlap) # downloads the best result
    # api.download(firest_result, 
    #    nodefilter=make_path_filter("*_B*.jp2")) # only downloads the image bands
    
    # Get the name of the downloaded image
    image_name = api.get_product_odata(best_overlap)['title']
    
    print('Downloaded image: {}'.format(image_name))
    