# Jacques Terblanche
# 22548602


import sys
import time
import os
import glob
from evolve import Evolution

# Parameters
###############

height = 16
width = 8
iterations = 8
axiom = "A"
seed = 1324
num_cycles = 15
num_individuals = 30
target_angle = 40

###############
start = time.time()
script_dir = os.path.dirname(__file__)
rel_path = "data//log.txt"
output_path = os.path.join(script_dir, rel_path)
sys.stdout = open(output_path, 'w')
cross_storage = os.path.join(script_dir, "Cross-sections//*.png")
coord_storage = os.path.join(script_dir, "Coordinate_storage//*.json")
files = glob.glob(coord_storage)

for f in files:
    os.remove(f)
files = glob.glob(cross_storage)
for f in files:
    os.remove(f)

target = [width * 10, height * 10]
Evo1 = Evolution(num_cycles, seed, target, target_angle)  # cycles, seed, seed
# Evo1.generate_initial_population(num_individuals, axiom, seed, target)  # num_individuals, axiom, seed, target
Evo1.evolve(num_individuals, axiom)
# Evo1.random_gen(2000, axiom)
print("Done")
end = time.time()
print("This program ran for: " + str(end - start) + " seconds")
sys.stdout.close()
