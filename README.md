# ongoing project for Blue-Green Infrastructure

Currently, the script runs on information uploaded from 2 files

"sample_land_data.txt"
-- contains information in three columns with a header. 
ID refers to an identifying number corresponding to a land parcel. 
Area is in m2. 
Landcover usage needs to be determined prior to running this script. 

"dataframes.txt"
-- contains information about some BGIs that target increasing retention capacity of stormwater or cooling the temperature
bgi_characteristics is a dictionary. bgi_df is the panda dataframes format of the dictionary. 
the order of bgis labeled here indicate how you should input matrices/arrays for the bgi dictionary/dataframe 

The code to check for suitability based on landcover and minimum area needed per BGI is in "feasibility_script.py"

the current result is not very polished but it is getting there. it is also not very flexible, so errors will arise if formatting is not what the script is expecting.
please email with questions and comments
kim.wang@wur.nl
