# species_codes.R

legend <- data.frame(
  BAUMART = c(
    "Fagus sylvatica", "Carpinus betulus", "Quercus robur", 
    "Populus spec.", "Fraxinus excelsior", "Fraxinus spec.", 
    "Acer pseudoplatanus", "Acer platanoides", "Acer campestre", 
    "Tilia cordata", "Tilia platyphyllus", "Alnus glutinosa", 
    "Ulmus spec.", "Ulmus minor", "Larix decidua", 
    "Sambucus nigra", "Aesculus hippocastanum", "Crataegus spec.", 
    "Corylus avellana"
  ),
  species_codes = c(
    15, 16, 17, 
    19, 21, 21, 
    23, 24, 25, 
    27, 27, 28, 
    30, 30, 10, 
    35, 35, 35, 
    35
  ),
  stringsAsFactors = FALSE
)