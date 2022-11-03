# Jacques Terblanche
# 22548602

import sys
import time
import os
import glob
from evolve import Evolution

###############
# Parameters
###############
# Random (0), generative (1)
search_type = 1

# Actuator
height = 16  # Maximum cross-section height
width = 8  # Maximum cross-section width
target_angle = 40

# L-system
iterations = 8  # Number of iterations of l-string rewriting
axiom = "A"

# Evolution settings
seed = 1324
num_cycles = 15
num_individuals = 30
elitism = 0.1
replacement = 0.2

###############
# Set-up
###############
# Start measuring program clock time
start = time.time()

# Set directories for clearing
script_dir = os.path.dirname(__file__)
data_path = "data//log.txt"
data_output_path = os.path.join(script_dir, data_path)
sys.stdout = open(data_output_path, 'w')
cross_storage = os.path.join(script_dir, "Cross-sections//*.png")
coord_storage = os.path.join(script_dir, "Coordinate_storage//*.json")
files = glob.glob(coord_storage)

# Clear files
for f in files:
    os.remove(f)
files = glob.glob(cross_storage)
for f in files:
    os.remove(f)

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
