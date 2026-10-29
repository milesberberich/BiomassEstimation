### Objective

A repo for estimating the 
**aboveground biomass** (AGB) of standing **deadwood** at the individual tree level to quantify **forest biomass loss**.

### Used data

- **Dead Trees polygons**: created using a finetuned [DeepTrees](https://deeptrees.de/)-model and arial imagery
- **Canopy height model** (CHM)
- **Tree species maps**: conifers/broadleaved, e.g. [Blickensdörfer et al.](https://www.openagrar.de/receive/openagrar_mods_00084346) or [Wegler et al.](https://geoservice.dlr.de/web/datasets/treespecies_de_2022)

### Methodoloy

[Jucker et al.](https://onlinelibrary.wiley.com/doi/10.1111/gcb.13388) developed a model to calculate AGB (and DBH)
only from parameters that could be remotely sensed:\
*Tree height* and *crown diameter*. This model is used. 

The model varies whether you estimate the biomass of a conifer or a broadleaved tree, 
therefore you need the tree species map. The *crown diameter* is derived from the dead tree polygons. Tree height is adopted from the CHM.