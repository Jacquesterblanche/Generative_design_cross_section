# Jacques Terblanche
# 22548602

import random
import math
import numpy as np
from l_syst import Lsystem
from l_syst import Interp
import subprocess
import os
import json


class Evolution:
    """
    An Evolution class to apply a genetic algorithm to a specified number of individuals accross
    cycles or to randomly generate 1 population.

    Attributes
    ----------
    pop_size : int
        The number of generations
    axiom : str
        The initial axiom used for the l-system
    population : list
        A list containing the l-system class objects
    seed : int
        The random seed used for the system's initialisation
    target : list
        The targeted end-coordinates for the cross-section's grid
    target_angle : float
        The target bending angle of the resultant soft bending actuator
    elitism : float
        The fraction of best performing individuals to be kept for the next cycle
    replacement : float
        The fraction of worst performing individuals to be regenerated for the next cycle

    Methods
    ----------
    generate_initial_population(num_individuals, axiom, seed, target)
        Produces the first generation of individuals
    evolve(num_individuals)
        Produces all individuals in all cycles
    crossover(parent_1, parent_2, i)
        Applies the cross-over variational operator to two parent individuals
    evaluate_pop_fitness(individuals, target, pop_number)
        Determines the fitness of all individuals through calling a FEM script and applying a fitness
        function
    select_parents(sel_pool, case)
        Applies roulette selection to determine parent individuals
    mutate(parent, i)
        Produces an individual with a random number of rules re-generated
    generate_next_gen(individuals, pop_num)
        Utilises selection rules to determine the composition of the next generation
    random_gen(num_individuals)
        Randomly generates a single population with the total number of individuals
        equal to the number provided

    """

    def __init__(self, population_size, seed, target, target_angle, axiom, elitism, replacement):
        """
        Parameters
        ----------
        population_size : int
            The number of generations
        seed : int
            The random seed used for the system's initialisation
        target : list
            The targeted end-coordinates for the cross-section's grid
        target_angle : float
            The target bending angle of the resultant soft bending actuator
        axiom : str
            The target bending angle of the resultant soft bending actuator
        elitism : float
            The fraction of best performing individuals to be kept for the next cycle
        replacement : float
            The fraction of worst performing individuals to be regenerated for the next cycle
        """

        self.pop_size = population_size
        self.axiom = axiom
        self.seed = seed
        self.target = target
        self.target_angle = target_angle
        self.elitism = elitism
        self.replacement = replacement

        # Initialise an empty population list
        self.population = []

    @staticmethod
    def generate_initial_population(num_individuals, axiom, seed, target):
        """Produces the first generation of individuals for the genetic algorithm"""
        individuals = list()
        # Generates L-system classes for the number of individuals specified. Also, interprets
        # the L-systems' resultant strings into grid-based drawings/images
        for i in range(num_individuals):
            individuals.append(Lsystem(axiom, seed + 2 * i))
            temp = Interp(individuals[i].sentence, target)
            individuals[i].pop_number = 0
            individuals[i].coords = temp.draw(0, i)

        return individuals

    def evolve(self, num_individuals):
        """Produces all individuals in all cycles, through calling the generate_initial_pop function, evaluation
        functions and generate_next_gen functions"""

        # Generate an initial population and store the seed
        individuals = self.generate_initial_population(num_individuals, self.axiom, self.seed, self.target)
        print(self.seed)
        # Evaluate initial population
        individuals = self.evaluate_pop_fitness(individuals, self.target, 0)
        self.population.append(individuals)

        # Generate subsequent generations of individuals and evaluate them
        new_gen = individuals
        for i in range(self.pop_size - 1):
            new_gen = self.generate_next_gen(new_gen, i + 1)
            new_gen = self.evaluate_pop_fitness(new_gen, self.target, i + 1)
            self.population.append(new_gen)

    def crossover(self, parent_1, parent_2, i):
        """Applies the cross-over variational operator to two parent individuals"""
        # Initialise to specified seed along with population specific variation
        random.seed(self.seed + i)

        # Randomly select cross-over points
        cross_over_point_1 = random.randrange(0, 3)
        cross_over_point_2 = random.randrange(0, 3)

        # Choose child rules based on parents' cross-over points
        child_1_rules = parent_1.rules[:cross_over_point_1] + parent_2.rules[cross_over_point_1:]
        child_2_rules = parent_2.rules[:cross_over_point_2] + parent_1.rules[cross_over_point_2:]
        # Generate L-system with child rules
        child_1 = Lsystem(self.axiom, self.seed + i, child_1_rules)
        child_2 = Lsystem(self.axiom, self.seed + i, child_2_rules)
        # Return new individuals

        return child_1, child_2

    def evaluate_pop_fitness(self, individuals, target, pop_number):
        """
         Determines the fitness of all individuals through calling a FEM script and applying a fitness
        function
        """
        # Sets the number of individuals and initialises running sum to zero
        num_individuals = len(individuals)
        running_sum = 0  # used for mean angle calculation

        # Each individiauls' coordinates in the current generation is exported to a JSON
        # file and each new individual is evaluated
        for i in range(num_individuals):
            individuals[i].gen_number = i
            individuals[i].pop_number = pop_number
            export_to_json(individuals[i].coords, target, pop_number, i)

            # If individual already has an angle, then its evaluation will be skipped (to save
            # computational costs)
            if individuals[i].angle:
                pass
            else:
                # The evaluate function is called, this function utilises a subprocess to launch
                # Abaqus CAE
                individuals[i].angle = evaluate()
            # The absolute distance between the target angle and the individual's angle is calculated
            individuals[i].distance = abs(self.target_angle - individuals[i].angle)

        print("=======")
        # Current generation individuals are sorted in descending order (according to angle)
        individuals.sort(key=lambda x: x.distance, reverse=False)

        # The rankings of all individuals are stored and printed
        for i in range(num_individuals):
            individuals[i].ranking = (i + 1)
            print("Individual_" + str(individuals[i].pop_number) + "_" + str(individuals[i].gen_number) + ": " + str(
                individuals[i].sentence))
            print("Angle: " + str(round(individuals[i].angle)))
            running_sum = running_sum + individuals[i].angle
        # The mean is calculated and printed
        print("=======" + str(running_sum / num_individuals) + "=======")

        # The fitness function is applied to all individuals. See report for further information
        for i in range(len(individuals)):
            individuals[i].fitness = 2 * (num_individuals + 1 - individuals[i].ranking) / (
                    num_individuals * (num_individuals + 1))

        return individuals

    @staticmethod
    def select_parents(sel_pool, case):
        """
        Applies roulette selection to determine parent individuals
        """
        num_individuals = len(sel_pool)
        # The fitness score for a cycle sums to 1 (with the chosen definition for fitness score)
        total_sum = 1
        # A random value is calculated for the initial partial sum
        partial_sum = random.uniform(0, 1)
        # Parents 1 and 2 are initialised to the best two performing individuals
        parent_1 = sel_pool[0]
        parent_2 = sel_pool[1]

        # Parent selection if cross-over is selected
        if case == 1:
            # With roulette selection, all individuals' fitness scores are added to the
            # partial sum. The individual's who value pushes the partial sum to be greater
            # than the total sum, is the chosen individual

            # First parent
            for i in range(num_individuals):
                partial_sum += sel_pool[i].fitness
                if partial_sum > total_sum:
                    parent_1 = sel_pool[i]
                    break

            # Second parent
            num_individuals = len(sel_pool)
            partial_sum = random.uniform(0, 1)

            for i in range(num_individuals):
                partial_sum += sel_pool[i].fitness

                if partial_sum > total_sum:
                    parent_2 = sel_pool[i]

                    break

            return parent_1, parent_2, sel_pool

        # Parent selection for other cases
        elif case == 2:
            for i in range(num_individuals):
                partial_sum += sel_pool[i].fitness

                if partial_sum > total_sum:
                    parent_1 = sel_pool[i]

            return parent_1, sel_pool

    def mutate(self, parent, i):
        """
        Produces an individual with a random number of rules re-generated
        """
        child = None
        random.seed(self.seed + i + i * i)
        num_mutations = random.randrange(1, 3)

        # The random generated number of mutations are each applied
        for x in range(num_mutations):
            random.seed(self.seed + i + x)
            rule_num = random.randrange(0, 6)
            child_rules = parent.rules
            child_rules[rule_num] = parent.l_mutate()

            child = Lsystem(self.axiom, self.seed + i, child_rules)

        return child

    def generate_next_gen(self, individuals, pop_num):
        """
        Utilises selection rules to determine the composition of the next generation
        """

        # Variables are initialised and the number of individuals is set
        new_individuals = []
        temp_list = []
        num_individuals = len(individuals)

        # Setup replacement point for next generation
        replacement_point = (num_individuals - (math.ceil(self.replacement * num_individuals)))
        final_list = []
        # Introduce elitism to new generation
        for i in range(math.ceil(self.elitism * len(individuals))):
            if i > 0 and individuals[i].sentence == individuals[i - 1].sentence:
                new_individuals.append(Lsystem(self.axiom, self.seed + 3 * i * pop_num + i + 10))
            else:
                new_individuals.append(individuals[i])
        # Count number of unique individuals in the population
        for j in range(num_individuals):
            temp_list.append(individuals[j].sentence)
        num_unique = len(np.unique(np.array(temp_list)))

        # Apply genetic variation operators to rest of population (not elite/replaced)
        i = math.ceil(self.elitism * num_individuals)
        while i < replacement_point:
            random.seed(self.seed + pop_num * i + i)

            rand_com = random.uniform(0, 2)
            rand_mut = random.uniform(0, 1)
            rand_com = rand_com + (1 - num_unique / num_individuals)

            # If angle is within 90% of targeted angle, individual is then kept
            if round(individuals[i].angle) == round(self.target_angle * 90 / 100) and final_list.count(
                    individuals[i].sentence) == 0:
                new_individuals.append(individuals[i])

                i += 1

            # Apply cross-over as long as there are enough individuals available
            # and if cross-over probability is activated
            elif rand_com <= 1 and (replacement_point - i != 1):
                temp = self.select_parents(individuals, 1)
                temp_object = self.crossover(temp[0], temp[1], pop_num * i)
                temp_1 = temp_object[0]
                temp_2 = temp_object[1]
                # Apply random mutation on cross-over individuals if mutation probability
                # is activated
                if rand_mut >= 0.5:
                    temp_1 = self.mutate(temp_object[0], pop_num * i + i)
                    temp_2 = self.mutate(temp_object[1], pop_num * i + 2 * i + 1)

                new_individuals.append(temp_1)
                new_individuals.append(temp_2)
                i += 2

            # Apply only mutation to individual if mutation probability is activated
            elif (rand_com > 1) or (replacement_point - i < 2):
                temp = self.select_parents(individuals, 2)
                new_individuals.append(self.mutate(temp[0], pop_num * i))
                i += 1

            # Error-case for development purposes (is used to pass selected parent if above results in error)
            else:
                new_individuals.append(self.select_parents(individuals, 2)[0])
                i += 1

        # Introduce replacement to new generation
        for k in range(math.ceil(self.replacement * num_individuals)):
            new_individuals.append(Lsystem(self.axiom, self.seed + 2 * k * pop_num + k + 10))

        # All new individuals are interpreted
        for j in range(len(new_individuals)):
            temp = Interp(new_individuals[j].sentence, self.target)
            new_individuals[j].pop_number = pop_num
            new_individuals[j].coords = temp.draw(pop_num, j)

        print("")
        return new_individuals

    def random_gen(self, num_individuals):
        """
        Randomly generates a single population with the total number of individuals
        equal to the number provided
        """

        individuals = list()
        # Generates, interprets and evaluates a single population
        for i in range(num_individuals):
            individuals.append(Lsystem(self.axiom, self.seed + 2 * i))
            temp = Interp(individuals[i].sentence, self.target)
            individuals[i].pop_number = 0
            individuals[i].coords = temp.draw(0, i)

        self.evaluate_pop_fitness(individuals, self.target, 0)


