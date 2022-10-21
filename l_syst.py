import matplotlib.pyplot as plt
import random
from PIL import Image
import math
import numpy as np
import json


class Lsystem:  # Creates the l-system class

    rules = []
    sentence = ""

    def __init__(self, axiom, seed, gen_rules=[]):  # Initialises the class with the input parameters
        self.axiom = axiom
        self.num_rules = 6
        self.pos = []
        self.alphabet = ["A", "B", "C", "D", "F", "E", "F", "H", "G", "-", "+", "F", "-", "+", "F", "-", "+", "", "{",
                         "}"]
        self.alphabet_pred = ["A", "B", "C", "D", "E", "F", "H", "G"]
        self.rules = []
        self.coords = []
        if gen_rules == []:
            self.gen_rules(seed)
        else:
            self.rules = gen_rules
        self.sentence = self.generate(5, self.rules)  # Number of iterations
        self.gen_number = int()
        self.pop_number = int()
        self.angle = float()
        self.fitness = []
        self.ranking = []
        self.distance = float()
        j = 0

        while self.sentence == 1001:
            j += 1
            self.rules = []
            self.gen_rules(j + seed)
            self.sentence = self.generate(8, self.rules)

        self.sentence = self.sentence + "F"

    def append_rules(self, predecessor, successor):
        self.rules.append([predecessor, successor])

    def gen_rules(self, seed):
        random.seed(seed)
        np.random.seed(seed)
        for i in range(self.num_rules):
            if i == 0:
                pred = "A"
                succ = random.choice(self.alphabet) + random.choice(self.alphabet) + random.choice(
                    self.alphabet_pred) + random.choice(
                    self.alphabet)
            if i == 1:
                pred = "B"
                succ = random.choice(self.alphabet) + random.choice(self.alphabet) + random.choice(
                    self.alphabet) + random.choice(self.alphabet) + random.choice(self.alphabet)
            if i == 2:
                pred = "C"
                succ = random.choice(self.alphabet) + random.choice(self.alphabet) + random.choice(
                    self.alphabet) + random.choice(self.alphabet) + random.choice(self.alphabet)
            if i == 3:
                pred = "D"
                succ = random.choice(self.alphabet) + random.choice(self.alphabet) + random.choice(
                    self.alphabet) + random.choice(self.alphabet) + random.choice(self.alphabet)
            if i == 4:
                pred = "E"
                succ = random.choice(self.alphabet) + random.choice(self.alphabet) + random.choice(
                    self.alphabet) + random.choice(self.alphabet) + random.choice(self.alphabet)
            if i == 5:
                pred = "G"
                succ = random.choice(self.alphabet) + random.choice(self.alphabet) + random.choice(
                    self.alphabet) + random.choice(self.alphabet) + random.choice(self.alphabet)
            if i == 6:
                pred = "H"
                succ = random.choice(self.alphabet) + random.choice(self.alphabet) + random.choice(
                    self.alphabet) + random.choice(self.alphabet) + random.choice(self.alphabet)

            self.append_rules(pred, succ)


    def form_string(self, sentence, rules):
        new_sentence = ""
        for i in range(len(sentence)):

            # if self.se

            if sentence[i] == rules[0][0]:
                new_sentence += rules[0][1]
            elif sentence[i] == rules[1][0]:
                new_sentence += rules[1][1]
            elif sentence[i] == rules[2][0]:
                new_sentence += rules[2][1]
            elif sentence[i] == rules[3][0]:
                new_sentence += rules[3][1]
            elif sentence[i] == rules[4][0]:
                new_sentence += rules[4][1]
            elif sentence[i] == rules[5][0]:
                new_sentence += rules[5][1]
            else:
                new_sentence += sentence[i]
        return new_sentence



    def generate(self, iterations, rules):

        self.sentence = self.axiom
        num_f = 0

        for count in range(iterations - 1):
            self.sentence = self.form_string(self.sentence, rules)
            # print(self.sentence)

        for j in range(len(self.sentence)):
            if self.sentence[j] == "F":
                num_f += 1
        if num_f > 0:
            return self.sentence
        else:
            return 1001

    def l_mutate(self, individual, seed):

        # Rule based mutation
        individual = random.choice(self.alphabet) + random.choice(self.alphabet) + random.choice(
            self.alphabet) + random.choice(self.alphabet) + random.choice(self.alphabet)

        return individual


