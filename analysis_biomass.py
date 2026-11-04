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
parser.add_argument("--basepath", type=str, default="/home/berberic/Documents/allometry")
parser.add_argument("--years", nargs="+", default=["2016", "2021"])
parser.add_argument("--export_results", action="store_true")
parser.add_argument("--export_plots", action="store_true")
args = parser.parse_args()

basepath = args.basepath
years = args.years
export_results = args.export_results
export_plots = args.export_plots


# ## load polygons

if "2016" in years:
    trees16 = gpd.read_file(f"{basepath}/trees/bonn_2016_vital.geojson")
if "2021" in years:
    trees21 = gpd.read_file(f"{basepath}/trees/bonn_2021_vital.geojson")
print("Polygons were loaded.")

# ## calculate diameter

if "2016" in years:
    trees16 = get_diameter(trees16)
if "2021" in years:
    trees21 = get_diameter(trees21)
print("Crown diameters were calculated.")

# ## get tree species

if "2016" in years:
    trees16 = get_treespecies(polygon=trees16, raster_path=f"{basepath}/treespecies/treespecies_blickensdoerfer.tif", data_source="blickensdoerfer")
if "2021" in years:
    trees21 = get_treespecies(polygon=trees21, raster_path=f"{basepath}/treespecies/treespecies_blickensdoerfer.tif", data_source="blickensdoerfer")
print("Tree species were derived.")

# ## get tree height

if "2016" in years:
    treeheights16 = get_treeheight_fromfile(polygon=trees16, raster_path=f"{basepath}/treeheight/CHM_1m_bonn.tif", scale=False)
    r = treeheights16["treeheight"].corr(treeheights16["diameter"])
    print(f"corellation between treeheight and diameter: {r}")
if "2021" in years:
    treeheights21 = get_treeheight_fromfile(polygon=trees21, raster_path=f"{basepath}/treeheight/CHM_1m_bonn.tif", scale=False)
print("Tree heights were derived.")

# handle zeros in treeheight by using mean instead

remove_zeros = True

if remove_zeros:  # Trees with 0 as treeheight, get the mean treeheight instead
    if "2016" in years:
        treeheights16.loc[treeheights16["treeheight"] == 0, "treeheight"] = treeheights16["treeheight"].mean()
    if "2021" in years:
        treeheights21.loc[treeheights21["treeheight"] == 0, "treeheight"] = treeheights21["treeheight"].mean()

plot_treeheight = False

if plot_treeheight:
    if "2016" in years:
        treeheights16["treeheight"].hist(bins=25)
        plt.show()
    if "2021" in years:
        treeheights21["treeheight"].hist(bins=25)
        plt.show()

# ## estimate biomass

if "2016" in years:
    biomass16 = estimate_biomass(treeheights16)
if "2021" in years:
    biomass21 = estimate_biomass(treeheights21)
print("Biomass was estimated.")

if export_results:
    if "2016" in years:
        biomass16.to_file(f"{basepath}/results/biomass/biomass16.geojson", driver="GeoJSON")
    if "2021" in years:
        biomass21.to_file(f"{basepath}/results/biomass/biomass21.geojson", driver="GeoJSON")

if "2016" in years:
    total_deadAGB16 = sum(biomass16["AGB"])
    print(f"dead tree biomass 2016:     {round(total_deadAGB16/1000)} tonnen")
    print(f"Mean biomass per dead tree in 2016: {biomass16['AGB'].mean()}")
if "2021" in years:
    total_deadAGB21 = sum(biomass21["AGB"])
    print(f"dead tree biomass 2021:    {round(total_deadAGB21/1000)} tonnen")
    print(f"Mean biomass per dead tree in 2021: {biomass21['AGB'].mean()}")

# ## Plots
# Ensure the plots directory exists before saving
os.makedirs(f"{basepath}/results/plots", exist_ok=True)

