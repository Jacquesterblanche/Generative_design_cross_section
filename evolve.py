import random
import math
import numpy as np
from l_syst import Lsystem
from l_syst import Interp
import subprocess
import os
import json


class Evolution:  # Creates the evolutionary algorithm class

    def __init__(self, population_size, seed, target,target_angle):  # Initialises the class with the input parameters
        self.pop_size = population_size
        self.population = []
        self.iterations = 8
        self.seed = seed
        self.target = target
        self.target_angle = target_angle

    def generate_initial_population(self, num_individuals, axiom, seed, target):
        individuals = list()
        for i in range(num_individuals):
            individuals.append(Lsystem(axiom, seed + 2*i))
            temp = Interp(individuals[i].sentence, target)
            individuals[i].pop_number = 0
            individuals[i].coords = temp.draw(0, i)

        return individuals

    def evolve(self, num_individuals, axiom):
        individuals = []
        self.axiom = axiom
        individuals = self.generate_initial_population(num_individuals, self.axiom, self.seed, self.target)
        print(self.seed)
        individuals = self.evaluate_pop_fitness(individuals, self.target, 0)
        self.population.append(individuals)
        
        new_gen = individuals

        for i in range(self.pop_size - 1):
            new_gen = self.generate_next_gen(new_gen, i + 1)

            new_gen = self.evaluate_pop_fitness(new_gen, self.target, i + 1)
            self.population.append(new_gen)

            

    def crossover(self, parent_1, parent_2, i):
        child_1_rules = None
        child_2_rules = None

        random.seed(self.seed + i)

        cross_over_point_1 = random.randrange(0, 3)
        cross_over_point_2 = random.randrange(0, 3)
        child_1_rules = parent_1.rules[:cross_over_point_1] + parent_2.rules[cross_over_point_1:]
        child_2_rules = parent_2.rules[:cross_over_point_2] + parent_1.rules[cross_over_point_2:]
        child_1 = Lsystem(self.axiom, self.seed + i, child_1_rules)
        child_2 = Lsystem(self.axiom, self.seed + i, child_2_rules)

        return child_1, child_2



    def evaluate_pop_fitness(self, individuals, target, pop_number):
        num_individuals = len(individuals)
        running_sum = 0

        for i in range(num_individuals):
            individuals[i].gen_number = i
            individuals[i].pop_number = pop_number
            export_to_json(individuals[i].coords, target, pop_number, i)
            
            if individuals[i].angle:
                pass
            else:
                individuals[i].angle = evaluate()
            individuals[i].distance = abs(self.target_angle - individuals[i].angle)

        

        print("=======")
        individuals.sort(key=lambda x: x.distance, reverse=False)
        for i in range(num_individuals):
            individuals[i].ranking = (i + 1)
            print("Individual_" + str(individuals[i].pop_number) +"_" + str(individuals[i].gen_number) + ": " + str(individuals[i].sentence))
            print("Angle: " + str(round(individuals[i].angle)))
            running_sum = running_sum + individuals[i].angle
        print("=======" + str(running_sum/num_individuals)+"=======" )

 

        for i in range(len(individuals)):
            individuals[i].fitness = 2 * (num_individuals + 1 - individuals[i].ranking) / (num_individuals * (num_individuals + 1))


        return individuals

    @staticmethod
    def select_parents(sel_pool, case):
        num_individuals = len(sel_pool)
        total_sum = 1
        partial_sum = random.uniform(0, 1)
        parent_1 = sel_pool[0]
        parent_2 = sel_pool[1]
        

        if case == 1:
            for i in range(num_individuals):
                partial_sum += sel_pool[i].fitness
                if partial_sum > total_sum:
                    parent_1 = sel_pool[i]
                    break


            num_individuals = len(sel_pool)
            partial_sum = random.uniform(0, 1)

            for i in range(num_individuals):
                partial_sum += sel_pool[i].fitness

                if partial_sum > total_sum:
                    parent_2 = sel_pool[i]

                    break
            
    

            return parent_1, parent_2, sel_pool

        elif case == 2:
            for i in range(num_individuals):
                partial_sum += sel_pool[i].fitness

                if partial_sum > total_sum:
                    parent_1 = sel_pool[i]
                    
                
            return parent_1, sel_pool

    def mutate(self, parent, i):
        random.seed(self.seed + i+i*i)
        
        num_mutations = random.randrange(1,3)
        
        for x in range(num_mutations):
            random.seed(self.seed + i+x)
            rule_num = random.randrange(0, 6)
            child_rules = parent.rules
            child_rules[rule_num] = parent.l_mutate(parent.rules[rule_num], self.seed + i)
        
            child = Lsystem(self.axiom, self.seed + i, child_rules)

        return child

    def generate_next_gen(self, individuals, pop_num):
        rand_mut = 0
        rand_com = 0
        new_individuals = []
        num_individuals = len(individuals)
        temp_list = []
        
        
        
        elitism = 0.1
        replacement = 0.2
        replacement_point = (num_individuals - (math.ceil(replacement * num_individuals)))
        final_list = []
        # Introduce elitism to new generation
        for i in range(math.ceil(elitism * len(individuals))):
            if i > 0 and individuals[i].sentence == individuals[i-1].sentence :
                new_individuals.append(Lsystem(self.axiom, self.seed + 3*i*pop_num + i+10))
            else:  
                new_individuals.append(individuals[i])
                
            
        for j in range(num_individuals):
            temp_list.append(individuals[j].sentence)
            
        num_unique = len(np.unique(np.array(temp_list)))
    

        i = math.ceil(elitism * num_individuals)
        print("This is the number kept for elite:" + str(math.ceil(elitism * len(individuals))))
        print("This is the number kept for replace:" + str(math.ceil(replacement * len(individuals))))

        while i < (replacement_point):
            random.seed(self.seed + pop_num*i+i)

            rand_com = random.uniform(0, 2)

            rand_mut = random.uniform(0,1)
            rand_com = rand_com + (1-num_unique/num_individuals)

            if round(individuals[i].angle) == round(self.target_angle*90/100) and final_list.count(individuals[i].sentence) == 0 :
                new_individuals.append(individuals[i])

                i += 1



            elif rand_com <= 1 and (replacement_point - i != 1):
                temp = self.select_parents(individuals, 1)
                temp_object = self.crossover(temp[0], temp[1], pop_num*i)
                temp_1 = temp_object[0]
                temp_2 = temp_object[1]

                
                if rand_mut>=0.5:
                    temp_1 = self.mutate(temp_object[0], pop_num*i + i)
                    temp_2 = self.mutate(temp_object[1], pop_num*i +2*i +1)
                    
                new_individuals.append(temp_1)
                new_individuals.append(temp_2)
                i += 2

            elif (rand_com > 1) or (replacement_point - i < 2):
                temp = self.select_parents(individuals, 2)
                new_individuals.append(self.mutate(temp[0], pop_num*i))
                i += 1

         
            else:
                new_individuals.append(self.select_parents(individuals, 2)[0])
                i += 1

        #Introduce replacement to new generation
        
        for k in range(math.ceil(replacement * num_individuals)):
            new_individuals.append(Lsystem(self.axiom, self.seed + 2*k*pop_num + k+10))

        for j in range(len(new_individuals)):
            temp = Interp(new_individuals[j].sentence, self.target)
            new_individuals[j].pop_number = pop_num
            new_individuals[j].coords = temp.draw(pop_num, j)

        print("")
        return new_individuals
    
    def random_gen(self,num_individuals,axiom):
        individuals = list()
        for i in range(num_individuals):
            individuals.append(Lsystem(axiom, self.seed + 2*i))

            temp = Interp(individuals[i].sentence, self.target)
            individuals[i].pop_number = 0
            individuals[i].coords = temp.draw(0, i)
            
        individuals = self.evaluate_pop_fitness(individuals, self.target, 0)





