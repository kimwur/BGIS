##### PACKAGES TO IMPORT 
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from matplotlib import pyplot as plt
import time

with open('bgi_information.txt') as file1:
    exec(file1.read())

with open('landcover_information.txt') as file2:
    exec(file2.read())

land_data = pd.read_csv('breda_land_data_text.txt', sep='\t', decimal=',')
land_data_df = pd.DataFrame(land_data)

# replacing zero values with 0.0001 
land_data_df = land_data_df.replace(0, 0.0001)

feasibility_matrix = np.loadtxt('output_matrix.txt', dtype=int)

# BASIC PARAMETERS
nbgi = len(types_bgi)
nlcv = len(types_landcover)

# separating landcover runoff from suitability (stored in last column)
landcover_mat = bgi_landcover_matrix[:,0:9]
runoff_coeffs = bgi_landcover_matrix[:,9]

total_cells = len(land_data_df)

Qred_arr = bgi_characteristics_matrix[0,:]
Tred_arr = bgi_characteristics_matrix[1,:]

# Function: applying maximum area constraints
# returns max applied area depending on BGI 

def MAX_AREA_RESTRICTIONS(c):
    feas_arr = feasibility_matrix[c,:]
    cell_area = land_data_df['area'].iloc[c]
    use_area = np.zeros(nbgi)
    for j in range(nbgi):
        if feas_arr[j] == 1:
            use_area[j] = cell_area
            max_area = bgi_characteristics_matrix[5,j]
            if cell_area > max_area and max_area > 0:
                use_area[j] = max_area
    return use_area

applicable_area = np.zeros([total_cells, nbgi])
for c in range(total_cells):
    applicable_area[c,:] = MAX_AREA_RESTRICTIONS(c)

# BGI Selection
# max Q and max T

Qimpact_mat = np.zeros([total_cells, nbgi]) # will be in m * m2
maxQ_selection = np.zeros(total_cells) - 1
Timpact_mat = np.zeros([total_cells, nbgi]) # will be in deg C * m2
maxT_selection = np.zeros(total_cells) - 1

for c in range(total_cells):
    for j in range(nbgi):
        use_area = applicable_area[c,j]
        Qele = use_area * Qred_arr[j]
        Tele = use_area * Tred_arr[j]
        Qimpact_mat[c,j] = Qele
        Timpact_mat[c,j] = Tele
    if any(Qimpact_mat[c,:]) > 0:
        maxQ_selection[c] = np.argmax(Qimpact_mat[c,:])
    if any(Timpact_mat[c,:]) > 0:
        maxT_selection[c] = np.argmax(Timpact_mat[c,:])

# BGI Selection 
# Multifunctional index 1,median
mfi_1_selection = np.zeros(total_cells) - 1

for c in range(total_cells):
    mfi_1_mat = np.zeros([total_cells,nbgi])
    cell_area = land_data_df['area'].iloc[c]
    for j in range(nbgi):
        use_area = applicable_area[c,j]
        if use_area > 0:
            Q_1_ind = use_area/cell_area * Qred_arr[j]/np.median(Qred_arr)
            T_1_ind = use_area/cell_area * Tred_arr[j]/np.median(Tred_arr)
            mfi_1 = Q_1_ind + T_1_ind
            mfi_1_mat[c,j] = mfi_1
    if any(mfi_1_mat[c,:]) > 0:
        mfi_1_selection[c] = np.argmax(mfi_1_mat[c,:])

selection_mat = np.hstack((maxQ_selection.reshape(-1, 1), \
maxT_selection.reshape(-1, 1), mfi_1_selection.reshape(-1, 1)))

mergeID_column = (land_data_df['mergeID'].values.reshape(-1,1))
labeled_selection_mat = np.hstack([mergeID_column, selection_mat])

with open('selection_matrix.txt', 'w') as f:
    for row in labeled_selection_mat:
        f.write(' '.join(map(lambda x: str(int(x)), row)) + '\n')

