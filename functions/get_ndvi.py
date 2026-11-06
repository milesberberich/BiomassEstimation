import geopandas as gpd
from rasterstats import zonal_stats
import rasterio

def get_ndvi(polygon: gpd.GeoDataFrame, raster_path: str, metric="median"):
    '''Load a ndvi dataset from a file and append the information to the polygons.'''
    with rasterio.open(raster_path) as src:
        if polygon.crs != src.crs:
            polygon = polygon.to_crs(src.crs)

    stats = zonal_stats(
        polygon.geometry,
        raster_path,
        stats=[metric],
        all_touched=True)

    polygon["ndvi"] = [item[metric] for item in stats]

    print("NDVI derived", flush=True)

    return polygon.to_crs("EPSG:25832")