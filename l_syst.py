import matplotlib.pyplot as plt
import random
from PIL import Image
import math
import numpy as np
import os


class Lsystem:
    """
    A Lsystem class for each individual in the generated population

    Attributes
    ----------
    axiom : str
        The starting character of the L-system
    seed : int
        A number to initialise the program's randomness
    alphabet : list
        The characters available for rule successor creation
    alphabet_pred : list
        The characters available for rule predecessor creation
    rules : list
        The set of rules generated for each individual
    sentence : str
        The resultant sentence from applying the rules to the axiom
    gen_number : int
        The individual's storage number within the current generation
    pop_number : int
        The population number which constraints this individual
    angle : float
        The evaluated angle result from this cross-section at current actuator parameters
    fitness : float
        The fitness score of the individual's angle against the population
    ranking : int
        The ranked position (according to the fitness score) of this individual within the population
    distance : float
        A distance metric calculated relative against the population used in the calculation of the fitness score

    Methods
    ----------
    gen_rules(seed, num_rules)
        Generate rules through combining random pre-deccessor and successor selections
    form_string(sentence, rules)
        Apply the rules to the current sentence to receive the new sentence
    generate(iterations, rules)
        Call the form_string method recursively for the specified number of iterations
    l_mutate(individual, seed)
        Re-generate a random rule from the rules-set
    random_succ()
        Produce a random combination of alphabet letters
    """

    def __init__(self, axiom, seed, generated_rules=None):
        """
        Parameters
        ----------
        axiom : str
            The starting character of the L-system
        seed : int
            A number to initialise the program's randomness
        generated_rules : list, optional
            The rules to create the individual (Default is empty)
        """
        num_rules = 6  # The number of rule sets per individual
        iterations = 8  # The number of iterations that the rules will be applied to the sentence
        self.axiom = axiom
        self.alphabet = ["A", "B", "C", "D", "F", "E", "F", "H", "G", "-", "+", "F", "-", "+", "F", "-", "+", "", "{",
                         "}"]
        self.alphabet_pred = ["A", "B", "C", "D", "E", "F", "H", "G"]
        self.rules = []

        # Initialise class attributes modified by evolve script
        self.gen_number = int()
        self.pop_number = int()
        self.angle = float()
        self.fitness = []
        self.ranking = []
        self.distance = float()
        self.coords = list()

        # Generates rules if not provided
        if not generated_rules:
            self.gen_rules(seed, num_rules)
        else:
            self.rules = generated_rules

        # Apply rules to receive sentence
        self.sentence = self.generate(iterations, self.rules)  # Number of iterations

        # Ensure that sentence is viable (contains F characters) and if not to re-generate the sentence
        j = 0
        while self.sentence == -1001:
            j += 1
            self.rules = []
            self.gen_rules(j + seed, num_rules)
            self.sentence = self.generate(iterations, self.rules)
        # Add additional "F" at end of sentence - > lowers number of straight line cross-sections generated
        self.sentence = self.sentence + "F"

    def gen_rules(self, seed, num_rules):
        """
        Based on the number of rules and seed specified, this randomly combines this number of rules
        """
        # Initialise following string variables
        pred = str()
        succ = str()
        # Initialise RNG with seed
        random.seed(seed)
        np.random.seed(seed)

        # Create the specified number of rules (pre-determined)
        for i in range(num_rules):
            if i == 0:
                pred = "A"
                # For each successor, a random combination of defined alphabet characters are chosen
                succ = random.choice(self.alphabet) + random.choice(self.alphabet) + random.choice(
                    self.alphabet_pred) + random.choice(
                    self.alphabet)
            elif i == 1:
                pred = "B"
                succ = self.random_succ()
            elif i == 2:
                pred = "C"
                succ = self.random_succ()
            elif i == 3:
                pred = "D"
                succ = self.random_succ()
            elif i == 4:
                pred = "E"
                succ = self.random_succ()
            elif i == 5:
                pred = "G"
                succ = self.random_succ()
            elif i == 6:
                pred = "H"
                succ = self.random_succ()

            self.rules.append([pred, succ])

    def generate(self, iterations, rules):
        """
        Recursively calls form_string to apply the rules for the specified iterations
        """
        # Assigns the axiom to the initial sentence
        self.sentence = self.axiom
        # Initialises the number of F's in the string to zero
        num_f = 0

        # Recursively calls the form_string function for the specified number of iterations
        for count in range(iterations - 1):
            self.sentence = self.form_string(self.sentence, rules)
        # Counts the number of F's in the string
        for j in range(len(self.sentence)):
            if self.sentence[j] == "F":
                num_f += 1
        if num_f > 0:
            return self.sentence
        else:
            # If no F's are present in the string, an error code is returned
            return -1001

    def l_mutate(self):
        """
        Generates random new rule to replace old rule
        """
        new_rule = random.choice(self.alphabet) + random.choice(self.alphabet) + random.choice(
            self.alphabet) + random.choice(self.alphabet) + random.choice(self.alphabet)

        return new_rule

    def random_succ(self):
        """
        Randomly generates a combination of characters selected from a pre-defined alphabet
        """
        return random.choice(self.alphabet) + random.choice(self.alphabet) + random.choice(
            self.alphabet) + random.choice(self.alphabet) + random.choice(self.alphabet)

    @staticmethod
    def form_string(sentence, rules):
        """
        Applies the rules to each character in the sentence
        """
        # Initialise the new sentence string
        new_sentence = str()
        # Each character in the provided sentence string is compared to each rule.
        # If the rule is applicable, then the sentence's ith character is replaced by the
        # rules' successor.
        for i in range(len(sentence)):

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


