from pystac_client import Client
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.io import MemoryFile



def get_biomass_fromDLR(catalog, year: int, aoi_path: str = "/home/berberic/Documents/data/training_data2/bonn_trainingdata/bonn_forest.geojson"):

    # defining AOI
    aoi = gpd.read_file(aoi_path)
    bbox = aoi.to_crs("EPSG:4326").total_bounds

    # pulling data via STAC
    search = catalog.search(collections=["FOREST_STRUCTURE_DE_AGBD_P1Y"], bbox=bbox, datetime=f"{year}-01-01/{year}-12-31")
    url = list(next(search.items()).assets.values())[0].href

    # converting to rasterio-dataset
    with rasterio.open(url) as src:
        out_image, out_transform = mask(src, aoi.to_crs(src.crs).geometry, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({"height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform})

    memfile = MemoryFile()
    dataset = memfile.open(**out_meta)
    dataset.write(out_image)
    dataset.set_band_description(1, "AGBD")

    return dataset