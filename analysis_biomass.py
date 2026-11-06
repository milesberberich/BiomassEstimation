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
from functions.get_ndvi import *
from functions.histogram_treespecies import *
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

#####################################################################################################################################################
# ## define basepath/settings ################################################################################################################################
#####################################################################################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("--basepath", type=str, default="/home/berberic/Documents/allometry/auwald_run_hightrees")
parser.add_argument("--aoi", nargs="+", default=["auwald_2023"])
parser.add_argument("--export_results", action="store_true")
parser.add_argument("--export_plots", action="store_true")
args = parser.parse_args()

basepath = args.basepath
aoi = args.aoi
export_results = args.export_results
export_plots = args.export_plots

filter_by_CHM = True # trees with a height lower than
# this get filter out. ( the tree height is derived using the max. values o fthe CHM that in the polygon)
filter_height = 10

filter_by_ndvi = True # trees with a ndvi lower than this get filter out. (the ndvi is derived using the 20cm DOPs mean value of pixels that intersect with the polygon)
filter_ndvi = 0.3

#####################################################################################################################################################
# ## load polygons ################################################################################################################################
#####################################################################################################################################################

if "bonn_2016" in aoi:
    trees16 = gpd.read_file(f"{basepath}/trees/bonn_2016_vital.geojson")
if "bonn_2021" in aoi:
    trees21 = gpd.read_file(f"{basepath}/trees/bonn_2021_vital.geojson")
if "auwald_2023" in aoi:
    trees23 = gpd.read_file(f"{basepath}/trees/auwald_2023_vital.geojson")
print("Polygons were loaded.")

#####################################################################################################################################################
# ## calculate NDVI ################################################################################################################################
#####################################################################################################################################################

if "bonn_2016" in aoi:
    trees16 = get_ndvi(trees16, f"{basepath}/ndvi/ndvi_bonn_2016.tif")
if "bonn_2021" in aoi:
    trees21 = get_ndvi(trees21, f"{basepath}/ndvi/ndvi_bonn_2021.tif")
if "auwald_2023" in aoi:
    trees23 = get_ndvi(trees23, f"{basepath}/ndvi/ndvi_auwald.tif")
print("NDVI values were derived and polygons reprojected.")

#####################################################################################################################################################
# ## calculate diameter ################################################################################################################################
#####################################################################################################################################################
if "bonn_2016" in aoi:
    trees16 = get_diameter(trees16)
if "bonn_2021" in aoi:
    trees21 = get_diameter(trees21)
if "auwald_2023" in aoi:
    trees23 = get_diameter(trees23)
print("Crown diameters were calculated.")

#####################################################################################################################################################
# ## get tree species ################################################################################################################################
#####################################################################################################################################################

if "bonn_2016" in aoi:
    trees16 = get_treespecies(polygon=trees16, raster_path=f"{basepath}/treespecies/treespecies_blickensdoerfer.tif", data_source="blickensdoerfer")
if "bonn_2021" in aoi:
    trees21 = get_treespecies(polygon=trees21, raster_path=f"{basepath}/treespecies/treespecies_blickensdoerfer.tif", data_source="blickensdoerfer")
if "auwald_2023" in aoi:
    trees23 = get_treespecies(polygon=trees23, raster_path=f"{basepath}/treespecies/treespecies_blickensdoerfer.tif", data_source="blickensdoerfer")
    trees23 = trees23.fillna({"treetype": "broadleaved"})    # fill NA! auwald dominated by oak...
print("Tree species were derived.")

#####################################################################################################################################################
# ## get tree height ################################################################################################################################
#####################################################################################################################################################

if "bonn_2016" in aoi:
    treeheights16 = get_treeheight_fromfile(polygon=trees16, raster_path=f"{basepath}/treeheight/CHM_1m_bonn.tif", scale=False)
    r = treeheights16["treeheight"].corr(treeheights16["diameter"])
    print(f"corellation between treeheight and diameter: {r}")
if "bonn_2021" in aoi:
    treeheights21 = get_treeheight_fromfile(polygon=trees21, raster_path=f"{basepath}/treeheight/CHM_1m_bonn.tif", scale=False)
