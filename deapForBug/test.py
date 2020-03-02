import random
import operator

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

def empty_pri0(out1,out2):
    return
def empty_pri1(out1,out2):
    return
def empty_pri2(out1,out2):
    return
def empty_ter0(out1,out2):
    return
def empty_ter1(out1,out2):
    return
def empty_ter2(out1,out2):
    return
def empty_ter3(out1,out2):
    return

# Initialize Multiplexer problem input and output vectors


pset = gp.PrimitiveSet("MAIN", 0)
pset.addPrimitive(empty_pri0, 2)
pset.addPrimitive(empty_pri1, 2)
pset.addPrimitive(empty_pri2, 2)
pset.addTerminal(empty_ter0)
pset.addTerminal(empty_ter1)
pset.addTerminal(empty_ter2)
pset.addTerminal(empty_ter3)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genFull, pset=pset, min_=2, max_=4)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)

pop = toolbox.population(n=3)

def evalMultiplexer(individual):
    #func = toolbox.compile(expr=individual)
    return 0,

toolbox.register("evaluate", evalMultiplexer)
toolbox.register("select", tools.selTournament, tournsize=7)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genGrow, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

def main():
#    random.seed(10)
    pop = toolbox.population(n=3)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    
    algorithms.eaSimple(pop, toolbox, 0.8, 0.1, 4, stats, halloffame=hof)
    
    return pop, stats, hof

if __name__ == "__main__":
    main()

