import random
import math
import numpy as np
import l_syst

from evolve import Evolution

## Test for abstraction
test = l_syst.Lsystem("A",1)
print(test.rules)
print(test.sentence)
string = test.sentence
target = [100,100]
test_output = l_syst.Interp(string,target)
test_output.draw(1,1)

## Test for reusability

test_output_2 = l_syst.Interp('F+F-F-FF+F',target)
test_output_2.draw(1,1)
test_output_3 = l_syst.Interp('F+F-F-{FF+F}',target)
test_output_3.draw(1,1)
test_output_3 = l_syst.Interp('F+{F-F-{FF+F}}',target)
test_output_3.draw(1,1)


## Test for conditionals and parameters

test_output_4 = l_syst.Interp('F+F-F-FF+F',[20,20])
test_output_4.draw(1,1)

test_output_5 = l_syst.Interp('F+F-F-FF+F',[30,20])
test_output_5.draw(1,1)

test_output_6 = l_syst.Interp('F+F-F-FF+F',[110,30])
test_output_6.draw(1,1)


## Test for conditionals and parameters

test_output_4 = l_syst.Interp('F+F-F-FF+F',[20,20])
test_output_4.draw(1,1)

test_output_5 = l_syst.Interp('F+F-F-FF+F',[30,20])
test_output_5.draw(1,1)

test_output_6 = l_syst.Interp('F+F-F-FF+F',[110,30])
test_output_6.draw(1,1)

## Test for operational variations

# Two l-system sets of rules are required

test_l_1 = l_syst.Lsystem("A",2)
rules_1 = test_l_1.rules
print("Rules 1")
print(rules_1)
test_l_2 = l_syst.Lsystem("A",3)
rules_2 = test_l_2.rules
print("Rules 2")
print(rules_2)
rules_2 = test_l_2.rules
test_evo = Evolution(1, 1, [1,1], 1)  # cycles, seed, seed
test_evo.axiom = "A"


result_cross = test_evo.crossover(test_l_1,test_l_2,1)
print("New rules 1")
print(result_cross[0].rules)
print("New rules 2")
print(result_cross[1].rules)


