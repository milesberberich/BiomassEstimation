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
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


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

trees21 = gpd.read_file(f"{basepath}/trees/bonn_2021_vital.geojson")
trees16 = gpd.read_file(f"{basepath}/trees/bonn_2016_vital.geojson")

# ## calculate diameter

trees16 = get_diameter(trees16)
trees21 = get_diameter(trees21)


# ## get tree species

trees16 = get_treespecies(polygon=trees16, raster_path= f"{basepath}/treespecies/treespecies_2016_bonn.tif")
trees21 = get_treespecies(polygon=trees21, raster_path=f"{basepath}/treespecies/treespecies_2021_bonn.tif")

print(trees16[["treespecies", "treetype"]].head())

# ## get tree height

treeheights16 = get_treeheight_fromfile(polygon=trees16, raster_path=f"{basepath}/treeheight/CHM_1m_bonn.tif", scale = False)
treeheights21 = get_treeheight_fromfile(polygon=trees21, raster_path=f"{basepath}/treeheight/CHM_1m_bonn.tif", scale = False)

# handle zeros in treeheight by using mean instead

remove_zeros = True

if remove_zeros: # Trees with 0 as treeheight, get the mean treeheight instead
    treeheights16.loc[treeheights16["treeheight"] == 0, "treeheight"] = treeheights16["treeheight"].mean()
    treeheights21.loc[treeheights21["treeheight"] == 0, "treeheight"] = treeheights21["treeheight"].mean()

plot_treeheight = False

if plot_treeheight:
    treeheights16["treeheight"].hist(bins=25)
    plt.show()
    treeheights21["treeheight"].hist(bins=25)
    plt.show()

# ## estimate biomass

biomass16 = estimate_biomass(treeheights16)
biomass21 = estimate_biomass(treeheights21)

if export_results:
    biomass16.to_file(f"{basepath}/results/biomass/biomass16.geojson", driver="GeoJSON")
    biomass21.to_file(f"{basepath}/results/biomass/biomass21.geojson", driver="GeoJSON")

total_deadAGB16 = sum(biomass16["AGB"])
print(f"dead tree biomass 2016:     {round(total_deadAGB16/1000)} tonnen")
total_deadAGB21 = sum(biomass21["AGB"])
print(f"dead tree biomass 2021:    {round(total_deadAGB21/1000)} tonnen")

# ## Plots
# Ensure the plots directory exists before saving
os.makedirs(f"{basepath}results/plots", exist_ok=True)

print(f"Mean biomass per dead tree in 2016: {biomass16['AGB'].mean()}")
print(f"Mean biomass per dead tree in 2021: {biomass21['AGB'].mean()}")

# 1. AGB Histogram 2016
biomass16["AGB"].hist(bins=50)
plt.title("per Tree AGB in 2016")
plt.xlabel("Tree AGB (kg)")
plt.ylabel("Number of Tree AGBs in 2016")
if export_plots: plt.savefig(f"{basepath}results/plots/agb_2016_hist.png", bbox_inches='tight')
plt.close()

# 2. AGB Histogram 2021
biomass21["AGB"].hist(bins=50)
plt.title("per Tree AGB in 2021")
plt.xlabel("Tree AGB (kg)")
plt.ylabel("Number of Tree AGBs in 2021")
if export_plots: plt.savefig(f"{basepath}results/plots/agb_2021_hist.png", bbox_inches='tight')
plt.close()

# 3. Tree Height vs Crown Diameter 2016
biomass16.plot.scatter(x="treeheight", y="diameter", figsize=(8, 5), alpha=0.5, title="Tree Height vs. Crown Diameter in 2016")
plt.xlabel("Tree Height (m)")
plt.ylabel("Crown Diameter (m)")
if export_plots: plt.savefig(f"{basepath}results/plots/height_vs_diameter_2016.png", bbox_inches='tight')
plt.close()

# 4. Tree Height vs Crown Diameter 2021
biomass21.plot.scatter(x="treeheight", y="diameter", figsize=(8, 5), alpha=0.5, title="Tree Height vs. Crown Diameter in 2021")
plt.xlabel("Tree Height (m)")
plt.ylabel("Crown Diameter (m)")
if export_plots: plt.savefig(f"{basepath}results/plots/height_vs_diameter_2021.png", bbox_inches='tight')
plt.close()

# 5. Crown Diameter vs AGB 2016
biomass16.plot.scatter(x="diameter", y="AGB", figsize=(8, 5), alpha=0.5, title="Diameter vs. AGB in 2016")
plt.xlabel("Crown Diameter (m)")
plt.ylabel("AGB (kg)")
if export_plots: plt.savefig(f"{basepath}results/plots/diameter_vs_agb_2016.png", bbox_inches='tight')
plt.close()

# 6. Crown Diameter vs AGB 2021
biomass21.plot.scatter(x="diameter", y="AGB", figsize=(8, 5), alpha=0.5, title="Diameter vs. AGB in 2021")
plt.xlabel("Crown Diameter (m)")
plt.ylabel("AGB (kg)")
if export_plots: plt.savefig(f"{basepath}results/plots/diameter_vs_agb_2021.png", bbox_inches='tight')
plt.close()

# 7. Tree Height vs AGB 2016
biomass16.plot.scatter(x="treeheight", y="AGB", figsize=(8, 5), alpha=0.5, title="Tree Height vs. AGB in 2016")
plt.xlabel("Tree Height (m)")
plt.ylabel("AGB (kg)")
if export_plots: plt.savefig(f"{basepath}results/plots/height_vs_agb_2016.png", bbox_inches='tight')
plt.close()

# 8. Tree Height vs AGB 2021
biomass21.plot.scatter(x="treeheight", y="AGB", figsize=(8, 5), alpha=0.5, title="Tree Height vs. AGB in 2021")
plt.xlabel("Tree Height (m)")
plt.ylabel("AGB (kg)")
if export_plots: plt.savefig(f"{basepath}results/plots/height_vs_agb_2021.png", bbox_inches='tight')
plt.close()


# ## plot from [jucker et al.](https://onlinelibrary.wiley.com/doi/10.1111/gcb.13388) (fig. 6)



biomass21["height x crown diameter"].hist(bins=50)
plt.title("Height (m) × Crown diameter (m) fro dead trees 2021")
plt.xlabel("Height (m) × Crown diameter (m)")
plt.ylabel("Number of Trees")
plt.show()

biomass16["height x crown diameter"] = biomass16["diameter"] * biomass16["treeheight"]
biomass21["height x crown diameter"] = biomass21["diameter"] * biomass21["treeheight"]

fig, ax = plt.subplots(figsize=(7, 7))

conifers = biomass21[biomass21["treetype"] == "coniferous"]
broadleaved = biomass21[biomass21["treetype"] == "broadleaved"]

ax.scatter(conifers["height x crown diameter"], conifers["AGB"], color="darkgreen", marker="o", label="Gymnosperms")
ax.scatter(broadleaved["height x crown diameter"], broadleaved["AGB"], color="lightgreen", edgecolors="grey", marker="o", label="Angiosperms")

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
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.show()