script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = "Abaqus"
abs_file_path = os.path.join(script_dir, rel_path)
rel_path = "Coordinate_storage"
abs_storage_path = os.path.join(script_dir, rel_path)


def evaluate():
    os.chdir(abs_file_path)
    subprocess.run('abaqus cae -noGUI Abaqus_script.py', shell=True)
    # subprocess.call('abaqus cae -noGUI Original_multi.py',shell=True)
    # print("Done")
    with open('angle.txt', 'r') as file:
        angle = float(file.read())
    return angle
    


def export_to_json(positions, target, pop_number, gen_number):
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    rel_path = "Abaqus"
    abs_file_path = os.path.join(script_dir, rel_path)

    export_data = []
    #transformed_data = []

    reduced_list = positions[::4]
    reduced_list.append((target[0], positions[-1][1]))
    #transformed_data.append((target[0], positions[-1][1]))

    for x in range(len(reduced_list) - 1):
        export_data.append([2 * target[0] - reduced_list[x][0], reduced_list[x][1]])

    export_data.reverse()
    export_data = (reduced_list + export_data)
    
    new_list = list()
    for x in range(len(export_data)):
        new_x = export_data[x][0]/10 
        new_y = export_data[x][1]/10 
        new_list.append([new_x,new_y])
 
    export_data = new_list
    

    os.chdir(abs_file_path)
    with open('input_data.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=4)
    os.chdir(abs_storage_path)
    with open('Individual' + str(pop_number) + '_' + str(gen_number) + '.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=4)

    os.chdir(script_dir)
