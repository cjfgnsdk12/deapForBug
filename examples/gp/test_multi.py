import copy
import math
import random
import re
import sys
import warnings

from collections import defaultdict, deque
from functools import partial, wraps
from inspect import isclass
from operator import eq, lt

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
def empty_pri3(out1,out2):
    return

def empty_ter0(out1,out2):
    test = 'dict0'
    return
def empty_ter1(out1,out2):
    test = 'dict1'
    return
def empty_ter2(out1,out2):
    test = 'dict2'
    return
def empty_ter3(out1,out2):
    return
def empty_ter4(out1,out2):
    return

def generate(pset, min_, max_,condition, type_=None):
    """Generate a Tree as a list of list. The tree is build
    from the root to the leaves, and it stop growing when the
    condition is fulfilled.

    :param pset: Primitive set from which primitives are selected.
    :param min_: Minimum height of the produced trees.
    :param max_: Maximum Height of the produced trees.
    :param condition: The condition is a function that takes two arguments,
                      the height of the tree to build and the current
                      depth in the tree.
    :param type_: The type that should return the tree when called, when
                  :obj:`None` (default) the type of :pset: (pset.ret)
                  is assumed.
    :returns: A grown tree with leaves at possibly different depths
              depending on the condition function.
    """
    if type_ is None:
        type_ = pset.ret
    expr = []
    #height = random.randint(min_, max_)
    stack = [(0, type_)]
    idx_tree=0
    idx_pri=0
    idx_ter=0
    while len(stack) != 0:
        depth, type_ = stack.pop()
        # make terminal node
        if (tree_arr[idx_tree]=='t')|(condition(max_,depth)):
            idx_tree+=1
            try:
                if(idx_ter<term_count):
                    term = pset.terminals[type_][idx_ter]
                    idx_ter+=1
                else:
                    continue
            except IndexError:
                _, _, traceback = sys.exc_info()
            if isclass(term):
                term = term()
            expr.append(term)
        # make primitive node
        else:
            idx_tree+=1
            try:
                if(idx_pri<pset.prims_count):
                    prim = pset.primitives[type_][idx_pri]
                    idx_pri+=1
                else:
                    continue
            except IndexError:
                _, _, traceback = sys.exc_info()
            expr.append(prim)
            for arg in reversed(prim.args):
                stack.append((depth + 1, arg))
    return expr

def genFull(pset, min_, max_, type_=None):
    """Generate an expression where each leaf has the same depth
    between *min* and *max*.

    :param pset: Primitive set from which primitives are selected.
    :param min_: Minimum height of the produced trees.
    :param max_: Maximum Height of the produced trees.
    :param type_: The type that should return the tree when called, when
                  :obj:`None` (default) the type of :pset: (pset.ret)
                  is assumed.
    :returns: A full tree with all leaves at the same depth.
    """

    def condition(height, depth):
        """Expression generation stops when the depth is equal to height."""
        return depth == height

    return generate(pset, min_, max_, condition, type_)

pset = gp.PrimitiveSet("MAIN", 0)
pset.addPrimitive(empty_pri0, 2)
pset.addPrimitive(empty_pri1, 2)
pset.addPrimitive(empty_pri2, 2)
pset.addPrimitive(empty_pri3, 2)
pset.addTerminal(empty_ter0)
pset.addTerminal(empty_ter1)
pset.addTerminal(empty_ter2)
pset.addTerminal(empty_ter3)
pset.addTerminal(empty_ter4)

term_count=5
tree_arr=['p','p','t','p','t','t','p','t','t']

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("expr", genFull, pset=pset, min_=2, max_=4)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)

def eval(individual):
    return 0,

toolbox.register("evaluate", eval)
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