class Interp:
    """
    A Interp class for each interpreted individual in the generated population.

    Attributes
    ----------
    sentence : str
        The generated string from the l-system
    target : list
        A list containing the x and y user-specified targeted coordinates
    img : list
        A list of lists containing each pixel position and colour (255,255,255)
    positions : list
        A list of floats containing all pixel positions that will be exported to Abaqus CAE

    Methods
    ----------
    direction_change(operator, direction, last_operator)
        Changes the direction according to the user's target parameters. Ensures that pixel placement does
        not occur outside of boundaries (condition) and that it adheres to defined direction limitations.
    draw(pop_number, gen_number)
        Interprets all characters in the generated sentence string, and places appropriate pixels
    get_temp_pos(direction, current_pos)
        Obtains the next possible pixel placement location according to the current position and direction
    check_neighbours(pos)
        Checks if the provided pixel placement location is viable according to the defined placement rules

    """

    def __init__(self, sentence, target):  # Initialises the class with the input parameters
        """
        Parameters
        ----------
        sentence : str
            The generated string from the l-system
        target : list
            A list containing the x and y user-specified targeted coordinates

        """
        self.sentence = sentence
        self.target = target

        # Initialises the cross-section image/grid with the dimensions of the target
        # and the position list with a starting entry
        self.img = Image.new('RGB', (self.target[0], self.target[1]), (255, 255, 255))
        self.positions = [[0, 0]]

        # Recounts the number of F's in the sentence string
        num_f = 0
        for j in range(len(self.sentence)):
            if self.sentence[j] == "F":
                num_f += 1
        # Determines the number of pixels placed per instance of character interpretation

        self.num_pixel_placement = math.ceil(self.target[0] / num_f)  # The width is divided by the number
        # of pixel placement operators (F)

    @staticmethod
    def direction_change(operator, direction, last_operator):
        """
        Determines the new direction and last operator used based on the current direction and operator
        """
        if operator == "-":
            direction -= 1
            last_operator = "-"
        if operator == "+":
            direction += 1
            last_operator = "+"

        if direction < 1:
            direction = 3
        if direction > 3:
            direction = 1
        return direction, last_operator

    def draw(self, pop_number, gen_number):
        """
        Uses the generated sentence to plot pixels according to their determined positions
        """
        # The current direction, number of "F"s and last_operator is initialised
        num_f = 0
        last_operator = "+"
        current_dir = 1
        # An initial pixel is placed at (0,0)
        self.img.putpixel((0, 0), (0, 0, 0))  # Always starts with a pixel at 0,0

        # The content between curly braces is repeated 3 times (number can be optimised)
        self.sentence = get_repeated(self.sentence, 3)

        # A while loop is implemented as a custom for loop (this is to allow loop decrements)
        # Initialise the for loop with i = 0
        i = 0
        while not i == len(self.sentence):

            # Direction change operators
            if self.sentence[i] == "-" or self.sentence[i] == "+":
                current_dir, last_operator = self.direction_change(self.sentence[i], current_dir, last_operator)
            # Pixel placement operator
            if self.sentence[i] == "F":

                # The pixel is placed at the determined position and repeated for num_pixel_placement times
                for k in range(self.num_pixel_placement):
                    temp_pos = self.get_temp_pos(current_dir, self.positions[num_f])
                    check = self.check_neighbours(temp_pos, self.target, self.img)

                    # If the pixel placement borders a valid number of neighbours, then the pixel is placed and the
                    # position is recorded
                    if check == 1:
                        num_f += 1
                        self.positions.append(temp_pos)
                        self.img.putpixel((self.positions[num_f][0], self.positions[num_f][1]), (0, 0, 0))

                    # If the number of neighbours is invalid, then the previous operator is re-applied and the process
                    # repeats
                    elif check == 4:
                        current_dir, last_operator = self.direction_change(last_operator, current_dir, last_operator)
                        i -= 1
                    # If the current operators and location is completely invalid, then the system passes the current
                    # placement
                    elif check == 3:
                        pass
            i += 1

        # If the grid still has space in the x-direction, then this is filled with the following
        # for loop

        for j in range(self.target[0] - self.positions[-1][0]):
            self.img.putpixel((self.positions[num_f][0] + j, self.positions[num_f][1]), (0, 0, 0))
            self.positions.append((self.positions[num_f][0] + j, self.positions[num_f][1]))

        # The grid is shown, named and stored in a folder
        plt.imshow(self.img)
        ax = plt.gca()
        ax.invert_yaxis()
        plt.axis("off")

        script_dir = os.path.dirname(__file__)
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
        """
        Determines the next possible pixel placement location based on th current direction and position
        """
        x = current_pos[0]
        y = current_pos[1]

        # The directions are pre-defined. See the final report for an illustration of the
        # direction placement.

        if direction == 0:
            x += 1
            y -= 1
        elif direction == 1:
            x += 1
        elif direction == 2:
            x += 1
            y += 1
        elif direction == 3:
            y += 1

        return x, y

    @staticmethod
    def check_neighbours(pos, target, img):
        """
        Determines if the provided position is valid according to pre-defined rules (based on target)
        """
        internal = 1  # condition to indicate if internal or edge case
        condition = 0  # condition to track number of interactions
        # Check canvas size limitations
        if pos[0] < 0:
            return 3
        elif pos[1] < 0:
            return 3
        elif pos[0] >= target[0]:
            return 3
        elif pos[1] >= target[1]:
            return 3

        # The following logic first checks all edge cases for potential pixel neighbours,
        # if an internal case is identified, then all internal cases are similarly checked

        # Check sides on edge cases

        if pos[0] == 0 and (0 < pos[1] < target[1] - 1):  # Left limit case only
            # Check top
            condition += 1
            internal = 0
            if img.getpixel((pos[0], pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check right
            if img.getpixel((pos[0] + 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check below
            if img.getpixel((pos[0], pos[1] - 1)) == (0, 0, 0):
                condition += 1

        elif pos[0] == target[0] - 1 and (0 < pos[1] < target[1] - 1):  # Right limit case only
            condition += 1
            internal = 0
            # Check top
            if img.getpixel((pos[0], pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check left
            if img.getpixel((pos[0] - 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check below
            if img.getpixel((pos[0], pos[1] - 1)) == (0, 0, 0):
                condition += 1

        elif pos[1] == 0 and (0 < pos[0] < target[0] - 1):  # Bottom limit case only
            condition += 1
            internal = 0
            # Check top
            if img.getpixel((pos[0], pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check left
            if img.getpixel((pos[0] - 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check right
            if img.getpixel((pos[0] + 1, pos[1])) == (0, 0, 0):
                condition += 1
        elif pos[1] == target[1] - 1 and (0 < pos[0] < target[0] - 1):  # Top limit case only
            condition += 1
            internal = 0
            # Check left
            if img.getpixel((pos[0] - 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check right
            if img.getpixel((pos[0] + 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check below
            if img.getpixel((pos[0], pos[1] - 1)) == (0, 0, 0):
                condition += 1

        elif pos[0] == 0 and pos[1] == 0:  # Left limit and Bottom limit case
            condition += 1
            internal = 0
            # Check top
            if img.getpixel((pos[0], pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check right
            if img.getpixel((pos[0] + 1, pos[1])) == (0, 0, 0):
                condition += 1

        elif pos[0] == target[0] - 1 and pos[1] == 0:  # Right limit and Bottom limit case
            condition += 1
            internal = 0
            # Check top
            if img.getpixel((pos[0], pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check left
            if img.getpixel((pos[0] - 1, pos[1])) == (0, 0, 0):
                condition += 1

        elif pos[0] == 0 and pos[1] == target[1] - 1:  # Left limit and Top limit case
            condition += 1
            internal = 0
            # Check below
            if img.getpixel((pos[0], pos[1] - 1)) == (0, 0, 0):
                condition += 1
            # Check right
            if img.getpixel((pos[0] + 1, pos[1])) == (0, 0, 0):
                condition += 1

        elif pos[0] == target[0] - 1 and pos[1] == target[1] - 1:  # Right limit and Top limit case
            condition += 1
            internal = 0
            # Check below
            if img.getpixel((pos[0], pos[1] - 1)) == (0, 0, 0):
                condition += 1
            # Check left
            if img.getpixel((pos[0] - 1, pos[1])) == (0, 0, 0):
                condition += 1

        # If one of the above cases is not true, then internal will equal to 1. Resulting
        # in the following logic being executed

        # Check sides on internal cases
        if not internal == 0:
            # Check top
            if img.getpixel((pos[0], pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check left
            if img.getpixel((pos[0] - 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check right
            if img.getpixel((pos[0] + 1, pos[1])) == (0, 0, 0):
                condition += 1
            # Check below
            if img.getpixel((pos[0], pos[1] - 1)) == (0, 0, 0):
                condition += 1
            # Check below left
            if img.getpixel((pos[0] - 1, pos[1] - 1)) == (0, 0, 0):
                condition += 1
            # Check below right
            if img.getpixel((pos[0] + 1, pos[1] - 1)) == (0, 0, 0):
                condition += 1
            # Check top right
            if img.getpixel((pos[0] + 1, pos[1] + 1)) == (0, 0, 0):
                condition += 1
            # Check top left
            if img.getpixel((pos[0] + 1, pos[1] - 1)) == (0, 0, 0):
                condition += 1

            # If the interior case pixel location has 2 or fewer neighbours,
            # then the programs return a successful code (1). Otherwise, an
            # unsuccessful code (4) is returned

            if condition <= 2:
                return 1
            else:
                return 4

        # If the exterior case pixel location has 2 neighbours,
        # then the programs return a successful code (1). Otherwise, an
        # unsuccessful code (4) is returned

        if condition == 2:
            return 1
        else:
            return 4


def get_in_brackets(sen):
    """
    Returns each level of content located within curly brackets. Note this function is modified
    from a stackoverflow user's response :
    https://stackoverflow.com/questions/4284991/parsing-nested-parentheses-in-python-grab-content-by-level
    """

    # A push/pop is implemented, with a list, to locate the content within nested curly braces
    stack = []

    for i, c in enumerate(sen):
        if c == '{':
            stack.append(i)
        elif c == '}' and stack:
            start = stack.pop()
            yield sen[start + 1: i]


def get_repeated(content, n):
    """
    Multiplies nested levels of content within curly brackets
    """
    inner = list(get_in_brackets(content))
    sen = content

    # The inner sentence content of each layer is multiplied by n.
    j = len(inner) - 1
    new_sen = sen
    while j != -1:
        new_sen = new_sen.replace("{" + inner[j] + "}", n * inner[j])
        j -= 1

    return new_sen
