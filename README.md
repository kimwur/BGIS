# BGIS
ongoing project

1. enter data following format of sample data text - each row corresponds with a land parcel saved in a shapefile (.shp) for use in GIS
2. you can altar properties of BGIs and landcover in the text files, bgi_information.txt and landcover_information
   bgi_information includes 9 possible BGI types
   
3. run **1_feasibility.py** (which includes step 0_land_analysis within it)
  within this script are functions for running constraints based on landcover type, minimum area requirements, and slope requirements.

  this will save a text file named "output_matrix.txt" where the first column is the cell ID number (corresponding to the .shp file). The following columns have a value of 0 (not feasible) and 1 (feasible) for each BGI. BGI columns correspond to the order of BGI listed in the bgi_information.txt file. 

4. run **2_selection.py**
   includes an idea for maximum area constraints which is currently unfinished
