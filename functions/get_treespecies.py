import geopandas as gpd
import rasterio
from rasterstats import zonal_stats


def get_treespecies(polygon: gpd.GeoDataFrame, raster_path: str) -> gpd.GeoDataFrame:

    with rasterio.open(raster_path) as src:
        if polygon.crs != src.crs:
            centroids = polygon.geometry.centroid.to_crs(src.crs)
        else:
            centroids = polygon.geometry.centroid

        coord_pairs = [(point.x, point.y) for point in centroids]

        polygon["treespecies"] = [val[0] for val in src.sample(coord_pairs)]

        species_mapping = {0: "pine", 1: "spruce", 2: "douglas fir", 3: "larch", 4: "fir", 5: "beech", 6: "oak", 7: "birch", 8: "alder", 9: "other deciduous", 800: "uncertain"}
        polygon["treespecies"] = polygon["treespecies"].map(species_mapping)

        # broadleaved/coniferous
        type_mapping = {"pine": "coniferous", "spruce": "coniferous", "douglas fir": "coniferous", "larch": "coniferous", "fir": "coniferous", "beech": "broadleaved", "oak": "broadleaved", "birch": "broadleaved", "alder": "broadleaved", "other deciduous": "broadleaved"}
        polygon["treetype"] = polygon["treespecies"].map(type_mapping)

    return polygon.to_crs("EPSG:25832")