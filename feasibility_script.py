##################################################################################
# packages to import
##################################################################################
import geopandas as gpd
import pyogrio
import pandas as pd
import ast
import numpy as np
import json

##################################################################################
# functions for loading text correctly
##################################################################################

def safe_parse(cell): 
  """ correctly read excel sheet """ 
    if pd.isna(cell):                                       # case: missing value
        return None                                       
    
    if isinstance(cell, str):                               # case: is string
        cleaned_string = cell.strip()                     
        
        if cleaned_string.lower() in ["true", "false"]:     # case: Boolean
            return cleaned_string.lower() == "true"       

        try:                                              
            parsed = json.loads(cleaned_string)             # attempt JSON parsing
        except Exception:                                 
            parsed = None

        if parsed is None:
            try:
                parsed = ast.literal_eval(cleaned_string)   # attempt literal parsing
            except Exception:
                parsed = cleaned_string
        cell = parsed

    if isinstance(cell, str):                               # case: string 
        return cell.strip()

    if isinstance(cell, dict):                              # case: dictionary
        return tuple(sorted(cell.items()))
        
    return cell 


def check_list(value):
  """ for when strings need to be in list """
    if value is None: 
        return []
    if isinstance(value, list):
        return value
    return [value]


##################################################################################
# load shapefile here
# example given is a small section of Amsterdam centrum (a few blocks from Keizersgracht - Prinsengracht) 
# shapefile with spatial information in polygons along with a specified land use/landcover deisgnation
# taken from Amsterdam Gemeente data 
##################################################################################

LULC_GDF = gpd.read_file('example_amsterdam_neigbhorhood.gpkg')

# run through safe parsing 
LULC_GDF['type'] = LULC_GDF['type'].apply(safe_parse)

# create copy and work with copy from here out
gdf = LULC_GDF.copy()

# calculate area if it is not already stored 
if "area_m2" in gdf.columns:
    print()
else:
    gdf['area_m2'] = gdf.geometry.area

# gather all types of LULC from GDF 
unique_types = sorted(
    str(x) for x in gdf["type"].dropna().unique()
) 

##################################################################################
# ! important ! dictionary ! here ! 
# to go from data-specific LULC into corresponding installation layer for BGI
# may be customized to different LULCs 
##################################################################################

landcover_dictionary = {
    'baan_voor_vliegverkeer':       'pavement', 
    'bassin':                       'feature',
    'berm':                         'ground',
    'erf':                          'ground',
    'fietspad':                     'pavement',
    'flat roof':                    'flatroof',
    'gesloten_verharding':          'ground',
    'grasland_overig':              'ground',
    'groenvoorziening':             'ground',
    'half_verhard':                 'ground',
    'inrit':                        'none',
    'kademuur_V':                   'quaywall',
    'lage_trafo':                   'infrastructure',
    'muur_V':                       'wall',
    'oever_slootkant':              'bank',
    'onverhard':                    'ground',
    'open_loods':                   'aviary',
    'open_verharding':              'ground',
    'ov-baan':                      'pavement',
    'pand':                         'angledroof',
    'parkeervlak':                  'pavement',
    'perron':                       'none',
    'rijbaan_lokale_weg':           'pavement',
    'rijbaan_regionale_weg':        'pavement',
    'sluis':                        'infrastructure',
    'struiken':                     'ground',
    'verkeerseiland':               'ground',
    'voetgangersgebied':            'pavement',
    'voetpad':                      'pavement',
    'voetpad_op_trap':              'stairs',
    'waterloop':                    'water',
    'woonerf':                      'ground',
    'zand':                         'ground'
}

# translation occurs here, adding another column to gdf 
gdf['install_layer'] = gdf['type'].str.lower().map(landcover_dictionary).fillna('none')

##################################################################################
# load in excel sheet with information on BGI technology here 
# excel sheet represents types of BGIs considered as well as any necessary requirements for installation
# can add new categories or modify existing easily
##################################################################################
BGI_SHEET = pd.read_excel('bgi_catalog_v1.xlsx', sheet_name=0)

# convert from excel data to a useful python dictionary
BGI_CATALOG = {}

# these need to be loaded as 'strings' and not as 's','t','r',... 
load_as_string_headers = [
    "install_layer",
    "geometry",
    "soil_type",
    "adaptive_siting",
    "vegetation",
    "modular",
    "maintenance_requirement",
    "permit"
]

for index, row in BGI_SHEET.iterrows():
    bgi_name = row["bgi_name"]
    entry = {}
    for column in BGI_SHEET.columns:
        if column in load_as_string_headers:
            clean = safe_parse(row.get(column))
            entry[column] = clean
        else:
            entry[column] = row.get(column)
    BGI_CATALOG[bgi_name] = entry

##################################################################################
# creating masks for various condition checks 
##################################################################################

def check_install_layer(gdf, catalog):
  """ check if the installation layer of the land matches one of the BGIs """ 
    catalog_layers = {
        name: set(entry["install_layer"])
        for name, entry in catalog.items()
    }
    series = gdf["install_layer"]
    return pd.DataFrame({
        name: series.isin(layers)
        for name, layers in catalog_layers.items()
    })

def check_area(gdf, catalog):
  """ check if the land polygon has the minimum or maximum area as specified by BGI characteristic """ 
    catalog_min_area = {
        name: float(entry["area_min"]) if pd.notna(entry["area_min"]) else 0
        for name, entry in catalog.items()
    } 
    catalog_max_area = {
        name: float(entry["area_max"]) if pd.notna(entry["area_max"]) else np.inf
        for name, entry in catalog.items()
    }
    series = gdf["area_m2"]
    return pd.DataFrame({
        name: (series >= catalog_min_area[name]) & (series <= catalog_max_area[name])
        for name in catalog.keys()
    })


def check_soil(gdf, catalog): 
  """ if soil data exists, it can also be checked againt custom BGI requirements """ 
    catalog_soils = {
        name: set(entry["soil_type"])
        for name, entry in catalog.items()
    }
    series = gdf["soil"]
    return pd.DataFrame({
        name: series.isin(layers)
        for name, layers in catalog_layers.items()
    })

def check_groundwater(gdf, catalog): 
  """ if groundwater levels exist, they can also be checked against custom BGI requirements """ 
    catalog_groundwater = {
        name: set(entry["groundwater_level"])
        for name, entry in catalog.items()
    }
    series = gdf["groundwater"]
    return pd.DataFrame({
        name: series.isin(layers)
        for name, layers in catalog_layers.items()
    })

##################################################################################
# creating final masks and output shapefile 
##################################################################################

valid_mask = pd.Series(True, index=BGI_CATALOG.keys())
area_mask = check_area(gdf, BGI_CATALOG)
lulc_mask = check_install_layer(gdf, BGI_CATALOG)
final_mask = area_mask & lulc_mask

# making the mask go from boolean to a readable result 
gdf['suitable_bgis'] = final_mask.apply(
    lambda row: [bgi for bgi, valid, in row.items() if valid],
    axis = 1
) 

# add binary matrix of 0/1s for easier visualization in QGIS 
bgi_binary_matrix = pd.DataFrame(
    0, 
    index = gdf.index, 
    columns = list(BGI_CATALOG.keys())
)
for idx, bgis in gdf['suitable_bgis'].items():
    if bgis:
        bgi_binary_matrix.loc[idx, bgis] = 1

output_gdf = pd.concat([gdf, bgi_binary_matrix], axis=1)

# save file
output_gdf.to_file("testing_standalone.gpkg", layer="feasibility", driver="GPKG")
