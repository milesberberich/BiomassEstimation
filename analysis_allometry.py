# This code will research the allometry on a single-tree level with regard to the tree species.

#!/usr/bin/env python
# coding: utf-8

# ## import functions/libraries


import geopandas as gpd
import rasterio, pandas
import argparse
from functions.estimate_biomass import estimate_biomass
from functions.get_diameter import *
from functions.get_treespecies import *
from functions.get_treeheight import *
from functions.histogram_treespecies import *
import matplotlib.pyplot as plt
import seaborn as sns


# ## define basepath/settings

parser = argparse.ArgumentParser()
parser.add_argument("--basepath", type=str, default="/home/berberic/Documents/allometry/")
parser.add_argument("--export_results", action="store_true")
parser.add_argument("--export_plots", action="store_true")
args = parser.parse_args()

basepath = args.basepath
export_results = args.export_results
export_plots = args.export_plots


# ## load polygons



trees21 = gpd.read_file(f"{basepath}trees/bonn_2021.geojson")
trees16 = gpd.read_file(f"{basepath}trees/bonn_2016.geojson")


# ## calculate diameter


trees16 = get_diameter(trees16)
trees21 = get_diameter(trees21)


# ## get tree species



trees16 = get_treespecies(polygon=trees16, raster_path= f"{basepath}/treespecies/treespecies_2016_bonn.tif")
trees21 = get_treespecies(polygon=trees21, raster_path=f"{basepath}/treespecies/treespecies_2021_bonn.tif")



print(trees16[["treespecies", "treetype"]].head())


# ## get tree height


trees16 = get_treeheight_fromDLR(polygon=trees16, year = 2016)
trees21 = get_treeheight_fromDLR(polygon=trees21, year = 2021)




# handle zeros in treeheight by using mean instead
remove_zeros = True

if remove_zeros: # Trees with 0 as treeheight, get the mean treeheight instead
    trees16.loc[trees16["treeheight"] == 0, "treeheight"] = trees16["treeheight"].mean()
    trees21.loc[trees21["treeheight"] == 0, "treeheight"] = trees21["treeheight"].mean()


# plots
## relationship between height and diameter

# 2016 Plot
plt.figure(figsize=(8, 5))
sns.scatterplot(data=trees16, x="treeheight", y="diameter", hue="treespecies", alpha=0.5)
plt.title("Tree Height vs. Crown Diameter in 2016")
plt.xlabel("Tree Height (m)")
plt.ylabel("Crown Diameter (m)")
plt.legend(title="Tree Species", bbox_to_anchor=(1.05, 1), loc="upper left")

if export_plots: plt.savefig(f"{basepath}results/plots/height_vs_diameter_2016.png", bbox_inches='tight')
plt.close()


# 2021 Plot
plt.figure(figsize=(8, 5))
sns.scatterplot(data=trees21, x="treeheight", y="diameter", hue="treespecies", alpha=0.5)
plt.title("Tree Height vs. Crown Diameter in 2021")
plt.xlabel("Tree Height (m)")
plt.ylabel("Crown Diameter (m)")
plt.legend(title="Tree Species", bbox_to_anchor=(1.05, 1), loc="upper left")

if export_plots: plt.savefig(f"{basepath}results/plots/height_vs_diameter_2021.png", bbox_inches='tight')
plt.close()