# Storage setup
script_dir = os.path.dirname(__file__)
rel_path = "Abaqus"
abs_file_path = os.path.join(script_dir, rel_path)
rel_path = "Coordinate_storage"
abs_storage_path = os.path.join(script_dir, rel_path)


def evaluate():
    """Uses a Windows subprocess to call the Abaqus python script from Abaqus CAE"""
    os.chdir(abs_file_path)
    subprocess.run('abaqus cae -noGUI Abaqus_script.py', shell=True)

    # Resultant angle is read from generated txt file
    with open('angle.txt', 'r') as file:
        angle = float(file.read())
    return angle


def export_to_json(positions, target, pop_number, gen_number):
    """Exports the position file, mirrors it and saves it a file accessible by Abaqus"""
    script_loc = os.path.dirname(__file__)
    abaqus_path = "Abaqus"
    abaqus_file_path = os.path.join(script_loc, abaqus_path)
    export_data = []

    # Select every other data point (a high number of points will lead to complex shapes
    # which require very refined mesh

    reduced_list = positions[::4]
    # Append middle point
    reduced_list.append((target[0], positions[-1][1]))

    # Mirror data points
    for x in range(len(reduced_list) - 1):
        export_data.append([2 * target[0] - reduced_list[x][0], reduced_list[x][1]])

    # Add reversed list to reduced list
    export_data.reverse()
    export_data = (reduced_list + export_data)

    # Resize coordinates (e.g. from 100 pixels to 10 mm)
    new_list = list()
    for x in range(len(export_data)):
        new_x = export_data[x][0] / 10
        new_y = export_data[x][1] / 10
        new_list.append([new_x, new_y])

    export_data = new_list

    # Export data to a JSON file
    os.chdir(abaqus_file_path)
    with open('input_data.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=4)
    os.chdir(abs_storage_path)
    with open('Individual' + str(pop_number) + '_' + str(gen_number) + '.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=4)
    os.chdir(script_dir)