class Interp:  # Creates the l-system string interpreter
    def __init__(self, string, target):  # Initialises the class with the input parameters
        self.string = string
        self.target = target
        self.x = 0
        self.y = 0
        self.direction = 1
        self.last_operator = "+"
        self.img = Image.new('RGB', (self.target[0], self.target[1]), (255, 255, 255))
        self.positions = [[0, 0]]
        self.num_f = 0
        self.angle = 0
        for j in range(len(self.string)):
            if string[j] == "F":
                self.num_f += 1

        self.num_pixel_placement = math.ceil(self.target[0] / self.num_f)

    def direction_change(self, operator):
        if operator == "-":
            self.direction -= 1
            self.last_operator = "-"
        if operator == "+":
            self.direction += 1
            self.last_operator = "+"

        if self.direction < 1:
            self.direction = 3
        if self.direction > 3:
            self.direction = 1

    def draw(self, pop_number, gen_number):
        self.img.putpixel((0, 0), (0, 0, 0))  # Always starts with a pixel at 0,0
        i = 0
        num_f = 0

        self.string = get_repeated(self.string, 3)

        while not i == len(self.string):

            if self.string[i] == "-" or self.string[i] == "+":
                self.direction_change(self.string[i])
            if self.string[i] == "F":

                for k in range(self.num_pixel_placement):
                    temp_pos = self.get_temp_pos(self.direction, self.positions[num_f])
                    check = self.check_neighbours(temp_pos)
                    if check == 1:
                        num_f += 1
                        self.positions.append(temp_pos)
                        # print(self.positions)
                        self.img.putpixel((self.positions[num_f][0], self.positions[num_f][1]), (0, 0, 0))
                    elif check == 2:
                        self.direction_change(self.last_operator)
                        i -= 1
                    elif check == 3:
                        pass
            i += 1

        # function to place pixels until end of grid

        for j in range(self.target[0] - self.positions[-1][0]):
            self.img.putpixel((self.positions[num_f][0] + j, self.positions[num_f][1]), (0, 0, 0))
            self.positions.append((self.positions[num_f][0] + j, self.positions[num_f][1]))

        plt.imshow(self.img)
        ax = plt.gca()
        ax.invert_yaxis()
        plt.axis("off")

        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "Cross-sections"
        abs_file_path = os.path.join(script_dir, rel_path)

        os.chdir(abs_file_path)
        filename = 'Individual_' + str(pop_number) + '_' + str(gen_number) + '.png'

        plt.savefig(filename, format="png", dpi=10)
        plt.show()
        plt.close()
        os.chdir(script_dir)

        return self.positions

    @staticmethod
    def get_temp_pos(direction, current_pos):
        x = current_pos[0]
        y = current_pos[1]
        if direction == 0:
            x += 1
            y -= 1
        if direction == 1:
            x += 1
        if direction == 2:
            x += 1
            y += 1
        if direction == 3:
            y += 1
        if direction == 4:
            x -= 1
            y += 1
        if direction == 5:
            x -= 1

        return x, y

    def check_neighbours(self, pos):
        internal = 1
        # Check above
        condition = 0
        # Check canvas
        if pos[0] < 0:
            return 3
        if pos[1] < 0:
            return 3
        if pos[0] > self.target[0] - 1:
            return 3
        if pos[1] > self.target[0] - 1:
            return 3

        # Check sides on edge cases

        if pos[0] == 0 and (pos[1] > 0 and pos[1] < self.target[1] - 1):  # Left limit case only
            # Check top
            condition += 1
            internal = 0
            if self.img.getpixel((pos[0], pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check right
            if self.img.getpixel((pos[0] + 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check below
            if self.img.getpixel((pos[0], pos[1] - 1)) == (0, 0, 0):
                condition += 1
            #  Check below right
            # if self.img.getpixel((pos[0]+1, pos[1]-1)) == (0, 0, 0):
            #     condition += 1
            # # Check top right
            # if self.img.getpixel((pos[0]+1, pos[1]+1)) == (0, 0, 0):
            #     condition += 1

        elif pos[0] == self.target[0] - 1 and (pos[1] > 0 and pos[1] < self.target[1] - 1):  # Right limit case only
            condition += 1
            internal = 0
            # Check top
            if self.img.getpixel((pos[0], pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check left
            if self.img.getpixel((pos[0] - 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check below
            if self.img.getpixel((pos[0], pos[1] - 1)) == (0, 0, 0):
                condition += 1

        elif pos[1] == 0 and (pos[0] > 0 and pos[0] < self.target[0] - 1):  # Bottom limit case only
            condition += 1
            internal = 0
            # Check top
            if self.img.getpixel((pos[0], pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check left
            if self.img.getpixel((pos[0] - 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check right
            if self.img.getpixel((pos[0] + 1, pos[1])) == (0, 0, 0):
                condition += 1
        elif pos[1] == self.target[1] - 1 and (pos[0] > 0 and pos[0] < self.target[0] - 1):  # Top limit case only
            condition += 1
            internal = 0
            # Check left
            if self.img.getpixel((pos[0] - 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check right
            if self.img.getpixel((pos[0] + 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check below
            if self.img.getpixel((pos[0], pos[1] - 1)) == (0, 0, 0):
                condition += 1

        elif pos[0] == 0 and pos[1] == 0:  # Left limit and Bottom limit case
            condition += 1
            internal = 0
            # Check top
            if self.img.getpixel((pos[0], pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check right
            if self.img.getpixel((pos[0] + 1, pos[1])) == (0, 0, 0):
                condition += 1

        elif pos[0] == self.target[0] - 1 and pos[1] == 0:  # Right limit and Bottom limit case
            condition += 1
            internal = 0
            # Check top
            if self.img.getpixel((pos[0], pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check left
            if self.img.getpixel((pos[0] - 1, pos[1])) == (0, 0, 0):
                condition += 1

        elif pos[0] == 0 and pos[1] == self.target[1] - 1:  # Left limit and Top limit case
            condition += 1
            internal = 0
            # Check below
            if self.img.getpixel((pos[0], pos[1] - 1)) == (0, 0, 0):
                condition += 1
            # Check right
            if self.img.getpixel((pos[0] + 1, pos[1])) == (0, 0, 0):
                condition += 1

        elif pos[0] == self.target[0] - 1 and pos[1] == self.target[1] - 1:  # Right limit and Top limit case
            condition += 1
            internal = 0
            # Check below
            if self.img.getpixel((pos[0], pos[1] - 1)) == (0, 0, 0):
                condition += 1
            # Check left
            if self.img.getpixel((pos[0] - 1, pos[1])) == (0, 0, 0):
                condition += 1

        # Check sides on internal cases
        if not internal == 0:
            if pos[0] >= self.target[0]:
                return 3
            if pos[1] >= self.target[1]:
                return 3
            # Check top
            if self.img.getpixel((pos[0], pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check left
            if self.img.getpixel((pos[0] - 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check right
            if self.img.getpixel((pos[0] + 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check below
            if self.img.getpixel((pos[0], pos[1] - 1)) == (0, 0, 0):
                condition += 1
            # Check below left
            if self.img.getpixel((pos[0] - 1, pos[1] - 1)) == (0, 0, 0):
                condition += 1
            # Check below right
            if self.img.getpixel((pos[0] + 1, pos[1] - 1)) == (0, 0, 0):
                condition += 1
            # Check top right
            if self.img.getpixel((pos[0] + 1, pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check top left
            if self.img.getpixel((pos[0] + 1, pos[1] - 1)) == (0, 0, 0):
                condition += 1

            if condition <= 2:
                return 1
            else:
                return 2

        if condition == 2:
            return 1
        else:
            return 2


import os


def parenthetic_contents(string):
    stack = []

    for i, c in enumerate(string):
        if c == '{':
            stack.append(i)
        elif c == '}' and stack:
            start = stack.pop()
            yield string[start + 1: i]


def get_repeated(content, n):
    inner = list(parenthetic_contents(content))
    string = content

    j = len(inner) - 1
    new_string = string
    while j != -1:
        new_string = new_string.replace("{" + inner[j] + "}", n * inner[j])
        # print(new_string)
        j -= 1

    return new_string
