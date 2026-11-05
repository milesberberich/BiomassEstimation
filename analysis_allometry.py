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


# ## load polygons  #####################################################

#trees21 = gpd.read_file(f"{basepath}trees/bonn_2021.geojson")
trees16 = gpd.read_file(f"{basepath}trees/bonn_2016.geojson")

# ## calculate diameter  #####################################################

trees16 = get_diameter(trees16)
#trees21 = get_diameter(trees21)

# ## get tree species  #####################################################

trees16 = get_treespecies(polygon=trees16, raster_path= f"{basepath}/treespecies/treespecies_2016_bonn.tif")
#trees21 = get_treespecies(polygon=trees21, raster_path=f"{basepath}/treespecies/treespecies_2021_bonn.tif")

print(trees16[["treespecies", "treetype"]].head())

# ## get tree height  #####################################################


treeheights16 = get_treeheight_fromfile(polygon=trees16, raster_path=f"{basepath}/treeheight/CHM_1m_bonn.tif", scale=False)
#trees21 = get_treeheight_fromDLR(polygon=trees21, year = 2021, aoi_path=f"{basepath}/aoi.geojson")

# handle zeros in treeheight by using mean instead
remove_zeros = True

if remove_zeros: # Trees with 0 as treeheight, get the mean treeheight instead
    trees16.loc[trees16["treeheight"] == 0, "treeheight"] = trees16["treeheight"].mean()
    #trees21.loc[trees21["treeheight"] == 0, "treeheight"] = trees21["treeheight"].mean()


# PLOTS #####################################################
## relationship between height and diameter

sns.set_theme(style="ticks", font="Arial", font_scale=1.1)
plt.rcParams['font.family'] = 'sans-serif'

# 2016 FacetGrid Plot
g16 = sns.FacetGrid(trees16, col="treespecies", col_wrap=4, height=3)
g16.map_dataframe(sns.histplot, x="treeheight", y="diameter", bins=30, cmap="viridis")
g16.set_axis_labels("Tree Height (m)", "Crown Diameter (m)")
g16.set_titles(col_template="{col_name}", fontweight='bold')
g16.fig.subplots_adjust(top=0.88)
g16.fig.suptitle("Tree Height vs. Crown Diameter Density (2016)", fontweight='bold')
if export_plots:
    plt.savefig(f"{basepath}results/plots/height_vs_diameter_2016_species.png", bbox_inches='tight', dpi=300)
plt.close()

# 2021 FacetGrid Plot
#g21 = sns.FacetGrid(trees21, col="treespecies", col_wrap=4, height=3)
#g21.map_dataframe(sns.histplot, x="treeheight", y="diameter", bins=30, cmap="viridis")
#g21.set_axis_labels("Tree Height (m)", "Crown Diameter (m)")
#g21.set_titles(col_template="{col_name}", fontweight='bold')
#g21.fig.subplots_adjust(top=0.88)
#g21.fig.suptitle("Tree Height vs. Crown Diameter Density (2021)", fontweight='bold')
#if export_plots:
    #plt.savefig(f"{basepath}results/plots/height_vs_diameter_2021.png", bbox_inches='tight', dpi=300)
#plt.close()