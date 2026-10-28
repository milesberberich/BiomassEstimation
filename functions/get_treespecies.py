import geopandas as gpd
import rasterio
from rasterstats import zonal_stats


def get_treespecies(polygon: gpd.GeoDataFrame, raster_path: str) -> gpd.GeoDataFrame:
    with rasterio.open(raster_path) as src:
        if polygon.crs != src.crs:
            polygon = polygon.to_crs(src.crs)

    stats = zonal_stats(polygon, raster_path, categorical=True, all_touched=True)

    results = []
    for s in stats:
        c0 = s.get(0, 0)
        c1 = s.get(1, 0)

        if c0 == 0 and c1 == 0:
            results.append(2)
        elif c1 > c0:
            results.append(1)
        else:
            results.append(0)

    polygon["treespecies"] = results
    return polygon.to_crs("EPSG:25832")