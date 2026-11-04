import numpy as np
import geopandas as gpd

def get_treeheight_fromfile(polygon: gpd.GeoDataFrame, raster_path: str, scale = True) -> gpd.GeoDataFrame:
    ''' Load a tree height dataset from a file and append the information to the polygons. '''
    with rasterio.open(raster_path) as src:
        if polygon.crs != src.crs:
            polygon = polygon.to_crs(src.crs)
        array = src.read(1).astype('float64') # float64 prevents numpy sum overflow
        transform = src.transform
        actual_nodata = src.nodata

    # Mask out actual nodata, NaNs, and negative CHM noise (anything < 0)
    if actual_nodata is not None:
        array[array == actual_nodata] = np.nan
    array[array < 0] = 0.0  # Clamp negative CHM noise to 0
    array[np.isnan(array)] = -9999.0

    stats = zonal_stats(
        polygon.geometry,
        array,
        affine=transform,
        nodata=-9999.0,
        stats=["mean"],
        all_touched=True
    )

    # Use float(s["mean"]) if not None, otherwise 0.0
    polygon["treeheight"] = [float(s["mean"]) if s["mean"] is not None else 0.0 for s in stats]

    # scaling to meters
    if scale:
        polygon["treeheight"] = polygon["treeheight"] / 100

    print("treeheight derived", flush=True)

    return polygon.to_crs("EPSG:25832")


#########################################################################################################

from pystac_client import Client
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.io import MemoryFile
from rasterstats import zonal_stats

def get_treeheight_fromDLR(polygon: gpd.GeoDataFrame, year: int, aoi_path: str):

    if year < 2017:
        print("The dataset begins in 2017. For all prior years, 2017 is used.")
        year = 2017

    # defining AOI
    aoi = gpd.read_file(aoi_path)
    bbox = aoi.to_crs("EPSG:4326").total_bounds

    # pulling data via STAC
    search = Client.open("https://geoservice.dlr.de/eoc/ogc/stac/v1").search(
        collections=["FOREST_STRUCTURE_DE_RH95_P1Y"], bbox=bbox, datetime=f"{year}-01-01/{year}-12-31")
    url = list(next(search.items()).assets.values())[0].href

    # converting to rasterio-dataset
    with rasterio.open(url) as src:
        out_image, out_transform = mask(src, aoi.to_crs(src.crs).geometry, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({"height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform})

    memfile = MemoryFile()
    dataset = memfile.open(**out_meta)
    dataset.write(out_image)
    dataset.set_band_description(1, "treeheight")

    if polygon.crs != dataset.crs:
        polygon = polygon.to_crs(dataset.crs)

    # get values to polygons
    stats = zonal_stats(polygon.geometry, dataset.read(1), affine=dataset.transform, nodata=dataset.nodata, stats=["mean"], all_touched=True)
    polygon["treeheight"] = [s.get("mean") or 0.0 for s in stats]

    print("treeheight derived")

    return polygon.to_crs("EPSG:25832")