if "auwald_2023" in aoi:
    treeheights23 = get_treeheight_fromfile(polygon=trees23, raster_path=f"{basepath}/treeheight/CHM_1m_auwald.tif", scale=False)
    r = treeheights23["treeheight"].corr(treeheights23["diameter"])
    print(f"corellation between treeheight and diameter: {r}")

print("Tree heights were derived.")

#####################################################################################################################################################
### filtering ############################################################################################################
#####################################################################################################################################################
# Because trees with a low height and/or ndvi seem off, they get filtered here

if filter_by_CHM:
    if "bonn_2016" in aoi: treeheights16 = treeheights16[treeheights16["treeheight"] >= filter_height]
    if "bonn_2021" in aoi: treeheights21 = treeheights21[treeheights21["treeheight"] >= filter_height]
    if "auwald_2023" in aoi: treeheights23 = treeheights23[treeheights23["treeheight"] >= filter_height]

if filter_by_ndvi:
    if "bonn_2016" in aoi: treeheights16 = treeheights16[treeheights16["ndvi"] >= filter_ndvi]
    if "bonn_2021" in aoi: treeheights21 = treeheights21[treeheights21["ndvi"] >= filter_ndvi]
    if "auwald_2023" in aoi: treeheights23 = treeheights23[treeheights23["ndvi"] >= filter_ndvi]

#####################################################################################################################################################
### estimate biomass ################################################################################################################################
#####################################################################################################################################################

if "bonn_2016" in aoi:
    biomass16 = estimate_biomass(treeheights16)
if "bonn_2021" in aoi:
    biomass21 = estimate_biomass(treeheights21)
if "auwald_2023" in aoi:
    biomass23 = estimate_biomass(treeheights23)
print("Biomass was estimated.")

if export_results:
    if "bonn_2016" in aoi:
        biomass16.to_file(f"{basepath}/results/biomass/biomass16.geojson", driver="GeoJSON")
    if "bonn_2021" in aoi:
        biomass21.to_file(f"{basepath}/results/biomass/biomass21.geojson", driver="GeoJSON")
    if "auwald_2023" in aoi:
        biomass23.to_file(f"{basepath}/results/biomass/biomass23.geojson", driver="GeoJSON")
print("polygons saved")

#####################################################################################################################################################
# ## summary ################################################################################################################################
#####################################################################################################################################################

if "bonn_2016" in aoi:
    total_deadAGB16 = sum(biomass16["AGB"])
    print(f" tree biomass 2016:     {round(total_deadAGB16/1000)} tonnen")
    print(f"Mean biomass per tree in 2016: {biomass16['AGB'].mean()}")
if "bonn_2021" in aoi:
    total_deadAGB21 = sum(biomass21["AGB"])
    print(f" tree biomass 2021:    {round(total_deadAGB21/1000)} tonnen")
    print(f"Mean biomass per tree in 2021: {biomass21['AGB'].mean()}")
if "auwald_2023" in aoi:
    total_deadAGB23 = sum(biomass23["AGB"])
    print(f" tree biomass 2023:    {round(total_deadAGB23/1000)} tonnen")
    print(f"Mean biomass per tree in 2023: {biomass23['AGB'].mean()}")

#####################################################################################################################################################
# ## Plots ################################################################################################################################
#####################################################################################################################################################
#####################################################################################################################################################
# ## Plots ################################################################################################################################
#####################################################################################################################################################

os.makedirs(f"{basepath}/results/plots", exist_ok=True)

