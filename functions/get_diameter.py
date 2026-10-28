import geopandas as gpd
import math

def get_diameter(polygon: gpd.GeoDataFrame) -> gpd.GeoDataFrame:

    polygon["area"] = polygon.area
    polygon["diameter"] = 2*((polygon["area"]/math.pi)**0.5)
    return polygon