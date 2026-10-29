import geopandas as gpd
import rasterio
from rasterstats import zonal_stats

def get_treeheight(polygon: gpd.GeoDataFrame, raster_path: str) -> gpd.GeoDataFrame:
    with rasterio.open(raster_path) as src:
        if polygon.crs != src.crs:
            polygon = polygon.to_crs(src.crs)

    stats = zonal_stats(polygon.geometry, raster_path, stats=["mean"], all_touched=True)

    polygon["treeheight"] = [s.get("mean") for s in stats]
    print(f"treeheight derived")

    return polygon.to_crs("EPSG:25832")

