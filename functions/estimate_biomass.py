import geopandas as gpd
import pandas as pd

def estimate_biomass(polygon: gpd.GeoDataFrame) -> gpd.GeoDataFrame:

    conifers = polygon[polygon["treetype"] == "coniferous"].copy()
    broadleaved = polygon[polygon["treetype"] == "broadleaved"].copy()

    # this is from https://onlinelibrary.wiley.com/doi/10.1111/gcb.13388
    broadleaved["AGB"] = 0.016 * ((broadleaved["treeheight"] * broadleaved["diameter"]) ** 2.013) * 1.0210
    conifers["AGB"] = (0.016 + 0.093) * ((conifers["treeheight"] * conifers["diameter"]) ** (2.013 - 0.223)) * 1.0210

    polygons = pd.concat([conifers, broadleaved], ignore_index=True)
    print("biomass derived")

    return polygons