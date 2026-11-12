import geopandas as gpd


tree_path = "/home/berberic/Documents/allometry/auwald_run_mayyolopolys/results/biomass/biomass23.geojson"
patch_path = "/home/berberic/Documents/allometry/auwald_run_mayyolopolys/patches.geojson"

trees = gpd.read_file(tree_path)
patch = gpd.read_file(patch_path).to_crs(trees.crs)

centroids = trees.copy()
centroids["geometry"] = trees.centroid
centroids = gpd.clip(centroids, patch)

trees = trees.loc[centroids.index]

print(f"Total Biomass: ", sum(trees["AGB"]))

trees.to_file("/home/berberic/Documents/allometry/auwald_run_mayyolopolys/filtered_biomass.geojson")
