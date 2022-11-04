# Jacques Terblanche
# 22548602

import sys
import time
import os
import glob
from evolve import Evolution
import json

###############
# Parameters
###############
# Random (0), generative (1)
search_type = 1

# Actuator
height = 16  # mm - Maximum cross-section height
width = 8  # mm - Maximum cross-section width
target_angle = 40 # degrees - User requested angle

cavity_total_depth = 20 # mm - Distance between inner walls (depth)
thickness = 1.4 # mm - Thickness of walls
num_cells = 8 # Number of cells
bottom_cavity_height = 6 # mm - The distance between the start of the generated cross-section and the bottom layer
bottom_thickness = 3 # mm - The thickness of the bottom layer

pressure_load = 0.04 # MPa
gravity_load = 9810.0 # mm/s^2

# L-system
iterations = 8  # Number of iterations of l-string rewriting
axiom = "A"

# Evolution settings
seed = 6546
num_cycles = 3
num_individuals = 3
elitism = 0.1
replacement = 0.2

###############
# Set-up
###############

# Start measuring program clock time
start = time.time()

# Set directories for clearing files and exporting parameters
script_dir = os.path.dirname(__file__)
data_path = "data//log.txt"
data_output_path = os.path.join(script_dir, data_path)
sys.stdout = open(data_output_path, 'w')
cross_storage = os.path.join(script_dir, "Cross-sections//*.png")
coord_storage = os.path.join(script_dir, "Coordinate_storage//*.json")
abaqus_file_path = os.path.join(script_dir, "Abaqus")
files = glob.glob(coord_storage)

# Clear files
for f in files:
    os.remove(f)
files = glob.glob(cross_storage)
for f in files:
    os.remove(f)

# Export Abaqus parameters
abaqus_parameters = [cavity_total_depth,thickness,num_cells,bottom_cavity_height,bottom_thickness,pressure_load,gravity_load]
os.chdir(abaqus_file_path)
with open('input_parameters.json', 'w', encoding='utf-8') as f:
    json.dump(abaqus_parameters, f, ensure_ascii=False, indent=4)
os.chdir(script_dir)


# Number of pixels based on coordinates is increased by factor of 10
# number can vary for program optimisation
pixel_factor = 10
target = [width * pixel_factor, height * pixel_factor]

# Call evolution algorithm and specify search mechanism
Evo1 = Evolution(num_cycles, seed, target, target_angle, axiom,elitism,replacement)  # cycles, seed, seed
if search_type == 0:
    Evo1.random_gen(num_individuals)
else:
    Evo1.evolve(num_individuals)

# End program, display total system run time
print("Done")
end = time.time()
print("This program ran for: " + str(end - start) + " seconds")
sys.stdout.close()
