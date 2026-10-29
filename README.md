### Objective

A repo for estimating the 
**aboveground biomass** (AGB) of standing **deadwood** at the individual tree level to quantify **forest biomass loss**.

### Used data

- **Dead Trees polygons**: created using a finetuned [DeepTrees](https://deeptrees.de/)-model and arial imagery
- **Canopy height model** (CHM) e.g. [Asam et al.](https://geoservice.dlr.de/web/datasets/woody_cover_by_23-24) or [Kacic et al.](https://geoservice.dlr.de/web/datasets/forest_structure)
- **Tree species maps**: conifers/broadleaved, e.g. [Blickensdörfer et al.](https://www.openagrar.de/receive/openagrar_mods_00084346) or [Wegler et al.](https://geoservice.dlr.de/web/datasets/treespecies_de_2022)

### Methodoloy

[Jucker et al.](https://onlinelibrary.wiley.com/doi/10.1111/gcb.13388) developed a model to calculate AGB (and DBH) only from parameters that could be remotely sensed:\
*Tree height* and *crown diameter*.\
This model is used. 

The *crown diameter* is derived from the dead tree polygons. Tree height is taken from the CHM.
The model varies whether you estimate the biomass of a conifer or a broadleaved tree, 
therefore you need the tree species map. 

### Contents

- **functions/get_diameter**: calculates the diameter (via the area) for each dead tree polygon.
- **functions/get_treespecies**: loads [Wegler et al.](https://geoservice.dlr.de/web/datasets/treespecies_de_2022) from a local file and appends the information (conifer/broadleaved) to the dead tree polygons.
- **functions/get_treeheight.py**: consists of two functions. get_treeheight_fromfile read a local CHM and appends those values to the dead tree polygons. get_treeheight_fromDLR pulls Wegler et al.](https://geoservice.dlr.de/web/datasets/treespecies_de_2022) via STAC and appends those values to the polygons. 
- **functions/estimate_biomass.py**: calculates the biomass using the approach of [Jucker et al.](https://onlinelibrary.wiley.com/doi/10.1111/gcb.13388)
- **analysis.ipynb**: uses all the function mentions above in a analysis pipeline