import geopandas as gpd
import rasterio


WEGLER_SPECIES = {
    0: "pine", 1: "spruce", 2: "douglas fir", 3: "larch", 4: "fir",
    5: "beech", 6: "oak", 7: "birch", 8: "alder", 9: "other deciduous",
    800: "uncertain",
}

BLICKENSDOERFER_SPECIES = {
    2: "birch", 3: "beech", 4: "douglas fir", 5: "oak", 6: "alder",
    8: "spruce", 9: "pine", 10: "larch", 14: "fir", 16: "odh", 17: "odl",
}

BROADLEAVED = {"beech", "oak", "birch", "alder", "other deciduous", "odh", "odl"}


def get_treespecies(polygon: gpd.GeoDataFrame, raster_path: str, data_source: str = "wegler") -> gpd.GeoDataFrame:

    if data_source == "wegler":
        species_mapping = WEGLER_SPECIES
    elif data_source == "blickensdoerfer":
        species_mapping = BLICKENSDOERFER_SPECIES
    else:
        raise ValueError(f"Unknown data_source: {data_source}")

    with rasterio.open(raster_path) as src:
        if polygon.crs != src.crs:
            centroids = polygon.geometry.centroid.to_crs(src.crs)
        else:
            centroids = polygon.geometry.centroid

        coord_pairs = [(point.x, point.y) for point in centroids]

        polygon["treespecies"] = [val[0] for val in src.sample(coord_pairs)]

    polygon["treespecies"] = polygon["treespecies"].map(species_mapping)

    # broadleaved/coniferous
    polygon["treetype"] = polygon["treespecies"].apply(
        lambda s: None if s is None or s != s  # None or NaN
        else ("broadleaved" if s in BROADLEAVED else "coniferous")
    )

    return polygon.to_crs("EPSG:25832")