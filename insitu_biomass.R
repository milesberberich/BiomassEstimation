#load libs and legend for species codes ##############################

library(rBDAT)
library(terra)
source("~/Documents/code/biomass/species_codes.R")

#load data and apply legend (if wanted, filtered by Kraftscher Klasse) ##############################

trees <- terra::vect("/home/berberic/Documents/allometry/insitu/insitu_tree_auwaldtile.geojson")
total_number_of_trees <- nrow(trees)
#trees <- trees[trees$kraftcode %in% c("5", "4", "3"), ] # KRAFT FILTER
               
# clean data for AGB estimation ##############################

trees$species_code <- legend$species_codes[match(trees$BAUMART, legend$BAUMART)] # species code for rbdat
trees$H1 <- 1.3 # measurement height
trees$tree_id <- 1:nrow(trees) # tree id

# filling missing BHD values from 2017 with valid 2020 values
missing_bhd <- (is.na(trees$BHD17) | trees$BHD17 == 0) & (!is.na(trees$BHD20) & trees$BHD20 > 0)
trees$BHD17[missing_bhd] <- trees$BHD20[missing_bhd] 

# filling missing Height (hG) values from 2017 with valid 2020 values
missing_hg <- (is.na(trees$hG17) | trees$hG17 == 0) & (!is.na(trees$hG20) & trees$hG20 > 0)
trees$hG17[missing_hg] <- trees$hG20[missing_hg] 

valid_rows <- !is.na(trees$BHD17) & trees$BHD17 > 0 & !is.na(trees$hG17) & trees$hG17 > 0
trees <- trees[valid_rows]

# convert to tree ##############################

bdat_trees <- buildTree(tree=as.data.frame(trees),
                        mapping = c("species_code" = "spp", "BHD17" = "D1", "H1" = "H1", "hG17" = "H"),
                        check="biomass")

# get biomass #######################

trees$AGB <- getBiomass(bdat_trees) 


paste("final biomass is:", round(sum(trees$AGB)/1000, 1), "Mg.")
paste(nrow(trees), "of", total_number_of_trees, "were used. Missing data (DBH and tree height) from 2017 was filled with values from 2020.")
paste("Mean Biomass per tree is:", round(sum(trees$AGB)/nrow(trees)), "kg.")

# saving clean version ##############################


trees_og <- terra::vect("/home/berberic/Documents/allometry/insitu/insitu_tree_auwaldtile.geojson")
trees_og <- trees_og[valid_rows]
trees$hG17 <- trees_og$hG17
trees$hG20 <- trees_og$hG20
trees$BHD17 <- trees_og$BHD17
trees$BHD20 <- trees_og$BHD20

#terra::writeVector(trees, "/home/berberic/Documents/allometry/results in situ biomass/results_insitu_biomass.geojson")