if "2016" in years:

    # 1. AGB Histogram 2016
    biomass16["AGB"].hist(bins=50)
    plt.title("per Tree AGB in 2016")
    plt.xlabel("Tree AGB (kg)")
    plt.ylabel("Number of Tree AGBs in 2016")
    if export_plots: plt.savefig(f"{basepath}/results/plots/agb_2016_hist.png", bbox_inches="tight")
    plt.close()

    # 3. Tree Height vs Crown Diameter 2016
    biomass16.plot.scatter(x="treeheight", y="diameter", figsize=(8, 5), alpha=0.5, title="Tree Height vs. Crown Diameter in 2016")
    plt.xlabel("Tree Height (m)")
    plt.ylabel("Crown Diameter (m)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/height_vs_diameter_2016.png", bbox_inches="tight")
    plt.close()

    # 5. Crown Diameter vs AGB 2016
    biomass16.plot.scatter(x="diameter", y="AGB", figsize=(8, 5), alpha=0.5, title="Diameter vs. AGB in 2016")
    plt.xlabel("Crown Diameter (m)")
    plt.ylabel("AGB (kg)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/diameter_vs_agb_2016.png", bbox_inches="tight")
    plt.close()

    # 7. Tree Height vs AGB 2016
    biomass16.plot.scatter(x="treeheight", y="AGB", figsize=(8, 5), alpha=0.5, title="Tree Height vs. AGB in 2016")
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

if "2021" in years:

    # 2. AGB Histogram 2021
    biomass21["AGB"].hist(bins=50)
    plt.title("per Tree AGB in 2021")
    plt.xlabel("Tree AGB (kg)")
    plt.ylabel("Number of Tree AGBs in 2021")
    if export_plots: plt.savefig(f"{basepath}/results/plots/agb_2021_hist.png", bbox_inches="tight")
    plt.close()

    # 4. Tree Height vs Crown Diameter 2021
    biomass21.plot.scatter(x="treeheight", y="diameter", figsize=(8, 5), alpha=0.5, title="Tree Height vs. Crown Diameter in 2021")
    plt.xlabel("Tree Height (m)")
    plt.ylabel("Crown Diameter (m)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/height_vs_diameter_2021.png", bbox_inches="tight")
    plt.close()

    # 6. Crown Diameter vs AGB 2021
    biomass21.plot.scatter(x="diameter", y="AGB", figsize=(8, 5), alpha=0.5, title="Diameter vs. AGB in 2021")
    plt.xlabel("Crown Diameter (m)")
    plt.ylabel("AGB (kg)")
    if export_plots: plt.savefig(f"{basepath}/results/plots/diameter_vs_agb_2021.png", bbox_inches="tight")
    plt.close()

    # 8. Tree Height vs AGB 2021
    biomass21.plot.scatter(x="treeheight", y="AGB", figsize=(8, 5), alpha=0.5, title="Tree Height vs. AGB in 2021")
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

# ## plot from [jucker et al.](https://onlinelibrary.wiley.com/doi/10.1111/gcb.13388) (fig. 6)

if "2016" in years:
    biomass16["height x crown diameter"] = biomass16["diameter"] * biomass16["treeheight"]

    fig, ax = plt.subplots(figsize=(7, 7))
    conifers = biomass16[biomass16["treetype"] == "coniferous"]
    broadleaved = biomass16[biomass16["treetype"] == "broadleaved"]

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
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if export_plots: plt.savefig(f"{basepath}/results/plots/publication_plot_2016.png", bbox_inches="tight")
    plt.close()

if "2021" in years:
    biomass21["height x crown diameter"] = biomass21["diameter"] * biomass21["treeheight"]

    biomass21["height x crown diameter"].hist(bins=50)
    plt.title("Height (m) × Crown diameter (m) for dead trees 2021")
    plt.xlabel("Height (m) × Crown diameter (m)")
    plt.ylabel("Number of Trees")
    if export_plots: plt.savefig(f"{basepath}/results/plots/height_x_diameter_2021_hist.png", bbox_inches="tight")
    plt.close()