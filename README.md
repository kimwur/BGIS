Latest BGIS update - Aug 6

T.O.C. 

1. EXAMPLE_BGI_DATABASE.TXT
   a text file structured to give characteristics of major types of BGI categories that can be read as dictionaries in python. very easy to add to, modify, or delete entries. customize to your own circumstances.

following dictionaries are defined and can be called on in python:
  "bgi_catalog"
    keys = types of bgi
    each bgi key has the following information 
      lulc: land use/land cover            *  necessary for feasbility analysis
      function: main function of bgi       - descriptive
      area_m2 : area in m2                 * necessary for feasibility analysis
      geometry: polygon or linear                            - future constraints application 
      slope_cat: slope category (see slope_categories_max_degree) as a description (gentle, mild, steep etc)
                                          * necessary for feasibility analysis 
      depth_m: minimum and maximum depth of installation     - future constraint application 
      groundwater_separation_required_m: minimum distance above groundwater table required - future constraint application
      soil_type: out of sand, loam, silt, or clay           - future constraint application 
      maintenance_required: see maintenance_categories      - future constraint application 
      pedestrians: true/false, needs to accommodate pedestrians 
      low traffic: true/false, needs to accommodate low vehicle usage
      high traffic: true/false, needs to accommodate heavy vehicle usage
      adaptive_siting: true/fals, if constraints can be overridden at higher installation costs 
      design_adaptation: continuing information about adaptive_siting 
      
  "slope_categories_max_degree"
    match descriptions (flat, gentle, moderate) to upper slope (degree) 
    
  "maintenance_categories"
    beginning to give an idea as to maintenance needed mostly in terms of maintenance events per year recommended. very easy to add to, modify, or delete entries. customize to your own circumstances.
   
2. EXAMPLE_SIMPLE_IMPACT.TXT
    a text file structured as a python dictionary to give very simple estimations of impacts of installing each BGI technology

following dictionary defined: 
  "bgi_simple_impact"
    keys = types of bgi (matching bgi_catalog) 
    value = dictionary containing following 
      retention: volume of stormwater retention as depth, m, per area, 1 m2
      RC: runoff coefficient
      cooling: average cooling ability in T air 
      capex: initial costs of material
      opex %: ongoing annual cost as percentage of capex 
      
3. FEASIBILITY_SCRIPT.PY
  python script to evaluate feasibility of BGIs based on land data and constraints placed. need to have textfiles (1 and 2) in same path. 
  see script for more notes
  input needed: shapefile
  current constraints: landuse/landcover, slope, area
  output: same shapefile with additional columns in attribute table
    column: suitable bgis, a list of strings of acceptable bgis
    columns: 0/1 for each bgi where 0 is not feasible and 1 is feasible 

4. OPTIMIZATION_SCRIPT.PY
   python script to find optimized combination of highest impact, here calculated as "MFI", for the lowest amount of
area needed for installation and under a maximum budget constraint (optional). runs linear programming optimization. allows
weighting for prioritization of functions. see script for more notes while running. 
   need to have textfiles (1 and 2) in same path. 
   
  