# # # # # # # # # # #
if "bonn_2016" in aoi:
# # # # # # # # # # #

    # 1. AGB Histogram 2016
    biomass16["AGB"].hist(bins=50)
    plt.title("per Tree AGB in 2016")
    plt.xlabel("Tree AGB (kg)")
    plt.ylabel("Number of Tree AGBs in 2016")
    if export_plots: plt.savefig(f"{basepath}/results/plots/agb_2016_hist.png", bbox_inches="tight")
    plt.close()

    # 3. Tree Height vs Crown Diameter 2016 (Heatmap)
    biomass16.plot.hexbin(x="treeheight", y="diameter", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="Tree Height vs. Crown Diameter in 2016")
    plt.xlabel("Tree Height (m)")
    plt.ylabel("Crown Diameter (m)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/height_vs_diameter_2016.png", bbox_inches="tight")
    plt.close()

    # 5. Crown Diameter vs AGB 2016 (Heatmap)
    biomass16.plot.hexbin(x="diameter", y="AGB", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="Diameter vs. AGB in 2016")
    plt.xlabel("Crown Diameter (m)")
    plt.ylabel("AGB (kg)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/diameter_vs_agb_2016.png", bbox_inches="tight")
    plt.close()

    # 7. Tree Height vs AGB 2016 (Heatmap)
    biomass16.plot.hexbin(x="treeheight", y="AGB", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="Tree Height vs. AGB in 2016")
    plt.xlabel("Tree Height (m)")
    plt.ylabel("AGB (kg)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/height_vs_agb_2016.png", bbox_inches="tight")
    plt.close()

    # 9. histogram treeheight 2016
    biomass16["treeheight"].hist(bins=50)
    plt.title("per Tree treeheight in 2016")
    plt.xlabel("Treeheight (m)")
    plt.ylabel("Treeheight in 2016")
    if export_plots: plt.savefig(f"{basepath}/results/plots/treeheight_2016_hist.png", bbox_inches="tight")
    plt.close()

    # 11. histogram diameter 2016
    biomass16["diameter"].hist(bins=50)
    plt.title("per Tree crown diameter in 2016")
    plt.xlabel("Crown diameter (m)")
    plt.ylabel("Number of trees in 2016")
    if export_plots: plt.savefig(f"{basepath}/results/plots/diameter_2016_hist.png", bbox_inches="tight")
    plt.close()

    # 13. pie chart treespecies 2016
    counts = biomass16["treespecies"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Tree species in 2016")
    ax.axis("equal")
    if export_plots: plt.savefig(f"{basepath}/results/plots/treespecies_2016_pie.png", bbox_inches="tight")
    plt.close()

    # NDVI Histogram 2016
    biomass16["ndvi"].hist(bins=50)
    plt.title("per Tree NDVI in 2016")
    plt.xlabel("NDVI")
    plt.ylabel("Number of trees in 2016")
    if export_plots: plt.savefig(f"{basepath}/results/plots/ndvi_2016_hist.png", bbox_inches="tight")
    plt.close()

    # NDVI vs AGB 2016 (Heatmap)
    biomass16.plot.hexbin(x="ndvi", y="AGB", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="NDVI vs. AGB in 2016")
    plt.xlabel("NDVI")
    plt.ylabel("AGB (kg)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/ndvi_vs_agb_2016.png", bbox_inches="tight")
    plt.close()

    # NDVI vs Tree Height 2016 (Heatmap)
    biomass16.plot.hexbin(x="ndvi", y="treeheight", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="NDVI vs. Tree Height in 2016")
    plt.xlabel("NDVI")
    plt.ylabel("Tree Height (m)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/ndvi_vs_height_2016.png", bbox_inches="tight")
    plt.close()

# # # # # # # # # # #
if "bonn_2021" in aoi:
# # # # # # # # # # #

    # 2. AGB Histogram 2021
    biomass21["AGB"].hist(bins=50)
    plt.title("per Tree AGB in 2021")
    plt.xlabel("Tree AGB (kg)")
    plt.ylabel("Number of Tree AGBs in 2021")
    if export_plots: plt.savefig(f"{basepath}/results/plots/agb_2021_hist.png", bbox_inches="tight")
    plt.close()

    # 4. Tree Height vs Crown Diameter 2021 (Heatmap)
    biomass21.plot.hexbin(x="treeheight", y="diameter", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="Tree Height vs. Crown Diameter in 2021")
    plt.xlabel("Tree Height (m)")
    plt.ylabel("Crown Diameter (m)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/height_vs_diameter_2021.png", bbox_inches="tight")
    plt.close()

    # 6. Crown Diameter vs AGB 2021 (Heatmap)
    biomass21.plot.hexbin(x="diameter", y="AGB", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="Diameter vs. AGB in 2021")
    plt.xlabel("Crown Diameter (m)")
    plt.ylabel("AGB (kg)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/diameter_vs_agb_2021.png", bbox_inches="tight")
    plt.close()

    # 8. Tree Height vs AGB 2021 (Heatmap)
    biomass21.plot.hexbin(x="treeheight", y="AGB", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="Tree Height vs. AGB in 2021")
    plt.xlabel("Tree Height (m)")
    plt.ylabel("AGB (kg)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/height_vs_agb_2021.png", bbox_inches="tight")
    plt.close()

    # 10. histogram treeheight 2021
    biomass21["treeheight"].hist(bins=50)
    plt.title("per Tree treeheight in 2021")
    plt.xlabel("Treeheight (m)")
    plt.ylabel("Treeheight in 2021")
    if export_plots: plt.savefig(f"{basepath}/results/plots/treeheight_2021_hist.png", bbox_inches="tight")
    plt.close()

    # 12. histogram diameter 2021
    biomass21["diameter"].hist(bins=50)
    plt.title("per Tree crown diameter in 2021")
    plt.xlabel("Crown diameter (m)")
    plt.ylabel("Number of trees in 2021")
    if export_plots: plt.savefig(f"{basepath}/results/plots/diameter_2021_hist.png", bbox_inches="tight")
    plt.close()

    # NDVI Histogram 2021
    biomass21["ndvi"].hist(bins=50)
    plt.title("per Tree NDVI in 2021")
    plt.xlabel("NDVI")
    plt.ylabel("Number of trees in 2021")
    if export_plots: plt.savefig(f"{basepath}/results/plots/ndvi_2021_hist.png", bbox_inches="tight")
    plt.close()

    # NDVI vs AGB 2021 (Heatmap)
    biomass21.plot.hexbin(x="ndvi", y="AGB", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="NDVI vs. AGB in 2021")
    plt.xlabel("NDVI")
    plt.ylabel("AGB (kg)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/ndvi_vs_agb_2021.png", bbox_inches="tight")
    plt.close()

    # NDVI vs Tree Height 2021 (Heatmap)
    biomass21.plot.hexbin(x="ndvi", y="treeheight", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="NDVI vs. Tree Height in 2021")
    plt.xlabel("NDVI")
    plt.ylabel("Tree Height (m)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/ndvi_vs_height_2021.png", bbox_inches="tight")
    plt.close()

# # # # # # # # # # #
if "auwald_2023" in aoi:
# # # # # # # # # # #

    # AGB Histogram 2023
    biomass23["AGB"].hist(bins=50)
    plt.title("per Tree AGB in 2023")
    plt.xlabel("Tree AGB (kg)")
    plt.ylabel("Number of Tree AGBs in 2023")
    if export_plots: plt.savefig(f"{basepath}/results/plots/agb_2023_hist.png", bbox_inches="tight")
    plt.close()

    # Tree Height vs Crown Diameter 2023 (Heatmap)
    biomass23.plot.hexbin(x="treeheight", y="diameter", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="Tree Height vs. Crown Diameter in 2023")
    plt.xlabel("Tree Height (m)")
    plt.ylabel("Crown Diameter (m)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/height_vs_diameter_2023.png", bbox_inches="tight")
    plt.close()

    # Crown Diameter vs AGB 2023 (Heatmap)
    biomass23.plot.hexbin(x="diameter", y="AGB", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="Diameter vs. AGB in 2023")
    plt.xlabel("Crown Diameter (m)")
    plt.ylabel("AGB (kg)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/diameter_vs_agb_2023.png", bbox_inches="tight")
    plt.close()

    # Tree Height vs AGB 2023 (Heatmap)
    biomass23.plot.hexbin(x="treeheight", y="AGB", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="Tree Height vs. AGB in 2023")
    plt.xlabel("Tree Height (m)")
    plt.ylabel("AGB (kg)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/height_vs_agb_2023.png", bbox_inches="tight")
    plt.close()

    # histogram treeheight 2023
    biomass23["treeheight"].hist(bins=50)
    plt.title("per Tree treeheight in 2023")
    plt.xlabel("Treeheight (m)")
    plt.ylabel("Treeheight in 2023")
    if export_plots: plt.savefig(f"{basepath}/results/plots/treeheight_2023_hist.png", bbox_inches="tight")
    plt.close()

    # histogram diameter 2023
    biomass23["diameter"].hist(bins=50)
    plt.title("per Tree crown diameter in 2023")
    plt.xlabel("Crown diameter (m)")
    plt.ylabel("Number of trees in 2023")
    if export_plots: plt.savefig(f"{basepath}/results/plots/diameter_2023_hist.png", bbox_inches="tight")
    plt.close()

    # pie chart treespecies 2023
    counts = biomass23["treespecies"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Tree species in 2023")
    ax.axis("equal")
    if export_plots: plt.savefig(f"{basepath}/results/plots/treespecies_2023_pie.png", bbox_inches="tight")
    plt.close()

    # NDVI Histogram 2023
    biomass23["ndvi"].hist(bins=50)
    plt.title("per Tree NDVI in 2023")
    plt.xlabel("NDVI")
    plt.ylabel("Number of trees in 2023")
    if export_plots: plt.savefig(f"{basepath}/results/plots/ndvi_2023_hist.png", bbox_inches="tight")
    plt.close()

    # NDVI vs AGB 2023 (Heatmap)
    biomass23.plot.hexbin(x="ndvi", y="AGB", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="NDVI vs. AGB in 2023")
    plt.xlabel("NDVI")
    plt.ylabel("AGB (kg)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/ndvi_vs_agb_2023.png", bbox_inches="tight")
    plt.close()

    # NDVI vs Tree Height 2023 (Heatmap)
    biomass23.plot.hexbin(x="ndvi", y="treeheight", gridsize=60, cmap="viridis", mincnt=1, figsize=(8, 5), title="NDVI vs. Tree Height in 2023")
    plt.xlabel("NDVI")
    plt.ylabel("Tree Height (m)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/ndvi_vs_height_2023.png", bbox_inches="tight")
    plt.close()


# ## plot from [jucker et al.](https://onlinelibrary.wiley.com/doi/10.1111/gcb.13388) (fig. 6)

# # # # # # # # # # #
if "bonn_2016" in aoi:
# # # # # # # # # # #

    biomass16["height x crown diameter"] = biomass16["diameter"] * biomass16["treeheight"]

    fig, ax = plt.subplots(figsize=(7, 7))
    conifers = biomass16[biomass16["treetype"] == "coniferous"]
    broadleaved = biomass16[biomass16["treetype"] == "broadleaved"]

    # Applied alpha=0.4 and edgecolors="none" to prevent solid blobs of overlapping points
    ax.scatter(conifers["height x crown diameter"], conifers["AGB"], color="darkgreen", marker="o", label="Gymnosperms", alpha=0.4, edgecolors="none")
    ax.scatter(broadleaved["height x crown diameter"], broadleaved["AGB"], color="lightgreen", marker="o", label="Angiosperms", alpha=0.4, edgecolors="none")

    ax.set_xscale("log")
    ax.set_yscale("log")
    x_ticks = [0.05, 0.5, 5, 50, 500, 5000]
    x_labels = ["0.05", "0.5", "5", "50", "500", "5000"]
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels)

    y_ticks = [0.01, 0.1, 1, 10, 100, 1000, 10000, 100000]
    y_labels = ["0.01", "0.1", "1", "10", "100", "1000", "10 000", "100 000"]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)

    ax.set_xlabel("Height (m) × Crown diameter (m)", fontsize=12)
    ax.set_ylabel("Aboveground biomass (kg)", fontsize=12)

    ax.legend(loc="lower right", frameon=False, fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if export_plots: plt.savefig(f"{basepath}/results/plots/publication_plot_2016.png", bbox_inches="tight")
    plt.close()

if "bonn_2021" in aoi:
    biomass21["height x crown diameter"] = biomass21["diameter"] * biomass21["treeheight"]

    biomass21["height x crown diameter"].hist(bins=50)
    plt.title("Height (m) × Crown diameter (m) for trees 2021")
    plt.xlabel("Height (m) × Crown diameter (m)")
    plt.ylabel("Number of Trees")
    if export_plots: plt.savefig(f"{basepath}/results/plots/height_x_diameter_2021_hist.png", bbox_inches="tight")
    plt.close()

if "auwald_2023" in aoi:
    biomass23["height x crown diameter"] = biomass23["diameter"] * biomass23["treeheight"]

    biomass23["height x crown diameter"].hist(bins=50)
    plt.title("Height (m) × Crown diameter (m) for trees 2023")
    plt.xlabel("Height (m) × Crown diameter (m)")
    plt.ylabel("Number of Trees")
    if export_plots: plt.savefig(f"{basepath}/results/plots/height_x_diameter_2023_hist.png", bbox_inches="tight")
    plt.close()