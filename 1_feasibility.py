%run 0_land_analysis.ipynb

# Function: constraints based on land cover

def LANDCOVER_FEAS(c):
    cell_cover = land_data_df['landcover'].iloc[c]
    cell_area = land_data_df['area'].iloc[c]
    feas_arr = np.zeros([nbgi])
    for i in range(nlcv):
        if cell_cover == types_landcover[i]:
            feas_arr = bgi_landcover_matrix[i,0:nbgi].copy()
    return feas_arr

# example of usage
landcover_constraint = np.zeros([total_cells, nbgi])
for c in range(total_cells):
    landcover_constraint[c,:] = LANDCOVER_FEAS(c)

landcover_constraint

# Function: constraints based on minimum area application 
# contains landcover check within function

def MIN_AREA_FEAS(c):
    feas_arr = LANDCOVER_FEAS(c)
    cell_area = land_data_df['area'].iloc[c]
    for j in range(nbgi):
        if feas_arr[j] == 1:
            min_area = bgi_characteristics_matrix[4,j]
            if cell_area < min_area and min_area > 0:
                feas_arr[j] = 0
    return feas_arr

landcover_minarea_constraints = np.zeros([total_cells, nbgi])
for c in range(total_cells):
    landcover_minarea_constraints[c,:] = MIN_AREA_FEAS(c)

landcover_minarea_constraints

# Function: constraints based on slope 
# individual check

slope_mapping = {category: rank for rank, category in enumerate(types_slope_categories)}
slope_level = (land_data_df['slope'].map(slope_mapping))

bgi_slope_level = bgi_characteristics_matrix[6,:]

def SLOPE_FEAS(c):
    cell_slope_level = slope_level[c]
    feas_arr = np.zeros([nbgi])
    for j in range(nbgi):
        if cell_slope_level <= bgi_slope_level[j]:
            feas_arr[j] = 1
    return feas_arr

slope_constraint = np.zeros([total_cells, nbgi])
for c in range(total_cells):
    slope_constraint[c,:] = SLOPE_FEAS(c)

slope_constraint


def FINAL_FEASIBILITY(*matrices):
    return_mat = np.zeros([total_cells, nbgi])
    for c in range(total_cells):
        for j in range(nbgi):
            ind = int(1)
            for matrix in matrices:
                ind *= matrix[c,j]
            if ind == 1:
                return_mat[c,j] = int(1)
    return return_mat

feasibility_mat = FINAL_FEASIBILITY(landcover_minarea_constraints, slope_constraint)

#mergeID = land_data_df['mergeID'].values.reshape(-1, 1)  # Convert to a column vector
mergeID_column = (land_data_df['mergeID'].values.reshape(-1,1))
labeled_feasibility_mat = np.hstack([mergeID_column, feasibility_mat])

# SAVING FEASIBILITY MATRICES 
with open('output_matrix.txt', 'w') as f:
    for row in labeled_feasibility_mat:
        f.write(' '.join(map(lambda x: str(int(x)), row)) + '\n')
